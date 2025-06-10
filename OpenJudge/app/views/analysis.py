import os
import base64
import uuid
from datetime import datetime,timezone
from flask import request, jsonify, Blueprint,current_app
from app.views import api
from app.models import db
from app.models.analysis_task import AnalysisTask
from app.utils.time_convert import to_rfc3339_seconds_zulu
from app.tasks import process_judge
from app.utils.auth import login_required_api


@api.route("/judge", methods=["POST"])
@login_required_api
def submit_judge():
    """提交判题请求"""
    try:
        if not request.is_json or request.get_json(silent=True) is None:
            return jsonify({"error": "invalid_request", "detail": "Request must be valid JSON."}), 400

        data = request.get_json()
        problem_id = data.get("problem_id")
        user_code = data.get("code")
        # 使用当前登录用户的ID（整数）
        user_id = request.current_user.id

        # 必填字段校验
        if not problem_id or not user_code:
            return jsonify({"error": "missing_param", "detail": "problem_id and code are required"}), 400
        
        # problem_id 校验
        if not isinstance(problem_id, (str, int)):
            return jsonify({"error": "invalid_problem_id", "detail": "problem_id must be a string or integer"}), 400
        
        if not str(problem_id).isdigit() or not (1 <= int(problem_id) <= 10):
            return jsonify({"error": "invalid_problem_id", "detail": "problem_id must be between 1 and 10"}), 400

        # 代码长度校验
        if not isinstance(user_code, str):
            return jsonify({"error": "invalid_code", "detail": "code must be a string"}), 400
        
        if len(user_code.strip()) == 0:
            return jsonify({"error": "empty_code", "detail": "code cannot be empty"}), 400
        
        if len(user_code) > 50000:  # 50KB限制
            return jsonify({"error": "code_too_long", "detail": "code cannot exceed 50KB"}), 400

        # detect dangerous code patterns
        dangerous_patterns = [
            'import os', 'import subprocess', 'import sys', 'import socket', 
            'import requests', 'import urllib', 'import shutil', 'import glob',
            'eval(', 'exec(', '__import__', 'open(', 'file(',
            'rmdir', 'remove', 'delete', 'kill'
        ]
        
        user_code_lower = user_code.lower()
        for pattern in dangerous_patterns:
            if pattern in user_code_lower:
                return jsonify({
                    "error": "unsafe_code", 
                    "detail": f"Code contains potentially unsafe pattern: {pattern}"
                }), 400

        submission_id = str(uuid.uuid4())

        # 存入数据库
        task = AnalysisTask(
            submission_id=submission_id,
            user_id=user_id,
            problem_id=problem_id,
            code=user_code,
            result="pending"
        )
        db.session.add(task)
        db.session.commit()

        # 调用 Celery 异步任务
        process_judge.delay(submission_id, problem_id, user_code)
        
        return jsonify({
            "submission_id": task.submission_id,
            "user_id": task.user_id,
            "problem_id": task.problem_id,
            "result": "pending",
            "created_at": to_rfc3339_seconds_zulu(task.created_at) if task.created_at else None,
            "updated_at": to_rfc3339_seconds_zulu(task.updated_at) if task.updated_at else None
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "unexpected_error", "detail": str(e)}), 500


@api.route("/judge", methods=["GET"])
@login_required_api
def get_judge_result():
    """获取判题结果"""
    try:
        submission_id = request.args.get("submission_id")

        if not submission_id:
            return jsonify({
                "error": "missing_submission_id",
                "detail": "The submission_id query parameter is required."
            }), 400

        # submission_id 格式校验 (UUID)
        try:
            uuid.UUID(submission_id)
        except ValueError:
            return jsonify({
                "error": "invalid_submission_id",
                "detail": "submission_id must be a valid UUID."
            }), 400

        task = db.session.get(AnalysisTask, submission_id)

        if not task:
            return jsonify({
                "error": "not_found",
                "detail": "No submission found with the given submission_id."
            }), 404

        # 检查是否是当前用户的提交
        if str(task.user_id) != str(request.current_user.id):
            return jsonify({
                "error": "forbidden",
                "detail": "You can only access your own submissions."
            }), 403

        return jsonify({
            "submission_id": task.submission_id,
            "user_id": task.user_id,
            "problem_id": task.problem_id,
            "code": task.code,
            "result": task.result,
            "stdout": task.stdout,
            "testcase_result": task.testcase_result,
            "created_at": to_rfc3339_seconds_zulu(task.created_at) if task.created_at else None,
            "updated_at": to_rfc3339_seconds_zulu(task.updated_at) if task.updated_at else None,
        }), 200

    except Exception as e:
        return jsonify({
            "error": "internal_error",
            "detail": str(e)
        }), 500


@api.route("/judge/list", methods=["GET"])
@login_required_api
def list_judge_tasks():
    """获取当前用户的判题任务（用于调试）"""
    try:
        # 可选的分页参数
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)  # 最多100条
        
        # 只返回当前用户的任务
        tasks = AnalysisTask.query.filter_by(user_id=request.current_user.id).order_by(AnalysisTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "tasks": [task.to_dict() for task in tasks.items],
            "total": tasks.total,
            "page": page,
            "per_page": per_page,
            "pages": tasks.pages
        }), 200
    except Exception as e:
        return jsonify({
            "error": "internal_error",
            "detail": str(e)
        }), 500


@api.route("/analysis", methods=["POST"])
def submit_analysis():
    """提交代码分析请求"""
    try:
        if not request.is_json or request.get_json(silent=True) is None:
            return jsonify({"error": "invalid_request", "detail": "Request must be valid JSON."}), 400

        data = request.get_json()
        problem_id = data.get("problem_id")
        user_code = data.get("code")
        language = data.get("language")
        user_id = data.get("user_id", "anonymous")

        # 必填字段校验
        if not problem_id or not user_code or not language:
            return jsonify({"error": "missing_param", "detail": "problem_id, code, and language are required"}), 400
        
        # problem_id 校验
        if not isinstance(problem_id, (str, int)):
            return jsonify({"error": "invalid_problem_id", "detail": "problem_id must be a string or integer"}), 400
        
        if not str(problem_id).isdigit() or not (1 <= int(problem_id) <= 10):
            return jsonify({"error": "invalid_problem_id", "detail": "problem_id must be between 1 and 10"}), 400

        # 代码长度校验
        if not isinstance(user_code, str):
            return jsonify({"error": "invalid_code", "detail": "code must be a string"}), 400
        
        if len(user_code.strip()) == 0:
            return jsonify({"error": "empty_code", "detail": "code cannot be empty"}), 400
        
        if len(user_code) > 50000:  # 50KB限制
            return jsonify({"error": "code_too_long", "detail": "code cannot exceed 50KB"}), 400

        # 语言校验
        if not isinstance(language, str):
            return jsonify({"error": "invalid_language", "detail": "language must be a string"}), 400
        
        if not language.strip():
            return jsonify({"error": "empty_language", "detail": "language cannot be empty"}), 400
        
        supported_languages = ["python", "java", "cpp", "c", "javascript"]
        if language not in supported_languages:
            return jsonify({
                "error": "unsupported_language", 
                "detail": f"language must be one of: {', '.join(supported_languages)}"
            }), 400

        # user_id 校验 - 检查是否显式传入空字符串
        if "user_id" in data:
            # 如果显式提供了user_id，则进行校验
            if not isinstance(user_id, str):
                return jsonify({"error": "invalid_user_id", "detail": "user_id must be a string"}), 400
            
            if not user_id.strip():
                return jsonify({"error": "empty_user_id", "detail": "user_id cannot be empty"}), 400
            
            if len(user_id) > 100:
                return jsonify({"error": "invalid_user_id", "detail": "user_id cannot exceed 100 characters"}), 400

        # 检查恶意代码模式
        dangerous_patterns = [
            'import os', 'import subprocess', 'import sys', 'import socket', 
            'import requests', 'import urllib', 'import shutil', 'import glob',
            'eval(', 'exec(', '__import__', 'open(', 'file(',
            'rmdir', 'remove', 'delete', 'kill'
        ]
        
        user_code_lower = user_code.lower()
        for pattern in dangerous_patterns:
            if pattern in user_code_lower:
                return jsonify({
                    "error": "unsafe_code", 
                    "detail": f"Code contains potentially unsafe pattern: {pattern}"
                }), 400

        submission_id = str(uuid.uuid4())

        # 存入数据库
        task = AnalysisTask(
            submission_id=submission_id,
            user_id=user_id,
            problem_id=problem_id,
            code=user_code,
            result="pending"
        )
        db.session.add(task)
        db.session.commit()

        # 调用 Celery 异步任务
        process_judge.delay(submission_id, problem_id, user_code)
        
        return jsonify({
            "id": task.submission_id,
            "task_id": task.submission_id,
            "submission_id": task.submission_id,
            "status": "pending",
            "user_id": task.user_id,
            "problem_id": task.problem_id,
            "language": language,
            "created_at": to_rfc3339_seconds_zulu(task.created_at) if task.created_at else None
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "unexpected_error", "detail": str(e)}), 500


@api.route("/analysis/<submission_id>", methods=["GET"])
def get_analysis_result(submission_id):
    """获取代码分析结果"""
    try:
        # submission_id 格式校验 (UUID)
        try:
            uuid.UUID(submission_id)
        except ValueError:
            return jsonify({
                "error": "invalid_submission_id",
                "detail": "submission_id must be a valid UUID."
            }), 400

        task = db.session.get(AnalysisTask, submission_id)

        if not task:
            return jsonify({
                "error": "not_found",
                "detail": "No submission found with the given submission_id."
            }), 404

        # 根据result字段确定status
        if task.result == "pending":
            status = "pending"
        elif task.result in ["processing", "running"]:
            status = "processing"
        elif task.testcase_result:
            # 解析测试结果
            import json
            try:
                test_results = json.loads(task.testcase_result)
                if isinstance(test_results, list):
                    all_passed = all(result.get("pass", False) for result in test_results)
                    status = "completed" if all_passed else "completed"
                else:
                    status = "completed"
            except:
                status = "completed"
        else:
            status = "completed"

        response = {
            "id": task.submission_id,
            "task_id": task.submission_id,
            "submission_id": task.submission_id,
            "status": status,
            "user_id": task.user_id,
            "problem_id": task.problem_id,
            "code": task.code,
            "result": task.result,
            "stdout": task.stdout,
            "created_at": to_rfc3339_seconds_zulu(task.created_at) if task.created_at else None,
            "updated_at": to_rfc3339_seconds_zulu(task.updated_at) if task.updated_at else None,
        }

        # 添加测试结果详情
        if task.testcase_result:
            try:
                import json
                test_results = json.loads(task.testcase_result)
                response["results"] = test_results
            except:
                response["results"] = []

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "error": "internal_error",
            "detail": str(e)
        }), 500


def submit_judge_internal(data):
    """内部判题提交函数，供Web界面调用"""
    try:
        problem_id = data.get("problem_id")
        user_code = data.get("code")
        user_id = data.get("user_id", "anonymous")

        # 必填字段校验
        if not problem_id or not user_code:
            return {"success": False, "error": "problem_id and code are required"}
        
        # problem_id 校验
        if not isinstance(problem_id, (str, int)):
            return {"success": False, "error": "problem_id must be a string or integer"}
        
        if not str(problem_id).isdigit() or not (1 <= int(problem_id) <= 10):
            return {"success": False, "error": "problem_id must be between 1 and 10"}

        # 代码长度校验
        if not isinstance(user_code, str):
            return {"success": False, "error": "code must be a string"}
        
        if len(user_code.strip()) == 0:
            return {"success": False, "error": "code cannot be empty"}
        
        if len(user_code) > 50000:  # 50KB限制
            return {"success": False, "error": "code cannot exceed 50KB"}

        # user_id 校验
        if user_id and not isinstance(user_id, str):
            return {"success": False, "error": "user_id must be a string"}
        
        if user_id and len(user_id) > 100:
            return {"success": False, "error": "user_id cannot exceed 100 characters"}

        # 检查恶意代码模式
        dangerous_patterns = [
            'import os', 'import subprocess', 'import sys', 'import socket', 
            'import requests', 'import urllib', 'import shutil', 'import glob',
            'eval(', 'exec(', '__import__', 'open(', 'file(',
            'rmdir', 'remove', 'delete', 'kill'
        ]
        
        user_code_lower = user_code.lower()
        for pattern in dangerous_patterns:
            if pattern in user_code_lower:
                return {"success": False, "error": f"Code contains potentially unsafe pattern: {pattern}"}

        submission_id = str(uuid.uuid4())

        # 存入数据库
        task = AnalysisTask(
            submission_id=submission_id,
            user_id=user_id,
            problem_id=problem_id,
            code=user_code,
            result="pending"
        )
        db.session.add(task)
        db.session.commit()

        # 调用 Celery 异步任务
        process_judge.delay(submission_id, problem_id, user_code)
        
        return {
            "success": True,
            "submission_id": task.submission_id,
            "user_id": task.user_id,
            "problem_id": task.problem_id,
            "result": "pending"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

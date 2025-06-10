from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.routes.problems import problems
from app.models.analysis_task import AnalysisTask
from app.models import db
from app.utils.auth import login_required_web, get_current_user
import requests
import json
from datetime import datetime

# 创建web blueprint
web = Blueprint('web', __name__, template_folder='../templates', static_folder='../static')

def from_json(value):
    """Jinja2 filter to parse JSON strings"""
    try:
        return json.loads(value) if value else []
    except (json.JSONDecodeError, TypeError):
        return []

# 注册自定义 Jinja2 filter
web.add_app_template_filter(from_json, 'from_json')

@web.route('/login')
def login():
    """登录页面"""
    # 如果已经登录，跳转到首页
    user = get_current_user()
    if user:
        return redirect(url_for('web.homepage'))
    return render_template('auth/login.html')

@web.route('/register')
def register():
    """注册页面"""
    # 如果已经登录，跳转到首页
    user = get_current_user()
    if user:
        return redirect(url_for('web.homepage'))
    return render_template('auth/register.html')

@web.route('/')
@login_required_web
def homepage():
    """首页 - 显示当前用户的提交记录"""
    # 只显示当前用户的提交记录，增加到100条
    current_user = request.current_user
    
    # 获取用户的总提交数量
    total_submissions = AnalysisTask.query.filter_by(user_id=str(current_user.id)).count()
    
    # 获取最新的100条提交记录
    submissions = AnalysisTask.query.filter_by(user_id=str(current_user.id)).order_by(AnalysisTask.created_at.desc()).limit(100).all()
    
    return render_template('homepage.html', 
                         submissions=submissions, 
                         problems=problems,
                         current_user=current_user,
                         total_submissions=total_submissions)

@web.route('/problems')
@login_required_web
def problems_list():
    """问题列表页面"""
    return render_template('problems.html', 
                         problems=problems,
                         current_user=request.current_user)

@web.route('/submit/<problem_id>')
@login_required_web
def submit_form(problem_id):
    """代码提交表单页面"""
    problem = problems.get(problem_id)
    if not problem:
        flash('Problem not found', 'error')
        return redirect(url_for('web.problems_list'))
    
    return render_template('submit_form.html', 
                         problem_id=problem_id, 
                         problem=problem,
                         current_user=request.current_user)

@web.route('/submit', methods=['POST'])
@login_required_web
def submit_code():
    """处理代码提交"""
    problem_id = request.form.get('problem_id')
    code = request.form.get('code')
    
    if not problem_id or not code:
        flash('Problem ID and code are required', 'error')
        return redirect(url_for('web.problems_list'))
    
    if problem_id not in problems:
        flash('Invalid problem ID', 'error')
        return redirect(url_for('web.problems_list'))
    
    # 调用内部API提交代码
    try:
        # 构造内部API请求，使用当前登录用户的ID
        current_user = request.current_user
        api_data = {
            "problem_id": problem_id,
            "code": code,
            "user_id": str(current_user.id)
        }
        
        # 这里我们直接使用数据库而不是HTTP请求，避免循环依赖
        from app.views.analysis import submit_judge_internal
        
        # 调用内部函数
        result = submit_judge_internal(api_data)
        
        if result['success']:
            flash('Code submitted successfully!', 'success')
        else:
            flash(f'Submission failed: {result["error"]}', 'error')
            
    except Exception as e:
        flash(f'Submission error: {str(e)}', 'error')
    
    # 提交后跳转到首页
    return redirect(url_for('web.homepage'))

@web.route('/submission/<submission_id>')
@login_required_web
def view_submission(submission_id):
    """查看单个提交详情"""
    submission = AnalysisTask.query.get_or_404(submission_id)
    
    # 检查是否是当前用户的提交
    current_user = request.current_user
    if str(submission.user_id) != str(current_user.id):
        flash('You can only view your own submissions', 'error')
        return redirect(url_for('web.homepage'))
    
    problem = problems.get(submission.problem_id, {})
    
    return render_template('submission_detail.html', 
                         submission=submission, 
                         problem=problem,
                         current_user=current_user)

@web.route('/api/submission/<submission_id>')
@login_required_web
def get_submission_detail(submission_id):
    """获取单个提交的详细信息的API"""
    print(f"\n=== Submission Detail Request: {submission_id} ===")
    
    submission = AnalysisTask.query.get_or_404(submission_id)
    
    # 检查是否是当前用户的提交
    current_user = request.current_user
    if str(submission.user_id) != str(current_user.id):
        return jsonify({'error': 'You can only view your own submissions'}), 403
    
    problem = problems.get(submission.problem_id, {})
    
    print(f"Problem ID: {submission.problem_id}")
    print(f"Submission Status: {submission.result}")
    print(f"Raw testcase_result: {submission.testcase_result}")
    
    # 解析测试结果
    test_results = []
    if submission.testcase_result:
        try:
            judge_output = json.loads(submission.testcase_result)
            print(f"Parsed judge output: {json.dumps(judge_output, indent=2)}")
            
            # 从judge_output中获取results
            test_results = judge_output.get('results', [])
            
            # 如果有错误消息，添加到test_results中
            if judge_output.get('message') and not test_results:
                test_results = [{
                    'input': '',
                    'expected': '',
                    'actual': '',
                    'error': judge_output['message'],
                    'pass': False
                }]
            
            print(f"Extracted test results: {json.dumps(test_results, indent=2)}")
        except Exception as e:
            print(f"Error parsing test results: {str(e)}")
            test_results = []
    else:
        print("No test results found")
    
    response_data = {
        'id': submission.submission_id,
        'problem': {
            'id': submission.problem_id,
            'description': problem.get('description', 'Unknown problem')
        },
        'code': submission.code,
        'result': submission.result,
        'test_results': test_results,
        'stdout': submission.stdout,
        'created_at': submission.created_at.strftime('%Y-%m-%d %H:%M') if submission.created_at else 'Unknown'
    }
    
    print(f"Response data: {json.dumps(response_data, indent=2)}")
    print("=== End of Request ===\n")
    
    return jsonify(response_data) 
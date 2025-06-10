import os
import json
import subprocess
import tempfile
import signal
import sys
from typing import Dict, List, Optional, Tuple

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out")

def run_code(code: str, input_data: str, timeout: int = 2) -> tuple[Optional[str], Optional[str]]:
    """
    在沙箱中运行用户代码
    :param code: 用户代码
    :param input_data: 输入数据
    :param timeout: 超时时间（秒）
    :return: (输出结果, 错误信息)
    """
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        # 设置超时处理器
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        # 运行代码
        process = subprocess.Popen(
            ['python3', temp_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(input=input_data, timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            return None, "Execution timed out"
        finally:
            # 取消超时
            signal.alarm(0)
        
        if process.returncode != 0:
            return None, stderr.strip()
        return stdout.strip(), None

    except TimeoutError:
        return None, "Execution timed out"
    except Exception as e:
        return None, str(e)
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file)
        except:
            pass

def read_testcases(file_path: str) -> List[Tuple[str, str]]:
    """
    读取测试用例文件
    :param file_path: 测试用例文件路径
    :return: 测试用例列表，每个用例为 (输入, 期望输出) 的元组
    """
    testcases = []
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for i in range(0, len(lines), 2):
                if i + 1 < len(lines):
                    input_data = lines[i].strip()
                    expected_output = lines[i + 1].strip()
                    testcases.append((input_data, expected_output))
    except Exception as e:
        raise Exception(f"Error reading testcases: {str(e)}")
    return testcases

def evaluate_testcase(code: str, input_data: str, expected_output: str) -> Dict:
    """
    评测单个测试用例
    """
    actual_output, error = run_code(code, input_data)
    
    if error:
        return {
            "input": input_data,
            "expected": expected_output,
            "actual": None,
            "pass": False,
            "error": error
        }

    # 标准化输出（去除首尾空白字符）
    actual_output = actual_output.strip() if actual_output else ""
    expected_output = expected_output.strip()
    
    return {
        "input": input_data,
        "expected": expected_output,
        "actual": actual_output,
        "pass": actual_output == expected_output,
        "error": None
    }

def judge_submission(problem_id: str, submission_id: str, user_code: str) -> Dict:
    """
    判题主函数
    :param problem_id: 问题ID
    :param submission_id: 提交ID
    :param user_code: 用户代码
    :return: 判题结果
    """
    if not all([problem_id, submission_id, user_code.strip()]):
        return {
            "status": "err",
            "message": "Missing required parameters or empty code",
            "results": []
        }

    # 构建问题目录路径 - 相对于app目录
    app_dir = os.path.dirname(os.path.abspath(__file__))
    problem_dir = os.path.join(app_dir, '..', 'problems', str(problem_id))
    testcases_file = os.path.join(problem_dir, 'testcases.txt')
    
    # 调试信息
    debug_info = {
        "app_dir": app_dir,
        "problem_dir": problem_dir,
        "testcases_file": testcases_file,
        "file_exists": os.path.exists(testcases_file)
    }
    
    if not os.path.exists(testcases_file):
        return {
            "status": "err",
            "message": f"Test cases file not found: {testcases_file}",
            "debug": debug_info,
            "results": []
        }

    # 读取测试用例
    try:
        testcases = read_testcases(testcases_file)
        if not testcases:
            return {
                "status": "err",
                "message": "No test cases found",
                "results": []
            }
    except Exception as e:
        return {
            "status": "err",
            "message": str(e),
            "results": []
        }

    # 评测所有测试用例
    results = []
    for input_data, expected_output in testcases:
        result = evaluate_testcase(user_code, input_data, expected_output)
        results.append(result)

    # 确定整体状态
    if any(r.get('error') for r in results):
        status = "err"
        message = next(r['error'] for r in results if r.get('error'))
    elif all(r['pass'] for r in results):
        status = "ok"
        message = None
    else:
        status = "fail"
        message = None

    # 输出结果
    output = {
        "status": status,
        "results": results
    }
    if message:
        output["message"] = message

    return output 
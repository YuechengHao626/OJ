import os
import subprocess
import json
from celery import Celery
from app.models import db
from app.models.analysis_task import AnalysisTask
from app import create_app
from datetime import datetime
from app.utils.judge import judge_submission

# Celery 配置
celery = Celery('coughoverflow')
celery.conf.broker_url = 'sqs://'
celery.conf.task_default_queue = "celery"
celery.conf.broker_transport_options = {
    "region": "us-east-1"
}

raw_db_url = os.environ.get("DATABASE_URL", "")
if raw_db_url.startswith("postgresql://"):
    celery.conf.result_backend = raw_db_url.replace("postgresql://", "db+postgresql://", 1)
else:
    celery.conf.result_backend = raw_db_url

@celery.task(name='process_judge', bind=True)
def process_judge(self, submission_id: str, problem_id: str, user_code: str):
    """处理判题任务"""
    try:
        self.update_state(state='STARTED')
        
        # 直接调用本地判题函数，不再使用docker容器
        judge_output = judge_submission(problem_id, submission_id, user_code)
        
        # 确保judge_output有results字段
        if 'results' not in judge_output:
            judge_output['results'] = []
        
        # 映射状态到数据库字段
        status = judge_output.get('status', 'err')
        if status == 'ok':
            final_result = "accepted"
        elif status == 'fail':
            final_result = "wrong_answer"
        else:  # status == 'err'
            final_result = "error"
        
        # 更新数据库
        app = create_app()
        with app.app_context():
            task = db.session.get(AnalysisTask, submission_id)
            if task:
                # 存储结果
                testcase_result = json.dumps(judge_output)  # 保存完整的judge_output
                
                # 映射judge状态到数据库状态
                status_mapping = {
                    'ok': 'ok',  # 直接显示为PASS
                    'fail': 'fail',
                    'err': 'error'
                }
                
                db_status = status_mapping.get(status, 'error')
                
                task.result = db_status
                task.status = 'completed'  # 不再使用中间状态
                task.updated_at = datetime.utcnow()
                task.testcase_result = testcase_result
                task.stdout = json.dumps(judge_output)  # 将judge输出作为stdout
            db.session.commit()
        
        return {
            'status': 'SUCCESS',
            'submission_id': submission_id,
            'judge_status': final_result,
            'result': judge_output
        }
    
    except Exception as e:
        print(f"[ERROR] Celery failed to process task {submission_id}: {e}")
        
        final_result = "error"
        judge_output = {
            "status": "err",
            "message": str(e),
            "results": [{
                "input": "",
                "expected_output": "",
                "actual_output": str(e),
                "pass": False
            }]
        }
        
        app = create_app()
        with app.app_context():
            task = db.session.get(AnalysisTask, submission_id)
            if task:
                task.result = final_result
                task.stdout = f"Internal error: {str(e)}"
                task.testcase_result = json.dumps(judge_output)  # 保存完整的judge_output
                db.session.commit()
        
        self.update_state(state='FAILURE')
        return {
            'status': 'FAILURE',
            'error': str(e),
            'submission_id': submission_id
        }

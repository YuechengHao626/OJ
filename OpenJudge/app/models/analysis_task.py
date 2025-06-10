from datetime import datetime, timezone
from app.models import db
from app.utils.time_convert import to_rfc3339_seconds_zulu

class AnalysisTask(db.Model):
    __tablename__ = 'analysis_tasks'

    submission_id = db.Column(db.String(36), primary_key=True)  # UUID 字符串
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 关联用户ID
    problem_id = db.Column(db.String(10), nullable=False)
    code = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(20), default="pending")  # pending/accepted/wrong_answer/runtime_error/time_limit_exceeded
    stdout = db.Column(db.Text)  # 运行输出
    testcase_result = db.Column(db.JSON)  # 测试用例结果详情
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间（时区敏感）
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 更新时间（时区敏感）

    # 关系定义
    user = db.relationship('User', backref='analysis_tasks')

    def to_dict(self):
        """将模型转换为字典格式"""
        return {
            "submission_id": self.submission_id,
            "user_id": self.user_id,
            "problem_id": self.problem_id,
            "code": self.code,
            "result": self.result,
            "stdout": self.stdout,
            "testcase_result": self.testcase_result,
            "created_at": to_rfc3339_seconds_zulu(self.created_at) if self.created_at else None,
            "updated_at": to_rfc3339_seconds_zulu(self.updated_at) if self.updated_at else None,
        }

    def __repr__(self):
        return f"<AnalysisTask {self.submission_id}>"

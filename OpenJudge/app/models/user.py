from datetime import datetime, timezone
import bcrypt
from app.models import db
from sqlalchemy import String, DateTime, Text


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(String(255), nullable=False)
    salt = db.Column(String(255), nullable=False)
    created_at = db.Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __init__(self, username, password):
        self.username = username
        self.set_password(password)
    
    def set_password(self, password):
        """设置密码，自动生成盐值并散列"""
        # 生成随机盐值
        self.salt = bcrypt.gensalt().decode('utf-8')
        # 使用盐值+密码进行散列
        combined = (password + self.salt).encode('utf-8')
        self.password_hash = bcrypt.hashpw(combined, bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        if not self.password_hash or not self.salt:
            return False
        # 使用相同的盐值+密码组合进行验证
        combined = (password + self.salt).encode('utf-8')
        return bcrypt.checkpw(combined, self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>' 
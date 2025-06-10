import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app, redirect, url_for
from app.models import db
from app.models.user import User


def generate_jwt_token(user_id, username):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),  # 24小时过期
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def verify_jwt_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """从请求中获取当前用户"""
    token = request.cookies.get('access_token')
    if not token:
        return None
    
    payload = verify_jwt_token(token)
    if not payload:
        return None
    
    user = User.query.get(payload['user_id'])
    return user


def login_required_api(f):
    """API路由的登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({'error': 'unauthorized', 'detail': 'Access token required'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'unauthorized', 'detail': 'Invalid or expired token'}), 401
        
        # 验证用户是否存在
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'unauthorized', 'detail': 'User not found'}), 401
        
        # 将用户信息添加到请求上下文
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def login_required_web(f):
    """Web页面的登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return redirect(url_for('web.login'))
        
        payload = verify_jwt_token(token)
        if not payload:
            return redirect(url_for('web.login'))
        
        # 验证用户是否存在
        user = User.query.get(payload['user_id'])
        if not user:
            return redirect(url_for('web.login'))
        
        # 将用户信息添加到请求上下文
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function 
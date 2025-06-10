from flask import request, jsonify, make_response
from app.views import api
from app.models import db
from app.models.user import User
from app.utils.auth import generate_jwt_token
import re


@api.route("/register", methods=["POST"])
def register():
    """用户注册API"""
    try:
        if not request.is_json or request.get_json(silent=True) is None:
            return jsonify({"error": "invalid_request", "detail": "Request must be valid JSON."}), 400

        data = request.get_json()
        username = data.get("username", "")
        password = data.get("password", "")
        
        # 数据类型验证
        if not isinstance(username, str):
            return jsonify({"error": "invalid_username", "detail": "Username must be a string"}), 400
        
        if not isinstance(password, str):
            return jsonify({"error": "invalid_password", "detail": "Password must be a string"}), 400
        
        # 清理字符串
        username = username.strip()

        # 输入验证
        if not username or not password:
            return jsonify({"error": "missing_param", "detail": "username and password are required"}), 400

        # 用户名验证
        if len(username) < 3 or len(username) > 20:
            return jsonify({"error": "invalid_username", "detail": "Username must be between 3 and 20 characters"}), 400
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return jsonify({"error": "invalid_username", "detail": "Username can only contain letters, numbers and underscore"}), 400

        # 密码验证
        if len(password) < 6:
            return jsonify({"error": "invalid_password", "detail": "Password must be at least 6 characters"}), 400
        
        if len(password) > 100:
            return jsonify({"error": "invalid_password", "detail": "Password cannot exceed 100 characters"}), 400

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "username_exists", "detail": "Username already exists"}), 409

        # 创建新用户
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@api.route("/login", methods=["POST"])
def login():
    """用户登录API"""
    try:
        if not request.is_json or request.get_json(silent=True) is None:
            return jsonify({"error": "invalid_request", "detail": "Request must be valid JSON."}), 400

        data = request.get_json()
        username = data.get("username", "")
        password = data.get("password", "")
        
        # 数据类型验证
        if not isinstance(username, str):
            return jsonify({"error": "invalid_username", "detail": "Username must be a string"}), 400
        
        if not isinstance(password, str):
            return jsonify({"error": "invalid_password", "detail": "Password must be a string"}), 400
        
        # 清理字符串
        username = username.strip()

        # 输入验证
        if not username or not password:
            return jsonify({"error": "missing_param", "detail": "username and password are required"}), 400

        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "invalid_credentials", "detail": "Invalid username or password"}), 401

        # 生成JWT token
        token = generate_jwt_token(user.id, user.username)

        # 创建响应并设置HTTP-only Cookie
        response = make_response(jsonify({
            "message": "Login successful",
            "user": user.to_dict()
        }))
        
        # 设置HTTP-only Cookie，24小时过期
        response.set_cookie(
            'access_token',
            token,
            max_age=24*60*60,  # 24小时
            httponly=True,     # HTTP-only
            secure=False,      # 开发环境设为False，生产环境应设为True
            samesite='Lax'     # CSRF保护
        )

        return response, 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@api.route("/logout", methods=["POST"])
def logout():
    """用户登出API"""
    try:
        response = make_response(jsonify({"message": "Logout successful"}))
        # 清除cookie
        response.set_cookie('access_token', '', expires=0, httponly=True)
        return response, 200
    except Exception as e:
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@api.route("/me", methods=["GET"])
def get_current_user_info():
    """获取当前用户信息API"""
    from app.utils.auth import get_current_user
    
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "unauthorized", "detail": "Not logged in"}), 401
        
        return jsonify({"user": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": "internal_error", "detail": str(e)}), 500 
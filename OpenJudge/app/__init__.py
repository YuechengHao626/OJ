import os
from flask import Flask
from app.models import db
from app.models.analysis_task import AnalysisTask  # 确保模型被导入
from app.models.user import User  # 导入User模型
from app.routes.routes import api  # Blueprint 路由
from app.routes.web_routes import web  # Web界面路由
from app.routes import auth  # 导入auth路由

def create_app(config_overrides=None):
    app = Flask(__name__)

    # ✅ 通过环境变量注入 PostgreSQL 连接字符串
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 添加 Flask session 支持（用于 flash 消息）
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # 测试或自定义配置覆盖
    if config_overrides:
        app.config.update(config_overrides)

    # 初始化数据库
    db.init_app(app)
    with app.app_context():
        db.create_all()
        db.session.commit()

    # 注册 Blueprint 路由
    app.register_blueprint(api, url_prefix="/api/v1")  # API 路由
    app.register_blueprint(web)  # Web界面路由

    return app

# -*- coding: utf-8 -*-
"""
考试系统 - Flask 应用工厂

修改历史：
- 2026-04-08 14:30:00: 添加异常处理到 init_admin_user() 函数，解决数据库表不存在导致的启动失败
- 2026-04-08 14:30:00: 修改模型导入方式，确保所有模型在应用启动时就被加载
- 2026-04-08 14:30:00: 兼容 Alibaba Cloud Linux 3.2104 LTS Docker 部署
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_migrate import Migrate

from exam_system.config import config
from exam_system.extensions import db, jwt, cors, socketio, init_redis
# 2026-04-08 14:30:00: 导入所有模型类，确保 db.create_all() 能正确创建所有表
from exam_system.models import User, ExamType, ExamSubject, Question, Paper, PaperQuestion, Exam, ExamAnswer, ExamLog, SystemLog, SystemConfig, Organization, Role, Menu, RoleMenu, OnlineUser, BizOperationLog


def create_app(config_name=None):
    """创建 Flask 应用。未指定 config_name 时读取环境变量 FLASK_CONFIG，默认 development。"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'development'
    if config_name not in config:
        config_name = 'development'
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 确保必要的目录存在
    ensure_directories(app)
    
    # 配置日志
    setup_logging(app)
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    socketio.init_app(app)
    
    # 初始化 Redis
    init_redis(app)
    
    # 初始化数据库迁移
    migrate = Migrate(app, db)
    
    # 注册蓝图
    register_blueprints(app)

    # 经 HTTPS/负载均衡转发时 Authorization 偶发未传到后端，允许用 X-Access-Token 传递同一 JWT
    register_request_hooks(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册 JWT 回调
    register_jwt_callbacks(app)
    
    # 2026-04-08 14:30:00: 创建数据库表（必须在 init_admin_user 之前执行）
    # 2026-04-08 23:15:00: 确保每次启动时都创建数据库表
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
        ensure_users_registration_read_column(app)
        init_admin_user()
    
    return app


def ensure_directories(app):
    """确保必要的目录存在"""
    dirs = [
        app.config['UPLOAD_FOLDER'],
        os.path.dirname(app.config.get('LOG_FILE', 'logs/app.log'))
    ]
    for d in dirs:
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)


def setup_logging(app):
    """配置日志"""
    if not app.debug:
        log_file = app.config.get('LOG_FILE')
        if log_file:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=10, encoding='utf-8'
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
            app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))


def register_blueprints(app):
    """注册蓝图"""
    from exam_system.api.auth import auth_bp
    from exam_system.api.user import user_bp
    from exam_system.api.question import question_bp
    from exam_system.api.paper import paper_bp
    from exam_system.api.exam import exam_bp
    from exam_system.api.score import score_bp
    from exam_system.api.upload import upload_bp
    from exam_system.api.system import system_bp
    from exam_system.api.organization import organization_bp
    from exam_system.api.user_management import user_management_bp
    from exam_system.api.role import role_bp
    from exam_system.api.online_users import online_users_bp
    from exam_system.api.biz_operation_logs import biz_operation_logs_bp
    from exam_system.api.data_storage import data_backup_bp, data_restore_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(question_bp, url_prefix='/api/question')
    app.register_blueprint(paper_bp, url_prefix='/api/paper')
    app.register_blueprint(exam_bp, url_prefix='/api/exam')
    app.register_blueprint(score_bp, url_prefix='/api/score')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    app.register_blueprint(organization_bp, url_prefix='/api/organization')
    app.register_blueprint(user_management_bp, url_prefix='/api/user-management')
    app.register_blueprint(role_bp, url_prefix='/api/role')
    app.register_blueprint(online_users_bp, url_prefix='/api/online-users')
    app.register_blueprint(biz_operation_logs_bp, url_prefix='/api/biz-operation-logs')
    app.register_blueprint(data_backup_bp, url_prefix='/api/data-backup')
    app.register_blueprint(data_restore_bp, url_prefix='/api/data-restore')


def register_request_hooks(app):
    """API 请求钩子：从 X-Access-Token 补全 Authorization，供 flask-jwt-extended 校验。"""

    @app.before_request
    def _inject_authorization_from_x_access_token():
        if not request.path.startswith('/api/'):
            return
        if request.headers.get('Authorization'):
            return
        raw = request.headers.get('X-Access-Token')
        if not raw:
            return
        token = str(raw).strip()
        if not token:
            return
        if token.lower().startswith('bearer '):
            request.environ['HTTP_AUTHORIZATION'] = token
        else:
            request.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'


def register_error_handlers(app):
    """注册错误处理"""
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'code': 400, 'message': '请求参数错误', 'data': None}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'code': 401, 'message': '未授权访问', 'data': None}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'code': 403, 'message': '禁止访问', 'data': None}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'code': 404, 'message': '资源不存在', 'data': None}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'code': 500, 'message': '服务器内部错误', 'data': None}), 500


def register_jwt_callbacks(app):
    """注册 JWT 回调函数"""
    from exam_system.extensions import jwt
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'code': 401, 'message': 'Token 已过期', 'data': None}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'code': 401, 'message': '无效的 Token', 'data': None}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'code': 401, 'message': '缺少 Token', 'data': None}), 401


def ensure_users_registration_read_column(app):
    """旧库升级：为 users 表增加 registration_read_at 列（用户注册审批未读/已读）。"""
    try:
        from sqlalchemy import inspect, text
        insp = inspect(db.engine)
        cols = [c['name'] for c in insp.get_columns('users')]
        if 'registration_read_at' in cols:
            return
        dialect = db.engine.dialect.name
        if dialect == 'sqlite':
            db.session.execute(text('ALTER TABLE users ADD COLUMN registration_read_at DATETIME'))
        elif dialect in ('mysql', 'mysqldb', 'pymysql'):
            db.session.execute(text('ALTER TABLE users ADD COLUMN registration_read_at DATETIME NULL'))
        else:
            db.session.execute(text('ALTER TABLE users ADD COLUMN registration_read_at TIMESTAMP NULL'))
        db.session.commit()
        app.logger.info('已添加 users.registration_read_at 列')
    except Exception as e:
        app.logger.warning('ensure_users_registration_read_column: %s', e)


# 2026-04-08 14:30:00: 添加异常处理，解决多进程环境下数据库表未创建的竞态条件问题
def init_admin_user():
    """初始化管理员账户；若库中 admin 为待审核(status=0)，登录会返回 403，启动时纠正为正常(status=1)。已禁用(status=2)不自动恢复。"""
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                real_name='系统管理员',
                email='admin@exam.com',
                role='admin',
                status=1
            )
            admin.set_password('admin123')
            db.session.add(admin)
        else:
            admin.role = 'admin'
            if admin.status == 0:
                admin.status = 1
        db.session.commit()
    except Exception:
        # 2026-04-08 14:30:00: 如果表不存在，忽略错误（可能在其他进程中已创建）
        pass


# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

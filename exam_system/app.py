# -*- coding: utf-8 -*-
"""
考试系统 - Flask应用工厂
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_migrate import Migrate

from exam_system.config import config
from exam_system.extensions import db, jwt, cors, socketio, init_redis
from exam_system.models import User, ExamType, ExamSubject, Question, Paper, PaperQuestion, Exam, ExamAnswer, ExamLog, SystemLog, SystemConfig


def create_app(config_name='default'):
    """创建Flask应用"""
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
    
    # 初始化Redis
    init_redis(app)
    
    # 初始化数据库迁移
    migrate = Migrate(app, db)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册JWT回调
    register_jwt_callbacks(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
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
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(question_bp, url_prefix='/api/question')
    app.register_blueprint(paper_bp, url_prefix='/api/paper')
    app.register_blueprint(exam_bp, url_prefix='/api/exam')
    app.register_blueprint(score_bp, url_prefix='/api/score')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(system_bp, url_prefix='/api/system')


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
    """注册JWT回调函数"""
    from exam_system.extensions import jwt
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'code': 401, 'message': 'Token已过期', 'data': None}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'code': 401, 'message': '无效的Token', 'data': None}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'code': 401, 'message': '缺少Token', 'data': None}), 401


def init_admin_user():
    """初始化管理员账户"""
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
        db.session.commit()


# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

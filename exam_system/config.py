# -*- coding: utf-8 -*-
"""
考试系统 - 核心配置文件
默认数据库为 MySQL 8.0（与 docker-compose 中 db 服务一致），可通过 DATABASE_URL 覆盖。
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


def _default_mysql_uri():
    """本地/容器内默认连接串组件可由环境变量覆盖。用户名与密码做 URL 编码，避免 @、!、# 等破坏连接串。"""
    from urllib.parse import quote_plus

    user = os.environ.get('MYSQL_USER', 'exam_user')
    password = os.environ.get('MYSQL_PASSWORD', 'exam_pass')
    host = os.environ.get('MYSQL_HOST', '127.0.0.1')
    port = os.environ.get('MYSQL_PORT', '3306')
    database = os.environ.get('MYSQL_DATABASE', 'exam_system')
    return (
        f'mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{database}'
        f'?charset=utf8mb4'
    )


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'exam-system-secret-key-2024'

    # 数据库：优先 DATABASE_URL / SQLALCHEMY_DATABASE_URI，否则 MySQL 默认连接
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or os.environ.get('SQLALCHEMY_DATABASE_URI')
        or _default_mysql_uri()
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    # MySQL 连接池与连接检测
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }

    JWT_SECRET_KEY = (
        os.environ.get('JWT_SECRET_KEY')
        or os.environ.get('JWT_SECRET')
        or 'jwt-secret-key-2024'
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_DB = int(os.environ.get('REDIS_DB') or 0)
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') or None

    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}

    EXAM_AUTO_SAVE_INTERVAL = 30
    EXAM_MAX_CONCURRENT = 1000

    SCORE_SINGLE_CHOICE = 1.0
    SCORE_MULTIPLE_CHOICE = 2.0
    SCORE_JUDGMENT = 0.5

    CORS_ORIGINS = '*'

    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.path.join(basedir, 'logs', 'exam_system.log')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

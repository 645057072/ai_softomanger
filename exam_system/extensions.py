# -*- coding: utf-8 -*-
"""
考试系统 - Flask扩展初始化
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
import redis

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')
redis_client = None


def init_redis(app):
    """初始化Redis连接"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            password=app.config['REDIS_PASSWORD'],
            decode_responses=True
        )
        redis_client.ping()
        app.logger.info('Redis连接成功')
    except Exception as e:
        app.logger.warning(f'Redis连接失败: {e}, 将使用内存缓存')
        redis_client = None
    return redis_client

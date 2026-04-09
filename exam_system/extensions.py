# -*- coding: utf-8 -*-
"""
考试系统 - Flask扩展初始化
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
import redis
import time

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')
redis_client = None


class _InMemoryRedis:
    """
    轻量级内存缓存（接口形状对齐 redis.Redis 的常用方法）。
    用途：当 Redis 不可用时，避免业务接口因 redis_client 为 None 而崩溃。
    说明：该实现仅用于当前进程内的限流/计数场景。
    """

    def __init__(self):
        self._store = {}

    def _now(self):
        return int(time.time())

    def _purge_if_expired(self, key):
        item = self._store.get(key)
        if not item:
            return
        value, expire_at = item
        if expire_at is not None and expire_at <= self._now():
            self._store.pop(key, None)

    def exists(self, key):
        self._purge_if_expired(key)
        return 1 if key in self._store else 0

    def ttl(self, key):
        self._purge_if_expired(key)
        item = self._store.get(key)
        if not item:
            return -2  # Redis 语义：key 不存在
        _, expire_at = item
        if expire_at is None:
            return -1  # Redis 语义：key 永不过期
        return max(0, expire_at - self._now())

    def get(self, key):
        self._purge_if_expired(key)
        item = self._store.get(key)
        if not item:
            return None
        value, _ = item
        return value

    def setex(self, key, seconds, value):
        expire_at = self._now() + int(seconds)
        self._store[key] = (str(value), expire_at)
        return True

    def delete(self, *keys):
        deleted = 0
        for key in keys:
            if key in self._store:
                self._store.pop(key, None)
                deleted += 1
        return deleted

    def incr(self, key):
        self._purge_if_expired(key)
        current = self.get(key)
        try:
            num = int(current) if current is not None else 0
        except Exception:
            num = 0
        num += 1
        # incr 不改变过期时间；这里沿用原 key 的 expire_at
        expire_at = self._store.get(key, (None, None))[1]
        self._store[key] = (str(num), expire_at)
        return num


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
        redis_client = _InMemoryRedis()
    return redis_client

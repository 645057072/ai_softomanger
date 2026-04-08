# -*- coding: utf-8 -*-
"""
考试系统 - 认证API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from exam_system.extensions import db, redis_client
from exam_system.models import User, SystemLog
from exam_system.utils.decorators import validate_json
from exam_system.utils.validators import user_login_schema, user_register_schema

auth_bp = Blueprint('auth', __name__)


def check_login_attempts(username, ip_address):
    """检查登录失败次数和冷却时间"""
    # 生成Redis键
    attempts_key = f'login:attempts:{username}:{ip_address}'
    lockout_key = f'login:lockout:{username}:{ip_address}'
    
    # 检查是否处于冷却期
    if redis_client.exists(lockout_key):
        remaining_time = redis_client.ttl(lockout_key)
        return False, f'登录失败次数过多，请在{remaining_time}秒后重试'
    
    # 检查失败次数
    attempts = redis_client.get(attempts_key)
    if attempts and int(attempts) >= 5:
        # 设置5分钟冷却期
        redis_client.setex(lockout_key, 300, '1')
        redis_client.delete(attempts_key)
        return False, '登录失败次数过多，请在5分钟后重试'
    
    return True, None

def increment_login_attempts(username, ip_address):
    """增加登录失败次数"""
    attempts_key = f'login:attempts:{username}:{ip_address}'
    attempts = redis_client.get(attempts_key)
    if attempts:
        redis_client.incr(attempts_key)
    else:
        # 设置10分钟过期
        redis_client.setex(attempts_key, 600, 1)

def reset_login_attempts(username, ip_address):
    """重置登录失败次数"""
    attempts_key = f'login:attempts:{username}:{ip_address}'
    lockout_key = f'login:lockout:{username}:{ip_address}'
    redis_client.delete(attempts_key)
    redis_client.delete(lockout_key)


@auth_bp.route('/login', methods=['POST'])
@validate_json(user_login_schema)
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    ip_address = request.remote_addr
    
    # 检查登录失败次数和冷却时间
    can_login, message = check_login_attempts(username, ip_address)
    if not can_login:
        return jsonify({'code': 429, 'message': message, 'data': None}), 429
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        # 增加登录失败次数
        increment_login_attempts(username, ip_address)
        return jsonify({'code': 401, 'message': '用户名或密码错误', 'data': None}), 401
    
    if user.status != 1:
        return jsonify({'code': 403, 'message': '账户已被禁用', 'data': None}), 403
    
    # 重置登录失败次数
    reset_login_attempts(username, ip_address)
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 记录登录日志
    log = SystemLog(
        user_id=user.id,
        module='认证',
        action='用户登录',
        ip_address=ip_address,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    # 生成Token
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }
    })


@auth_bp.route('/register', methods=['POST'])
@validate_json(user_register_schema)
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    real_name = data.get('real_name', username)
    
    # 检查用户名是否存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在', 'data': None}), 400
    
    # 检查邮箱是否存在
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'message': '邮箱已被注册', 'data': None}), 400
    
    # 创建用户
    user = User(
        username=username,
        email=email,
        real_name=real_name,
        role='student',
        status=1
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': user.to_dict()
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新Token"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.status != 1:
        return jsonify({'code': 401, 'message': '用户不存在或已被禁用', 'data': None}), 401
    
    access_token = create_access_token(identity=user_id)
    
    return jsonify({
        'code': 200,
        'message': 'Token刷新成功',
        'data': {'access_token': access_token}
    })


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    user_id = get_jwt_identity()
    
    # 记录登出日志
    log = SystemLog(
        user_id=user_id,
        module='认证',
        action='用户登出',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '登出成功', 'data': None})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': user.to_dict()
    })


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'code': 400, 'message': '参数不完整', 'data': None}), 400
    
    user = User.query.get(user_id)
    
    if not user.check_password(old_password):
        return jsonify({'code': 400, 'message': '原密码错误', 'data': None}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '密码修改成功', 'data': None})

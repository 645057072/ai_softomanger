# -*- coding: utf-8 -*-
"""
考试系统 - 用户管理API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from exam_system.extensions import db
from exam_system.models import User, SystemLog
from exam_system.utils.decorators import admin_required, teacher_required

user_bp = Blueprint('user', __name__)


@user_bp.route('/list', methods=['GET'])
@jwt_required()
@admin_required
def get_user_list():
    """获取用户列表（管理员）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    role = request.args.get('role')
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '')
    
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    if status is not None:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            db.or_(
                User.username.like(f'%{keyword}%'),
                User.real_name.like(f'%{keyword}%'),
                User.email.like(f'%{keyword}%')
            )
        )
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users = [user.to_dict() for user in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': users,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """获取用户详情"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 只有管理员或本人可以查看
    if current_user.role != 'admin' and current_user_id != user_id:
        return jsonify({'code': 403, 'message': '无权访问', 'data': None}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': user.to_dict()
    })


@user_bp.route('/create', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """创建用户（管理员）"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    real_name = data.get('real_name')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role', 'student')
    
    if not all([username, password, real_name, email]):
        return jsonify({'code': 400, 'message': '参数不完整', 'data': None}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在', 'data': None}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'message': '邮箱已被注册', 'data': None}), 400
    
    user = User(
        username=username,
        real_name=real_name,
        email=email,
        phone=phone,
        role=role,
        status=1
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=get_jwt_identity(),
        module='用户管理',
        action=f'创建用户: {username}',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': user.to_dict()
    })


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用户信息"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 只有管理员或本人可以修改
    if current_user.role != 'admin' and current_user_id != user_id:
        return jsonify({'code': 403, 'message': '无权操作', 'data': None}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404
    
    data = request.get_json()
    
    # 普通用户只能修改部分信息
    if current_user.role == 'admin':
        user.real_name = data.get('real_name', user.real_name)
        user.phone = data.get('phone', user.phone)
        user.role = data.get('role', user.role)
        user.status = data.get('status', user.status)
        
        new_email = data.get('email')
        if new_email and new_email != user.email:
            if User.query.filter_by(email=new_email).first():
                return jsonify({'code': 400, 'message': '邮箱已被使用', 'data': None}), 400
            user.email = new_email
    else:
        user.real_name = data.get('real_name', user.real_name)
        user.phone = data.get('phone', user.phone)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': user.to_dict()
    })


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """删除用户（管理员）"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404
    
    if user.role == 'admin':
        return jsonify({'code': 400, 'message': '不能删除管理员账户', 'data': None}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=get_jwt_identity(),
        module='用户管理',
        action=f'删除用户: {user.username}',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '删除成功', 'data': None})


@user_bp.route('/batch-import', methods=['POST'])
@jwt_required()
@admin_required
def batch_import_users():
    """批量导入用户"""
    data = request.get_json()
    users_data = data.get('users', [])
    
    if not users_data:
        return jsonify({'code': 400, 'message': '无用户数据', 'data': None}), 400
    
    success_count = 0
    fail_count = 0
    errors = []
    
    for i, user_data in enumerate(users_data):
        try:
            username = user_data.get('username')
            if User.query.filter_by(username=username).first():
                errors.append(f'第{i+1}行: 用户名已存在')
                fail_count += 1
                continue
            
            user = User(
                username=username,
                real_name=user_data.get('real_name', username),
                email=user_data.get('email'),
                phone=user_data.get('phone'),
                role=user_data.get('role', 'student'),
                status=1
            )
            user.set_password(user_data.get('password', '123456'))
            db.session.add(user)
            success_count += 1
        except Exception as e:
            errors.append(f'第{i+1}行: {str(e)}')
            fail_count += 1
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': f'导入完成: 成功{success_count}条, 失败{fail_count}条',
        'data': {
            'success_count': success_count,
            'fail_count': fail_count,
            'errors': errors
        }
    })

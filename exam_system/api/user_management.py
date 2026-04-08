# -*- coding: utf-8 -*-
"""
考试系统 - 用户管理 API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from exam_system.extensions import db
from exam_system.models import User, SystemLog
from exam_system.utils.decorators import validate_json

user_management_bp = Blueprint('user_management', __name__)


@user_management_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_users():
    """获取待审核用户列表"""
    user_id = get_jwt_identity()
    
    # 检查是否为管理员
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = User.query.filter_by(status=0).order_by(
        User.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    users = [u.to_dict() for u in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': users,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@user_management_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_users():
    """获取所有用户列表"""
    user_id = get_jwt_identity()
    
    # 检查是否为管理员
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=int)
    
    query = User.query
    
    if status is not None:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users = [u.to_dict() for u in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': users,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@user_management_bp.route('/<int:user_id>/approve', methods=['POST'])
@jwt_required()
def approve_user(user_id):
    """审核通过用户"""
    admin_id = get_jwt_identity()
    
    # 检查是否为管理员
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404
    
    if user.status != 0:
        return jsonify({'code': 400, 'message': '用户状态异常', 'data': None}), 400
    
    user.status = 1  # 审核通过
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=admin_id,
        module='用户管理',
        action='审核通过用户',
        detail=f'审核通过用户：{user.username}',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '审核通过',
        'data': user.to_dict()
    })


@user_management_bp.route('/<int:user_id>/reject', methods=['POST'])
@jwt_required()
def reject_user(user_id):
    """审核退回用户"""
    admin_id = get_jwt_identity()
    
    # 检查是否为管理员
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404
    
    if user.status != 0:
        return jsonify({'code': 400, 'message': '用户状态异常', 'data': None}), 400
    
    user.status = 0  # 保持待审核状态
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=admin_id,
        module='用户管理',
        action='审核退回用户',
        detail=f'审核退回用户：{user.username}',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '已退回，请重新提交',
        'data': None
    })


@user_management_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    admin_id = get_jwt_identity()
    
    # 检查是否为管理员
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404
    
    if user.role == 'admin':
        return jsonify({'code': 400, 'message': '不能删除管理员账户', 'data': None}), 400
    
    user.status = 2  # 禁用状态
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=admin_id,
        module='用户管理',
        action='删除用户',
        detail=f'删除用户：{user.username}',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功',
        'data': None
    })


@user_management_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@validate_json({
    'type': 'object',
    'properties': {
        'real_name': {'type': 'string'},
        'email': {'type': 'string'},
        'phone': {'type': 'string'},
        'id_card': {'type': 'string'},
        'role': {'type': 'string'},
        'status': {'type': 'integer'}
    }
})
def update_user(user_id):
    """更新用户信息"""
    admin_id = get_jwt_identity()
    
    # 检查是否为管理员
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404
    
    data = request.get_json()
    
    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'id_card' in data:
        user.id_card = data['id_card']
    if 'role' in data:
        user.role = data['role']
    if 'status' in data:
        user.status = data['status']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=admin_id,
        module='用户管理',
        action='更新用户信息',
        detail=f'更新用户信息：{user.username}',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': user.to_dict()
    })

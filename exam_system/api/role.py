# -*- coding: utf-8 -*-
"""
考试系统 - 角色管理 API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from exam_system.extensions import db
from exam_system.models import Role, SystemLog

role_bp = Blueprint('role', __name__)


@role_bp.route('', methods=['GET'])
@jwt_required()
def get_roles():
    """获取角色列表"""
    user_id = get_jwt_identity()
    
    from exam_system.models import User
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Role.query.filter_by(status=1).order_by(
        Role.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    roles = [role.to_dict() for role in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': roles,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@role_bp.route('', methods=['POST'])
@jwt_required()
def create_role():
    """创建角色"""
    user_id = get_jwt_identity()
    
    from exam_system.models import User
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'code': 400, 'message': '角色名称不能为空', 'data': None}), 400
    
    # 检查角色名是否已存在
    if Role.query.filter_by(name=data.get('name')).first():
        return jsonify({'code': 400, 'message': '角色名已存在', 'data': None}), 400
    
    role = Role(
        name=data.get('name'),
        description=data.get('description', '')
    )
    
    db.session.add(role)
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=user_id,
        module='角色管理',
        action='创建角色',
        detail=f'创建角色：{role.name}',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': role.to_dict()
    })


@role_bp.route('/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    """更新角色"""
    user_id = get_jwt_identity()
    
    from exam_system.models import User
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'code': 404, 'message': '角色不存在', 'data': None}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        role.name = data['name']
    if 'description' in data:
        role.description = data['description']
    if 'status' in data:
        role.status = data['status']
    
    role.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': role.to_dict()
    })


@role_bp.route('/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    """删除角色"""
    user_id = get_jwt_identity()
    
    from exam_system.models import User
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'code': 404, 'message': '角色不存在', 'data': None}), 404
    
    role.status = 0
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功',
        'data': None
    })

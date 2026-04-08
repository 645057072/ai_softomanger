# -*- coding: utf-8 -*-
"""
考试系统 - 组织机构管理 API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from exam_system.extensions import db
from exam_system.models import Organization, SystemLog
from exam_system.utils.decorators import validate_json

organization_bp = Blueprint('organization', __name__)


@organization_bp.route('', methods=['GET'])
@jwt_required()
def get_organizations():
    """获取组织机构列表"""
    user_id = get_jwt_identity()
    
    # 检查是否为管理员
    from exam_system.models import User
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Organization.query.filter_by(status=1).order_by(
        Organization.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    organizations = [org.to_dict() for org in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': organizations,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@organization_bp.route('/<int:org_id>', methods=['GET'])
@jwt_required()
def get_organization(org_id):
    """获取组织机构详情"""
    user_id = get_jwt_identity()
    
    from exam_system.models import User
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'code': 404, 'message': '组织机构不存在', 'data': None}), 404
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': org.to_dict()
    })


@organization_bp.route('', methods=['POST'])
@jwt_required()
@validate_json({
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'tax_id': {'type': 'string'},
        'address': {'type': 'string'},
        'phone': {'type': 'string'},
        'legal_representative': {'type': 'string'},
        'registration_date': {'type': 'string'},
        'industry': {'type': 'string'}
    },
    'required': ['name']
})
def create_organization():
    """创建组织机构"""
    user_id = get_jwt_identity()
    
    from exam_system.models import User
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    data = request.get_json()
    
    org = Organization(
        name=data.get('name'),
        tax_id=data.get('tax_id', ''),
        address=data.get('address', ''),
        phone=data.get('phone', ''),
        legal_representative=data.get('legal_representative', ''),
        registration_date=datetime.strptime(data.get('registration_date'), '%Y-%m-%d').date() if data.get('registration_date') else None,
        industry=data.get('industry', '')
    )
    
    db.session.add(org)
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=user_id,
        module='组织机构管理',
        action='创建组织机构',
        detail=f'创建组织机构：{org.name}',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': org.to_dict()
    })


@organization_bp.route('/<int:org_id>', methods=['PUT'])
@jwt_required()
@validate_json({
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'tax_id': {'type': 'string'},
        'address': {'type': 'string'},
        'phone': {'type': 'string'},
        'legal_representative': {'type': 'string'},
        'registration_date': {'type': 'string'},
        'industry': {'type': 'string'}
    }
})
def update_organization(org_id):
    """更新组织机构"""
    user_id = get_jwt_identity()
    
    from exam_system.models import User
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'code': 404, 'message': '组织机构不存在', 'data': None}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        org.name = data['name']
    if 'tax_id' in data:
        org.tax_id = data['tax_id']
    if 'address' in data:
        org.address = data['address']
    if 'phone' in data:
        org.phone = data['phone']
    if 'legal_representative' in data:
        org.legal_representative = data['legal_representative']
    if 'registration_date' in data and data['registration_date']:
        org.registration_date = datetime.strptime(data['registration_date'], '%Y-%m-%d').date()
    if 'industry' in data:
        org.industry = data['industry']
    
    org.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=user_id,
        module='组织机构管理',
        action='更新组织机构',
        detail=f'更新组织机构：{org.name}',
        ip_address=request.remote_addr,
        status=1
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': org.to_dict()
    })


@organization_bp.route('/<int:org_id>', methods=['DELETE'])
@jwt_required()
def delete_organization(org_id):
    """删除组织机构"""
    user_id = get_jwt_identity()
    
    from exam_system.models import User
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'code': 404, 'message': '组织机构不存在', 'data': None}), 404
    
    org.status = 0
    db.session.commit()
    
    # 记录日志
    log = SystemLog(
        user_id=user_id,
        module='组织机构管理',
        action='删除组织机构',
        detail=f'删除组织机构：{org.name}',
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

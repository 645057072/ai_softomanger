# -*- coding: utf-8 -*-
"""在线用户 API（管理员）"""
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from exam_system.extensions import db
from exam_system.models import User, OnlineUser
from exam_system.utils.jwt_helper import resolve_user_id
from exam_system.utils.decorators import validate_json

online_users_bp = Blueprint('online_users', __name__)

_online_create_schema = {
    'user_id': {'required': True, 'type': int},
    'username': {'required': False, 'type': str, 'max_length': 50},
    'ip_address': {'required': False, 'type': str, 'max_length': 50},
    'status': {'required': False, 'type': str, 'max_length': 20},
}


def _admin_or_403():
    uid = resolve_user_id()
    user = User.query.get(uid) if uid is not None else None
    if not user or user.role != 'admin':
        return None, jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    return user, None


@online_users_bp.route('', methods=['GET'])
@jwt_required()
def list_online_users():
    """分页列表，支持按用户名模糊查询"""
    _, err = _admin_or_403()
    if err:
        return err

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    username_kw = request.args.get('username', type=str, default='') or ''

    q = OnlineUser.query
    if username_kw.strip():
        kw = f'%{username_kw.strip()}%'
        q = q.filter(OnlineUser.username.like(kw))

    pagination = q.order_by(OnlineUser.login_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    items = [r.to_dict() for r in pagination.items]

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@online_users_bp.route('/<int:row_id>', methods=['GET', 'DELETE', 'PUT'])
@jwt_required()
def online_user_item(row_id):
    """单条查询 / 强制下线 / 更新状态（同一 URL 合并注册，避免 Flask 路由覆盖）"""
    _, err = _admin_or_403()
    if err:
        return err

    row = OnlineUser.query.get(row_id)
    method = request.method

    if method == 'GET':
        if not row:
            return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404
        return jsonify({'code': 200, 'message': '获取成功', 'data': row.to_dict()})

    if method == 'DELETE':
        if not row:
            return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404
        db.session.delete(row)
        db.session.commit()
        return jsonify({'code': 200, 'message': '已移除在线记录', 'data': None})

    # PUT
    if not row:
        return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404
    data = request.get_json() or {}
    if 'status' in data and isinstance(data['status'], str):
        row.status = data['status'][:20]
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': row.to_dict()})


@online_users_bp.route('', methods=['POST'])
@jwt_required()
@validate_json(_online_create_schema)
def create_online_user():
    """手工写入在线记录（管理员/第三方集成）；同一 user_id 仅保留一条"""
    _, err = _admin_or_403()
    if err:
        return err

    data = request.get_json()
    uid = int(data['user_id'])
    u = User.query.get(uid)
    if not u:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404

    uname = (data.get('username') or u.username or '')[:50]
    ip = (data.get('ip_address') or request.remote_addr or '')[:50]
    st = (data.get('status') or '在线')[:20]

    OnlineUser.query.filter_by(user_id=uid).delete()
    row = OnlineUser(
        user_id=uid,
        username=uname,
        ip_address=ip,
        login_time=datetime.utcnow(),
        status=st,
    )
    db.session.add(row)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': row.to_dict()})

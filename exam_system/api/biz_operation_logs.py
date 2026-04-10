# -*- coding: utf-8 -*-
"""业务操作日志 API（数据管理-日志）"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from exam_system.extensions import db
from exam_system.models import User, BizOperationLog
from exam_system.utils.jwt_helper import resolve_user_id
from exam_system.utils.decorators import validate_json

biz_operation_logs_bp = Blueprint('biz_operation_logs', __name__)


def _admin_or_403():
    uid = resolve_user_id()
    user = User.query.get(uid) if uid is not None else None
    if not user or user.role != 'admin':
        return None, jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    return user, None


_log_create_schema = {
    'description': {'required': True, 'type': str, 'min_length': 1, 'max_length': 100},
    'op_status': {'required': True, 'type': str, 'min_length': 1, 'max_length': 20},
    'failure_detail': {'required': False, 'type': str, 'max_length': 20000},
}


@biz_operation_logs_bp.route('', methods=['GET'])
@jwt_required()
def list_logs():
    """分页查询，可按用户名、操作状态筛选"""
    _, err = _admin_or_403()
    if err:
        return err

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    username_kw = request.args.get('username', type=str, default='') or ''
    op_status = request.args.get('op_status', type=str, default='') or ''

    q = BizOperationLog.query
    if username_kw.strip():
        kw = f'%{username_kw.strip()}%'
        q = q.filter(BizOperationLog.username.like(kw))
    if op_status.strip():
        q = q.filter(BizOperationLog.op_status == op_status.strip())

    pagination = q.order_by(BizOperationLog.created_at.desc()).paginate(
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


@biz_operation_logs_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log(log_id):
    _, err = _admin_or_403()
    if err:
        return err

    row = BizOperationLog.query.get(log_id)
    if not row:
        return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404
    return jsonify({'code': 200, 'message': '获取成功', 'data': row.to_dict()})


@biz_operation_logs_bp.route('', methods=['POST'])
@jwt_required()
@validate_json(_log_create_schema)
def create_log():
    """手工补录日志（管理员）"""
    admin, err = _admin_or_403()
    if err:
        return err

    data = request.get_json()
    desc = (data.get('description') or '')[:100]
    op_st = (data.get('op_status') or '提交')[:20]
    fail = data.get('failure_detail')

    row = BizOperationLog(
        user_id=admin.id,
        username=admin.username,
        ip_address=request.remote_addr,
        description=desc,
        op_status=op_st,
        failure_detail=fail,
    )
    db.session.add(row)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': row.to_dict()})


_log_update_schema = {
    'description': {'required': False, 'type': str, 'max_length': 100},
    'op_status': {'required': False, 'type': str, 'max_length': 20},
    'failure_detail': {'required': False, 'type': str, 'max_length': 20000},
}


@biz_operation_logs_bp.route('/<int:log_id>', methods=['PUT'])
@jwt_required()
@validate_json(_log_update_schema)
def update_log(log_id):
    _, err = _admin_or_403()
    if err:
        return err

    row = BizOperationLog.query.get(log_id)
    if not row:
        return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404

    data = request.get_json()
    if 'description' in data:
        row.description = (data['description'] or '')[:100]
    if 'op_status' in data:
        row.op_status = (data['op_status'] or '')[:20]
    if 'failure_detail' in data:
        row.failure_detail = data['failure_detail']
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': row.to_dict()})


@biz_operation_logs_bp.route('/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_log(log_id):
    _, err = _admin_or_403()
    if err:
        return err

    row = BizOperationLog.query.get(log_id)
    if not row:
        return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404

    db.session.delete(row)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功', 'data': None})

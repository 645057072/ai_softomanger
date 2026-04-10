# -*- coding: utf-8 -*-
"""数据备份与恢复（SQLite 环境下复制库文件）"""
import os
import shutil
from datetime import datetime

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from exam_system.models import User
from exam_system.utils.jwt_helper import resolve_user_id
from exam_system.utils.decorators import validate_json

data_backup_bp = Blueprint('data_backup', __name__)
data_restore_bp = Blueprint('data_restore', __name__)


def _admin_or_403():
    uid = resolve_user_id()
    user = User.query.get(uid) if uid is not None else None
    if not user or user.role != 'admin':
        return None, jsonify({'code': 403, 'message': '无权限访问', 'data': None}), 403
    return user, None


def _sqlite_db_path():
    uri = current_app.config.get('SQLALCHEMY_DATABASE_URI') or ''
    if not uri.startswith('sqlite:'):
        return None
    # 与 SQLAlchemy 一致：sqlite:/// 后接相对路径，sqlite://// 接绝对路径
    rest = uri[10:]
    if rest.startswith('/'):
        return rest
    return os.path.join(current_app.root_path, rest)


def _backup_dir():
    root = current_app.config.get('UPLOAD_FOLDER') or os.path.join(current_app.root_path, 'uploads')
    d = os.path.join(root, 'backups')
    os.makedirs(d, exist_ok=True)
    return d


@data_backup_bp.route('', methods=['GET'])
@jwt_required()
def list_backups():
    _, err = _admin_or_403()
    if err:
        return err

    d = _backup_dir()
    files = []
    for name in sorted(os.listdir(d), reverse=True):
        if not name.endswith('.db'):
            continue
        fp = os.path.join(d, name)
        if os.path.isfile(fp):
            st = os.stat(fp)
            files.append({
                'filename': name,
                'size': st.st_size,
                'created': datetime.utcfromtimestamp(st.st_ctime).isoformat() + 'Z'
            })

    return jsonify({'code': 200, 'message': '获取成功', 'data': {'list': files}})


@data_backup_bp.route('', methods=['POST'])
@jwt_required()
def create_backup():
    _, err = _admin_or_403()
    if err:
        return err

    db_path = _sqlite_db_path()
    if not db_path or not os.path.isfile(db_path):
        return jsonify({'code': 400, 'message': '当前环境非 SQLite 或数据库文件不存在，无法备份', 'data': None}), 400

    name = f"exam_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
    dest = os.path.join(_backup_dir(), name)
    shutil.copy2(db_path, dest)
    return jsonify({
        'code': 200,
        'message': '备份成功',
        'data': {'filename': name, 'path': dest}
    })


@data_backup_bp.route('', methods=['DELETE'])
@jwt_required()
def delete_backup():
    """删除备份文件（管理员）"""
    _, err = _admin_or_403()
    if err:
        return err

    filename = request.args.get('filename', type=str, default='') or ''
    filename = os.path.basename(filename.strip())
    if not filename or '..' in filename:
        return jsonify({'code': 400, 'message': '非法文件名', 'data': None}), 400
    if not filename.endswith('.db'):
        return jsonify({'code': 400, 'message': '仅允许删除 .db 备份文件', 'data': None}), 400

    fp = os.path.join(_backup_dir(), filename)
    if not os.path.isfile(fp):
        return jsonify({'code': 404, 'message': '备份文件不存在', 'data': None}), 404

    os.remove(fp)
    return jsonify({'code': 200, 'message': '已删除备份文件', 'data': {'filename': filename}})


@data_restore_bp.route('', methods=['POST'])
@jwt_required()
@validate_json({
    'filename': {'required': True, 'type': str, 'min_length': 1, 'max_length': 200},
})
def restore_backup():
    _, err = _admin_or_403()
    if err:
        return err

    data = request.get_json()
    filename = os.path.basename(data.get('filename', ''))
    if '..' in filename or filename.startswith('/'):
        return jsonify({'code': 400, 'message': '非法文件名', 'data': None}), 400

    src = os.path.join(_backup_dir(), filename)
    if not os.path.isfile(src):
        return jsonify({'code': 404, 'message': '备份文件不存在', 'data': None}), 404

    db_path = _sqlite_db_path()
    if not db_path:
        return jsonify({'code': 400, 'message': '当前环境非 SQLite，无法恢复', 'data': None}), 400

    shutil.copy2(src, db_path)
    return jsonify({'code': 200, 'message': '已覆盖数据库文件，请重启后端服务使恢复生效', 'data': None})

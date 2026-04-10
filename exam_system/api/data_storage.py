# -*- coding: utf-8 -*-
"""数据备份与恢复（MySQL：mysqldump 导出 / mysql 导入 SQL 文件）"""
import os
import subprocess
from datetime import datetime
from urllib.parse import unquote, urlparse

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


def _parse_mysql_from_uri(uri):
    """从 SQLAlchemy URI 解析 mysqldump/mysql 所需参数。"""
    if not uri or 'mysql' not in uri:
        return None
    s = uri.strip()
    if s.startswith('mysql+pymysql://'):
        s = 'mysql://' + s[len('mysql+pymysql://') :]
    elif s.startswith('mysql://'):
        pass
    else:
        return None
    u = urlparse(s)
    if not u.hostname:
        return None
    dbname = (u.path or '/').lstrip('/').split('?')[0] or ''
    return {
        'host': u.hostname,
        'port': u.port or 3306,
        'user': unquote(u.username or ''),
        'password': unquote(u.password or ''),
        'database': dbname,
    }


def _mysql_params():
    uri = current_app.config.get('SQLALCHEMY_DATABASE_URI') or ''
    return _parse_mysql_from_uri(uri)


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
        if not name.endswith('.sql'):
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

    p = _mysql_params()
    if not p:
        return jsonify({'code': 400, 'message': '当前数据库非 MySQL 连接，无法备份', 'data': None}), 400

    name = f"exam_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
    dest = os.path.join(_backup_dir(), name)
    env = os.environ.copy()
    env['MYSQL_PWD'] = p['password']
    cmd = [
        'mysqldump',
        f"-h{p['host']}",
        f"-P{str(p['port'])}",
        f"-u{p['user']}",
        '--single-transaction',
        '--routines',
        '--triggers',
        '--set-gtid-purged=OFF',
        p['database'],
    ]
    with open(dest, 'w', encoding='utf-8') as out:
        subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, env=env, check=True)
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
    if not filename.endswith('.sql'):
        return jsonify({'code': 400, 'message': '仅允许删除 .sql 备份文件', 'data': None}), 400

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

    p = _mysql_params()
    if not p:
        return jsonify({'code': 400, 'message': '当前数据库非 MySQL 连接，无法恢复', 'data': None}), 400

    env = os.environ.copy()
    env['MYSQL_PWD'] = p['password']
    cmd = [
        'mysql',
        f"-h{p['host']}",
        f"-P{str(p['port'])}",
        f"-u{p['user']}",
        p['database'],
    ]
    with open(src, 'r', encoding='utf-8', errors='replace') as f:
        subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, env=env, check=True)

    return jsonify({
        'code': 200,
        'message': '已从 SQL 备份导入数据库，建议重启后端服务并刷新页面',
        'data': None
    })

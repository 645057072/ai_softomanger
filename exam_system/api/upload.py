# -*- coding: utf-8 -*-
"""
考试系统 - 文件上传API
"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__)


def allowed_file(filename, allowed_extensions=None):
    """检查文件扩展名"""
    if allowed_extensions is None:
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@upload_bp.route('/file', methods=['POST'])
@jwt_required()
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未上传文件', 'data': None}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '未选择文件', 'data': None}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'code': 400, 'message': '不支持的文件格式', 'data': None}), 400
    
    # 生成唯一文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}.{ext}"
    
    # 按日期分目录存储
    date_dir = datetime.now().strftime('%Y/%m/%d')
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], date_dir)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    
    # 返回相对路径
    relative_path = os.path.join(date_dir, filename).replace('\\', '/')
    
    return jsonify({
        'code': 200,
        'message': '上传成功',
        'data': {
            'filename': filename,
            'path': relative_path,
            'url': f'/api/upload/file/{relative_path}'
        }
    })


@upload_bp.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    """上传图片"""
    allowed_images = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未上传文件', 'data': None}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '未选择文件', 'data': None}), 400
    
    if not allowed_file(file.filename, allowed_images):
        return jsonify({'code': 400, 'message': '不支持的图片格式', 'data': None}), 400
    
    # 生成唯一文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}.{ext}"
    
    # 图片存储目录
    image_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    filepath = os.path.join(image_dir, filename)
    file.save(filepath)
    
    return jsonify({
        'code': 200,
        'message': '上传成功',
        'data': {
            'filename': filename,
            'url': f'/api/upload/file/images/{filename}'
        }
    })


@upload_bp.route('/file/<path:filepath>', methods=['GET'])
def get_file(filepath):
    """获取文件"""
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filepath)
    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    
    if not os.path.exists(full_path):
        return jsonify({'code': 404, 'message': '文件不存在', 'data': None}), 404
    
    return send_from_directory(directory, filename)


@upload_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """上传头像"""
    from models import User, db
    
    allowed_images = {'png', 'jpg', 'jpeg', 'gif'}
    
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未上传文件', 'data': None}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '未选择文件', 'data': None}), 400
    
    if not allowed_file(file.filename, allowed_images):
        return jsonify({'code': 400, 'message': '不支持的图片格式', 'data': None}), 400
    
    user_id = get_jwt_identity()
    
    # 生成唯一文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    
    # 头像存储目录
    avatar_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    if not os.path.exists(avatar_dir):
        os.makedirs(avatar_dir)
    
    filepath = os.path.join(avatar_dir, filename)
    file.save(filepath)
    
    # 更新用户头像
    user = User.query.get(user_id)
    if user:
        user.avatar = f'/api/upload/file/avatars/{filename}'
        db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '上传成功',
        'data': {
            'avatar': f'/api/upload/file/avatars/{filename}'
        }
    })

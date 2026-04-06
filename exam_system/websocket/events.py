# -*- coding: utf-8 -*-
"""
考试系统 - WebSocket事件处理
"""
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from datetime import datetime

from extensions import socketio, redis_client
import json


@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    emit('connected', {'message': '连接成功'})


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    pass


@socketio.on('join_exam')
def handle_join_exam(data):
    """加入考试房间"""
    exam_id = data.get('exam_id')
    user_id = data.get('user_id')
    
    if exam_id and user_id:
        room = f'exam_{exam_id}'
        join_room(room)
        
        # 缓存用户连接信息
        if redis_client:
            redis_client.hset(f'exam_users:{exam_id}', user_id, datetime.utcnow().isoformat())
        
        emit('joined', {'exam_id': exam_id, 'message': '已加入考试'})


@socketio.on('leave_exam')
def handle_leave_exam(data):
    """离开考试房间"""
    exam_id = data.get('exam_id')
    user_id = data.get('user_id')
    
    if exam_id:
        room = f'exam_{exam_id}'
        leave_room(room)
        
        # 移除缓存
        if redis_client and user_id:
            redis_client.hdel(f'exam_users:{exam_id}', user_id)
        
        emit('left', {'exam_id': exam_id, 'message': '已离开考试'})


@socketio.on('sync_time')
def handle_sync_time(data):
    """同步考试时间"""
    exam_id = data.get('exam_id')
    
    if exam_id and redis_client:
        # 获取考试开始时间
        cache_key = f'exam:{exam_id}:start_time'
        start_time_str = redis_client.get(cache_key)
        
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str)
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            emit('time_sync', {
                'elapsed': int(elapsed),
                'server_time': datetime.utcnow().isoformat()
            })


@socketio.on('heartbeat')
def handle_heartbeat(data):
    """心跳检测"""
    exam_id = data.get('exam_id')
    user_id = data.get('user_id')
    
    if exam_id and user_id and redis_client:
        # 更新用户活跃时间
        redis_client.hset(f'exam_users:{exam_id}', user_id, datetime.utcnow().isoformat())
        
        emit('heartbeat_ack', {'status': 'ok'})


@socketio.on('auto_save')
def handle_auto_save(data):
    """自动保存答案"""
    exam_id = data.get('exam_id')
    user_id = data.get('user_id')
    answers = data.get('answers', {})
    
    if exam_id and user_id and redis_client:
        cache_key = f'exam:{exam_id}:{user_id}'
        cache_data = redis_client.get(cache_key)
        
        if cache_data:
            cache_data = json.loads(cache_data)
            cache_data['answers'] = answers
            cache_data['last_save'] = datetime.utcnow().isoformat()
            redis_client.setex(cache_key, 7200, json.dumps(cache_data))
            
            emit('save_success', {
                'message': '自动保存成功',
                'time': datetime.utcnow().isoformat()
            })


def broadcast_exam_end(exam_id):
    """广播考试结束"""
    room = f'exam_{exam_id}'
    socketio.emit('exam_end', {
        'exam_id': exam_id,
        'message': '考试时间已到，请立即提交'
    }, room=room)


def broadcast_warning(exam_id, user_id, message):
    """广播警告消息（防作弊）"""
    room = f'exam_{exam_id}'
    socketio.emit('warning', {
        'user_id': user_id,
        'message': message
    }, room=room)

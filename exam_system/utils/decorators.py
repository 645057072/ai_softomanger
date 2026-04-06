# -*- coding: utf-8 -*-
"""
考试系统 - 装饰器
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from models import User


def admin_required(fn):
    """管理员权限装饰器"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'code': 403, 'message': '需要管理员权限', 'data': None}), 403
        
        return fn(*args, **kwargs)
    return wrapper


def teacher_required(fn):
    """教师权限装饰器"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'code': 403, 'message': '需要教师权限', 'data': None}), 403
        
        return fn(*args, **kwargs)
    return wrapper


def student_required(fn):
    """学生权限装饰器"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 401, 'message': '请先登录', 'data': None}), 401
        
        return fn(*args, **kwargs)
    return wrapper


def validate_json(schema):
    """JSON验证装饰器"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import request
            
            if not request.is_json:
                return jsonify({'code': 400, 'message': '请求必须是JSON格式', 'data': None}), 400
            
            data = request.get_json()
            errors = validate_schema(data, schema)
            
            if errors:
                return jsonify({'code': 400, 'message': errors[0], 'data': None}), 400
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def validate_schema(data, schema):
    """验证数据是否符合schema"""
    errors = []
    
    for field, rules in schema.items():
        if rules.get('required', False) and field not in data:
            errors.append(f'{field}是必填字段')
            continue
        
        if field in data:
            value = data[field]
            
            if 'type' in rules:
                expected_type = rules['type']
                if expected_type == str and not isinstance(value, str):
                    errors.append(f'{field}必须是字符串')
                elif expected_type == int and not isinstance(value, int):
                    errors.append(f'{field}必须是整数')
                elif expected_type == float and not isinstance(value, (int, float)):
                    errors.append(f'{field}必须是数字')
            
            if 'min_length' in rules and isinstance(value, str):
                if len(value) < rules['min_length']:
                    errors.append(f'{field}长度不能小于{rules["min_length"]}')
            
            if 'max_length' in rules and isinstance(value, str):
                if len(value) > rules['max_length']:
                    errors.append(f'{field}长度不能超过{rules["max_length"]}')
    
    return errors

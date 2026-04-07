# -*- coding: utf-8 -*-
"""
考试系统 - 系统管理API
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from exam_system.extensions import db
from exam_system.models import User, Question, Paper, Exam, SystemLog, SystemConfig, ExamType, ExamSubject
from exam_system.utils.decorators import admin_required

system_bp = Blueprint('system', __name__)


@system_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard():
    """获取仪表盘数据"""
    # 用户统计
    total_users = User.query.count()
    student_count = User.query.filter_by(role='student').count()
    teacher_count = User.query.filter_by(role='teacher').count()
    
    # 题库统计
    total_questions = Question.query.count()
    
    # 试卷统计
    total_papers = Paper.query.count()
    active_papers = Paper.query.filter_by(status=1).count()
    
    # 考试统计
    total_exams = Exam.query.filter_by(status=2).count()
    today_exams = Exam.query.filter(
        Exam.status == 2,
        Exam.submit_time >= datetime.utcnow().date()
    ).count()
    
    # 最近7天考试趋势
    trend = []
    for i in range(6, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = Exam.query.filter(
            Exam.status == 2,
            func.date(Exam.submit_time) == date
        ).count()
        trend.append({
            'date': date.strftime('%m-%d'),
            'count': count
        })
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'users': {
                'total': total_users,
                'students': student_count,
                'teachers': teacher_count
            },
            'questions': total_questions,
            'papers': {
                'total': total_papers,
                'active': active_papers
            },
            'exams': {
                'total': total_exams,
                'today': today_exams
            },
            'trend': trend
        }
    })


@system_bp.route('/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_logs():
    """获取系统日志"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    module = request.args.get('module')
    user_id = request.args.get('user_id', type=int)
    
    query = SystemLog.query
    
    if module:
        query = query.filter_by(module=module)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    pagination = query.order_by(SystemLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    logs = []
    for log in pagination.items:
        log_dict = {
            'id': log.id,
            'user_id': log.user_id,
            'user_name': log.user.real_name if log.user else None,
            'module': log.module,
            'action': log.action,
            'detail': log.detail,
            'ip_address': log.ip_address,
            'status': log.status,
            'created_at': log.created_at.isoformat() if log.created_at else None
        }
        logs.append(log_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': logs,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@system_bp.route('/config', methods=['GET'])
@jwt_required()
@admin_required
def get_configs():
    """获取系统配置"""
    configs = SystemConfig.query.all()
    
    result = {}
    for config in configs:
        result[config.config_key] = config.config_value
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': result
    })


@system_bp.route('/config', methods=['POST'])
@jwt_required()
@admin_required
def update_config():
    """更新系统配置"""
    data = request.get_json()
    
    for key, value in data.items():
        config = SystemConfig.query.filter_by(config_key=key).first()
        if config:
            config.config_value = str(value)
        else:
            config = SystemConfig(
                config_key=key,
                config_value=str(value)
            )
            db.session.add(config)
    
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '更新成功', 'data': None})


@system_bp.route('/exam-types', methods=['GET'])
@jwt_required()
def get_exam_types():
    """获取试卷类型列表"""
    types = ExamType.query.order_by(ExamType.id).all()
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [t.to_dict() for t in types]
    })


@system_bp.route('/exam-types', methods=['POST'])
@jwt_required()
@admin_required
def create_exam_type():
    """创建试卷类型"""
    data = request.get_json()
    
    if ExamType.query.filter_by(name=data.get('name')).first():
        return jsonify({'code': 400, 'message': '类型名称已存在', 'data': None}), 400
    
    exam_type = ExamType(
        name=data.get('name'),
        description=data.get('description')
    )
    db.session.add(exam_type)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': exam_type.to_dict()
    })


@system_bp.route('/exam-types/<int:type_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_exam_type(type_id):
    """更新试卷类型"""
    exam_type = ExamType.query.get(type_id)
    if not exam_type:
        return jsonify({'code': 404, 'message': '类型不存在', 'data': None}), 404
    
    data = request.get_json()
    exam_type.name = data.get('name', exam_type.name)
    exam_type.description = data.get('description', exam_type.description)
    exam_type.status = data.get('status', exam_type.status)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': exam_type.to_dict()
    })


@system_bp.route('/exam-types/<int:type_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_exam_type(type_id):
    """删除试卷类型"""
    exam_type = ExamType.query.get(type_id)
    if not exam_type:
        return jsonify({'code': 404, 'message': '类型不存在', 'data': None}), 404
    
    db.session.delete(exam_type)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '删除成功', 'data': None})


@system_bp.route('/exam-subjects', methods=['GET'])
@jwt_required()
def get_exam_subjects():
    """获取试卷科目列表"""
    subjects = ExamSubject.query.order_by(ExamSubject.id).all()
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [s.to_dict() for s in subjects]
    })


@system_bp.route('/exam-subjects', methods=['POST'])
@jwt_required()
@admin_required
def create_exam_subject():
    """创建试卷科目"""
    data = request.get_json()
    
    if ExamSubject.query.filter_by(name=data.get('name')).first():
        return jsonify({'code': 400, 'message': '科目名称已存在', 'data': None}), 400
    
    subject = ExamSubject(
        name=data.get('name'),
        description=data.get('description')
    )
    db.session.add(subject)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': subject.to_dict()
    })


@system_bp.route('/exam-subjects/<int:subject_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_exam_subject(subject_id):
    """更新试卷科目"""
    subject = ExamSubject.query.get(subject_id)
    if not subject:
        return jsonify({'code': 404, 'message': '科目不存在', 'data': None}), 404
    
    data = request.get_json()
    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    subject.status = data.get('status', subject.status)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': subject.to_dict()
    })


@system_bp.route('/exam-subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_exam_subject(subject_id):
    """删除试卷科目"""
    subject = ExamSubject.query.get(subject_id)
    if not subject:
        return jsonify({'code': 404, 'message': '科目不存在', 'data': None}), 404
    
    db.session.delete(subject)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '删除成功', 'data': None})


@system_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'code': 200,
        'message': 'OK',
        'data': {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }
    })

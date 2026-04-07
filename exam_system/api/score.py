# -*- coding: utf-8 -*-
"""
考试系统 - 成绩管理API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from exam_system.extensions import db
from exam_system.models import Exam, Paper, User, ExamAnswer, Question
from exam_system.utils.decorators import admin_required, teacher_required

score_bp = Blueprint('score', __name__)


@score_bp.route('/list', methods=['GET'])
@jwt_required()
@teacher_required
def get_score_list():
    """获取成绩列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    paper_id = request.args.get('paper_id', type=int)
    user_id = request.args.get('user_id', type=int)
    status = request.args.get('status', type=int)
    
    query = Exam.query.filter(Exam.status == 2)
    
    if paper_id:
        query = query.filter_by(paper_id=paper_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if status is not None:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Exam.submit_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    result = []
    for exam in pagination.items:
        exam_dict = exam.to_dict()
        exam_dict['user_name'] = exam.user.real_name if exam.user else None
        exam_dict['username'] = exam.user.username if exam.user else None
        exam_dict['paper_title'] = exam.paper.title if exam.paper else None
        exam_dict['pass'] = float(exam.total_score) >= float(exam.paper.pass_score) if exam.paper else False
        result.append(exam_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@score_bp.route('/statistics', methods=['GET'])
@jwt_required()
@teacher_required
def get_statistics():
    """获取成绩统计"""
    paper_id = request.args.get('paper_id', type=int)
    
    if not paper_id:
        return jsonify({'code': 400, 'message': '缺少试卷ID', 'data': None}), 400
    
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'code': 404, 'message': '试卷不存在', 'data': None}), 404
    
    # 基本统计
    stats = db.session.query(
        func.count(Exam.id).label('total'),
        func.avg(Exam.total_score).label('avg_score'),
        func.max(Exam.total_score).label('max_score'),
        func.min(Exam.total_score).label('min_score')
    ).filter(Exam.paper_id == paper_id, Exam.status == 2).first()
    
    # 及格人数
    pass_count = Exam.query.filter(
        Exam.paper_id == paper_id,
        Exam.status == 2,
        Exam.total_score >= paper.pass_score
    ).count()
    
    # 分数段统计
    score_ranges = [
        (0, 60),
        (60, 70),
        (70, 80),
        (80, 90),
        (90, 100)
    ]
    
    score_distribution = []
    for low, high in score_ranges:
        count = Exam.query.filter(
            Exam.paper_id == paper_id,
            Exam.status == 2,
            Exam.total_score >= low,
            Exam.total_score < high
        ).count()
        score_distribution.append({
            'range': f'{low}-{high}',
            'count': count
        })
    
    # 题目正确率
    question_stats = db.session.query(
        Question.id,
        Question.question_text,
        func.count(ExamAnswer.id).label('total_count'),
        func.sum(ExamAnswer.is_correct).label('correct_count')
    ).join(ExamAnswer).join(Exam).filter(
        Exam.paper_id == paper_id,
        Exam.status == 2
    ).group_by(Question.id).all()
    
    question_accuracy = []
    for q in question_stats:
        accuracy = (q.correct_count / q.total_count * 100) if q.total_count > 0 else 0
        question_accuracy.append({
            'question_id': q.id,
            'question_text': q.question_text[:50] + '...' if len(q.question_text) > 50 else q.question_text,
            'accuracy': round(accuracy, 2)
        })
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'paper_title': paper.title,
            'total_examinees': stats.total or 0,
            'avg_score': round(float(stats.avg_score or 0), 2),
            'max_score': float(stats.max_score or 0),
            'min_score': float(stats.min_score or 0),
            'pass_count': pass_count,
            'pass_rate': round(pass_count / (stats.total or 1) * 100, 2),
            'score_distribution': score_distribution,
            'question_accuracy': question_accuracy
        }
    })


@score_bp.route('/ranking', methods=['GET'])
@jwt_required()
def get_ranking():
    """获取排行榜"""
    paper_id = request.args.get('paper_id', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    if not paper_id:
        return jsonify({'code': 400, 'message': '缺少试卷ID', 'data': None}), 400
    
    exams = Exam.query.filter_by(
        paper_id=paper_id, status=2
    ).order_by(Exam.total_score.desc()).limit(limit).all()
    
    ranking = []
    for i, exam in enumerate(exams, 1):
        ranking.append({
            'rank': i,
            'user_name': exam.user.real_name if exam.user else None,
            'total_score': float(exam.total_score),
            'submit_time': exam.submit_time.isoformat() if exam.submit_time else None
        })
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': ranking
    })


@score_bp.route('/my-scores', methods=['GET'])
@jwt_required()
def get_my_scores():
    """获取我的成绩"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Exam.query.filter_by(
        user_id=user_id, status=2
    ).order_by(Exam.submit_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    result = []
    for exam in pagination.items:
        exam_dict = exam.to_dict()
        exam_dict['paper_title'] = exam.paper.title if exam.paper else None
        exam_dict['pass'] = float(exam.total_score) >= float(exam.paper.pass_score) if exam.paper else False
        result.append(exam_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@score_bp.route('/export', methods=['GET'])
@jwt_required()
@admin_required
def export_scores():
    """导出成绩"""
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    
    paper_id = request.args.get('paper_id', type=int)
    
    query = Exam.query.filter(Exam.status == 2)
    if paper_id:
        query = query.filter_by(paper_id=paper_id)
    
    exams = query.all()
    
    data = []
    for exam in exams:
        data.append({
            '考试ID': exam.id,
            '考生姓名': exam.user.real_name if exam.user else '',
            '用户名': exam.user.username if exam.user else '',
            '试卷名称': exam.paper.title if exam.paper else '',
            '得分': float(exam.total_score) if exam.total_score else 0,
            '满分': float(exam.paper.total_score) if exam.paper else 100,
            '是否及格': '是' if float(exam.total_score or 0) >= float(exam.paper.pass_score or 60) else '否',
            '提交时间': exam.submit_time.strftime('%Y-%m-%d %H:%M:%S') if exam.submit_time else '',
            '考试次数': exam.attempt
        })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='成绩列表')
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='scores_export.xlsx'
    )


@score_bp.route('/analysis', methods=['GET'])
@jwt_required()
@teacher_required
def get_analysis():
    """获取成绩分析报告"""
    paper_id = request.args.get('paper_id', type=int)
    
    if not paper_id:
        return jsonify({'code': 400, 'message': '缺少试卷ID', 'data': None}), 400
    
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'code': 404, 'message': '试卷不存在', 'data': None}), 404
    
    # 按题型分析
    type_analysis = db.session.query(
        Question.question_type,
        func.count(ExamAnswer.id).label('total'),
        func.sum(ExamAnswer.is_correct).label('correct')
    ).join(ExamAnswer).join(Exam).filter(
        Exam.paper_id == paper_id,
        Exam.status == 2
    ).group_by(Question.question_type).all()
    
    type_stats = []
    for t in type_analysis:
        accuracy = (t.correct / t.total * 100) if t.total > 0 else 0
        type_stats.append({
            'type': t.question_type,
            'total': t.total,
            'correct': t.correct,
            'accuracy': round(accuracy, 2)
        })
    
    # 按难度分析
    difficulty_analysis = db.session.query(
        Question.difficulty,
        func.count(ExamAnswer.id).label('total'),
        func.sum(ExamAnswer.is_correct).label('correct')
    ).join(ExamAnswer).join(Exam).filter(
        Exam.paper_id == paper_id,
        Exam.status == 2
    ).group_by(Question.difficulty).all()
    
    difficulty_stats = []
    for d in difficulty_analysis:
        accuracy = (d.correct / d.total * 100) if d.total > 0 else 0
        difficulty_name = {1: '简单', 2: '中等', 3: '困难'}.get(d.difficulty, '未知')
        difficulty_stats.append({
            'difficulty': d.difficulty,
            'difficulty_name': difficulty_name,
            'total': d.total,
            'correct': d.correct,
            'accuracy': round(accuracy, 2)
        })
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'paper_title': paper.title,
            'type_analysis': type_stats,
            'difficulty_analysis': difficulty_stats
        }
    })

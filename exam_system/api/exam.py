# -*- coding: utf-8 -*-
"""
考试系统 - 在线考试API
"""
import random
import json
import re
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from exam_system.extensions import db, redis_client
from exam_system.models import Paper, PaperQuestion, Question, Exam, ExamAnswer, ExamLog, User
from exam_system.utils.decorators import student_required

exam_bp = Blueprint('exam', __name__)


def get_cache_key(exam_id, user_id):
    """获取缓存键"""
    return f'exam:{exam_id}:{user_id}'


def get_exam_questions(paper):
    """获取考试题目（支持随机组卷）"""
    if paper.paper_type == 'fixed':
        # 固定试卷
        questions = []
        for pq in paper.paper_questions:
            q = pq.question
            question_dict = q.to_dict()
            question_dict['order'] = pq.order
            question_dict['paper_score'] = float(pq.score)
            questions.append(question_dict)
        questions.sort(key=lambda x: x.get('order', 0))
    else:
        # 随机组卷
        questions = []
        order = 1
        
        # 单选题
        if paper.single_choice_count > 0:
            single_qs = Question.query.filter_by(
                question_type='single_choice',
                status=1
            ).order_by(db.func.random()).limit(paper.single_choice_count).all()
            for q in single_qs:
                question_dict = q.to_dict()
                question_dict['order'] = order
                question_dict['paper_score'] = float(paper.single_choice_score)
                questions.append(question_dict)
                order += 1
        
        # 多选题
        if paper.multiple_choice_count > 0:
            multi_qs = Question.query.filter_by(
                question_type='multiple_choice',
                status=1
            ).order_by(db.func.random()).limit(paper.multiple_choice_count).all()
            for q in multi_qs:
                question_dict = q.to_dict()
                question_dict['order'] = order
                question_dict['paper_score'] = float(paper.multiple_choice_score)
                questions.append(question_dict)
                order += 1
        
        # 判断题
        if paper.judgment_count > 0:
            judge_qs = Question.query.filter_by(
                question_type='judgment',
                status=1
            ).order_by(db.func.random()).limit(paper.judgment_count).all()
            for q in judge_qs:
                question_dict = q.to_dict()
                question_dict['order'] = order
                question_dict['paper_score'] = float(paper.judgment_score)
                questions.append(question_dict)
                order += 1
        
        # 是否乱序
        if paper.shuffle:
            random.shuffle(questions)
            for i, q in enumerate(questions):
                q['order'] = i + 1
    
    # 隐藏正确答案
    for q in questions:
        q.pop('correct_answer', None)
        q.pop('explanation', None)
    
    return questions


@exam_bp.route('/start/<int:paper_id>', methods=['POST'])
@jwt_required()
@student_required
def start_exam(paper_id):
    """开始考试"""
    user_id = get_jwt_identity()
    paper = Paper.query.get(paper_id)
    
    if not paper:
        return jsonify({'code': 404, 'message': '试卷不存在', 'data': None}), 404
    
    if paper.status != 1:
        return jsonify({'code': 400, 'message': '试卷未发布', 'data': None}), 400
    
    # 检查考试时间
    now = datetime.utcnow()
    if paper.start_time and now < paper.start_time:
        return jsonify({'code': 400, 'message': '考试尚未开始', 'data': None}), 400
    if paper.end_time and now > paper.end_time:
        return jsonify({'code': 400, 'message': '考试已结束', 'data': None}), 400
    
    # 检查考试次数
    attempt_count = Exam.query.filter_by(paper_id=paper_id, user_id=user_id).count()
    if attempt_count >= paper.max_attempts:
        return jsonify({'code': 400, 'message': '已达到最大考试次数', 'data': None}), 400
    
    # 检查是否有进行中的考试
    ongoing = Exam.query.filter_by(
        paper_id=paper_id, user_id=user_id, status=0
    ).first()
    if ongoing:
        return jsonify({
            'code': 200,
            'message': '继续考试',
            'data': {
                'exam_id': ongoing.id,
                'remaining_time': get_remaining_time(ongoing)
            }
        })
    
    # 创建考试记录
    exam = Exam(
        paper_id=paper_id,
        user_id=user_id,
        status=0,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        attempt=attempt_count + 1
    )
    db.session.add(exam)
    db.session.commit()
    
    # 获取题目
    questions = get_exam_questions(paper)
    
    # 缓存考试状态
    cache_key = get_cache_key(exam.id, user_id)
    cache_data = {
        'questions': questions,
        'answers': {},
        'start_time': datetime.utcnow().isoformat()
    }
    
    if redis_client:
        redis_client.setex(cache_key, paper.duration * 60, json.dumps(cache_data))
    
    return jsonify({
        'code': 200,
        'message': '考试开始',
        'data': {
            'exam_id': exam.id,
            'paper': paper.to_dict(),
            'questions': questions,
            'duration': paper.duration,
            'remaining_time': paper.duration * 60
        }
    })


def get_remaining_time(exam):
    """获取剩余时间（秒）"""
    from datetime import timedelta
    
    elapsed = datetime.utcnow() - exam.start_time
    total_seconds = exam.paper.duration * 60
    remaining = total_seconds - elapsed.total_seconds()
    return max(0, int(remaining))


@exam_bp.route('/<int:exam_id>/save', methods=['POST'])
@jwt_required()
def save_answer(exam_id):
    """保存答案"""
    user_id = get_jwt_identity()
    exam = Exam.query.get(exam_id)
    
    if not exam:
        return jsonify({'code': 404, 'message': '考试不存在', 'data': None}), 404
    
    if exam.user_id != user_id:
        return jsonify({'code': 403, 'message': '无权操作', 'data': None}), 403
    
    if exam.status != 0:
        return jsonify({'code': 400, 'message': '考试已结束', 'data': None}), 400
    
    data = request.get_json()
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    # 更新缓存
    cache_key = get_cache_key(exam_id, user_id)
    if redis_client:
        cache_data = redis_client.get(cache_key)
        if cache_data:
            cache_data = json.loads(cache_data)
            cache_data['answers'][str(question_id)] = answer
            redis_client.setex(cache_key, exam.paper.duration * 60, json.dumps(cache_data))
    
    # 保存到数据库
    exam_answer = ExamAnswer.query.filter_by(
        exam_id=exam_id, question_id=question_id
    ).first()
    
    if exam_answer:
        exam_answer.user_answer = answer
    else:
        exam_answer = ExamAnswer(
            exam_id=exam_id,
            question_id=question_id,
            user_answer=answer
        )
        db.session.add(exam_answer)
    
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '保存成功', 'data': None})


@exam_bp.route('/<int:exam_id>/submit', methods=['POST'])
@jwt_required()
def submit_exam(exam_id):
    """提交试卷"""
    user_id = get_jwt_identity()
    exam = Exam.query.get(exam_id)
    
    if not exam:
        return jsonify({'code': 404, 'message': '考试不存在', 'data': None}), 404
    
    if exam.user_id != user_id:
        return jsonify({'code': 403, 'message': '无权操作', 'data': None}), 403
    
    if exam.status != 0:
        return jsonify({'code': 400, 'message': '考试已提交', 'data': None}), 400
    
    # 获取所有答案
    answers = ExamAnswer.query.filter_by(exam_id=exam_id).all()
    
    # 批改
    total_score = 0
    for answer in answers:
        question = answer.question
        if check_answer(question, answer.user_answer):
            answer.is_correct = 1
            answer.score = question.score
            total_score += float(question.score)
        else:
            answer.is_correct = 0
            answer.score = 0
    
    # 更新考试记录
    exam.status = 2
    exam.submit_time = datetime.utcnow()
    exam.total_score = total_score
    
    db.session.commit()
    
    # 清除缓存
    cache_key = get_cache_key(exam_id, user_id)
    if redis_client:
        redis_client.delete(cache_key)
    
    return jsonify({
        'code': 200,
        'message': '提交成功',
        'data': {
            'total_score': total_score,
            'pass': total_score >= float(exam.paper.pass_score)
        }
    })


def check_answer(question, user_answer):
    """检查答案是否正确"""
    if not user_answer:
        return False
    
    correct = question.correct_answer
    
    if question.question_type == 'single_choice':
        return user_answer.upper() == correct.upper()
    
    elif question.question_type == 'multiple_choice':
        # 处理多种格式：ABC, A,B,C, A、B、C
        user_set = set(re.findall(r'[A-D]', user_answer.upper()))
        correct_set = set(re.findall(r'[A-D]', correct.upper()))
        return user_set == correct_set
    
    elif question.question_type == 'judgment':
        return user_answer == correct
    
    return False




@exam_bp.route('/<int:exam_id>/log', methods=['POST'])
@jwt_required()
def log_exam_action(exam_id):
    """记录考试行为（防作弊）"""
    user_id = get_jwt_identity()
    exam = Exam.query.get(exam_id)
    
    if not exam:
        return jsonify({'code': 404, 'message': '考试不存在', 'data': None}), 404
    
    data = request.get_json()
    action = data.get('action')
    detail = data.get('detail', '')
    
    log = ExamLog(
        exam_id=exam_id,
        user_id=user_id,
        action=action,
        detail=detail,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '记录成功', 'data': None})


@exam_bp.route('/<int:exam_id>/status', methods=['GET'])
@jwt_required()
def get_exam_status(exam_id):
    """获取考试状态"""
    user_id = get_jwt_identity()
    exam = Exam.query.get(exam_id)
    
    if not exam:
        return jsonify({'code': 404, 'message': '考试不存在', 'data': None}), 404
    
    if exam.user_id != user_id:
        return jsonify({'code': 403, 'message': '无权访问', 'data': None}), 403
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'status': exam.status,
            'remaining_time': get_remaining_time(exam) if exam.status == 0 else 0,
            'total_score': float(exam.total_score) if exam.total_score else None
        }
    })


@exam_bp.route('/history', methods=['GET'])
@jwt_required()
def get_exam_history():
    """获取考试历史"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Exam.query.filter_by(user_id=user_id).order_by(
        Exam.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    result = []
    for exam in pagination.items:
        exam_dict = exam.to_dict()
        exam_dict['paper_title'] = exam.paper.title if exam.paper else None
        exam_dict['duration'] = exam.paper.duration if exam.paper else None
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


@exam_bp.route('/<int:exam_id>/review', methods=['GET'])
@jwt_required()
def review_exam(exam_id):
    """查看考试详情（考后回顾）"""
    user_id = get_jwt_identity()
    exam = Exam.query.get(exam_id)
    
    if not exam:
        return jsonify({'code': 404, 'message': '考试不存在', 'data': None}), 404
    
    if exam.user_id != user_id:
        return jsonify({'code': 403, 'message': '无权访问', 'data': None}), 403
    
    if exam.status == 0:
        return jsonify({'code': 400, 'message': '考试尚未结束', 'data': None}), 400
    
    # 检查是否允许查看答案
    paper = exam.paper
    if paper.show_answer == 0:
        return jsonify({'code': 403, 'message': '不允许查看答案', 'data': None}), 403
    
    # 获取答题详情
    answers = []
    for answer in exam.answers:
        question = answer.question
        answer_dict = {
            'question': question.to_dict(),
            'user_answer': answer.user_answer,
            'is_correct': answer.is_correct,
            'score': float(answer.score)
        }
        if paper.show_answer == 2:
            answer_dict['correct_answer'] = question.correct_answer
            answer_dict['explanation'] = question.explanation
        answers.append(answer_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'exam': exam.to_dict(),
            'paper': paper.to_dict(),
            'answers': answers,
            'total_score': float(exam.total_score),
            'pass': float(exam.total_score) >= float(paper.pass_score)
        }
    })

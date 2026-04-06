# -*- coding: utf-8 -*-
"""
考试系统 - 试卷管理API
"""
import random
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Paper, PaperQuestion, Question, User, SystemLog
from utils.decorators import admin_required, teacher_required

paper_bp = Blueprint('paper', __name__)


@paper_bp.route('/list', methods=['GET'])
@jwt_required()
def get_paper_list():
    """获取试卷列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    paper_type = request.args.get('paper_type')
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '')
    
    query = Paper.query
    
    if paper_type:
        query = query.filter_by(paper_type=paper_type)
    if status is not None:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(Paper.title.like(f'%{keyword}%'))
    
    pagination = query.order_by(Paper.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    papers = []
    for p in pagination.items:
        paper_dict = p.to_dict()
        paper_dict['creator_name'] = p.creator.real_name if p.creator else None
        papers.append(paper_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': papers,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@paper_bp.route('/<int:paper_id>', methods=['GET'])
@jwt_required()
def get_paper(paper_id):
    """获取试卷详情"""
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'code': 404, 'message': '试卷不存在', 'data': None}), 404
    
    paper_dict = paper.to_dict()
    paper_dict['creator_name'] = paper.creator.real_name if paper.creator else None
    
    # 获取试卷题目
    questions = []
    for pq in paper.paper_questions:
        q = pq.question
        question_dict = q.to_dict()
        question_dict['order'] = pq.order
        question_dict['paper_score'] = float(pq.score)
        questions.append(question_dict)
    
    # 按顺序排序
    questions.sort(key=lambda x: x.get('order', 0))
    paper_dict['questions'] = questions
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': paper_dict
    })


@paper_bp.route('/create', methods=['POST'])
@jwt_required()
@teacher_required
def create_paper():
    """创建试卷"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    paper = Paper(
        title=data.get('title'),
        description=data.get('description'),
        exam_type_id=data.get('exam_type_id'),
        exam_subject_id=data.get('exam_subject_id'),
        paper_type=data.get('paper_type', 'fixed'),
        total_score=data.get('total_score', 100),
        duration=data.get('duration', 60),
        pass_score=data.get('pass_score', 60),
        single_choice_count=data.get('single_choice_count', 0),
        single_choice_score=data.get('single_choice_score', 1),
        multiple_choice_count=data.get('multiple_choice_count', 0),
        multiple_choice_score=data.get('multiple_choice_score', 2),
        judgment_count=data.get('judgment_count', 0),
        judgment_score=data.get('judgment_score', 0.5),
        start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
        end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
        show_answer=data.get('show_answer', 0),
        shuffle=data.get('shuffle', 0),
        max_attempts=data.get('max_attempts', 1),
        creator_id=user_id,
        status=data.get('status', 0)
    )
    
    db.session.add(paper)
    db.session.commit()
    
    # 如果是固定试卷，添加题目
    if paper.paper_type == 'fixed' and data.get('question_ids'):
        add_paper_questions(paper.id, data.get('question_ids'))
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': paper.to_dict()
    })


@paper_bp.route('/<int:paper_id>', methods=['PUT'])
@jwt_required()
@teacher_required
def update_paper(paper_id):
    """更新试卷"""
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'code': 404, 'message': '试卷不存在', 'data': None}), 404
    
    data = request.get_json()
    
    paper.title = data.get('title', paper.title)
    paper.description = data.get('description', paper.description)
    paper.exam_type_id = data.get('exam_type_id', paper.exam_type_id)
    paper.exam_subject_id = data.get('exam_subject_id', paper.exam_subject_id)
    paper.total_score = data.get('total_score', paper.total_score)
    paper.duration = data.get('duration', paper.duration)
    paper.pass_score = data.get('pass_score', paper.pass_score)
    paper.single_choice_count = data.get('single_choice_count', paper.single_choice_count)
    paper.single_choice_score = data.get('single_choice_score', paper.single_choice_score)
    paper.multiple_choice_count = data.get('multiple_choice_count', paper.multiple_choice_count)
    paper.multiple_choice_score = data.get('multiple_choice_score', paper.multiple_choice_score)
    paper.judgment_count = data.get('judgment_count', paper.judgment_count)
    paper.judgment_score = data.get('judgment_score', paper.judgment_score)
    
    if data.get('start_time'):
        paper.start_time = datetime.fromisoformat(data['start_time'])
    if data.get('end_time'):
        paper.end_time = datetime.fromisoformat(data['end_time'])
    
    paper.show_answer = data.get('show_answer', paper.show_answer)
    paper.shuffle = data.get('shuffle', paper.shuffle)
    paper.max_attempts = data.get('max_attempts', paper.max_attempts)
    paper.status = data.get('status', paper.status)
    
    # 更新题目
    if paper.paper_type == 'fixed' and data.get('question_ids'):
        PaperQuestion.query.filter_by(paper_id=paper_id).delete()
        add_paper_questions(paper_id, data.get('question_ids'))
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': paper.to_dict()
    })


@paper_bp.route('/<int:paper_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_paper(paper_id):
    """删除试卷"""
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'code': 404, 'message': '试卷不存在', 'data': None}), 404
    
    # 删除关联的题目
    PaperQuestion.query.filter_by(paper_id=paper_id).delete()
    db.session.delete(paper)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '删除成功', 'data': None})


@paper_bp.route('/<int:paper_id>/publish', methods=['POST'])
@jwt_required()
@teacher_required
def publish_paper(paper_id):
    """发布试卷"""
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'code': 404, 'message': '试卷不存在', 'data': None}), 404
    
    if paper.paper_type == 'fixed':
        question_count = PaperQuestion.query.filter_by(paper_id=paper_id).count()
        if question_count == 0:
            return jsonify({'code': 400, 'message': '请先添加题目', 'data': None}), 400
    
    paper.status = 1
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '发布成功', 'data': None})


@paper_bp.route('/generate-random', methods=['POST'])
@jwt_required()
@teacher_required
def generate_random_paper():
    """随机组卷"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # 创建试卷
    paper = Paper(
        title=data.get('title'),
        description=data.get('description'),
        exam_type_id=data.get('exam_type_id'),
        exam_subject_id=data.get('exam_subject_id'),
        paper_type='random',
        duration=data.get('duration', 60),
        pass_score=data.get('pass_score', 60),
        single_choice_count=data.get('single_choice_count', 0),
        single_choice_score=data.get('single_choice_score', 1),
        multiple_choice_count=data.get('multiple_choice_count', 0),
        multiple_choice_score=data.get('multiple_choice_score', 2),
        judgment_count=data.get('judgment_count', 0),
        judgment_score=data.get('judgment_score', 0.5),
        start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
        end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
        show_answer=data.get('show_answer', 0),
        shuffle=data.get('shuffle', 1),
        max_attempts=data.get('max_attempts', 1),
        creator_id=user_id,
        status=1
    )
    
    db.session.add(paper)
    db.session.commit()
    
    # 计算总分
    total_score = (
        paper.single_choice_count * paper.single_choice_score +
        paper.multiple_choice_count * paper.multiple_choice_score +
        paper.judgment_count * paper.judgment_score
    )
    paper.total_score = total_score
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '随机试卷创建成功',
        'data': paper.to_dict()
    })


@paper_bp.route('/<int:paper_id>/questions', methods=['POST'])
@jwt_required()
@teacher_required
def add_questions(paper_id):
    """为固定试卷添加题目"""
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'code': 404, 'message': '试卷不存在', 'data': None}), 404
    
    if paper.paper_type != 'fixed':
        return jsonify({'code': 400, 'message': '只能为固定试卷添加题目', 'data': None}), 400
    
    data = request.get_json()
    question_ids = data.get('question_ids', [])
    
    add_paper_questions(paper_id, question_ids)
    
    # 更新总分
    update_paper_total_score(paper_id)
    
    return jsonify({'code': 200, 'message': '添加成功', 'data': None})


def add_paper_questions(paper_id, question_ids):
    """添加试卷题目"""
    for i, q_id in enumerate(question_ids):
        question = Question.query.get(q_id)
        if question:
            pq = PaperQuestion(
                paper_id=paper_id,
                question_id=q_id,
                order=i + 1,
                score=question.score
            )
            db.session.add(pq)
    db.session.commit()


def update_paper_total_score(paper_id):
    """更新试卷总分"""
    total = db.session.query(db.func.sum(PaperQuestion.score)).filter(
        PaperQuestion.paper_id == paper_id
    ).scalar()
    
    paper = Paper.query.get(paper_id)
    paper.total_score = total or 0
    db.session.commit()


@paper_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_papers():
    """获取可参加的考试列表"""
    now = datetime.utcnow()
    user_id = get_jwt_identity()
    
    papers = Paper.query.filter(
        Paper.status == 1,
        db.or_(Paper.start_time.is_(None), Paper.start_time <= now),
        db.or_(Paper.end_time.is_(None), Paper.end_time >= now)
    ).all()
    
    result = []
    for p in papers:
        paper_dict = p.to_dict()
        # 检查是否已达到最大考试次数
        from models import Exam
        attempt_count = Exam.query.filter_by(
            paper_id=p.id, user_id=user_id
        ).count()
        paper_dict['attempt_count'] = attempt_count
        paper_dict['can_take'] = attempt_count < p.max_attempts
        result.append(paper_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': result
    })

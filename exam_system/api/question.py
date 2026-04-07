# -*- coding: utf-8 -*-
"""
考试系统 - 题库管理API
"""
import os
import re
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from exam_system.extensions import db
from exam_system.models import Question, ExamType, ExamSubject, SystemLog
from exam_system.utils.decorators import admin_required, teacher_required

question_bp = Blueprint('question', __name__)


def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@question_bp.route('/list', methods=['GET'])
@jwt_required()
def get_question_list():
    """获取题目列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    question_type = request.args.get('question_type')
    exam_type_id = request.args.get('exam_type_id', type=int)
    exam_subject_id = request.args.get('exam_subject_id', type=int)
    difficulty = request.args.get('difficulty', type=int)
    keyword = request.args.get('keyword', '')
    
    query = Question.query
    
    if question_type:
        query = query.filter_by(question_type=question_type)
    if exam_type_id:
        query = query.filter_by(exam_type_id=exam_type_id)
    if exam_subject_id:
        query = query.filter_by(exam_subject_id=exam_subject_id)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if keyword:
        query = query.filter(Question.question_text.like(f'%{keyword}%'))
    
    pagination = query.order_by(Question.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    questions = [q.to_dict() for q in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': questions,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@question_bp.route('/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question(question_id):
    """获取题目详情"""
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'code': 404, 'message': '题目不存在', 'data': None}), 404
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': question.to_dict()
    })


@question_bp.route('/create', methods=['POST'])
@jwt_required()
@teacher_required
def create_question():
    """创建题目"""
    data = request.get_json()
    
    question = Question(
        exam_type_id=data.get('exam_type_id'),
        exam_subject_id=data.get('exam_subject_id'),
        question_type=data.get('question_type'),
        question_no=data.get('question_no'),
        question_text=data.get('question_text'),
        option_a=data.get('option_a'),
        option_b=data.get('option_b'),
        option_c=data.get('option_c'),
        option_d=data.get('option_d'),
        correct_answer=data.get('correct_answer'),
        explanation=data.get('explanation'),
        score=data.get('score', 1.0),
        difficulty=data.get('difficulty', 1)
    )
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': question.to_dict()
    })


@question_bp.route('/<int:question_id>', methods=['PUT'])
@jwt_required()
@teacher_required
def update_question(question_id):
    """更新题目"""
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'code': 404, 'message': '题目不存在', 'data': None}), 404
    
    data = request.get_json()
    
    question.exam_type_id = data.get('exam_type_id', question.exam_type_id)
    question.exam_subject_id = data.get('exam_subject_id', question.exam_subject_id)
    question.question_type = data.get('question_type', question.question_type)
    question.question_no = data.get('question_no', question.question_no)
    question.question_text = data.get('question_text', question.question_text)
    question.option_a = data.get('option_a', question.option_a)
    question.option_b = data.get('option_b', question.option_b)
    question.option_c = data.get('option_c', question.option_c)
    question.option_d = data.get('option_d', question.option_d)
    question.correct_answer = data.get('correct_answer', question.correct_answer)
    question.explanation = data.get('explanation', question.explanation)
    question.score = data.get('score', question.score)
    question.difficulty = data.get('difficulty', question.difficulty)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': question.to_dict()
    })


@question_bp.route('/<int:question_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_question(question_id):
    """删除题目"""
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'code': 404, 'message': '题目不存在', 'data': None}), 404
    
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '删除成功', 'data': None})


@question_bp.route('/import', methods=['POST'])
@jwt_required()
@teacher_required
def import_questions():
    """导入题目（支持PDF/Word/Excel）"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未上传文件', 'data': None}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '未选择文件', 'data': None}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'code': 400, 'message': '不支持的文件格式', 'data': None}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    exam_type_id = request.form.get('exam_type_id', type=int)
    exam_subject_id = request.form.get('exam_subject_id', type=int)
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    try:
        if ext == 'pdf':
            questions = parse_pdf(filepath)
        elif ext in ['doc', 'docx']:
            questions = parse_word(filepath)
        elif ext in ['xls', 'xlsx']:
            questions = parse_excel(filepath)
        else:
            return jsonify({'code': 400, 'message': '不支持的文件格式', 'data': None}), 400
        
        # 保存题目到数据库
        success_count = 0
        for q in questions:
            question = Question(
                exam_type_id=exam_type_id,
                exam_subject_id=exam_subject_id,
                question_type=q.get('question_type'),
                question_no=q.get('question_no'),
                question_text=q.get('question_text'),
                option_a=q.get('option_a'),
                option_b=q.get('option_b'),
                option_c=q.get('option_c'),
                option_d=q.get('option_d'),
                correct_answer=q.get('correct_answer'),
                explanation=q.get('explanation'),
                score=q.get('score', 1.0),
                source=filename,
                page_number=q.get('page_number')
            )
            db.session.add(question)
            success_count += 1
        
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=get_jwt_identity(),
            module='题库管理',
            action=f'导入题目: {filename}',
            detail=f'成功导入{success_count}道题目',
            ip_address=request.remote_addr,
            status=1
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': f'成功导入{success_count}道题目',
            'data': {'count': success_count}
        })
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'导入失败: {str(e)}', 'data': None}), 500


def parse_pdf(filepath):
    """解析PDF文件"""
    import pdfplumber
    
    questions = []
    current_question = None
    question_type = None
    
    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 检测题目类型标题
                if '单选题' in line:
                    question_type = 'single_choice'
                    continue
                elif '多选题' in line:
                    question_type = 'multiple_choice'
                    continue
                elif '判断题' in line:
                    question_type = 'judgment'
                    continue
                
                # 解析题目
                q_match = re.match(r'^(\d+)\.(.+)$', line)
                if q_match:
                    if current_question:
                        questions.append(current_question)
                    
                    current_question = {
                        'question_type': question_type,
                        'question_no': int(q_match.group(1)),
                        'question_text': q_match.group(2).strip(),
                        'page_number': page_num
                    }
                    continue
                
                # 解析选项
                opt_match = re.match(r'^([A-D])\.(.+)$', line)
                if opt_match and current_question:
                    opt_key = f'option_{opt_match.group(1).lower()}'
                    current_question[opt_key] = opt_match.group(2).strip()
                    continue
                
                # 解析答案
                if line.startswith('答案：') or line.startswith('答案:'):
                    if current_question:
                        current_question['correct_answer'] = line.replace('答案：', '').replace('答案:', '').strip()
                    continue
                
                # 解析解析
                if line.startswith('解析：') or line.startswith('解析:'):
                    if current_question:
                        current_question['explanation'] = line.replace('解析：', '').replace('解析:', '').strip()
                    continue
        
        if current_question:
            questions.append(current_question)
    
    return questions


def parse_word(filepath):
    """解析Word文件"""
    from docx import Document
    
    questions = []
    current_question = None
    question_type = None
    
    doc = Document(filepath)
    
    for para in doc.paragraphs:
        line = para.text.strip()
        if not line:
            continue
        
        if '单选题' in line:
            question_type = 'single_choice'
            continue
        elif '多选题' in line:
            question_type = 'multiple_choice'
            continue
        elif '判断题' in line:
            question_type = 'judgment'
            continue
        
        q_match = re.match(r'^(\d+)\.(.+)$', line)
        if q_match:
            if current_question:
                questions.append(current_question)
            
            current_question = {
                'question_type': question_type,
                'question_no': int(q_match.group(1)),
                'question_text': q_match.group(2).strip()
            }
            continue
        
        opt_match = re.match(r'^([A-D])\.(.+)$', line)
        if opt_match and current_question:
            opt_key = f'option_{opt_match.group(1).lower()}'
            current_question[opt_key] = opt_match.group(2).strip()
            continue
        
        if line.startswith('答案：') or line.startswith('答案:'):
            if current_question:
                current_question['correct_answer'] = line.replace('答案：', '').replace('答案:', '').strip()
            continue
        
        if line.startswith('解析：') or line.startswith('解析:'):
            if current_question:
                current_question['explanation'] = line.replace('解析：', '').replace('解析:', '').strip()
            continue
    
    if current_question:
        questions.append(current_question)
    
    return questions


def parse_excel(filepath):
    """解析Excel文件"""
    import pandas as pd
    
    questions = []
    
    df = pd.read_excel(filepath)
    
    for _, row in df.iterrows():
        question = {
            'question_type': row.get('题目类型', 'single_choice'),
            'question_no': row.get('题号'),
            'question_text': row.get('题目内容'),
            'option_a': row.get('选项A'),
            'option_b': row.get('选项B'),
            'option_c': row.get('选项C'),
            'option_d': row.get('选项D'),
            'correct_answer': row.get('正确答案'),
            'explanation': row.get('解析'),
            'score': row.get('分值', 1.0)
        }
        
        if question['question_text'] and question['correct_answer']:
            questions.append(question)
    
    return questions


@question_bp.route('/export', methods=['GET'])
@jwt_required()
@teacher_required
def export_questions():
    """导出题目"""
    import pandas as pd
    from io import BytesIO
    
    question_ids = request.args.get('ids', '')
    if question_ids:
        ids = [int(id) for id in question_ids.split(',')]
        questions = Question.query.filter(Question.id.in_(ids)).all()
    else:
        questions = Question.query.limit(1000).all()
    
    data = []
    for q in questions:
        data.append({
            '题目ID': q.id,
            '题目类型': q.question_type,
            '题号': q.question_no,
            '题目内容': q.question_text,
            '选项A': q.option_a,
            '选项B': q.option_b,
            '选项C': q.option_c,
            '选项D': q.option_d,
            '正确答案': q.correct_answer,
            '解析': q.explanation,
            '分值': float(q.score),
            '难度': q.difficulty
        })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='题目列表')
    
    output.seek(0)
    
    from flask import send_file
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='questions_export.xlsx'
    )


@question_bp.route('/types', methods=['GET'])
@jwt_required()
def get_exam_types():
    """获取试卷类型列表"""
    types = ExamType.query.filter_by(status=1).all()
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [t.to_dict() for t in types]
    })


@question_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_exam_subjects():
    """获取试卷科目列表"""
    subjects = ExamSubject.query.filter_by(status=1).all()
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [s.to_dict() for s in subjects]
    })


@question_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取题库统计"""
    total = Question.query.count()
    single_choice = Question.query.filter_by(question_type='single_choice').count()
    multiple_choice = Question.query.filter_by(question_type='multiple_choice').count()
    judgment = Question.query.filter_by(question_type='judgment').count()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': total,
            'single_choice': single_choice,
            'multiple_choice': multiple_choice,
            'judgment': judgment
        }
    })

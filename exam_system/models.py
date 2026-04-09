# -*- coding: utf-8 -*-
"""
考试系统 - 数据库模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

from exam_system.extensions import db


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    id_card = db.Column(db.String(18), nullable=True)  # 身份证号码
    role = db.Column(db.String(20), nullable=False, default='student')  # student, teacher, admin
    status = db.Column(db.Integer, default=0)  # 0:待审核 1:正常 2:禁用
    avatar = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,
            'phone': self.phone,
            'id_card': self.id_card,
            'role': self.role,
            'status': self.status,
            'avatar': self.avatar,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExamType(db.Model):
    """试卷类型表"""
    __tablename__ = 'exam_types'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status
        }


class ExamSubject(db.Model):
    """试卷科目表"""
    __tablename__ = 'exam_subjects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status
        }


class Question(db.Model):
    """题目表"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_type_id = db.Column(db.Integer, db.ForeignKey('exam_types.id'), nullable=True)
    exam_subject_id = db.Column(db.Integer, db.ForeignKey('exam_subjects.id'), nullable=True)
    question_type = db.Column(db.String(20), nullable=False)  # single_choice, multiple_choice, judgment, fill_blank
    question_no = db.Column(db.Integer, nullable=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=True)
    option_b = db.Column(db.String(500), nullable=True)
    option_c = db.Column(db.String(500), nullable=True)
    option_d = db.Column(db.String(500), nullable=True)
    correct_answer = db.Column(db.String(50), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    score = db.Column(db.Numeric(5, 2), nullable=False, default=1.0)
    difficulty = db.Column(db.Integer, default=1)  # 1:简单 2:中等 3:困难
    source = db.Column(db.String(100), nullable=True)  # 来源文件名
    page_number = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    exam_type = db.relationship('ExamType', backref='questions')
    exam_subject = db.relationship('ExamSubject', backref='questions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'exam_type_id': self.exam_type_id,
            'exam_subject_id': self.exam_subject_id,
            'question_type': self.question_type,
            'question_no': self.question_no,
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'score': float(self.score),
            'difficulty': self.difficulty,
            'source': self.source,
            'page_number': self.page_number,
            'status': self.status
        }


class Paper(db.Model):
    """试卷表"""
    __tablename__ = 'papers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    exam_type_id = db.Column(db.Integer, db.ForeignKey('exam_types.id'), nullable=True)
    exam_subject_id = db.Column(db.Integer, db.ForeignKey('exam_subjects.id'), nullable=True)
    paper_type = db.Column(db.String(20), nullable=False)  # fixed:固定试卷 random:随机试卷
    total_score = db.Column(db.Numeric(5, 2), default=100.0)
    duration = db.Column(db.Integer, default=60)  # 考试时长(分钟)
    pass_score = db.Column(db.Numeric(5, 2), default=60.0)
    single_choice_count = db.Column(db.Integer, default=0)
    single_choice_score = db.Column(db.Numeric(5, 2), default=1.0)
    multiple_choice_count = db.Column(db.Integer, default=0)
    multiple_choice_score = db.Column(db.Numeric(5, 2), default=2.0)
    judgment_count = db.Column(db.Integer, default=0)
    judgment_score = db.Column(db.Numeric(5, 2), default=0.5)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    show_answer = db.Column(db.Integer, default=0)  # 0:不显示 1:考试后显示 2:立即显示
    shuffle = db.Column(db.Integer, default=0)  # 0:不乱序 1:乱序
    max_attempts = db.Column(db.Integer, default=1)  # 最大考试次数
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Integer, default=1)  # 0:草稿 1:已发布 2:已结束
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('User', backref='papers')
    exam_type = db.relationship('ExamType', backref='papers')
    exam_subject = db.relationship('ExamSubject', backref='papers')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'exam_type_id': self.exam_type_id,
            'exam_subject_id': self.exam_subject_id,
            'paper_type': self.paper_type,
            'total_score': float(self.total_score),
            'duration': self.duration,
            'pass_score': float(self.pass_score),
            'single_choice_count': self.single_choice_count,
            'single_choice_score': float(self.single_choice_score),
            'multiple_choice_count': self.multiple_choice_count,
            'multiple_choice_score': float(self.multiple_choice_score),
            'judgment_count': self.judgment_count,
            'judgment_score': float(self.judgment_score),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'show_answer': self.show_answer,
            'shuffle': self.shuffle,
            'max_attempts': self.max_attempts,
            'creator_id': self.creator_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PaperQuestion(db.Model):
    """试卷题目关联表"""
    __tablename__ = 'paper_questions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    score = db.Column(db.Numeric(5, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    paper = db.relationship('Paper', backref='paper_questions')
    question = db.relationship('Question', backref='paper_questions')
    
    __table_args__ = (db.UniqueConstraint('paper_id', 'question_id'),)


class Exam(db.Model):
    """考试记录表"""
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    submit_time = db.Column(db.DateTime, nullable=True)
    total_score = db.Column(db.Numeric(5, 2), nullable=True)
    status = db.Column(db.Integer, default=0)  # 0:进行中 1:已提交 2:已批改
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    attempt = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    paper = db.relationship('Paper', backref='exams')
    user = db.relationship('User', backref='exams')
    
    def to_dict(self):
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'submit_time': self.submit_time.isoformat() if self.submit_time else None,
            'total_score': float(self.total_score) if self.total_score else None,
            'status': self.status,
            'ip_address': self.ip_address,
            'attempt': self.attempt
        }


class ExamAnswer(db.Model):
    """考试答案表"""
    __tablename__ = 'exam_answers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_answer = db.Column(db.String(500), nullable=True)
    is_correct = db.Column(db.Integer, default=0)  # 0:错误 1:正确 2:部分正确
    score = db.Column(db.Numeric(5, 2), default=0)
    answer_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    exam = db.relationship('Exam', backref='answers')
    question = db.relationship('Question', backref='exam_answers')
    
    __table_args__ = (db.UniqueConstraint('exam_id', 'question_id'),)


class ExamLog(db.Model):
    """考试日志表（防作弊）"""
    __tablename__ = 'exam_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 切屏、复制、粘贴等
    detail = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    exam = db.relationship('Exam', backref='logs')
    user = db.relationship('User', backref='exam_logs')


class SystemLog(db.Model):
    """系统日志表"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    module = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Integer, default=1)  # 1:成功 0:失败
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='system_logs')


class SystemConfig(db.Model):
    """系统配置表"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Organization(db.Model):
    """组织机构表"""
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)  # 组织机构名称
    tax_id = db.Column(db.String(50), nullable=True)  # 纳税人识别号
    address = db.Column(db.String(500), nullable=True)  # 注册地址
    phone = db.Column(db.String(20), nullable=True)  # 联系电话
    legal_representative = db.Column(db.String(50), nullable=True)  # 法定代表人
    registration_date = db.Column(db.Date, nullable=True)  # 注册日期
    industry = db.Column(db.String(100), nullable=True)  # 所属行业
    status = db.Column(db.Integer, default=1)  # 1:正常 0:禁用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tax_id': self.tax_id,
            'address': self.address,
            'phone': self.phone,
            'legal_representative': self.legal_representative,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'industry': self.industry,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Role(db.Model):
    """角色表"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status
        }


class Menu(db.Model):
    """菜单表"""
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('menus.id'), default=0)
    name = db.Column(db.String(50), nullable=False)
    path = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    order = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    parent = db.relationship('Menu', remote_side=[id], backref='children')
    
    def to_dict(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'name': self.name,
            'path': self.path,
            'icon': self.icon,
            'order': self.order,
            'status': self.status
        }


class RoleMenu(db.Model):
    """角色菜单关联表"""
    __tablename__ = 'role_menus'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('role_id', 'menu_id'),)

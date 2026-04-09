# -*- coding: utf-8 -*-
"""
考试系统 - 数据验证器
"""

user_login_schema = {
    'username': {'required': True, 'type': str, 'min_length': 3, 'max_length': 50},
    'password': {'required': True, 'type': str, 'min_length': 6, 'max_length': 100}
}

user_register_schema = {
    'username': {'required': True, 'type': str, 'min_length': 3, 'max_length': 50},
    'password': {'required': True, 'type': str, 'min_length': 8, 'max_length': 100},
    'email': {'required': True, 'type': str, 'max_length': 100},
    'real_name': {'required': True, 'type': str, 'min_length': 1, 'max_length': 50},
    'phone': {'required': True, 'type': str, 'min_length': 11, 'max_length': 20},
    'id_card': {'required': True, 'type': str, 'min_length': 15, 'max_length': 18},
}

question_schema = {
    'question_type': {'required': True, 'type': str},
    'question_text': {'required': True, 'type': str},
    'correct_answer': {'required': True, 'type': str}
}

paper_schema = {
    'title': {'required': True, 'type': str, 'max_length': 200},
    'paper_type': {'required': True, 'type': str},
    'duration': {'required': True, 'type': int}
}

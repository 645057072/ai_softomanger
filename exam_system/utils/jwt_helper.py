# -*- coding: utf-8 -*-
"""
JWT 身份解析：统一将 get_jwt_identity() 转为整型用户主键，避免类型不一致导致 User.query.get 查不到记录。
"""
from flask_jwt_extended import get_jwt_identity


def resolve_user_id():
    """从 JWT 解析当前用户 ID，无法解析时返回 None。"""
    raw = get_jwt_identity()
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None

# -*- coding: utf-8 -*-
"""业务操作日志写入（供注册、审核、异常等场景调用）"""
from exam_system.extensions import db
from exam_system.models import BizOperationLog


def write_biz_log(user_id, username, ip_address, description, op_status, failure_detail=None):
    """
    op_status: 提交、审核、失败
    description: 最长 100 字
    failure_detail: 失败时的详细日志（如异常栈）
    """
    if description and len(description) > 100:
        description = description[:100]
    row = BizOperationLog(
        user_id=user_id,
        username=username or '',
        ip_address=ip_address,
        description=description or '',
        op_status=op_status or '提交',
        failure_detail=failure_detail,
    )
    db.session.add(row)
    db.session.commit()
    return row

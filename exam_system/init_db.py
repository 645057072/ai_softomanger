# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建所有数据库表并初始化管理员账户
"""
from exam_system.app import create_app
from exam_system.extensions import db
from exam_system.models import User, SystemConfig

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建成功！")
        
        # 检查管理员账户是否存在
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # 创建管理员账户
            admin = User(
                username='admin',
                real_name='系统管理员',
                email='admin@example.com',
                role='admin',
                status=1
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("管理员账户创建成功！用户名：admin 密码：admin123")
        else:
            print("管理员账户已存在")

if __name__ == '__main__':
    init_database()

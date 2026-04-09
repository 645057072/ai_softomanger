# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 用于创建数据库表和初始化管理员账户
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exam_system import create_app, db
from exam_system.models import User
from datetime import datetime

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        print("正在创建数据库表...")
        db.create_all()
        print("✓ 数据库表创建成功")
        
        # 检查是否已有管理员账户
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            # 创建默认管理员账户
            print("正在创建默认管理员账户...")
            admin = User(
                username='admin',
                email='admin@example.com',
                real_name='系统管理员',
                role='admin',
                status=1  # 已审核状态
            )
            admin.set_password('admin123')
            admin.created_at = datetime.utcnow()
            
            db.session.add(admin)
            db.session.commit()
            
            print("✓ 默认管理员账户创建成功")
            print("  用户名：admin")
            print("  密码：admin123")
        else:
            print("✓ 管理员账户已存在")
        
        # 检查数据库文件
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        print(f"✓ 数据库文件路径：{db_path}")
        print(f"✓ 数据库文件大小：{db_size / 1024:.2f} KB")

if __name__ == '__main__':
    try:
        init_database()
        print("\n✓ 数据库初始化完成")
    except Exception as e:
        print(f"\n✗ 数据库初始化失败：{str(e)}")
        sys.exit(1)

#!/bin/bash
# 数据库初始化脚本
# 用于在 Docker 容器启动时初始化数据库

set -e

echo "开始初始化数据库..."

# 使用 Python 直接初始化数据库
python << 'EOF'
import os
import sys
import logging
from exam_system.app import create_app
from exam_system.extensions import db
from exam_system.models import User
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    app = create_app()
    
    with app.app_context():
        # 检查数据库文件
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        logger.info(f"数据库路径：{db_path}")
        
        # 创建所有表
        logger.info("正在创建数据库表...")
        db.create_all()
        logger.info("✓ 数据库表创建成功")
        
        # 检查数据库文件大小
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)
            logger.info(f"✓ 数据库文件大小：{db_size / 1024:.2f} KB")
        else:
            logger.error("✗ 数据库文件不存在")
            sys.exit(1)
        
        # 检查并创建管理员账户
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            logger.info("正在创建默认管理员账户...")
            admin = User(
                username='admin',
                email='admin@example.com',
                real_name='系统管理员',
                role='admin',
                status=1
            )
            admin.set_password('admin123')
            admin.created_at = datetime.utcnow()
            
            db.session.add(admin)
            db.session.commit()
            
            logger.info("✓ 默认管理员账户创建成功")
            logger.info("  用户名：admin")
            logger.info("  密码：admin123")
        else:
            logger.info("✓ 管理员账户已存在")
        
        logger.info("✓ 数据库初始化完成")
        
except Exception as e:
    logger.error(f"✗ 数据库初始化失败：{str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

echo "数据库初始化完成"

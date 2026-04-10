#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将历史 SQLite 库数据迁移到 MySQL（表结构由应用 models 在目标库上 create_all）。

用法：设置 DATABASE_URL，或设置 MYSQL_HOST/MYSQL_USER/MYSQL_PASSWORD/MYSQL_DATABASE（与 config 一致），例如：
  python scripts/migrate_sqlite_to_mysql.py --sqlite exam_system/exam_system.db
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    parser = argparse.ArgumentParser(description='SQLite -> MySQL 数据迁移')
    parser.add_argument(
        '--sqlite',
        default=os.path.join(ROOT, 'exam_system', 'exam_system.db'),
        help='SQLite 数据库文件路径',
    )
    parser.add_argument(
        '--mysql-uri',
        default=None,
        help='MySQL 连接串（默认 DATABASE_URL，或由 MYSQL_* 组装）',
    )
    args = parser.parse_args()

    mysql_uri = args.mysql_uri or os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
    if not mysql_uri:
        from exam_system.config import _default_mysql_uri

        mysql_uri = _default_mysql_uri()
    if not mysql_uri:
        print('请设置 DATABASE_URL、--mysql-uri，或完整 MYSQL_* 环境变量', file=sys.stderr)
        sys.exit(1)
    args.mysql_uri = mysql_uri
    if not os.path.isfile(args.sqlite):
        print(f'未找到 SQLite 文件: {args.sqlite}', file=sys.stderr)
        sys.exit(1)

    os.environ['DATABASE_URL'] = args.mysql_uri
    os.environ.setdefault('SQLALCHEMY_DATABASE_URI', args.mysql_uri)
    os.environ['FLASK_CONFIG'] = 'production'

    from sqlalchemy import create_engine, inspect, text

    from exam_system.app import app
    from exam_system.extensions import db

    sqlite_engine = create_engine(f'sqlite:///{os.path.abspath(args.sqlite)}')
    src_insp = inspect(sqlite_engine)
    src_tables = set(src_insp.get_table_names())

    with app.app_context():
        db.create_all()
        db.session.execute(text('SET FOREIGN_KEY_CHECKS=0'))
        db.session.commit()

        for table in db.metadata.sorted_tables:
            if table.name not in src_tables:
                print(f'跳过（SQLite 无表）: {table.name}')
                continue
            conn = sqlite_engine.connect()
            try:
                res = conn.execute(table.select())
                keys = list(res.keys())
                rows = res.fetchall()
            finally:
                conn.close()
            if not rows:
                print(f'空表: {table.name}')
                continue
            n = 0
            for row in rows:
                data = {keys[i]: row[i] for i in range(len(keys))}
                db.session.execute(table.insert().values(**data))
                n += 1
                if n % 300 == 0:
                    db.session.commit()
            db.session.commit()
            print(f'已迁移 {n} 行 -> {table.name}')

        db.session.execute(text('SET FOREIGN_KEY_CHECKS=1'))
        db.session.commit()

    print('迁移完成')


if __name__ == '__main__':
    main()

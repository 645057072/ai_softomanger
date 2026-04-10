# -*- coding: utf-8 -*-
"""
API 冒烟 UAT：管理员登录后调用关键接口，验证路由与鉴权可用。
用法（项目根目录）：  python scripts/uat_api_smoke.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('FLASK_ENV', 'development')


def main():
    from exam_system.app import app

    client = app.test_client()
    login = client.post(
        '/api/auth/login',
        json={'username': 'admin', 'password': 'admin123'},
        content_type='application/json',
    )
    assert login.status_code == 200, login.get_data(as_text=True)
    body = login.get_json()
    assert body.get('code') == 200, body
    token = body['data']['access_token']
    headers = {'Authorization': 'Bearer ' + token}

    checks = [
        ('GET', '/api/user-management/pending?page=1&per_page=1&inbox=unread'),
        ('GET', '/api/user-management/pending?page=1&per_page=1&inbox=read'),
        ('GET', '/api/organization?page=1&per_page=1'),
        ('GET', '/api/online-users?page=1&per_page=5'),
        ('GET', '/api/biz-operation-logs?page=1&per_page=5'),
        ('GET', '/api/data-backup'),
    ]
    for method, path in checks:
        r = client.open(path, method=method, headers=headers)
        assert r.status_code == 200, (path, r.status_code, r.get_data(as_text=True)[:500])
        j = r.get_json()
        assert j.get('code') == 200, (path, j)

    print('UAT smoke: OK')


if __name__ == '__main__':
    main()

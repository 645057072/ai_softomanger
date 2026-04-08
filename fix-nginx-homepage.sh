#!/bin/bash
# 2026-04-08 15:30:00: 创建默认首页脚本
# 用于在前端构建完成前提供默认页面

cd /opt/ai_softomanger

# 检查 frontend/dist 目录是否存在
if [ ! -d "frontend/dist" ]; then
    echo "创建 frontend/dist 目录..."
    mkdir -p frontend/dist
fi

# 创建默认 index.html
cat > frontend/dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>考试系统 - 加载中</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 60px 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        .logo { font-size: 80px; margin-bottom: 20px; }
        h1 { color: #333; font-size: 36px; margin-bottom: 20px; }
        .subtitle { color: #666; font-size: 18px; margin-bottom: 40px; }
        .status {
            display: inline-block;
            padding: 12px 30px;
            background: #f0f0f0;
            border-radius: 25px;
            margin: 10px;
            font-size: 14px;
            color: #666;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.warning { background: #fff3cd; color: #856404; }
        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 30px 0;
            text-align: left;
            border-radius: 5px;
        }
        .info-box h3 { color: #667eea; margin-bottom: 15px; }
        .info-box p { color: #555; line-height: 1.8; margin: 8px 0; }
        .loading {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .footer { margin-top: 40px; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📚</div>
        <h1>考试系统</h1>
        <p class="subtitle">Online Examination System</p>
        <div class="loading"></div>
        <div style="margin: 30px 0;">
            <div class="status success">✓ Nginx 服务正常</div>
            <div class="status warning"> 前端构建中...</div>
        </div>
        <div class="info-box">
            <h3>📋 系统信息</h3>
            <p><strong>服务器：</strong>http://47.93.44.247</p>
            <p><strong>API：</strong>http://47.93.44.247/api</p>
            <p><strong>健康检查：</strong>http://47.93.44.247/api/system/health</p>
        </div>
        <div class="info-box">
            <h3>🔐 默认管理员</h3>
            <p><strong>用户名：</strong>admin</p>
            <p><strong>密码：</strong>admin123</p>
        </div>
        <div class="footer">
            <p>考试系统 © 2026 | 前端构建完成后将自动跳转</p>
        </div>
    </div>
</body>
</html>
EOF

echo "默认首页已创建：frontend/dist/index.html"
echo ""
echo "现在重启服务..."
docker-compose down
docker-compose up -d --build

echo ""
echo "服务已重启，访问：http://47.93.44.247"

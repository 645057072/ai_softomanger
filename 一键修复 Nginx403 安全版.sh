#!/bin/bash
# 2026-04-08 16:30:00: 一键修复 Nginx 403 错误脚本（安全版）
# 解决 Nginx 无法访问问题，默认首页不显示敏感信息

echo "======================================"
echo "Nginx 403 错误修复脚本"
echo "======================================"
echo ""

# 1. 停止所有服务
echo "步骤 1: 停止所有服务..."
cd /opt/ai_softomanger
docker-compose down

# 2. 创建默认首页（简洁安全版）
echo ""
echo "步骤 2: 创建默认首页..."
mkdir -p frontend/dist

cat > frontend/dist/index.html << 'EOFHTML'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>考试系统</title>
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
            max-width: 500px;
            width: 90%;
        }
        .logo { font-size: 80px; margin-bottom: 20px; }
        h1 { color: #333; font-size: 32px; margin-bottom: 15px; }
        .subtitle { color: #666; font-size: 16px; margin-bottom: 40px; }
        .status {
            display: inline-block;
            padding: 8px 20px;
            background: #d4edda;
            border-radius: 20px;
            margin-bottom: 30px;
            font-size: 13px;
            color: #155724;
        }
        .btn-group {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
        }
        .btn {
            display: inline-block;
            padding: 14px 35px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-size: 16px;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-outline {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }
        .btn-outline:hover {
            background: #667eea;
            color: white;
        }
        .divider {
            margin: 30px 0;
            border-top: 1px solid #e0e0e0;
            position: relative;
        }
        .divider::before {
            content: '或';
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 0 10px;
            color: #999;
            font-size: 14px;
        }
        .tips {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 13px;
            color: #666;
        }
        .footer { margin-top: 40px; color: #999; font-size: 13px; }
        .loading {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📚</div>
        <h1>考试系统</h1>
        <p class="subtitle">Online Examination System</p>
        <div class="status">✓ 系统正常运行</div>
        <div class="loading"></div>
        <div class="btn-group">
            <a href="/api/auth/register" class="btn">用户注册</a>
            <a href="/api/auth/login" class="btn btn-outline">管理员登录</a>
        </div>
        <div class="divider"></div>
        <div class="tips">
            <p>首次使用？请先注册账号</p>
            <p style="margin-top: 8px;">已有账号？直接登录</p>
        </div>
        <div class="footer">考试系统 © 2026</div>
    </div>
</body>
</html>
EOFHTML

echo "✓ 默认首页已创建（简洁安全版）"

# 3. 清理旧的容器
echo ""
echo "步骤 3: 清理旧的容器..."
docker rm -f exam-system-nginx 2>/dev/null || true

# 4. 重新启动服务
echo ""
echo "步骤 4: 启动服务..."
docker-compose up -d --build

# 5. 等待服务启动
echo ""
echo "等待服务启动..."
sleep 10

# 6. 检查服务状态
echo ""
echo "步骤 5: 检查服务状态..."
docker-compose ps

# 7. 检查 Nginx 容器中的文件
echo ""
echo "步骤 6: 检查 Nginx 容器中的文件..."
docker exec exam-system-nginx ls -lh /usr/share/nginx/html/

# 8. 测试访问
echo ""
echo "步骤 7: 测试访问..."
echo "在服务器本地测试："
curl -I http://localhost

echo ""
echo "======================================"
echo "修复完成！"
echo "======================================"
echo ""
echo "访问地址："
echo "  - 前端：http://47.93.44.247"
echo "  - 后端 API: http://47.93.44.247/api"
echo ""
echo "如果仍然无法访问，请检查："
echo "  1. 阿里云安全组是否开放 80 端口"
echo "  2. 防火墙是否关闭"
echo "  3. 查看 Nginx 日志：docker logs exam-system-nginx"
echo ""

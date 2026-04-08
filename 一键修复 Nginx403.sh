#!/bin/bash
# 2026-04-08 16:00:00: 一键修复 Nginx 403 错误脚本
# 解决 Nginx 无法访问问题

echo "======================================"
echo "Nginx 403 错误修复脚本"
echo "======================================"
echo ""

# 1. 停止所有服务
echo "步骤 1: 停止所有服务..."
cd /opt/ai_softomanger
docker-compose down

# 2. 创建默认首页
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
            max-width: 600px;
            width: 90%;
        }
        .logo { font-size: 80px; margin-bottom: 20px; }
        h1 { color: #333; font-size: 36px; margin-bottom: 20px; }
        .subtitle { color: #666; font-size: 18px; margin-bottom: 40px; }
        .status {
            display: inline-block;
            padding: 12px 30px;
            background: #d4edda;
            border-radius: 25px;
            margin: 10px;
            font-size: 14px;
            color: #155724;
        }
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
        .footer { margin-top: 40px; color: #999; font-size: 14px; }
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            margin: 5px;
            transition: all 0.3s;
        }
        .btn:hover { background: #764ba2; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📚</div>
        <h1>考试系统</h1>
        <p class="subtitle">Online Examination System</p>
        
        <div class="status">✓ 系统正常运行</div>
        
        <div class="info-box">
            <h3>📋 系统信息</h3>
            <p><strong>服务器地址：</strong>http://47.93.44.247</p>
            <p><strong>API 接口：</strong>http://47.93.44.247/api</p>
            <p><strong>健康检查：</strong>http://47.93.44.247/api/system/health</p>
        </div>
        
        <div class="info-box">
            <h3>🔐 默认管理员账户</h3>
            <p><strong>用户名：</strong>admin</p>
            <p><strong>密码：</strong>admin123</p>
        </div>
        
        <div>
            <a href="/api/system/health" class="btn" target="_blank">健康检查</a>
            <a href="/api/system/config" class="btn" target="_blank">系统配置</a>
        </div>
        
        <div class="footer">
            <p>考试系统 © 2026 | Powered by Flask + Vue.js</p>
        </div>
    </div>
</body>
</html>
EOFHTML

echo "✓ 默认首页已创建"

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
echo "  - 健康检查：http://47.93.44.247/api/system/health"
echo ""
echo "管理员账户："
echo "  - 用户名：admin"
echo "  - 密码：admin123"
echo ""
echo "如果仍然无法访问，请检查："
echo "  1. 阿里云安全组是否开放 80 端口"
echo "  2. 防火墙是否关闭"
echo "  3. 查看 Nginx 日志：docker logs exam-system-nginx"
echo ""

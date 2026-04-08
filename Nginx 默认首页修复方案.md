# Nginx 默认首页修复方案

**问题**: Nginx 启动后显示 403 Forbidden 或无默认首页

**原因**: 
1. 前端构建需要时间，构建完成前 `/usr/share/nginx/html` 目录为空
2. Nginx 配置中没有默认 index.html 文件

## 解决方案

### 方案一：在服务器上执行修复脚本（推荐）

```bash
# 1. SSH 登录服务器
ssh root@47.93.44.247
# 密码：AAAAa@321

# 2. 进入项目目录
cd /opt/ai_softomanger

# 3. 执行修复脚本
chmod +x fix-nginx-homepage.sh
./fix-nginx-homepage.sh
```

### 方案二：手动创建默认首页

```bash
# 1. 登录服务器
ssh root@47.93.44.247

# 2. 创建目录
cd /opt/ai_softomanger
mkdir -p frontend/dist

# 3. 创建默认 index.html
cat > frontend/dist/index.html << 'EOF'
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
        }
        .logo { font-size: 80px; }
        h1 { color: #333; margin: 20px 0; }
        .status {
            display: inline-block;
            padding: 10px 20px;
            background: #d4edda;
            border-radius: 20px;
            margin: 10px;
        }
        .info {
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📚</div>
        <h1>考试系统</h1>
        <div class="status">✓ Nginx 正常</div>
        <div class="info">
            <h3>系统信息</h3>
            <p>服务器：http://47.93.44.247</p>
            <p>API: http://47.93.44.247/api</p>
            <p>管理员：admin / admin123</p>
        </div>
    </div>
</body>
</html>
EOF

# 4. 重启服务
docker-compose down
docker-compose up -d --build
```

### 方案三：直接在容器中添加首页

```bash
# 1. 登录服务器
ssh root@47.93.44.247

# 2. 直接在 Nginx 容器中创建首页
docker exec exam-system-nginx sh -c 'cat > /usr/share/nginx/html/index.html << '\''EOF'\''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>考试系统</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 { color: #333; }
        .info {
            background: #f0f0f0;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 考试系统</h1>
        <div class="info">
            <p><strong>服务器地址：</strong>http://47.93.44.247</p>
            <p><strong>API 接口：</strong>http://47.93.44.247/api</p>
            <p><strong>管理员：</strong>admin / admin123</p>
        </div>
        <p>Nginx 服务正常运行</p>
    </div>
</body>
</html>
EOF'

# 3. 验证
docker exec exam-system-nginx ls -lh /usr/share/nginx/html/
```

## 验证修复

```bash
# 1. 检查文件是否存在
docker exec exam-system-nginx ls -lh /usr/share/nginx/html/

# 2. 测试访问
curl http://localhost

# 3. 外部访问
# 浏览器访问：http://47.93.44.247
```

## 完整部署流程（包含默认首页）

```bash
# 1. 登录服务器
ssh root@47.93.44.247

# 2. 进入项目目录
cd /opt/ai_softomanger

# 3. 创建默认首页（在前端构建前）
mkdir -p frontend/dist

# 复制本地的 index.html 到服务器
# 或者在服务器上创建简单的 index.html

# 4. 停止旧服务
docker-compose down

# 5. 重新构建和启动
docker-compose up -d --build

# 6. 查看日志
docker-compose logs -f

# 7. 检查服务状态
docker-compose ps

# 8. 测试访问
curl http://localhost
```

## 前端构建完成后的处理

当前端构建完成后，`frontend/dist` 目录会被 Vue 构建的文件覆盖，默认首页会自动被替换为真正的 Vue 应用。

```bash
# 查看前端构建日志
docker logs exam-system-frontend

# 构建完成后，访问真正的系统
# http://47.93.44.247
```

## 常见问题

### 问题 1: 仍然显示 403

```bash
# 检查文件权限
docker exec exam-system-nginx ls -lh /usr/share/nginx/html/

# 如果文件不存在，手动创建
docker exec exam-system-nginx sh -c "echo '<h1>OK</h1>' > /usr/share/nginx/html/index.html"
```

### 问题 2: 前端构建失败

```bash
# 查看前端日志
docker logs exam-system-frontend

# 进入前端容器调试
docker exec -it exam-system-frontend sh

# 手动构建
cd /app/frontend
npm install --registry=https://registry.npmmirror.com
npm run build
```

### 问题 3: Nginx 配置错误

```bash
# 测试 Nginx 配置
docker exec exam-system-nginx nginx -t

# 重新加载配置
docker exec exam-system-nginx nginx -s reload
```

## 访问地址

- **默认首页**: http://47.93.44.247
- **后端 API**: http://47.93.44.247/api
- **健康检查**: http://47.93.44.247/api/system/health
- **管理员账户**: admin / admin123

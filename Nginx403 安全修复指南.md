# Nginx 403 安全修复指南

## 默认首页说明

✅ **已移除敏感信息**：
- ❌ 不显示服务器 IP
- ❌ 不显示 API 地址
- ❌ 不显示管理员账户密码

✅ **提供功能入口**：
- ✓ 用户注册按钮
- ✓ 管理员登录按钮
- ✓ 系统状态指示

## 快速修复（推荐）

### 方法一：直接在容器中创建首页

```bash
# 1. SSH 登录服务器
ssh root@47.93.44.247
# 密码：AAAAa@321

# 2. 直接在 Nginx 容器中创建首页
docker exec exam-system-nginx sh -c 'cat > /usr/share/nginx/html/index.html << '\''ENDOFHTML'\''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>考试系统</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        .logo { font-size: 80px; margin-bottom: 20px; }
        h1 { color: #333; margin: 20px 0; }
        .status {
            display: inline-block;
            padding: 10px 20px;
            background: #d4edda;
            color: #155724;
            border-radius: 20px;
            margin: 10px 0;
        }
        .btn-group { margin-top: 30px; }
        .btn {
            display: inline-block;
            padding: 14px 35px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 30px;
            margin: 0 10px;
            font-size: 16px;
        }
        .btn-outline {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }
        .tips {
            margin-top: 30px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 10px;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📚</div>
        <h1>考试系统</h1>
        <div class="status">✓ 系统正常运行</div>
        <div class="btn-group">
            <a href="/api/auth/register" class="btn">用户注册</a>
            <a href="/api/auth/login" class="btn btn-outline">管理员登录</a>
        </div>
        <div class="tips">
            <p>首次使用？请先注册账号</p>
            <p style="margin-top: 8px;">已有账号？直接登录</p>
        </div>
    </div>
</body>
</html>
ENDOFHTML'

# 3. 验证
docker exec exam-system-nginx ls -lh /usr/share/nginx/html/index.html

# 4. 测试访问
curl http://localhost
```

### 方法二：执行修复脚本

```bash
# 1. SSH 登录
ssh root@47.93.44.247

# 2. 进入目录
cd /opt/ai_softomanger

# 3. 执行脚本
chmod +x 一键修复 Nginx403 安全版.sh
./一键修复 Nginx403 安全版.sh
```

## 验证修复

```bash
# 1. 检查容器状态
docker-compose ps

# 2. 检查文件
docker exec exam-system-nginx ls -lh /usr/share/nginx/html/

# 3. 本地测试
curl http://localhost

# 4. 浏览器访问
# http://47.93.44.247
```

## 首页效果

默认首页包含：
- ✅ 系统 Logo 和名称
- ✅ 系统状态指示器
- ✅ 用户注册按钮
- ✅ 管理员登录按钮
- ✅ 使用提示
- ✅ 美观的渐变背景

## 如果仍然 403

### 1. 检查 Nginx 配置

```bash
docker exec exam-system-nginx nginx -t
docker exec exam-system-nginx nginx -s reload
```

### 2. 检查文件权限

```bash
docker exec exam-system-nginx ls -la /usr/share/nginx/html/
```

### 3. 查看日志

```bash
docker logs exam-system-nginx
```

### 4. 检查安全组

登录阿里云控制台，确保开放 80 端口。

## 访问地址

- ✅ **前端首页**: http://47.93.44.247
- ✅ **用户注册**: http://47.93.44.247/api/auth/register
- ✅ **管理员登录**: http://47.93.44.247/api/auth/login
- ✅ **后端 API**: http://47.93.44.247/api

## 安全说明

默认首页已移除所有敏感信息：
- 不显示服务器 IP 地址
- 不显示 API 接口地址
- 不显示管理员账户和密码

用户需要通过以下方式进入系统：
1. **新用户**：点击"用户注册"创建账号
2. **已有账号**：点击"管理员登录"输入凭据

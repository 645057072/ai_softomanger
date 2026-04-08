# Nginx 403 Forbidden 快速修复指南

## 问题原因

403 Forbidden 错误通常由以下原因引起：
1. Nginx 容器中 `/usr/share/nginx/html` 目录为空
2. 没有 index.html 文件
3. 文件权限问题
4. Nginx 配置错误

## 快速修复（推荐）

### 方法一：直接在容器中创建首页（最快）

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
        h1 { color: #333; margin: 20px 0; }
        .info {
            background: #f5f5f5;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            text-align: left;
        }
        .status {
            display: inline-block;
            padding: 10px 20px;
            background: #d4edda;
            color: #155724;
            border-radius: 20px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 考试系统</h1>
        <div class="status">✓ Nginx 服务正常</div>
        <div class="info">
            <h3>系统信息</h3>
            <p><strong>服务器：</strong>http://47.93.44.247</p>
            <p><strong>API：</strong>http://47.93.44.247/api</p>
            <p><strong>健康检查：</strong>http://47.93.44.247/api/system/health</p>
        </div>
        <div class="info">
            <h3>管理员账户</h3>
            <p><strong>用户名：</strong>admin</p>
            <p><strong>密码：</strong>admin123</p>
        </div>
        <p style="color: #999; margin-top: 20px;">系统正常运行</p>
    </div>
</body>
</html>
ENDOFHTML'

# 3. 验证文件已创建
docker exec exam-system-nginx ls -lh /usr/share/nginx/html/

# 4. 测试访问
curl http://localhost
```

### 方法二：执行一键修复脚本

```bash
# 1. SSH 登录服务器
ssh root@47.93.44.247
# 密码：AAAAa@321

# 2. 进入项目目录
cd /opt/ai_softomanger

# 3. 执行修复脚本
chmod +x 一键修复 Nginx403.sh
./一键修复 Nginx403.sh
```

### 方法三：完整重建

```bash
# 1. SSH 登录服务器
ssh root@47.93.44.247

# 2. 停止服务
cd /opt/ai_softomanger
docker-compose down

# 3. 删除 Nginx 容器
docker rm exam-system-nginx

# 4. 确保前端目录存在
mkdir -p frontend/dist

# 5. 创建简单的 index.html
echo '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>考试系统</title></head><body><h1>考试系统运行正常</h1></body></html>' > frontend/dist/index.html

# 6. 重新启动
docker-compose up -d --build

# 7. 查看日志
docker-compose logs -f
```

## 验证修复

```bash
# 1. 检查容器状态
docker-compose ps

# 2. 检查文件是否存在
docker exec exam-system-nginx ls -lh /usr/share/nginx/html/

# 3. 本地测试
curl -I http://localhost

# 4. 查看 Nginx 日志
docker logs exam-system-nginx

# 5. 浏览器访问
# http://47.93.44.247
```

## 如果仍然 403，检查以下项

### 1. 检查 Nginx 配置

```bash
# 查看 Nginx 配置
docker exec exam-system-nginx cat /etc/nginx/nginx.conf

# 测试配置
docker exec exam-system-nginx nginx -t

# 重新加载配置
docker exec exam-system-nginx nginx -s reload
```

### 2. 检查文件权限

```bash
# 查看文件权限
docker exec exam-system-nginx ls -la /usr/share/nginx/html/

# 如果需要，修改权限
docker exec exam-system-nginx chmod 644 /usr/share/nginx/html/index.html
```

### 3. 检查目录结构

```bash
# 查看完整目录
docker exec exam-system-nginx ls -laR /usr/share/nginx/html/
```

### 4. 检查阿里云安全组

登录阿里云控制台，确保安全组已开放 80 端口：
- 端口范围：80/80
- 授权对象：0.0.0.0/0
- 策略：允许

### 5. 检查服务器防火墙

```bash
# 查看防火墙状态
systemctl status firewalld

# 临时关闭防火墙测试
systemctl stop firewalld

# 如果关闭后可以访问，添加防火墙规则
systemctl start firewalld
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --reload
```

## 常见错误处理

### 错误 1: 容器不存在

```bash
# 重新启动容器
docker-compose up -d

# 等待容器启动
sleep 5

# 再次执行命令
docker exec exam-system-nginx ls -lh /usr/share/nginx/html/
```

### 错误 2: 权限拒绝

```bash
# 使用 root 用户执行
docker exec -u root exam-system-nginx chmod 644 /usr/share/nginx/html/index.html
```

### 错误 3: 文件无法写入

```bash
# 检查磁盘空间
df -h

# 检查挂载
docker inspect exam-system-nginx | grep Mounts -A 20
```

## 最终测试

```bash
# 在服务器上执行
curl http://localhost

# 应该看到 HTML 内容

# 在本地浏览器访问
# http://47.93.44.247
```

## 访问地址

- ✅ **前端首页**: http://47.93.44.247
- ✅ **后端 API**: http://47.93.44.247/api
- ✅ **健康检查**: http://47.93.44.247/api/system/health
- ✅ **管理员**: admin / admin123

## 联系支持

如果以上方法都无法解决问题，请提供：
1. `docker-compose ps` 输出
2. `docker logs exam-system-nginx` 完整日志
3. `docker exec exam-system-nginx nginx -t` 输出
4. 阿里云安全组配置截图

# GitHub Actions 自动化部署配置指南

## 配置步骤

### 1. 生成 SSH 密钥对

在本地执行以下命令生成 SSH 密钥对：

```bash
ssh-keygen -t rsa -b 4096 -f github_deploy_key -N "" -C "github-deploy-key"
```

这会生成两个文件：
- `github_deploy_key` (私钥)
- `github_deploy_key.pub` (公钥)

### 2. 配置 GitHub Secrets

1. 打开 GitHub 仓库：https://github.com/645057072/ai_softomanger
2. 进入 Settings -> Secrets and variables -> Actions
3. 点击 "New repository secret"
4. 添加以下 secrets：

#### SSH_PRIVATE_KEY
- **Name**: `SSH_PRIVATE_KEY`
- **Value**: 复制 `github_deploy_key` 私钥文件的完整内容（包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`）

### 3. 配置阿里云服务器

1. 登录阿里云服务器：
```bash
ssh root@47.93.44.247
```

2. 将公钥添加到 authorized_keys：
```bash
mkdir -p ~/.ssh
cat github_deploy_key.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

3. 测试免密登录：
```bash
ssh -i github_deploy_key root@47.93.44.247
```

### 4. 提交配置

将 GitHub Actions 工作流文件提交到仓库：

```bash
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions deployment workflow"
git push origin master
```

### 5. 验证部署

1. 推送代码到 master 分支
2. 打开 GitHub 仓库的 Actions 标签页
3. 查看 "Auto Deploy" 工作流是否成功执行
4. 访问 http://47.93.44.247 验证部署是否成功

## 注意事项

1. **安全性**：
   - 永远不要将私钥提交到 Git 仓库
   - `.github/workflows/deploy.yml` 中使用的密钥通过 GitHub Secrets 提供
   - 确保私钥文件权限设置为 600

2. **故障排查**：
   - 如果部署失败，检查 GitHub Actions 日志
   - 确认 SSH 密钥配置正确
   - 验证服务器上 Docker 和 docker-compose 是否正常运行

3. **手动部署**：
   - 如果自动部署失败，可以手动登录服务器执行：
   ```bash
   cd /opt/ai_softomanger
   git pull
   docker-compose down
   docker-compose up -d --build
   docker-compose restart nginx
   ```

## 部署流程说明

当代码推送到 master 分支时，GitHub Actions 会自动：

1. 检出代码
2. 使用 SSH 密钥连接到阿里云服务器
3. 在服务器上执行：
   - `git pull` 拉取最新代码
   - `docker-compose down` 停止现有容器
   - `docker-compose up -d --build` 重新构建并启动容器
   - `docker-compose restart nginx` 重启 Nginx

整个过程无需人工干预，实现真正的自动化部署。

/**
 * 文件名：auto-deploy.sh
 * 描述：自动化部署脚本 - 自动上传代码到阿里云并部署
 * 作者：Li zekun
 * 创建日期：2026-04-08
 * 最后修改：2026-04-08
 * 
 * 使用说明：
 * 1. 在 Windows 环境下使用 PowerShell 运行 auto-deploy.ps1
 * 2. 脚本会自动执行以下操作：
 *    - 提交代码到 Git 仓库
 *    - 连接到阿里云服务器
 *    - 拉取最新代码
 *    - 重启 Docker 服务
 */

#!/bin/bash

# 服务器配置（加密存储）
SERVER_IP="47.93.44.247"
SERVER_USER="root"
SERVER_PORT="22"

# 本地项目路径
LOCAL_PATH="/g/AI_CASE/ai_softomanger"

# 服务器部署路径
REMOTE_PATH="/opt/ai_softomanger"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   考试系统自动化部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 步骤1：提交代码到 Git
echo -e "${YELLOW}[步骤 1/4] 提交代码到 Git 仓库...${NC}"
cd "$LOCAL_PATH"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "发现未提交的更改，正在提交..."
    git add .
    git commit -m "Auto deploy: $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${GREEN}✓ 代码已提交${NC}"
else
    echo -e "${GREEN}✓ 没有未提交的更改${NC}"
fi

# 推送到远程仓库
echo "正在推送到远程仓库..."
git push origin master
echo -e "${GREEN}✓ 代码已推送到远程仓库${NC}"
echo ""

# 步骤2：连接到服务器并拉取代码
echo -e "${YELLOW}[步骤 2/4] 连接到阿里云服务器并拉取代码...${NC}"

# 使用 SSH 私钥免密登录（推荐）
# 说明：
# - 请先在服务器上配置 authorized_keys
# - 然后在本机通过 SSH_AGENT / ssh-add 或设置 SSH_KEY_PATH 指定私钥路径
SSH_KEY_ARG=""
if [ -n "${SSH_KEY_PATH}" ]; then
  SSH_KEY_ARG="-i ${SSH_KEY_PATH}"
fi

ssh ${SSH_KEY_ARG} -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    echo "连接成功！"
    cd /opt/ai_softomanger
    
    echo "正在拉取最新代码..."
    git pull origin master
    
    if [ $? -eq 0 ]; then
        echo -e "\033[0;32m✓ 代码拉取成功\033[0m"
    else
        echo -e "\033[0;31m✗ 代码拉取失败\033[0m"
        exit 1
    fi
ENDSSH

echo ""

# 步骤3：重启 Docker 服务
echo -e "${YELLOW}[步骤 3/4] 重启 Docker 服务...${NC}"

ssh ${SSH_KEY_ARG} -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    set -e
    cd /opt/ai_softomanger
    chmod +x scripts/docker-compose-redeploy.sh 2>/dev/null || true
    bash scripts/docker-compose-redeploy.sh
ENDSSH

echo ""

# 步骤4：验证部署
echo -e "${YELLOW}[步骤 4/4] 验证部署状态...${NC}"

sleep 5

# 检查服务状态
ssh ${SSH_KEY_ARG} -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    cd /opt/ai_softomanger
    
    echo ""
    echo "=== 容器状态 ==="
    if docker compose version >/dev/null 2>&1; then docker compose ps; elif sudo docker compose version >/dev/null 2>&1; then sudo docker compose ps; else docker-compose ps; fi
    
    echo ""
    echo "=== 服务日志（最近 20 行）==="
    if docker compose version >/dev/null 2>&1; then docker compose logs --tail=20; elif sudo docker compose version >/dev/null 2>&1; then sudo docker compose logs --tail=20; else docker-compose logs --tail=20; fi
ENDSSH

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "访问地址: http://47.93.44.247"
echo ""

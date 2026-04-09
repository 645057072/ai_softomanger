# File: deploy.ps1
# Description: Automated deployment script for Windows environment
# Author: Li zekun
# Created: 2026-04-08
# Last Modified: 2026-04-08

# Configuration
$SERVER_IP = "47.93.44.247"
$SERVER_USER = "root"
$REMOTE_PATH = "/opt/ai_softomanger"

# 说明：
# - 本脚本会：提交代码 -> 推送 GitHub -> 直连服务器部署（不依赖等待 GitHub Actions）
# - 免密要求：服务器已配置 authorized_keys；本机已加载 ssh-agent 或设置环境变量 SSH_KEY_PATH 指向私钥

# 获取 SSH 私钥参数（可选）
function Get-SshKeyArg {
    $sshKeyPath = $env:SSH_KEY_PATH
    if ([string]::IsNullOrWhiteSpace($sshKeyPath)) {
        return ""
    }
    return "-i `"$sshKeyPath`""
}

# Main function
function Deploy {
    Write-Host ""
    Write-Host "====================================="
    Write-Host "Exam System Deployment Script v2.0"
    Write-Host "====================================="
    Write-Host ""

    try {
        $sshKeyArg = Get-SshKeyArg
        $sshCommonArgs = "$sshKeyArg -o StrictHostKeyChecking=no"

        # Step 1: Commit & push
        Write-Host "Step 1/3: Commit code and push to GitHub"
        Write-Host "-------------------------------------"
        
        $gitStatus = git status --porcelain
        if ($gitStatus) {
            Write-Host "Found uncommitted changes"
            git add .
            $commitMsg = "Auto deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            git commit -m $commitMsg
            Write-Host "Code committed"
        } else {
            Write-Host "No uncommitted changes"
        }

        Write-Host "Pushing to GitHub..."
        git push origin master
        Write-Host "Code pushed to GitHub"

        # Step 2: Build frontend
        Write-Host ""
        Write-Host "Step 2/3: Build frontend application"
        Write-Host "-------------------------------------"
        Write-Host "Building frontend..."
        Set-Location frontend
        npm install
        npm run build
        Set-Location ..
        Write-Host "Frontend built successfully"

        # Step 3: Deploy to server (git pull + docker compose)
        Write-Host ""
        Write-Host "Step 3/3: Deploy to server"
        Write-Host "-------------------------------------"
        Write-Host "Connecting server and deploying..."

        $remoteScript = @"
set -e
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:`$PATH"
cd $REMOTE_PATH
git pull origin master
if docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose"
else
  echo "ERROR: docker compose / docker-compose not found in PATH"
  exit 127
fi
`$COMPOSE down
`$COMPOSE up -d --build
`$COMPOSE restart nginx
"@

        $deployCommand = "ssh $sshCommonArgs ${SERVER_USER}@${SERVER_IP} ""bash -lc '$remoteScript'"""
        Invoke-Expression $deployCommand
        Write-Host "Server deployed successfully"

        # Wait for services to start
        Write-Host "Waiting for services to start..."
        Start-Sleep -Seconds 5

        # Complete
        Write-Host ""
        Write-Host "====================================="
        Write-Host "Deployment completed!"
        Write-Host "====================================="
        Write-Host "Access URL: http://${SERVER_IP}"
        Write-Host ""

    } catch {
        Write-Host "Deployment failed: $($_.Exception.Message)"
        exit 1
    }
}

# Execute deployment
Deploy
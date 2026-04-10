# File: deploy.ps1
# Description: 本地构建后推送 GitHub，并 SSH 到服务器执行 git pull 与 docker compose 全量重建
# Author: Li zekun

$SERVER_IP = "47.93.44.247"
$SERVER_USER = "root"
$REMOTE_PATH = "/opt/ai_softomanger"

function Get-SshKeyArg {
    if ($env:SSH_KEY_PATH) {
        return "-i `"$($env:SSH_KEY_PATH)`""
    }
    return ""
}

function Deploy {
    Write-Host ""
    Write-Host "====================================="
    Write-Host "Exam System Deployment Script"
    Write-Host "====================================="
    Write-Host ""

    $sshKeyArg = Get-SshKeyArg
    $sshTarget = "${SERVER_USER}@${SERVER_IP}"

    try {
        Write-Host "Step 1/4: Git commit & push"
        Write-Host "-------------------------------------"

        $gitStatus = git status --porcelain
        if ($gitStatus) {
            git add .
            $commitMsg = "Auto deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            git commit -m $commitMsg
        }
        git push origin master
        Write-Host "Pushed to origin master"

        Write-Host ""
        Write-Host "Step 2/4: Build frontend"
        Write-Host "-------------------------------------"
        Set-Location frontend
        npm install
        npm run build
        Set-Location ..
        Write-Host "Frontend build OK"

        Write-Host ""
        Write-Host "Step 3/4: Upload frontend dist to server"
        Write-Host "-------------------------------------"
        $scpCmd = "scp $sshKeyArg -o StrictHostKeyChecking=no -r frontend/dist/* ${sshTarget}:${REMOTE_PATH}/frontend/dist/"
        Invoke-Expression $scpCmd
        Write-Host "dist uploaded"

        Write-Host ""
        Write-Host "Step 4/4: Server git pull + sudo/docker compose up -d --build"
        Write-Host "-------------------------------------"

        # 通过 stdin 传入脚本；与 GitHub Actions 共用 scripts/docker-compose-redeploy.sh（自动 sudo docker compose）
        $remoteBash = @'
set -e
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
cd /opt/ai_softomanger
git config --global --add safe.directory /opt/ai_softomanger || true
git fetch origin master || true
git reset --hard origin/master || true
git clean -fd || true
git pull origin master || true
if [ -f scripts/docker-compose-redeploy.sh ]; then
  chmod +x scripts/docker-compose-redeploy.sh || true
  bash scripts/docker-compose-redeploy.sh
else
  echo "ERROR: scripts/docker-compose-redeploy.sh missing"
  exit 1
fi
'@

        $remoteBash | ssh $sshKeyArg -o StrictHostKeyChecking=no $sshTarget "bash -s"

        Write-Host ""
        Write-Host "====================================="
        Write-Host "Deployment completed"
        Write-Host "http://${SERVER_IP}"
        Write-Host "====================================="
    }
    catch {
        Write-Host "Deployment failed: $($_.Exception.Message)"
        exit 1
    }
}

Deploy

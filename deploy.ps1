# File: deploy.ps1
# Description: Automated deployment script for Windows environment
# Author: Li zekun
# Created: 2026-04-08
# Last Modified: 2026-04-08

# Configuration
$SERVER_IP = "47.93.44.247"
$SERVER_USER = "root"
$REMOTE_PATH = "/opt/ai_softomanger"

# Main function
function Deploy {
    Write-Host ""
    Write-Host "====================================="
    Write-Host "Exam System Deployment Script v1.0"
    Write-Host "====================================="
    Write-Host ""

    try {
        # Step 1: Commit code
        Write-Host "Step 1/4: Commit code to Git repository"
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
        Write-Host "Step 2/4: Build frontend application"
        Write-Host "-------------------------------------"
        Write-Host "Building frontend..."
        Set-Location frontend
        npm install
        npm run build
        Set-Location ..
        Write-Host "Frontend built successfully"

        # Step 3: Upload files
        Write-Host ""
        Write-Host "Step 3/4: Upload files to server"
        Write-Host "-------------------------------------"
        Write-Host "Uploading frontend files..."
        
        # 使用 scp 上传文件到服务器
        $scpCommand = "scp -r frontend/dist/* ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/frontend/dist/"
        Invoke-Expression $scpCommand
        Write-Host "Frontend files uploaded"

        # Step 4: Restart services
        Write-Host ""
        Write-Host "Step 4/4: Restart services"
        Write-Host "-------------------------------------"
        Write-Host "Restarting services..."
        
        # 重启 Docker 服务
        $restartCommand = "ssh ${SERVER_USER}@${SERVER_IP} 'cd ${REMOTE_PATH} && docker compose restart nginx'"
        Invoke-Expression $restartCommand
        Write-Host "Services restarted"

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
# 文件名：auto-deploy.ps1
# 描述：自动化部署脚本 - 自动上传代码到阿里云并部署
# 作者：Li zekun
# 创建日期：2026-04-08
# 最后修改：2026-04-08
#
# 使用说明：
# 1. 在 Windows 环境下运行此脚本
# 2. 脚本会自动执行以下操作：
#    - 提交代码到 Git 仓库
#    - 连接到阿里云服务器
#    - 拉取最新代码
#    - 重启 Docker 服务
# 3. 需要安装：Git、OpenSSH（Windows 10 自带）

# 服务器配置
$SERVER_IP = "47.93.44.247"
$SERVER_USER = "root"
$SERVER_PASSWORD = "AAAAa@321"
$SERVER_PORT = "22"

# 本地项目路径
$LOCAL_PATH = "G:\AI_CASE\ai_softomanger"

# 服务器部署路径
$REMOTE_PATH = "/opt/ai_softomanger"

# 颜色输出函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# 主函数
function Main {
    Write-ColorOutput "========================================" "Green"
    Write-ColorOutput "   考试系统自动化部署脚本" "Green"
    Write-ColorOutput "========================================" "Green"
    Write-Host ""

    # 步骤1：提交代码到 Git
    Write-ColorOutput "[步骤 1/4] 提交代码到 Git 仓库..." "Yellow"
    Set-Location $LOCAL_PATH

    # 检查是否有未提交的更改
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Host "发现未提交的更改，正在提交..."
        git add .
        $commitMessage = "Auto deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git commit -m $commitMessage
        Write-ColorOutput "✓ 代码已提交" "Green"
    } else {
        Write-ColorOutput "✓ 没有未提交的更改" "Green"
    }

    # 推送到远程仓库
    Write-Host "正在推送到远程仓库..."
    git push origin main
    Write-ColorOutput "✓ 代码已推送到远程仓库" "Green"
    Write-Host ""

    # 步骤2：连接到服务器并拉取代码
    Write-ColorOutput "[步骤 2/4] 连接到阿里云服务器并拉取代码..." "Yellow"

    # 使用 plink（PuTTY）或 ssh 命令
    $sshCommand = "ssh -o StrictHostKeyChecking=no $($SERVER_USER)@$($SERVER_IP)"
    
    # 创建远程命令
    $remoteCommands = @"
cd $($REMOTE_PATH)
echo "正在拉取最新代码..."
git pull origin main
if [ `$? -eq 0 ]; then
    echo -e "\\033[0;32m✓ 代码拉取成功\\033[0m"
else
    echo -e "\\033[0;31m✗ 代码拉取失败\\033[0m"
    exit 1
fi
"@

    # 执行远程命令
    $result = echo $remoteCommands | $sshCommand
    Write-Host $result
    Write-ColorOutput "✓ 代码拉取完成" "Green"
    Write-Host ""

    # 步骤3：重启 Docker 服务
    Write-ColorOutput "[步骤 3/4] 重启 Docker 服务..." "Yellow"

    $deployCommands = @"
cd $($REMOTE_PATH)
echo "停止现有服务..."
docker-compose down

echo "构建并启动服务..."
docker-compose up -d --build

if [ `$? -eq 0 ]; then
    echo -e "\\033[0;32m✓ 服务启动成功\\033[0m"
else
    echo -e "\\033[0;31m✗ 服务启动失败\\033[0m"
    exit 1
fi
"@

    $deployResult = echo $deployCommands | $sshCommand
    Write-Host $deployResult
    Write-ColorOutput "✓ 服务重启完成" "Green"
    Write-Host ""

    # 步骤4：验证部署
    Write-ColorOutput "[步骤 4/4] 验证部署状态..." "Yellow"

    Start-Sleep -Seconds 5

    $checkCommands = @"
cd $($REMOTE_PATH)
echo ""
echo "=== 容器状态 ==="
docker-compose ps

echo ""
echo "=== 服务日志（最近 20 行）==="
docker-compose logs --tail=20
"@

    $checkResult = echo $checkCommands | $sshCommand
    Write-Host $checkResult

    Write-Host ""
    Write-ColorOutput "========================================" "Green"
    Write-ColorOutput "   部署完成！" "Green"
    Write-ColorOutput "========================================" "Green"
    Write-Host ""
    Write-Host "访问地址: http://$SERVER_IP"
    Write-Host ""
}

# 执行主函数
try {
    Main
} catch {
    Write-ColorOutput "部署过程中发生错误: $_" "Red"
    Write-ColorOutput "请检查网络连接和服务器状态" "Yellow"
    exit 1
}

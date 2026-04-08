# 文件名：deploy.ps1
# 描述：简化版自动化部署脚本 - 适用于 Windows 环境
# 作者：Li zekun
# 创建日期：2026-04-08
# 最后修改：2026-04-08
#
# 使用说明：
# 1. 确保已安装 Git 和 OpenSSH 客户端
# 2. 运行此脚本：.\deploy.ps1
# 3. 脚本会自动完成代码提交、推送到 GitHub、连接服务器、部署

param(
    [switch]$SkipCommit = $false
)

# 配置信息
$REPO_URL = "github.com:645057072/ai_softomanger.git"
$SERVER_IP = "47.93.44.247"
$SERVER_USER = "root"
$SERVER_PASSWORD = "AAAAa@321"
$REMOTE_PATH = "/opt/ai_softomanger"

# 颜色输出
function Write-Success { param([string]$msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info { param([string]$msg) Write-Host "ℹ $msg" -ForegroundColor Cyan }
function Write-Error { param([string]$msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Step { param([string]$msg) Write-Host "`n━━━ $msg ━━━" -ForegroundColor Yellow }

# 主函数
function Deploy {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     考试系统自动化部署脚本 v1.0      ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""

    try {
        # 步骤1：提交代码
        if (-not $SkipCommit) {
            Write-Step "步骤 1/4：提交代码到 Git 仓库"
            
            $gitStatus = git status --porcelain
            if ($gitStatus) {
                Write-Info "发现未提交的更改"
                git add .
                $commitMsg = "Auto deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
                git commit -m $commitMsg
                Write-Success "代码已提交"
            } else {
                Write-Info "没有未提交的更改"
            }

            Write-Info "正在推送到 GitHub..."
            git push origin master
            Write-Success "代码已推送到 GitHub"
        } else {
            Write-Info "跳过代码提交步骤"
        }

        # 步骤2：连接服务器
        Write-Step "步骤 2/4：连接到阿里云服务器"
        Write-Info "服务器地址: $SERVER_IP"
        Write-Info "部署路径: $REMOTE_PATH"

        # 步骤3：拉取代码
        Write-Step "步骤 3/4：拉取最新代码并部署"
        
        $sshCommands = @"
cd $REMOTE_PATH
echo "正在拉取最新代码..."
git pull origin master
if [ `$? -eq 0 ]; then
    echo "✓ 代码拉取成功"
else
    echo "✗ 代码拉取失败"
    exit 1
fi
"@

        $result = echo $sshCommands | ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP"
        Write-Host $result
        Write-Success "代码拉取完成"

        # 步骤4：重启服务
        Write-Step "步骤 4/4：重启 Docker 服务"
        
        $deployCommands = @"
cd $REMOTE_PATH
echo "停止现有服务..."
docker-compose down

echo "构建并启动服务..."
docker-compose up -d --build

if [ `$? -eq 0 ]; then
    echo "✓ 服务启动成功"
else
    echo "✗ 服务启动失败"
    exit 1
fi
"@

        $deployResult = echo $deployCommands | ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP"
        Write-Host $deployResult
        Write-Success "服务重启完成"

        # 等待服务启动
        Write-Info "等待服务启动..."
        Start-Sleep -Seconds 5

        # 验证部署
        Write-Step "验证部署状态"
        
        $checkCommands = @"
cd $REMOTE_PATH
echo ""
echo "=== 容器状态 ==="
docker-compose ps
"@

        $checkResult = echo $checkCommands | ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP"
        Write-Host $checkResult

        # 完成
        Write-Host ""
        Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║          部署完成！                   ║" -ForegroundColor Green
        Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Green
        Write-Host ""
        Write-Host "访问地址: http://$SERVER_IP" -ForegroundColor Cyan
        Write-Host ""

    } catch {
        Write-Error "部署过程中发生错误: $_"
        Write-Host ""
        Write-Host "请检查以下内容：" -ForegroundColor Yellow
        Write-Host "  1. 网络连接是否正常" -ForegroundColor Yellow
        Write-Host "  2. 服务器是否可访问" -ForegroundColor Yellow
        Write-Host "  3. Git 和 SSH 是否已安装" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
}

# 执行部署
Deploy

# 基于 Python 3.9 的官方镜像
# 修改历史：
# - 2026-04-08 14:30:00: 移除 sed 命令修改 sources.list（slim 镜像中该文件不存在）
# - 2026-04-08 14:30:00: 创建数据库初始化脚本，解决多进程竞态条件问题
# - 2026-04-08 14:30:00: 兼容 Alibaba Cloud Linux 3.2104 LTS Docker 部署
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 2026-04-08 14:30:00: 安装系统依赖（使用默认源，slim 镜像没有 sources.list 文件）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2026-04-08 14:30:00: 安装 setuptools 和 pip（使用清华源加速）
RUN python -m ensurepip --upgrade && \
    python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

# 复制 requirements.txt
COPY requirements.txt .

# 2026-04-08 14:30:00: 安装 Python 依赖（使用清华源加速）
RUN python -m pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

# 复制项目文件
COPY . .

# 创建上传目录
RUN mkdir -p uploads

# 2026-04-08 14:30:00: 创建数据库初始化脚本（解决多进程竞态条件）
# 脚本逻辑：先单进程初始化数据库，再启动多进程 gunicorn
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# 使用单进程模式初始化数据库\n\
python -c "from exam_system.app import create_app; app = create_app()"\n\
\n\
# 启动 gunicorn\n\
exec gunicorn "exam_system.app:app" -w 4 -b "0.0.0.0:5001" --timeout 300' > /app/start.sh && chmod +x /app/start.sh

# 暴露端口
EXPOSE 5001

# 2026-04-08 14:30:00: 使用启动脚本启动应用
CMD ["/app/start.sh"]

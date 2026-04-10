# 基于 Python 3.9 的官方镜像（Alibaba Cloud Linux / 通用 Linux 部署）
# 注意：docker-compose 中 backend 的 build.context 必须为项目根目录「.」，不能为 ./exam_system
FROM python:3.9-slim

WORKDIR /app

# 构建依赖与 MySQL 客户端（mysqldump / mysql，用于管理端备份与恢复）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-mysql-client \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m ensurepip --upgrade && \
    python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

COPY . .

RUN mkdir -p uploads && chmod +x /app/scripts/docker-start.sh

EXPOSE 5001

CMD ["/app/scripts/docker-start.sh"]

# 基于Python 3.9的官方镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["gunicorn", "run:app", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "300"]

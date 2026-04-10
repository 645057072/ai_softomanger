# 构建上下文为 nginx/目录。主配置打入镜像；清空默认 html，避免未挂载 dist 时仍显示欢迎页
FROM nginx:alpine

RUN rm -f /etc/nginx/conf.d/default.conf \
    && rm -rf /usr/share/nginx/html/*

COPY nginx.conf /etc/nginx/nginx.conf

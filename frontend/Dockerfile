# 多阶段：构建 Vite 产物，再由 nginx 提供静态资源（供入口 nginx 反代，避免宿主机未挂载 dist 时出现默认欢迎页）
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --registry=https://registry.npmmirror.com
COPY . .
RUN npm run build

FROM nginx:alpine
RUN rm -f /etc/nginx/conf.d/default.conf \
    && rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx-spa.conf /etc/nginx/nginx.conf
EXPOSE 80
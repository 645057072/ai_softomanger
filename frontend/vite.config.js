import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
// 开发：npm run dev，默认打开 /login；API 由 /api 代理到本机 5001（需先启动后端）
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    strictPort: true,
    // 绑定所有网卡，便于本机以外设备访问开发环境（原仅 127.0.0.1 时局域网无法打开登录页）
    host: true,
    open: '/login',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  },
  preview: {
    port: 4173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true
      }
    }
  }
})

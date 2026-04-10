<!--
  文件名：Login.vue
  描述：用户登录页面组件
  作者：Li zekun
  创建日期：2026-04-08
  最后修改：2026-04-08
-->

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo"></div>
        <h1>考试系统</h1>
        <p class="subtitle">Online Examination System</p>
      </div>

      <div class="login-form">
        <div class="form-item">
          <label class="form-label">用户：</label>
          <input 
            type="text" 
            v-model="username" 
            placeholder="请输入用户名"
            autocomplete="off"
            class="form-input"
          />
        </div>

        <div class="form-item">
          <label class="form-label">密码：</label>
          <input 
            type="password" 
            v-model="password" 
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
            class="form-input"
          />
        </div>

        <div class="form-item">
          <label class="form-label">日期：</label>
          <input 
            type="date" 
            v-model="loginDate" 
            class="form-input"
          />
        </div>

        <div class="form-buttons">
          <button class="btn-register" @click="handleRegister">注册</button>
          <button class="btn-login" :disabled="loginSubmitting" @click="handleLogin">{{ loginSubmitting ? '登录中...' : '登录' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useUserStore } from '../../store'
import { authApi } from '../../api'
import { normalizeAccessToken } from '../../utils/accessToken'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      loginDate: new Date().toISOString().split('T')[0],
      loginSubmitting: false
    }
  },
  methods: {
    async handleLogin() {
      if (!this.username || !this.password) {
        this.$message.error('请输入用户名和密码')
        return
      }
      if (this.loginSubmitting) return
      this.loginSubmitting = true

      try {
        const result = await authApi.login({
          username: this.username,
          password: this.password
        })

        if (result.code === 200) {
          const rawToken = result.data?.access_token
          if (!rawToken || typeof rawToken !== 'string') {
            this.$message.error('登录响应缺少访问令牌，请重试或联系管理员')
            return
          }
          const userStore = useUserStore()
          userStore.login(rawToken, result.data.user)
          // 显式传入 access_token，避免拦截器与 localStorage 写入的竞态导致未带 Authorization
          try {
            const pr = await authApi.getProfile(rawToken)
            if (pr.code === 200 && pr.data) {
              userStore.login(rawToken, pr.data)
              if (typeof sessionStorage !== 'undefined') {
                sessionStorage.setItem('profile_synced_token', normalizeAccessToken(rawToken))
              }
              this.$message.success('登录成功')
              await this.$router.push('/home')
            } else {
              userStore.logout()
              this.$message.error(pr.message || '会话校验失败，请重新登录')
            }
          } catch (e) {
            userStore.logout()
            const m = e?.response?.data?.message
            this.$message.error(m || '会话校验失败，请重新登录')
          }
        } else {
          this.$message.error(result.message)
          // 用户名保留，清空密码便于重新输入
          this.password = ''
        }
      } catch (error) {
        console.error('登录失败:', error)
        const backendMessage = error?.response?.data?.message
        this.$message.error(backendMessage || '登录失败，请检查网络连接')
        // 用户名保留，清空密码便于重新输入
        this.password = ''
      } finally {
        this.loginSubmitting = false
      }
    },

    handleRegister() {
      this.$router.push('/register')
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 50px 40px;
  width: 100%;
  max-width: 420px;
}

.login-header {
  text-align: center;
  margin-bottom: 35px;
}

.logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 15px;
  border-radius: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.25);
}

.login-header h1 {
  color: #333;
  font-size: 28px;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.form-item {
  display: flex;
  align-items: center;
  margin-bottom: 22px;
}

.form-label {
  width: 60px;
  color: #555;
  font-size: 14px;
  font-weight: 500;
  text-align: right;
  padding-right: 10px;
  flex-shrink: 0;
}

.form-input {
  flex: 1;
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-buttons {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn-register,
.btn-login {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.btn-register {
  background: #f5f5f5;
  color: #666;
}

.btn-register:hover {
  background: #e0e0e0;
}

.btn-login {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-login:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}
</style>

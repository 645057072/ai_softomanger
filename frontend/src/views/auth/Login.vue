<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo">📚</div>
        <h1>考试系统</h1>
        <p class="subtitle">Online Examination System</p>
      </div>

      <div class="login-form">
        <div class="form-item">
          <label>用户名</label>
          <input 
            type="text" 
            v-model="username" 
            placeholder="请输入用户名"
            autocomplete="off"
          />
        </div>

        <div class="form-item">
          <label>密码</label>
          <input 
            type="password" 
            v-model="password" 
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
        </div>

        <div class="form-item">
          <label>登录日期</label>
          <input 
            type="date" 
            v-model="loginDate" 
          />
        </div>

        <div class="form-buttons">
          <button class="btn-cancel" @click="handleCancel">取消</button>
          <button class="btn-login" @click="handleLogin">登录</button>
        </div>

        <div class="form-footer">
          <p>还没有账号？<router-link to="/register">立即注册</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      loginDate: new Date().toISOString().split('T')[0]
    }
  },
  methods: {
    ...mapActions(['login']),
    
    handleLogin() {
      if (!this.username || !this.password) {
        this.$message.error('请输入用户名和密码')
        return
      }

      this.login({
        username: this.username,
        password: this.password
      }).then(() => {
        this.$message.success('登录成功')
        this.$router.push('/home')
      }).catch(error => {
        this.$message.error(error.response?.data?.message || '登录失败')
      })
    },

    handleCancel() {
      this.username = ''
      this.password = ''
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
  max-width: 450px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  font-size: 70px;
  margin-bottom: 15px;
}

.login-header h1 {
  color: #333;
  font-size: 28px;
  margin-bottom: 10px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.form-item {
  margin-bottom: 25px;
}

.form-item label {
  display: block;
  color: #555;
  font-size: 14px;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-item input {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-item input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-buttons {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn-cancel,
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

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
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

.form-footer {
  margin-top: 25px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.form-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <h2>考试系统登录</h2>
          <p>请输入您的账号和密码</p>
        </div>
      </template>
      <el-form
        ref="loginForm"
        :model="loginForm"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
          <el-link type="primary" href="/register">立即注册</el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../store'
import { authApi } from '../../api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const loading = ref(false)
    const loginForm = reactive({
      username: '',
      password: ''
    })
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
      ]
    }

    const handleLogin = async () => {
      loading.value = true
      try {
        const response = await authApi.login(loginForm)
        if (response.code === 200) {
          userStore.login(response.data.access_token, response.data.user)
          router.push('/')
        } else {
          ElMessage.error(response.message)
        }
      } catch (error) {
        ElMessage.error('登录失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }

    return {
      loginForm,
      rules,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  overflow: hidden;
}

.login-header {
  text-align: center;
  margin-bottom: 20px;
}

.login-header h2 {
  color: #303133;
  margin-bottom: 8px;
}

.login-header p {
  color: #606266;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  margin-bottom: 10px;
}
</style>

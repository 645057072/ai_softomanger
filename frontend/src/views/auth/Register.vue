<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="register-header">
          <h2>用户注册</h2>
          <p>创建一个新账号</p>
        </div>
      </template>
      <el-form
        ref="registerForm"
        :model="registerForm"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            prefix-icon="Message"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item label="真实姓名" prop="realName">
          <el-input
            v-model="registerForm.realName"
            placeholder="请输入真实姓名"
            prefix-icon="Avatar"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            class="register-btn"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
          <el-link type="primary" href="/login">已有账号？去登录</el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../../api'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const registerForm = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      realName: ''
    })
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在3-20之间', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== registerForm.password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ],
      realName: [
        { required: true, message: '请输入真实姓名', trigger: 'blur' }
      ]
    }

    const handleRegister = async () => {
      loading.value = true
      try {
        const response = await authApi.register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          real_name: registerForm.realName
        })
        if (response.code === 200) {
          ElMessage.success('注册成功，请登录')
          router.push('/login')
        } else {
          ElMessage.error(response.message)
        }
      } catch (error) {
        ElMessage.error('注册失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }

    return {
      registerForm,
      rules,
      loading,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.register-card {
  width: 450px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  overflow: hidden;
}

.register-header {
  text-align: center;
  margin-bottom: 20px;
}

.register-header h2 {
  color: #303133;
  margin-bottom: 8px;
}

.register-header p {
  color: #606266;
  font-size: 14px;
}

.register-btn {
  width: 100%;
  margin-bottom: 10px;
}
</style>

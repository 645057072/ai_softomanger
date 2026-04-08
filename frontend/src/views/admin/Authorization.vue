<template>
  <div class="authorization-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>功能授权</span>
        </div>
      </template>
      <div class="auth-content">
        <el-alert
          title="功能授权用于为不同角色分配系统功能权限"
          type="info"
          :closable="false"
          show-icon
        />
        <div class="placeholder">
          <p>功能授权模块开发中...</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'

export default {
  name: 'Authorization',
  setup() {
    return {}
  }
}
</script>

<style scoped>
.authorization-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.auth-content {
  padding: 20px 0;
}

.placeholder {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}
</style>

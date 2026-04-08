<template>
  <div class="data-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据管理</span>
        </div>
      </template>
      <div class="data-content">
        <el-alert
          title="数据管理用于系统数据备份与恢复操作"
          type="warning"
          :closable="false"
          show-icon
        />
        <div class="placeholder">
          <p>数据管理模块开发中...</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'

export default {
  name: 'Data',
  setup() {
    return {}
  }
}
</script>

<style scoped>
.data-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-content {
  padding: 20px 0;
}

.placeholder {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}
</style>

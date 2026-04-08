<template>
  <div class="role-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" @click="handleAdd">新增角色</el-button>
        </div>
      </template>
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="description" label="角色描述" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 1" type="success">正常</el-tag>
            <el-tag v-else type="danger">禁用</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Role',
  setup() {
    const tableData = ref([])
    
    const fetchData = async () => {
      try {
        const response = await fetch('/api/role', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        const result = await response.json()
        if (result.code === 200) {
          tableData.value = result.data.list || []
        }
      } catch (error) {
        ElMessage.error('获取数据失败')
      }
    }
    
    const handleAdd = () => {
      ElMessage.info('功能开发中...')
    }
    
    const handleEdit = (row) => {
      ElMessage.info('功能开发中...')
    }
    
    const handleDelete = (row) => {
      ElMessage.info('功能开发中...')
    }
    
    onMounted(() => {
      fetchData()
    })
    
    return {
      tableData,
      handleAdd,
      handleEdit,
      handleDelete
    }
  }
}
</script>

<style scoped>
.role-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

<template>
  <div class="page-wrap">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据备份</span>
          <el-button type="primary" :loading="loading" @click="handleBackup">立即备份</el-button>
        </div>
      </template>
      <el-table :data="list" border>
        <el-table-column type="index" label="序号" width="70" />
        <el-table-column prop="filename" label="备份文件名" min-width="240" />
        <el-table-column prop="size" label="大小(字节)" width="120" />
        <el-table-column prop="created" label="创建时间" width="220" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button style="margin-top: 16px" @click="loadList">刷新列表</el-button>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dataBackupApi } from '../../api'

export default {
  name: 'DataBackupPage',
  setup() {
    const list = ref([])
    const loading = ref(false)

    const loadList = async () => {
      try {
        const result = await dataBackupApi.list()
        if (result.code === 200) {
          list.value = result.data.list || []
        } else {
          ElMessage.error(result.message || '获取失败')
        }
      } catch (e) {
        const m = e?.response?.data?.message
        ElMessage.error(m || '获取失败')
      }
    }

    const handleDelete = (row) => {
      ElMessageBox.confirm(`确定删除备份文件「${row.filename}」吗？`, '提示', { type: 'warning' })
        .then(async () => {
          try {
            const result = await dataBackupApi.remove(row.filename)
            if (result.code === 200) {
              ElMessage.success(result.message || '已删除')
              loadList()
            } else {
              ElMessage.error(result.message || '删除失败')
            }
          } catch (e) {
            const m = e?.response?.data?.message
            ElMessage.error(m || '删除失败')
          }
        })
        .catch(() => {})
    }

    const handleBackup = async () => {
      loading.value = true
      try {
        const result = await dataBackupApi.create()
        if (result.code === 200) {
          ElMessage.success(result.message || '备份成功')
          loadList()
        } else {
          ElMessage.error(result.message || '备份失败')
        }
      } catch (e) {
        const m = e?.response?.data?.message
        ElMessage.error(m || '备份失败')
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadList()
    })

    return { list, loading, loadList, handleBackup, handleDelete }
  }
}
</script>

<style scoped>
.page-wrap {
  padding: 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

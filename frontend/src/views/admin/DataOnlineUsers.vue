<template>
  <div class="page-wrap">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>在线用户</span>
          <div class="toolbar">
            <el-input
              v-model="queryUsername"
              placeholder="按用户名查询"
              clearable
              style="width: 200px; margin-right: 12px"
              @clear="fetchData"
            />
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleRefresh">刷新</el-button>
          </div>
        </div>
      </template>
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column type="index" label="序号" width="70" :index="indexMethod" />
        <el-table-column prop="username" label="用户名" width="140" />
        <el-table-column prop="ip_address" label="IP地址" width="160" />
        <el-table-column prop="login_time" label="登录时间" min-width="180" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" type="danger" @click="handleRemove(scope.row)">下线</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        layout="total, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end"
        @current-change="fetchData"
      />
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onlineUsersApi } from '../../api'

export default {
  name: 'DataOnlineUsers',
  setup() {
    const tableData = ref([])
    const queryUsername = ref('')
    const pagination = reactive({ page: 1, per_page: 10, total: 0 })

    const fetchData = async () => {
      try {
        const params = {
          page: pagination.page,
          per_page: pagination.per_page
        }
        if (queryUsername.value.trim()) {
          params.username = queryUsername.value.trim()
        }
        const result = await onlineUsersApi.getList(params)
        if (result.code === 200) {
          tableData.value = result.data.list
          pagination.total = result.data.total
        } else {
          ElMessage.error(result.message || '获取失败')
        }
      } catch (e) {
        const m = e?.response?.data?.message
        ElMessage.error(m || '获取失败')
      }
    }

    const handleSearch = () => {
      pagination.page = 1
      fetchData()
    }

    const handleRefresh = () => {
      fetchData()
    }

    const handleRemove = (row) => {
      ElMessageBox.confirm('确定将该用户从在线列表移除吗？', '提示', {
        type: 'warning'
      }).then(async () => {
        try {
          const result = await onlineUsersApi.remove(row.id)
          if (result.code === 200) {
            ElMessage.success('已移除')
            fetchData()
          } else {
            ElMessage.error(result.message || '操作失败')
          }
        } catch (e) {
          const m = e?.response?.data?.message
          ElMessage.error(m || '操作失败')
        }
      }).catch(() => {})
    }

    const indexMethod = (index) => {
      return (pagination.page - 1) * pagination.per_page + index + 1
    }

    onMounted(() => {
      fetchData()
    })

    return {
      tableData,
      queryUsername,
      pagination,
      fetchData,
      handleSearch,
      handleRefresh,
      handleRemove,
      indexMethod
    }
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
  flex-wrap: wrap;
  gap: 12px;
}
.toolbar {
  display: flex;
  align-items: center;
}
</style>

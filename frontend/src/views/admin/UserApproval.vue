<template>
  <div class="approval-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户注册审批</span>
          <el-button type="primary" @click="handleRefresh">刷新</el-button>
        </div>
      </template>
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="real_name" label="真实姓名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="id_card" label="身份证号" />
        <el-table-column prop="created_at" label="注册时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" type="success" @click="handleApprove(scope.row)">通过</el-button>
            <el-button size="small" type="warning" @click="handleReject(scope.row)">退回</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        @current-change="handlePageChange"
        layout="total, prev, pager, next"
      />
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'UserApproval',
  setup() {
    const tableData = ref([])
    const pagination = reactive({
      page: 1,
      per_page: 10,
      total: 0
    })

    const fetchData = async () => {
      try {
        const response = await fetch(
          `/api/user-management/pending?page=${pagination.page}&per_page=${pagination.per_page}`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        )
        const result = await response.json()
        if (result.code === 200) {
          tableData.value = result.data.list
          pagination.total = result.data.total
        }
      } catch (error) {
        ElMessage.error('获取数据失败')
      }
    }

    const handleRefresh = () => {
      pagination.page = 1
      fetchData()
    }

    const handleApprove = (row) => {
      ElMessageBox.confirm('确定要通过该用户的注册申请吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await fetch(`/api/user-management/${row.id}/approve`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          })
          const result = await response.json()
          if (result.code === 200) {
            ElMessage.success('审核通过')
            fetchData()
          } else {
            ElMessage.error(result.message)
          }
        } catch (error) {
          ElMessage.error('操作失败')
        }
      })
    }

    const handleReject = (row) => {
      ElMessageBox.confirm('确定要退回该用户的注册申请吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await fetch(`/api/user-management/${row.id}/reject`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          })
          const result = await response.json()
          if (result.code === 200) {
            ElMessage.success('已退回')
            fetchData()
          } else {
            ElMessage.error(result.message)
          }
        } catch (error) {
          ElMessage.error('操作失败')
        }
      })
    }

    const handleDelete = (row) => {
      ElMessageBox.confirm('确定要删除该用户吗？删除后不可恢复', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await fetch(`/api/user-management/${row.id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          })
          const result = await response.json()
          if (result.code === 200) {
            ElMessage.success('删除成功')
            fetchData()
          } else {
            ElMessage.error(result.message)
          }
        } catch (error) {
          ElMessage.error('删除失败')
        }
      })
    }

    const handlePageChange = () => {
      fetchData()
    }

    onMounted(() => {
      fetchData()
    })

    return {
      tableData,
      pagination,
      handleRefresh,
      handleApprove,
      handleReject,
      handleDelete,
      handlePageChange
    }
  }
}
</script>

<style scoped>
.approval-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>

<template>
  <div class="user-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleRefresh">刷新</el-button>
        </div>
      </template>
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="real_name" label="真实姓名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="id_card" label="身份证号" />
        <el-table-column prop="role" label="角色">
          <template #default="scope">
            <el-tag v-if="scope.row.role === 'admin'" type="danger">管理员</el-tag>
            <el-tag v-else-if="scope.row.role === 'teacher'" type="warning">教师</el-tag>
            <el-tag v-else>学生</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 0" type="warning">待审核</el-tag>
            <el-tag v-else-if="scope.row.status === 1" type="success">正常</el-tag>
            <el-tag v-else type="danger">禁用</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
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

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" title="编辑用户" width="600px">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="用户名">
          <el-input v-model="formData.username" disabled />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="formData.real_name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="formData.phone" />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="formData.id_card" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="待审核" :value="0" />
            <el-option label="正常" :value="1" />
            <el-option label="禁用" :value="2" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'UserManagement',
  setup() {
    const tableData = ref([])
    const pagination = reactive({
      page: 1,
      per_page: 10,
      total: 0
    })
    const dialogVisible = ref(false)
    const formRef = ref(null)
    const formData = reactive({
      id: null,
      username: '',
      real_name: '',
      email: '',
      phone: '',
      id_card: '',
      role: '',
      status: 1
    })

    const rules = {
      real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ]
    }

    const fetchData = async () => {
      try {
        const response = await fetch(
          `/api/user-management/all?page=${pagination.page}&per_page=${pagination.per_page}`,
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

    const handleEdit = (row) => {
      Object.assign(formData, row)
      dialogVisible.value = true
    }

    const handleSubmit = async () => {
      if (!formRef.value) return
      await formRef.value.validate(async (valid) => {
        if (valid) {
          try {
            const response = await fetch(`/api/user-management/${formData.id}`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
              },
              body: JSON.stringify(formData)
            })
            const result = await response.json()
            if (result.code === 200) {
              ElMessage.success('更新成功')
              dialogVisible.value = false
              fetchData()
            } else {
              ElMessage.error(result.message)
            }
          } catch (error) {
            ElMessage.error('操作失败')
          }
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
      dialogVisible,
      formRef,
      formData,
      rules,
      handleRefresh,
      handleEdit,
      handleSubmit,
      handleDelete,
      handlePageChange
    }
  }
}
</script>

<style scoped>
.user-container {
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

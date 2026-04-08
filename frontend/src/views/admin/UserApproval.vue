<template>
  <div class="message-center-container">
    <el-row :gutter="20" style="height: 100%">
      <!-- 左侧消息分类菜单 -->
      <el-col :span="4" style="border-right: 1px solid #e4e7ed; padding-right: 0;">
        <div class="message-categories">
          <div 
            class="category-item" 
            :class="{ 'active': currentCategory === 'unread' }"
            @click="switchCategory('unread')"
          >
            <span class="category-icon">📬</span>
            <span class="category-name">未读消息</span>
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" style="margin-left: auto;" />
          </div>
          <div 
            class="category-item" 
            :class="{ 'active': currentCategory === 'read' }"
            @click="switchCategory('read')"
          >
            <span class="category-icon">📭</span>
            <span class="category-name">已读消息</span>
          </div>
          <div 
            class="category-item" 
            :class="{ 'active': currentCategory === 'deleted' }"
            @click="switchCategory('deleted')"
          >
            <span class="category-icon">🗑️</span>
            <span class="category-name">已删除</span>
          </div>
        </div>
      </el-col>

      <!-- 右侧消息列表和详情 -->
      <el-col :span="20">
        <!-- 消息列表 -->
        <div v-if="!selectedMessage" class="message-list-container">
          <div class="list-header">
            <h3>{{ categoryNames[currentCategory] }}</h3>
            <el-button type="primary" @click="fetchData" icon="Refresh">刷新</el-button>
          </div>
          
          <el-table 
            :data="tableData" 
            border 
            style="width: 100%"
            @row-click="handleRowClick"
            :row-class-name="tableRowClassName"
          >
            <el-table-column type="index" label="序号" width="60" :index="indexMethod" />
            <el-table-column prop="username" label="用户" width="120" />
            <el-table-column prop="real_name" label="姓名" width="100" />
            <el-table-column label="消息标题" min-width="300">
              <template #default="scope">
                <span class="message-title">{{ scope.row.username }} 提交的用户注册消息，请审批</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="提交日期" width="180" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="scope">
                <el-button size="small" @click.stop="viewDetail(scope.row)">查看</el-button>
                <el-button 
                  v-if="currentCategory === 'unread'" 
                  size="small" 
                  type="success" 
                  @click.stop="handleApprove(scope.row)"
                >同意</el-button>
                <el-button 
                  v-if="currentCategory === 'unread'" 
                  size="small" 
                  type="warning" 
                  @click.stop="handleReject(scope.row)"
                >退回</el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click.stop="handleDelete(scope.row)"
                >删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.per_page"
            :total="pagination.total"
            @current-change="handlePageChange"
            layout="total, prev, pager, next"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </div>

        <!-- 消息详情 -->
        <div v-else class="message-detail-container">
          <div class="detail-header">
            <el-button @click="backToList">← 返回列表</el-button>
            <div class="detail-actions">
              <el-button 
                v-if="currentCategory === 'unread'" 
                type="success" 
                @click="handleApprove(selectedMessage)"
              >同意</el-button>
              <el-button 
                v-if="currentCategory === 'unread'" 
                type="warning" 
                @click="handleReject(selectedMessage)"
              >退回</el-button>
              <el-button type="danger" @click="handleDelete(selectedMessage)">删除</el-button>
            </div>
          </div>
          
          <el-card class="detail-card">
            <template #header>
              <div class="card-header">
                <span>用户注册申请表单</span>
              </div>
            </template>
            
            <el-form :model="selectedMessage" label-width="120px" size="large">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="用户名：">
                    <span>{{ selectedMessage.username }}</span>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="真实姓名：">
                    <span>{{ selectedMessage.real_name }}</span>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="邮箱：">
                    <span>{{ selectedMessage.email }}</span>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="手机号：">
                    <span>{{ selectedMessage.phone }}</span>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="身份证号：">
                    <span>{{ selectedMessage.id_card }}</span>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="角色：">
                    <el-tag v-if="selectedMessage.role === 'admin'" type="danger">管理员</el-tag>
                    <el-tag v-else-if="selectedMessage.role === 'teacher'" type="warning">教师</el-tag>
                    <el-tag v-else>学生</el-tag>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="注册日期：">
                    <span>{{ selectedMessage.created_at }}</span>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="状态：">
                    <el-tag v-if="selectedMessage.status === 0" type="warning">待审核</el-tag>
                    <el-tag v-else-if="selectedMessage.status === 1" type="success">正常</el-tag>
                    <el-tag v-else type="danger">禁用</el-tag>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'UserApproval',
  setup() {
    const currentCategory = ref('unread')
    const selectedMessage = ref(null)
    const tableData = ref([])
    const unreadCount = ref(0)
    const pagination = reactive({
      page: 1,
      per_page: 10,
      total: 0
    })

    const categoryNames = {
      unread: '未读消息',
      read: '已读消息',
      deleted: '已删除'
    }

    const fetchData = async () => {
      try {
        let url
        if (currentCategory.value === 'unread') {
          url = `/api/user-management/pending?page=${pagination.page}&per_page=${pagination.per_page}`
        } else if (currentCategory.value === 'read') {
          url = `/api/user-management/approved?page=${pagination.page}&per_page=${pagination.per_page}`
        } else {
          url = `/api/user-management/all?page=${pagination.page}&per_page=${pagination.per_page}&status=2`
        }
        
        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        const result = await response.json()
        if (result.code === 200) {
          tableData.value = result.data.list
          pagination.total = result.data.total
          
          if (currentCategory.value === 'unread') {
            unreadCount.value = result.data.total
          }
        }
      } catch (error) {
        ElMessage.error('获取数据失败')
      }
    }

    const switchCategory = (category) => {
      currentCategory.value = category
      selectedMessage.value = null
      pagination.page = 1
      fetchData()
    }

    const handleRowClick = (row) => {
      viewDetail(row)
    }

    const viewDetail = (row) => {
      selectedMessage.value = row
    }

    const backToList = () => {
      selectedMessage.value = null
    }

    const handleApprove = (row) => {
      ElMessageBox.confirm('确定要同意该用户的注册申请吗？', '提示', {
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

    const indexMethod = (index) => {
      return (pagination.page - 1) * pagination.per_page + index + 1
    }

    const tableRowClassName = ({ row, rowIndex }) => {
      if (currentCategory.value === 'unread') {
        return 'unread-row'
      }
      return ''
    }

    onMounted(() => {
      fetchData()
    })

    return {
      currentCategory,
      selectedMessage,
      tableData,
      unreadCount,
      pagination,
      categoryNames,
      fetchData,
      switchCategory,
      handleRowClick,
      viewDetail,
      backToList,
      handleApprove,
      handleReject,
      handleDelete,
      handlePageChange,
      indexMethod,
      tableRowClassName
    }
  }
}
</script>

<style scoped>
.message-center-container {
  height: calc(100vh - 120px);
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.message-categories {
  padding: 20px 0;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.category-item:hover {
  background: #f5f7fa;
}

.category-item.active {
  background: #ecf5ff;
  border-left-color: #409eff;
  color: #409eff;
}

.category-icon {
  font-size: 20px;
  margin-right: 12px;
}

.category-name {
  font-size: 15px;
  font-weight: 500;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.list-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.message-title {
  color: #409eff;
  cursor: pointer;
}

.message-title:hover {
  text-decoration: underline;
}

:deep(.el-table__row.unread-row) {
  background-color: #f0f9ff;
}

:deep(.el-table__row.unread-row:hover) {
  background-color: #e6f7ff;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #f5f7fa;
}

.detail-actions {
  display: flex;
  gap: 10px;
}

.detail-card {
  margin: 20px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
</style>

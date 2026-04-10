<template>
  <div class="page-wrap">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>日志</span>
          <div class="toolbar">
            <el-input
              v-model="queryUsername"
              placeholder="按用户查询"
              clearable
              style="width: 160px; margin-right: 8px"
              @clear="fetchData"
            />
            <el-select
              v-model="queryStatus"
              placeholder="操作状态"
              clearable
              style="width: 130px; margin-right: 8px"
              @clear="fetchData"
            >
              <el-option label="提交" value="提交" />
              <el-option label="审核" value="审核" />
              <el-option label="失败" value="失败" />
            </el-select>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleRefresh">刷新</el-button>
            <el-button type="success" @click="openCreate">新增</el-button>
          </div>
        </div>
      </template>
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column type="index" label="序号" width="70" :index="indexMethod" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="description" label="操作功能详细说明" min-width="200" show-overflow-tooltip />
        <el-table-column prop="op_status" label="操作状态" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.op_status === '失败'" type="danger">{{ scope.row.op_status }}</el-tag>
            <el-tag v-else-if="scope.row.op_status === '审核'" type="success">{{ scope.row.op_status }}</el-tag>
            <el-tag v-else type="info">{{ scope.row.op_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="失败详情" width="120">
          <template #default="scope">
            <el-button
              v-if="scope.row.op_status === '失败' && scope.row.failure_detail"
              link
              type="primary"
              @click="showDetail(scope.row)"
            >
              查看详情
            </el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openEdit(scope.row)">编辑</el-button>
            <el-button link type="danger" @click="handleRemove(scope.row)">删除</el-button>
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

    <el-dialog v-model="detailVisible" title="失败详细日志" width="640px">
      <pre class="log-pre">{{ detailText }}</pre>
    </el-dialog>

    <el-dialog v-model="editVisible" :title="editId ? '编辑日志' : '新增日志'" width="520px" @closed="resetForm">
      <el-form :model="form" label-width="120px">
        <el-form-item label="操作说明" required>
          <el-input v-model="form.description" maxlength="100" show-word-limit type="textarea" :rows="3" placeholder="100字以内" />
        </el-form-item>
        <el-form-item label="操作状态" required>
          <el-select v-model="form.op_status" style="width: 100%">
            <el-option label="提交" value="提交" />
            <el-option label="审核" value="审核" />
            <el-option label="失败" value="失败" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.op_status === '失败'" label="失败详情">
          <el-input v-model="form.failure_detail" type="textarea" :rows="6" placeholder="log4 风格详细日志" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { bizOperationLogsApi } from '../../api'

export default {
  name: 'DataLogs',
  setup() {
    const tableData = ref([])
    const queryUsername = ref('')
    const queryStatus = ref('')
    const pagination = reactive({ page: 1, per_page: 10, total: 0 })
    const detailVisible = ref(false)
    const detailText = ref('')
    const editVisible = ref(false)
    const editId = ref(null)
    const form = reactive({
      description: '',
      op_status: '提交',
      failure_detail: ''
    })

    const fetchData = async () => {
      try {
        const params = {
          page: pagination.page,
          per_page: pagination.per_page
        }
        if (queryUsername.value.trim()) params.username = queryUsername.value.trim()
        if (queryStatus.value) params.op_status = queryStatus.value
        const result = await bizOperationLogsApi.getList(params)
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

    const showDetail = (row) => {
      detailText.value = row.failure_detail || ''
      detailVisible.value = true
    }

    const resetForm = () => {
      editId.value = null
      form.description = ''
      form.op_status = '提交'
      form.failure_detail = ''
    }

    const openCreate = () => {
      resetForm()
      editVisible.value = true
    }

    const openEdit = (row) => {
      editId.value = row.id
      form.description = row.description || ''
      form.op_status = row.op_status || '提交'
      form.failure_detail = row.failure_detail || ''
      editVisible.value = true
    }

    const submitForm = async () => {
      if (!form.description.trim()) {
        ElMessage.error('请填写操作说明')
        return
      }
      try {
        if (editId.value) {
          const result = await bizOperationLogsApi.update(editId.value, {
            description: form.description.trim(),
            op_status: form.op_status,
            failure_detail: form.failure_detail || undefined
          })
          if (result.code === 200) {
            ElMessage.success('保存成功')
            editVisible.value = false
            fetchData()
          } else {
            ElMessage.error(result.message || '保存失败')
          }
        } else {
          const result = await bizOperationLogsApi.create({
            description: form.description.trim(),
            op_status: form.op_status,
            failure_detail: form.failure_detail || undefined
          })
          if (result.code === 200) {
            ElMessage.success('创建成功')
            editVisible.value = false
            fetchData()
          } else {
            ElMessage.error(result.message || '创建失败')
          }
        }
      } catch (e) {
        const m = e?.response?.data?.message
        ElMessage.error(m || '操作失败')
      }
    }

    const handleRemove = (row) => {
      ElMessageBox.confirm('确定删除该条日志吗？', '提示', { type: 'warning' })
        .then(async () => {
          try {
            const result = await bizOperationLogsApi.remove(row.id)
            if (result.code === 200) {
              ElMessage.success('已删除')
              fetchData()
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

    const indexMethod = (index) => {
      return (pagination.page - 1) * pagination.per_page + index + 1
    }

    onMounted(() => {
      fetchData()
    })

    return {
      tableData,
      queryUsername,
      queryStatus,
      pagination,
      detailVisible,
      detailText,
      editVisible,
      editId,
      form,
      resetForm,
      openCreate,
      openEdit,
      submitForm,
      handleRemove,
      fetchData,
      handleSearch,
      handleRefresh,
      showDetail,
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
  flex-wrap: wrap;
}
.log-pre {
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow: auto;
  font-size: 12px;
  line-height: 1.5;
}
</style>

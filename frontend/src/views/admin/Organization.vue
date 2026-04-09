<template>
  <div class="organization-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>组织机构管理</span>
          <el-button type="primary" @click="handleAdd">新增</el-button>
        </div>
      </template>
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="name" label="组织机构名称" />
        <el-table-column prop="tax_id" label="纳税人识别号" />
        <el-table-column prop="address" label="注册地址" />
        <el-table-column prop="phone" label="联系电话" />
        <el-table-column prop="legal_representative" label="法定代表人" />
        <el-table-column prop="registration_date" label="注册日期" />
        <el-table-column prop="industry" label="所属行业" />
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

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="组织机构名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入组织机构名称" />
        </el-form-item>
        <el-form-item label="纳税人识别号" prop="tax_id">
          <el-input v-model="formData.tax_id" placeholder="请输入纳税人识别号" />
        </el-form-item>
        <el-form-item label="注册地址" prop="address">
          <el-input v-model="formData.address" placeholder="请输入注册地址" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="法定代表人" prop="legal_representative">
          <el-input v-model="formData.legal_representative" placeholder="请输入法定代表人" />
        </el-form-item>
        <el-form-item label="注册日期" prop="registration_date">
          <el-date-picker
            v-model="formData.registration_date"
            type="date"
            placeholder="选择注册日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="所属行业" prop="industry">
          <el-select v-model="formData.industry" placeholder="请选择所属行业" style="width: 100%">
            <el-option label="信息技术" value="信息技术" />
            <el-option label="金融" value="金融" />
            <el-option label="教育" value="教育" />
            <el-option label="医疗" value="医疗" />
            <el-option label="制造业" value="制造业" />
            <el-option label="服务业" value="服务业" />
            <el-option label="其他" value="其他" />
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
import { organizationApi } from '../../api'

export default {
  name: 'Organization',
  setup() {
    const tableData = ref([])
    const pagination = reactive({
      page: 1,
      per_page: 10,
      total: 0
    })
    const dialogVisible = ref(false)
    const dialogTitle = ref('新增')
    const formRef = ref(null)
    const formData = reactive({
      id: null,
      name: '',
      tax_id: '',
      address: '',
      phone: '',
      legal_representative: '',
      registration_date: '',
      industry: ''
    })

    const rules = {
      name: [{ required: true, message: '请输入组织机构名称', trigger: 'blur' }]
    }

    const fetchData = async () => {
      try {
        const result = await organizationApi.getList({
          page: pagination.page,
          per_page: pagination.per_page
        })
        if (result.code === 200) {
          tableData.value = result.data.list
          pagination.total = result.data.total
        } else {
          ElMessage.error(result.message || '获取数据失败')
        }
      } catch (error) {
        const backendMessage = error?.response?.data?.message
        ElMessage.error(backendMessage || '获取数据失败')
      }
    }

    const handleAdd = () => {
      dialogTitle.value = '新增'
      Object.assign(formData, {
        id: null,
        name: '',
        tax_id: '',
        address: '',
        phone: '',
        legal_representative: '',
        registration_date: '',
        industry: ''
      })
      dialogVisible.value = true
    }

    const handleEdit = (row) => {
      dialogTitle.value = '编辑'
      Object.assign(formData, row)
      dialogVisible.value = true
    }

    const handleSubmit = async () => {
      if (!formRef.value) return
      await formRef.value.validate(async (valid) => {
        if (valid) {
          try {
            const url = formData.id
              ? `/api/organization/${formData.id}`
              : '/api/organization'
            const method = formData.id ? 'PUT' : 'POST'
            const result = formData.id
              ? await organizationApi.update(formData.id, formData)
              : await organizationApi.create(formData)
            if (result.code === 200) {
              ElMessage.success(dialogTitle.value === '新增' ? '创建成功' : '更新成功')
              dialogVisible.value = false
              fetchData()
            } else {
              ElMessage.error(result.message)
            }
          } catch (error) {
            const backendMessage = error?.response?.data?.message
            ElMessage.error(backendMessage || '操作失败')
          }
        }
      })
    }

    const handleDelete = (row) => {
      ElMessageBox.confirm('确定要删除该组织机构吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const result = await organizationApi.remove(row.id)
          if (result.code === 200) {
            ElMessage.success('删除成功')
            fetchData()
          } else {
            ElMessage.error(result.message)
          }
        } catch (error) {
          const backendMessage = error?.response?.data?.message
          ElMessage.error(backendMessage || '删除失败')
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
      dialogTitle,
      formRef,
      formData,
      rules,
      handleAdd,
      handleEdit,
      handleSubmit,
      handleDelete,
      handlePageChange
    }
  }
}
</script>

<style scoped>
.organization-container {
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

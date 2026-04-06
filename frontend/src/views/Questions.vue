<template>
  <Layout>
    <div class="questions">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>题库管理</span>
            <el-button type="primary" @click="handleImport">
              <el-icon><Upload /></el-icon>
              导入题目
            </el-button>
            <el-button type="success" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出题目
            </el-button>
            <el-button type="warning" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建题目
            </el-button>
          </div>
        </template>
        
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="题目类型">
            <el-select v-model="searchForm.question_type" placeholder="全部">
              <el-option label="单选题" value="single_choice" />
              <el-option label="多选题" value="multiple_choice" />
              <el-option label="判断题" value="judgment" />
            </el-select>
          </el-form-item>
          <el-form-item label="关键词">
            <el-input v-model="searchForm.keyword" placeholder="搜索题目" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-table :data="questionsData" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="question_type" label="类型" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.question_type === 'single_choice'">单选题</el-tag>
              <el-tag type="success" v-else-if="scope.row.question_type === 'multiple_choice'">多选题</el-tag>
              <el-tag type="warning" v-else>判断题</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="question_no" label="题号" width="80" />
          <el-table-column prop="question_text" label="题目内容" min-width="300">
            <template #default="scope">
              {{ scope.row.question_text.length > 50 ? scope.row.question_text.substring(0, 50) + '...' : scope.row.question_text }}
            </template>
          </el-table-column>
          <el-table-column prop="score" label="分值" width="80" />
          <el-table-column prop="difficulty" label="难度" width="80">
            <template #default="scope">
              <el-rate v-model="scope.row.difficulty" disabled />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEdit(scope.row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { questionApi } from '../api'

export default {
  name: 'Questions',
  setup() {
    const questionsData = ref([])
    const searchForm = reactive({
      question_type: '',
      keyword: ''
    })
    const pagination = reactive({
      page: 1,
      pageSize: 10,
      total: 0
    })
    
    const loadQuestions = async () => {
      const response = await questionApi.getList({
        page: pagination.page,
        per_page: pagination.pageSize,
        question_type: searchForm.question_type,
        keyword: searchForm.keyword
      })
      if (response.code === 200) {
        questionsData.value = response.data.list
        pagination.total = response.data.total
      }
    }
    
    const handleSearch = () => {
      pagination.page = 1
      loadQuestions()
    }
    
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadQuestions()
    }
    
    const handleCurrentChange = (current) => {
      pagination.page = current
      loadQuestions()
    }
    
    const handleCreate = () => {
      // 打开新建题目对话框
    }
    
    const handleEdit = (row) => {
      // 打开编辑题目对话框
    }
    
    const handleDelete = (id) => {
      ElMessageBox.confirm('确定要删除这个题目吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const response = await questionApi.delete(id)
        if (response.code === 200) {
          ElMessage.success('删除成功')
          loadQuestions()
        }
      })
    }
    
    const handleImport = () => {
      // 打开导入对话框
    }
    
    const handleExport = () => {
      // 导出题目
    }
    
    onMounted(() => {
      loadQuestions()
    })
    
    return {
      questionsData,
      searchForm,
      pagination,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      handleCreate,
      handleEdit,
      handleDelete,
      handleImport,
      handleExport
    }
  }
}
</script>

<style scoped>
.questions {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>

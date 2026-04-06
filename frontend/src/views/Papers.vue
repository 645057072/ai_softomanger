<template>
  <Layout>
    <div class="papers">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>试卷管理</span>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建试卷
            </el-button>
            <el-button type="success" @click="handleRandom">
              <el-icon><Refresh /></el-icon>
              随机组卷
            </el-button>
          </div>
        </template>
        
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="试卷类型">
            <el-select v-model="searchForm.paper_type" placeholder="全部">
              <el-option label="固定试卷" value="fixed" />
              <el-option label="随机试卷" value="random" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="全部">
              <el-option label="草稿" value="0" />
              <el-option label="已发布" value="1" />
              <el-option label="已结束" value="2" />
            </el-select>
          </el-form-item>
          <el-form-item label="关键词">
            <el-input v-model="searchForm.keyword" placeholder="搜索试卷" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-table :data="papersData" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="试卷名称" min-width="300" />
          <el-table-column prop="paper_type" label="类型" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.paper_type === 'fixed'">固定试卷</el-tag>
              <el-tag type="info" v-else>随机试卷</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_score" label="总分" width="80" />
          <el-table-column prop="duration" label="时长(分钟)" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.status === 0">草稿</el-tag>
              <el-tag type="success" v-else-if="scope.row.status === 1">已发布</el-tag>
              <el-tag type="warning" v-else>已结束</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEdit(scope.row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="success" v-if="scope.row.status === 0" @click="handlePublish(scope.row.id)">
                <el-icon><Check /></el-icon>
                发布
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
import { paperApi } from '../api'

export default {
  name: 'Papers',
  setup() {
    const papersData = ref([])
    const searchForm = reactive({
      paper_type: '',
      status: '',
      keyword: ''
    })
    const pagination = reactive({
      page: 1,
      pageSize: 10,
      total: 0
    })
    
    const loadPapers = async () => {
      const response = await paperApi.getList({
        page: pagination.page,
        per_page: pagination.pageSize,
        paper_type: searchForm.paper_type,
        status: searchForm.status,
        keyword: searchForm.keyword
      })
      if (response.code === 200) {
        papersData.value = response.data.list
        pagination.total = response.data.total
      }
    }
    
    const handleSearch = () => {
      pagination.page = 1
      loadPapers()
    }
    
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadPapers()
    }
    
    const handleCurrentChange = (current) => {
      pagination.page = current
      loadPapers()
    }
    
    const handleCreate = () => {
      // 打开新建试卷对话框
    }
    
    const handleEdit = (row) => {
      // 打开编辑试卷对话框
    }
    
    const handlePublish = async (id) => {
      const response = await paperApi.publish(id)
      if (response.code === 200) {
        ElMessage.success('发布成功')
        loadPapers()
      }
    }
    
    const handleDelete = (id) => {
      ElMessageBox.confirm('确定要删除这个试卷吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const response = await paperApi.delete(id)
        if (response.code === 200) {
          ElMessage.success('删除成功')
          loadPapers()
        }
      })
    }
    
    const handleRandom = () => {
      // 打开随机组卷对话框
    }
    
    onMounted(() => {
      loadPapers()
    })
    
    return {
      papersData,
      searchForm,
      pagination,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      handleCreate,
      handleEdit,
      handlePublish,
      handleDelete,
      handleRandom
    }
  }
}
</script>

<style scoped>
.papers {
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

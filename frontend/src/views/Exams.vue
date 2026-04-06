<template>
  <Layout>
    <div class="exams">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>在线考试</span>
          </div>
        </template>
        
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="全部">
              <el-option label="未开始" value="0" />
              <el-option label="进行中" value="1" />
              <el-option label="已完成" value="2" />
            </el-select>
          </el-form-item>
          <el-form-item label="关键词">
            <el-input v-model="searchForm.keyword" placeholder="搜索考试" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-table :data="examsData" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="paper_title" label="试卷名称" min-width="300" />
          <el-table-column prop="start_time" label="开始时间" width="180" />
          <el-table-column prop="end_time" label="结束时间" width="180" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.status === 0">未开始</el-tag>
              <el-tag type="warning" v-else-if="scope.row.status === 1">进行中</el-tag>
              <el-tag type="success" v-else>已完成</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="得分" width="80" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button size="small" type="primary" v-if="scope.row.status === 1" @click="handleContinue(scope.row.id)">
                <el-icon><Play /></el-icon>
                继续
              </el-button>
              <el-button size="small" type="primary" v-else-if="scope.row.status === 0" @click="handleStart(scope.row.id)">
                <el-icon><Play /></el-icon>
                开始
              </el-button>
              <el-button size="small" type="info" v-else @click="handleReview(scope.row.id)">
                <el-icon><View /></el-icon>
                查看
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
      
      <el-card shadow="hover" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>可用试卷</span>
          </div>
        </template>
        <el-table :data="availablePapers" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="试卷名称" min-width="300" />
          <el-table-column prop="total_score" label="总分" width="80" />
          <el-table-column prop="duration" label="时长(分钟)" width="100" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="scope">
              <el-button size="small" type="primary" @click="handleStartExam(scope.row.id)">
                <el-icon><Play /></el-icon>
                开始考试
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </Layout>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { examApi, paperApi } from '../api'

export default {
  name: 'Exams',
  setup() {
    const examsData = ref([])
    const availablePapers = ref([])
    const searchForm = reactive({
      status: '',
      keyword: ''
    })
    const pagination = reactive({
      page: 1,
      pageSize: 10,
      total: 0
    })
    
    const loadExams = async () => {
      const response = await examApi.getHistory({
        page: pagination.page,
        per_page: pagination.pageSize,
        status: searchForm.status,
        keyword: searchForm.keyword
      })
      if (response.code === 200) {
        examsData.value = response.data.list
        pagination.total = response.data.total
      }
    }
    
    const loadAvailablePapers = async () => {
      const response = await paperApi.getAvailable()
      if (response.code === 200) {
        availablePapers.value = response.data
      }
    }
    
    const handleSearch = () => {
      pagination.page = 1
      loadExams()
    }
    
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadExams()
    }
    
    const handleCurrentChange = (current) => {
      pagination.page = current
      loadExams()
    }
    
    const handleStart = (examId) => {
      // 开始考试
    }
    
    const handleContinue = (examId) => {
      // 继续考试
    }
    
    const handleReview = (examId) => {
      // 查看考试结果
    }
    
    const handleStartExam = async (paperId) => {
      const response = await examApi.start(paperId)
      if (response.code === 200) {
        // 跳转到考试页面
      }
    }
    
    onMounted(() => {
      loadExams()
      loadAvailablePapers()
    })
    
    return {
      examsData,
      availablePapers,
      searchForm,
      pagination,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      handleStart,
      handleContinue,
      handleReview,
      handleStartExam
    }
  }
}
</script>

<style scoped>
.exams {
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

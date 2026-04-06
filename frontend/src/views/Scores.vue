<template>
  <Layout>
    <div class="scores">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>成绩管理</span>
            <el-button type="success" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出成绩
            </el-button>
          </div>
        </template>
        
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="试卷">
            <el-select v-model="searchForm.paper_id" placeholder="全部">
              <el-option label="全部" value="" />
              <el-option v-for="paper in papers" :key="paper.id" :label="paper.title" :value="paper.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="用户">
            <el-input v-model="searchForm.username" placeholder="搜索用户" />
          </el-form-item>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-table :data="scoresData" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="real_name" label="真实姓名" width="120" />
          <el-table-column prop="paper_title" label="试卷名称" min-width="200" />
          <el-table-column prop="score" label="得分" width="80" />
          <el-table-column prop="total_score" label="总分" width="80" />
          <el-table-column prop="duration" label="用时(分钟)" width="100" />
          <el-table-column prop="submit_time" label="提交时间" width="180" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="scope">
              <el-button size="small" type="primary" @click="handleReview(scope.row.id)">
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
            <span>成绩分析</span>
          </div>
        </template>
        <div class="analysis">
          <el-row :gutter="20">
            <el-col :span="12">
              <div id="scoreChart" style="width: 100%; height: 300px;"></div>
            </el-col>
            <el-col :span="12">
              <div id="rankChart" style="width: 100%; height: 300px;"></div>
            </el-col>
          </el-row>
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { scoreApi } from '../api'

export default {
  name: 'Scores',
  setup() {
    const scoresData = ref([])
    const papers = ref([])
    const dateRange = ref([])
    const searchForm = reactive({
      paper_id: '',
      username: ''
    })
    const pagination = reactive({
      page: 1,
      pageSize: 10,
      total: 0
    })
    
    const loadScores = async () => {
      const response = await scoreApi.getList({
        page: pagination.page,
        per_page: pagination.pageSize,
        paper_id: searchForm.paper_id,
        username: searchForm.username,
        start_date: dateRange.value[0] ? dateRange.value[0] : '',
        end_date: dateRange.value[1] ? dateRange.value[1] : ''
      })
      if (response.code === 200) {
        scoresData.value = response.data.list
        pagination.total = response.data.total
      }
    }
    
    const handleSearch = () => {
      pagination.page = 1
      loadScores()
    }
    
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadScores()
    }
    
    const handleCurrentChange = (current) => {
      pagination.page = current
      loadScores()
    }
    
    const handleReview = (examId) => {
      // 查看考试结果
    }
    
    const handleExport = () => {
      // 导出成绩
    }
    
    onMounted(() => {
      loadScores()
    })
    
    return {
      scoresData,
      papers,
      dateRange,
      searchForm,
      pagination,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      handleReview,
      handleExport
    }
  }
}
</script>

<style scoped>
.scores {
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

.analysis {
  margin-top: 20px;
}
</style>

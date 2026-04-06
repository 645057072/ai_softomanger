<template>
  <Layout>
    <div class="home">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <el-statistic title="用户总数" :value="dashboardData?.users?.total || 0">
              <template #suffix>
                <el-icon><user /></el-icon>
              </template>
            </el-statistic>
            <div class="stat-desc">
              学生: {{ dashboardData?.users?.students || 0 }}
              教师: {{ dashboardData?.users?.teachers || 0 }}
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <el-statistic title="题库总量" :value="dashboardData?.questions || 0">
              <template #suffix>
                <el-icon><document /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <el-statistic title="试卷数量" :value="dashboardData?.papers?.total || 0">
              <template #suffix>
                <el-icon><folder /></el-icon>
              </template>
            </el-statistic>
            <div class="stat-desc">
              已发布: {{ dashboardData?.papers?.active || 0 }}
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <el-statistic title="考试次数" :value="dashboardData?.exams?.total || 0">
              <template #suffix>
                <el-icon><timer /></el-icon>
              </template>
            </el-statistic>
            <div class="stat-desc">
              今日: {{ dashboardData?.exams?.today || 0 }}
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card shadow="hover" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>最近7天考试趋势</span>
          </div>
        </template>
        <div id="trendChart" style="width: 100%; height: 300px;"></div>
      </el-card>
    </div>
  </Layout>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { systemApi } from '../api'
import * as echarts from 'echarts'

export default {
  name: 'Home',
  setup() {
    const dashboardData = ref({})
    const trendChart = ref(null)
    
    const loadDashboard = async () => {
      const response = await systemApi.getDashboard()
      if (response.code === 200) {
        dashboardData.value = response.data
        initChart()
      }
    }
    
    const initChart = () => {
      if (dashboardData.value.trend) {
        const chart = echarts.init(document.getElementById('trendChart'))
        const option = {
          xAxis: {
            type: 'category',
            data: dashboardData.value.trend.map(item => item.date)
          },
          yAxis: {
            type: 'value'
          },
          series: [{
            data: dashboardData.value.trend.map(item => item.count),
            type: 'line',
            smooth: true
          }]
        }
        chart.setOption(option)
        window.addEventListener('resize', () => chart.resize())
      }
    }
    
    onMounted(() => {
      loadDashboard()
    })
    
    return {
      dashboardData
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px 0;
}

.stat-card {
  height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-desc {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

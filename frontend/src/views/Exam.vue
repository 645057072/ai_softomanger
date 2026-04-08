<!--
  文件名：Exam.vue
  描述：考试中心页面组件
  作者：Li zekun
  创建日期：2026-04-08
  最后修改：2026-04-08
-->

<template>
  <div class="exam-container">
    <div class="page-header">
      <h1>✏️ 考试中心</h1>
      <p>在线考试与答题</p>
    </div>
    
    <div class="exam-content">
      <div class="placeholder-card">
        <div class="placeholder-icon">✏️</div>
        <h2>考试中心</h2>
        <p>在线考试、答题界面、交卷评分等功能开发中...</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Exam',
  mounted() {
    console.log('Exam component mounted')
  }
}
</script>

<style scoped>
.exam-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: #333;
  font-size: 28px;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  font-size: 14px;
}

.exam-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.placeholder-card {
  background: white;
  border-radius: 20px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
}

.placeholder-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.placeholder-card h2 {
  color: #333;
  font-size: 24px;
  margin-bottom: 15px;
}

.placeholder-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}
</style>

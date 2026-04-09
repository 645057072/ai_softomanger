<!--
  文件名：Paper.vue
  描述：试卷中心页面组件
  作者：Li zekun
  创建日期：2026-04-08
  最后修改：2026-04-08
-->

<template>
  <div class="paper-container">
    <div class="page-header">
      <h1>试卷中心</h1>
      <p>试卷管理与组卷</p>
    </div>
    
    <div class="paper-content">
      <div class="placeholder-card">
        <div class="placeholder-icon">卷</div>
        <h2>试卷中心</h2>
        <p>试卷列表、智能组卷、试卷管理等功能开发中...</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Paper',
  mounted() {
    console.log('Paper component mounted')
  }
}
</script>

<style scoped>
.paper-container {
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

.paper-content {
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

<!--
  文件名：Home.vue
  描述：系统首页组件
  作者：Li zekun
  创建日期：2026-04-08
  最后修改：2026-04-08
-->

<template>
  <div class="home-container">
    <div class="welcome-card">
      <h1>欢迎使用考试系统</h1>
      <p class="subtitle">Online Examination System</p>
      
      <div class="quick-actions">
        <div class="action-item" @click="$router.push('/bi')">
          <div class="action-icon">📊</div>
          <div class="action-text">驾驶 BI</div>
        </div>
        
        <div class="action-item" @click="$router.push('/study')">
          <div class="action-icon">📚</div>
          <div class="action-text">学习中心</div>
        </div>
        
        <div class="action-item" @click="$router.push('/paper')">
          <div class="action-icon">📝</div>
          <div class="action-text">试卷中心</div>
        </div>
        
        <div class="action-item" @click="$router.push('/exam')">
          <div class="action-icon">✏️</div>
          <div class="action-text">考试中心</div>
        </div>
        
        <div class="action-item" @click="$router.push('/system')">
          <div class="action-icon">⚙️</div>
          <div class="action-text">系统设置</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  mounted() {
    console.log('Home component mounted')
  }
}
</script>

<style scoped>
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 100px);
  padding: 20px;
}

.welcome-card {
  background: white;
  border-radius: 20px;
  padding: 60px 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 800px;
  width: 100%;
}

.welcome-card h1 {
  color: #333;
  font-size: 36px;
  margin-bottom: 10px;
}

.subtitle {
  color: #666;
  font-size: 18px;
  margin-bottom: 50px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
  background: #f8f9fa;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.action-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.action-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.action-text {
  color: #555;
  font-size: 16px;
  font-weight: 500;
}
</style>

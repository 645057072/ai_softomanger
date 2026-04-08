<!--
  文件名：System.vue
  描述：系统设置页面组件
  作者：Li zekun
  创建日期：2026-04-08
  最后修改：2026-04-08
-->

<template>
  <div class="system-container">
    <div class="page-header">
      <h1>⚙️ 系统设置</h1>
      <p>系统配置与管理</p>
    </div>
    
    <div class="system-content">
      <div class="placeholder-card">
        <div class="placeholder-icon">⚙️</div>
        <h2>系统设置</h2>
        <p>用户管理、权限配置、系统参数等功能开发中...</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'System',
  mounted() {
    console.log('System component mounted')
  }
}
</script>

<style scoped>
.system-container {
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

.system-content {
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

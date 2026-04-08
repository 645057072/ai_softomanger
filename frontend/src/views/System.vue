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
      <div class="menu-grid">
        <div class="menu-item" @click="$router.push('/admin/organization')">
          <div class="menu-icon">🏢</div>
          <div class="menu-title">组织机构管理</div>
          <div class="menu-desc">管理系统全局组织机构信息</div>
        </div>
        
        <div class="menu-item">
          <div class="menu-icon">👥</div>
          <div class="menu-title">用户管理</div>
          <div class="menu-desc">用户注册审批、用户信息管理</div>
          <div class="submenu-list">
            <div class="submenu-item" @click.stop="$router.push('/admin/user-approval')">
              用户注册审批
            </div>
            <div class="submenu-item" @click.stop="$router.push('/admin/user-management')">
              用户管理
            </div>
          </div>
        </div>
        
        <div class="menu-item" @click="$router.push('/admin/role')">
          <div class="menu-icon">🎭</div>
          <div class="menu-title">角色管理</div>
          <div class="menu-desc">系统角色配置与权限管理</div>
        </div>
        
        <div class="menu-item" @click="$router.push('/admin/authorization')">
          <div class="menu-icon">🔐</div>
          <div class="menu-title">功能授权</div>
          <div class="menu-desc">系统功能权限分配</div>
        </div>
        
        <div class="menu-item" @click="$router.push('/admin/data')">
          <div class="menu-icon">📊</div>
          <div class="menu-title">数据管理</div>
          <div class="menu-desc">系统数据备份与恢复</div>
        </div>
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
  align-items: flex-start;
  padding: 20px;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 1200px;
}

.menu-item {
  background: white;
  border-radius: 15px;
  padding: 30px 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.menu-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15);
  border-color: #667eea;
}

.menu-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.menu-title {
  color: #333;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
}

.menu-desc {
  color: #666;
  font-size: 13px;
  line-height: 1.6;
}

.submenu-list {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.submenu-item {
  color: #667eea;
  font-size: 14px;
  padding: 8px 0;
  cursor: pointer;
  transition: all 0.2s;
}

.submenu-item:hover {
  color: #4a5fd6;
  padding-left: 5px;
}
</style>

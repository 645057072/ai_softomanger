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
      <div class="menu-container">
        <!-- 一级菜单：组织机构管理 -->
        <div class="menu-level-1">
          <div class="menu-title-item" @click="toggleMenu('org')">
            <span class="menu-icon">🏢</span>
            <span class="menu-text">组织机构管理</span>
            <span class="arrow" :class="{ 'arrow-down': expandedMenus.includes('org') }">▼</span>
          </div>
          <div v-show="expandedMenus.includes('org')" class="menu-level-2">
            <div class="menu-item" @click="$router.push('/admin/organization')">
              <span class="menu-dot">•</span>
              <span>组织机构信息</span>
            </div>
          </div>
        </div>

        <!-- 一级菜单：用户管理 -->
        <div class="menu-level-1">
          <div class="menu-title-item" @click="toggleMenu('user')">
            <span class="menu-icon">👥</span>
            <span class="menu-text">用户管理</span>
            <span class="arrow" :class="{ 'arrow-down': expandedMenus.includes('user') }">▼</span>
          </div>
          <div v-show="expandedMenus.includes('user')" class="menu-level-2">
            <div class="menu-level-3">
              <div class="menu-subtitle" @click="toggleSubMenu('userApproval')">
                <span class="menu-dot">•</span>
                <span>用户注册审批</span>
              </div>
              <div v-show="expandedMenus.includes('userApproval')" class="menu-level-3-content">
                <div class="menu-item" @click="$router.push('/admin/user-approval')">
                  <span class="menu-dot">•</span>
                  <span>审批列表</span>
                </div>
              </div>
            </div>
            <div class="menu-level-3">
              <div class="menu-subtitle" @click="toggleSubMenu('userManagement')">
                <span class="menu-dot">•</span>
                <span>用户管理</span>
              </div>
              <div v-show="expandedMenus.includes('userManagement')" class="menu-level-3-content">
                <div class="menu-item" @click="$router.push('/admin/user-management')">
                  <span class="menu-dot">•</span>
                  <span>用户列表</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 一级菜单：角色管理 -->
        <div class="menu-level-1">
          <div class="menu-title-item" @click="toggleMenu('role')">
            <span class="menu-icon">🎭</span>
            <span class="menu-text">角色管理</span>
            <span class="arrow" :class="{ 'arrow-down': expandedMenus.includes('role') }">▼</span>
          </div>
          <div v-show="expandedMenus.includes('role')" class="menu-level-2">
            <div class="menu-item" @click="$router.push('/admin/role')">
              <span class="menu-dot">•</span>
              <span>角色配置</span>
            </div>
          </div>
        </div>

        <!-- 一级菜单：功能授权 -->
        <div class="menu-level-1">
          <div class="menu-title-item" @click="toggleMenu('auth')">
            <span class="menu-icon">🔐</span>
            <span class="menu-text">功能授权</span>
            <span class="arrow" :class="{ 'arrow-down': expandedMenus.includes('auth') }">▼</span>
          </div>
          <div v-show="expandedMenus.includes('auth')" class="menu-level-2">
            <div class="menu-item" @click="$router.push('/admin/authorization')">
              <span class="menu-dot">•</span>
              <span>权限分配</span>
            </div>
          </div>
        </div>

        <!-- 一级菜单：数据管理 -->
        <div class="menu-level-1">
          <div class="menu-title-item" @click="toggleMenu('data')">
            <span class="menu-icon">📊</span>
            <span class="menu-text">数据管理</span>
            <span class="arrow" :class="{ 'arrow-down': expandedMenus.includes('data') }">▼</span>
          </div>
          <div v-show="expandedMenus.includes('data')" class="menu-level-2">
            <div class="menu-item" @click="$router.push('/admin/data')">
              <span class="menu-dot">•</span>
              <span>数据备份与恢复</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'

export default {
  name: 'System',
  setup() {
    const expandedMenus = ref(['org', 'user'])
    
    const toggleMenu = (menuName) => {
      const index = expandedMenus.value.indexOf(menuName)
      if (index > -1) {
        expandedMenus.value.splice(index, 1)
      } else {
        expandedMenus.value.push(menuName)
      }
    }
    
    const toggleSubMenu = (menuName) => {
      const index = expandedMenus.value.indexOf(menuName)
      if (index > -1) {
        expandedMenus.value.splice(index, 1)
      } else {
        expandedMenus.value.push(menuName)
      }
    }

    return {
      expandedMenus,
      toggleMenu,
      toggleSubMenu
    }
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

.menu-container {
  width: 100%;
  max-width: 800px;
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.menu-level-1 {
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.menu-level-1:last-child {
  border-bottom: none;
}

.menu-title-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
  color: #333;
}

.menu-title-item:hover {
  background: #e9ecef;
}

.menu-icon {
  font-size: 24px;
  margin-right: 12px;
}

.menu-text {
  flex: 1;
  font-size: 16px;
}

.arrow {
  font-size: 12px;
  transition: transform 0.3s;
  color: #999;
}

.arrow-down {
  transform: rotate(90deg);
}

.menu-level-2 {
  margin-top: 10px;
  margin-left: 20px;
  padding-left: 15px;
  border-left: 2px solid #667eea;
}

.menu-level-3 {
  margin-bottom: 10px;
}

.menu-level-3:last-child {
  margin-bottom: 0;
}

.menu-subtitle {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  color: #555;
  font-size: 15px;
  transition: all 0.2s;
}

.menu-subtitle:hover {
  color: #667eea;
  background: #f8f9fa;
  border-radius: 4px;
}

.menu-level-3-content {
  margin-left: 20px;
  margin-top: 5px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  color: #666;
  font-size: 14px;
  transition: all 0.2s;
}

.menu-item:hover {
  color: #667eea;
  background: #f8f9fa;
  border-radius: 4px;
  padding-left: 15px;
}

.menu-dot {
  margin-right: 8px;
  color: #667eea;
  font-size: 16px;
}
</style>

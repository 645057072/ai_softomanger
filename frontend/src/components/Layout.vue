<!--
  文件名：Layout.vue
  描述：系统主布局组件（上中下三部分布局）
  作者：Li zekun
  创建日期：2026-04-08
  最后修改：2026-04-08
-->

<template>
  <div class="layout-container">
    <!-- 上部布局：占据屏幕 1/30 高度 -->
    <header class="top-header">
      <div class="header-content">
        <div class="logo">考试系统</div>
        <div class="header-info">
          <!-- 消息预警图标（仅管理员：待审核注册数） -->
          <div v-if="isAdmin" class="message-notification" @click="goToMessageCenter">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
              <div class="message-icon">
                <img :src="messageIcon" alt="消息" />
              </div>
            </el-badge>
          </div>
          <span class="welcome">欢迎，{{ currentUser }}</span>
          <span class="current-date">{{ currentDate }}</span>
          <button class="btn-logout" @click="handleLogout">退出</button>
        </div>
      </div>
    </header>

    <!-- 中间布局：左右分割 -->
    <div class="main-container">
      <!-- 左侧导航菜单：1/10 宽度 -->
      <aside class="sidebar">
        <nav class="nav-menu">
          <div 
            class="nav-item" 
            :class="{ active: currentMenu === 'bi' }"
            @click="navigateTo('bi')"
          >
            <span class="nav-icon"><img :src="biIcon" alt="BI" /></span>
            <span class="nav-text">驾驶 BI</span>
          </div>

          <div 
            class="nav-item" 
            :class="{ active: currentMenu === 'study' }"
            @click="navigateTo('study')"
          >
            <span class="nav-icon"><img :src="studyIcon" alt="学习" /></span>
            <span class="nav-text">学习中心</span>
          </div>

          <div 
            class="nav-item" 
            :class="{ active: currentMenu === 'paper' }"
            @click="navigateTo('paper')"
          >
            <span class="nav-icon"><img :src="paperIcon" alt="试卷" /></span>
            <span class="nav-text">试卷中心</span>
          </div>

          <div 
            class="nav-item" 
            :class="{ active: currentMenu === 'exam' }"
            @click="navigateTo('exam')"
          >
            <span class="nav-icon"><img :src="examIcon" alt="考试" /></span>
            <span class="nav-text">考试中心</span>
          </div>

          <!-- 系统设置菜单（带子菜单），仅管理员可见 -->
          <div v-if="isAdmin" class="nav-item-wrapper">
            <div 
              class="nav-item system-menu-title"
              :class="{ active: currentMenu === 'system' }"
              @click="toggleSystemMenu"
            >
              <span class="nav-icon"><img :src="settingsIcon" alt="设置" /></span>
              <span class="nav-text">系统设置</span>
              <span class="nav-arrow" :class="{ 'arrow-down': systemMenuExpanded }">▶</span>
            </div>
            
            <!-- 系统设置二级菜单 -->
            <div v-show="systemMenuExpanded" class="system-submenu">
              <div 
                class="submenu-item"
                :class="{ active: currentSubmenu === 'organization' }"
                @click="navigateToSubmenu('organization', '/admin/organization')"
              >
                <span class="submenu-icon"><img :src="orgIcon" alt="组织机构" /></span>
                <span class="submenu-text">组织机构管理</span>
              </div>
              
              <div 
                class="submenu-item"
                :class="{ active: currentSubmenu === 'user' }"
                @click="toggleUserSubmenu"
              >
                <span class="submenu-icon"><img :src="userIcon" alt="用户" /></span>
                <span class="submenu-text">用户管理</span>
                <span class="submenu-arrow" :class="{ 'arrow-down': userSubmenuExpanded }">▶</span>
              </div>
              
              <!-- 用户管理三级菜单 -->
              <div v-show="userSubmenuExpanded" class="third-level-menu">
                <div 
                  class="third-level-item"
                  :class="{ active: currentSubmenu === 'user-approval' }"
                  @click="navigateToSubmenu('user-approval', '/admin/user-approval')"
                >
                  <span class="third-icon">•</span>
                  <span>用户注册审批</span>
                </div>
                <div 
                  class="third-level-item"
                  :class="{ active: currentSubmenu === 'user-management' }"
                  @click="navigateToSubmenu('user-management', '/admin/user-management')"
                >
                  <span class="third-icon">•</span>
                  <span>用户管理</span>
                </div>
              </div>
              
              <div 
                class="submenu-item"
                :class="{ active: currentSubmenu === 'role' }"
                @click="navigateToSubmenu('role', '/admin/role')"
              >
                <span class="submenu-icon"><img :src="roleIcon" alt="角色" /></span>
                <span class="submenu-text">角色管理</span>
              </div>
              
              <div 
                class="submenu-item"
                :class="{ active: currentSubmenu === 'authorization' }"
                @click="navigateToSubmenu('authorization', '/admin/authorization')"
              >
                <span class="submenu-icon"><img :src="authIcon" alt="授权" /></span>
                <span class="submenu-text">功能授权</span>
              </div>
              
              <div class="submenu-item-wrapper">
                <div
                  class="submenu-item"
                  :class="{ active: currentSubmenu === 'data' }"
                  @click="toggleDataSubmenu"
                >
                  <span class="submenu-icon"><img :src="dataIcon" alt="数据" /></span>
                  <span class="submenu-text">数据管理</span>
                  <span class="submenu-arrow" :class="{ 'arrow-down': dataSubmenuExpanded }">▶</span>
                </div>
                <div v-show="dataSubmenuExpanded" class="third-level-menu">
                  <div
                    class="third-level-item"
                    :class="{ active: currentDataSubmenu === 'online' }"
                    @click="navigateToDataChild('online', '/admin/data/online-users')"
                  >
                    <span class="third-icon">•</span>
                    <span>在线用户</span>
                  </div>
                  <div
                    class="third-level-item"
                    :class="{ active: currentDataSubmenu === 'logs' }"
                    @click="navigateToDataChild('logs', '/admin/data/logs')"
                  >
                    <span class="third-icon">•</span>
                    <span>日志</span>
                  </div>
                  <div
                    class="third-level-item"
                    :class="{ active: currentDataSubmenu === 'backup' }"
                    @click="navigateToDataChild('backup', '/admin/data/backup')"
                  >
                    <span class="third-icon">•</span>
                    <span>数据备份</span>
                  </div>
                  <div
                    class="third-level-item"
                    :class="{ active: currentDataSubmenu === 'restore' }"
                    @click="navigateToDataChild('restore', '/admin/data/restore')"
                  >
                    <span class="third-icon">•</span>
                    <span>数据恢复</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </nav>
      </aside>

      <!-- 右侧内容区：菜单窗口浏览区 -->
      <main class="content-area">
        <router-view />
      </main>
    </div>

    <!-- 下部布局：占据屏幕 1/50 高度 -->
    <footer class="bottom-footer">
      <div class="footer-content">
        <span>考试系统 © 2026 | Powered by Flask + Vue.js</span>
        <span>技术支持</span>
      </div>
    </footer>
  </div>
</template>

<script>
import { useUserStore } from '../store'
import { userManagementApi, authApi } from '../api'
import biIcon from '../assets/icons/bi.svg'
import studyIcon from '../assets/icons/study.svg'
import paperIcon from '../assets/icons/paper.svg'
import examIcon from '../assets/icons/exam.svg'
import settingsIcon from '../assets/icons/settings.svg'
import orgIcon from '../assets/icons/org.svg'
import userIcon from '../assets/icons/user.svg'
import roleIcon from '../assets/icons/role.svg'
import authIcon from '../assets/icons/auth.svg'
import dataIcon from '../assets/icons/data.svg'
import messageIcon from '../assets/icons/msg-unread.svg'

export default {
  name: 'Layout',
  data() {
    return {
      currentMenu: 'bi',
      currentDate: '',
      unreadCount: 0,
      systemMenuExpanded: false,
      userSubmenuExpanded: false,
      dataSubmenuExpanded: false,
      currentDataSubmenu: '',
      currentSubmenu: ''
    }
  },
  created() {
    this.biIcon = biIcon
    this.studyIcon = studyIcon
    this.paperIcon = paperIcon
    this.examIcon = examIcon
    this.settingsIcon = settingsIcon
    this.orgIcon = orgIcon
    this.userIcon = userIcon
    this.roleIcon = roleIcon
    this.authIcon = authIcon
    this.dataIcon = dataIcon
    this.messageIcon = messageIcon
  },
  computed: {
    currentUser() {
      const userStore = useUserStore()
      return userStore.userInfo?.username || '用户'
    },
    isAdmin() {
      return useUserStore().isAdmin
    }
  },
  mounted() {
    this.updateDate()
    setInterval(this.updateDate, 60000) // 每分钟更新一次
    this.fetchUnreadCount()
    setInterval(this.fetchUnreadCount, 30000) // 每 30 秒更新一次未读数
    
    // 根据路由设置当前菜单
    this.setMenuFromRoute()
  },
  watch: {
    '$route'() {
      this.setMenuFromRoute()
    }
  },
  methods: {
    updateDate() {
      const now = new Date()
      this.currentDate = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    setMenuFromRoute() {
      const path = this.$route.path
      if (path.includes('/bi')) this.currentMenu = 'bi'
      else if (path.includes('/study')) this.currentMenu = 'study'
      else if (path.includes('/paper')) this.currentMenu = 'paper'
      else if (path.includes('/exam')) this.currentMenu = 'exam'
      else if (path.includes('/system') || path.includes('/admin/')) {
        this.currentMenu = 'system'
        // 根据路由展开对应的子菜单
        if (path.includes('/admin/')) {
          this.systemMenuExpanded = true
          this.setSubmenuFromRoute(path)
        }
      }
    },

    setSubmenuFromRoute(path) {
      if (path.includes('/organization')) {
        this.currentSubmenu = 'organization'
        this.userSubmenuExpanded = false
        this.dataSubmenuExpanded = false
      } else if (path.includes('/user-approval')) {
        this.currentSubmenu = 'user-approval'
        this.userSubmenuExpanded = true
        this.dataSubmenuExpanded = false
      } else if (path.includes('/user-management')) {
        this.currentSubmenu = 'user-management'
        this.userSubmenuExpanded = true
        this.dataSubmenuExpanded = false
      } else if (path.includes('/role')) {
        this.currentSubmenu = 'role'
        this.userSubmenuExpanded = false
        this.dataSubmenuExpanded = false
      } else if (path.includes('/authorization')) {
        this.currentSubmenu = 'authorization'
        this.userSubmenuExpanded = false
        this.dataSubmenuExpanded = false
      } else if (path.includes('/admin/data')) {
        this.currentSubmenu = 'data'
        this.userSubmenuExpanded = false
        this.dataSubmenuExpanded = true
        if (path.includes('/admin/data/online-users')) this.currentDataSubmenu = 'online'
        else if (path.includes('/admin/data/logs')) this.currentDataSubmenu = 'logs'
        else if (path.includes('/admin/data/backup')) this.currentDataSubmenu = 'backup'
        else if (path.includes('/admin/data/restore')) this.currentDataSubmenu = 'restore'
        else this.currentDataSubmenu = 'online'
      }
    },

    navigateTo(menu) {
      this.currentMenu = menu
      const routes = {
        'bi': '/bi',
        'study': '/study',
        'paper': '/paper',
        'exam': '/exam',
        'system': '/system'
      }
      this.$router.push(routes[menu])
    },

    toggleSystemMenu() {
      this.systemMenuExpanded = !this.systemMenuExpanded
      if (this.systemMenuExpanded) {
        this.currentMenu = 'system'
      }
    },

    toggleUserSubmenu() {
      this.userSubmenuExpanded = !this.userSubmenuExpanded
    },

    toggleDataSubmenu() {
      this.dataSubmenuExpanded = !this.dataSubmenuExpanded
      if (this.dataSubmenuExpanded) {
        this.currentSubmenu = 'data'
        this.$router.push('/admin/data/online-users')
      }
    },

    navigateToDataChild(key, path) {
      this.currentSubmenu = 'data'
      this.currentDataSubmenu = key
      this.$router.push(path)
    },

    navigateToSubmenu(submenu, path) {
      this.currentSubmenu = submenu
      this.$router.push(path)
    },

    handleLogout() {
      this.$confirm('确定要退出系统吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await authApi.logout()
        } catch (e) {
          console.error('登出接口调用失败', e)
        }
        const userStore = useUserStore()
        userStore.logout()
        this.$message.success('已退出系统')
        this.$router.push('/login')
      }).catch(() => {})
    },

    // 获取未读消息数量（仅管理员：待审核注册数）
    async fetchUnreadCount() {
      const store = useUserStore()
      if (!store.isAdmin) {
        this.unreadCount = 0
        return
      }
      try {
        const result = await userManagementApi.getPending({ page: 1, per_page: 1, inbox: 'unread' })
        if (result.code === 200) {
          this.unreadCount = result.data.total || 0
        }
      } catch (error) {
        console.error('获取未读消息数失败', error)
      }
    },

    // 跳转到消息中心
    goToMessageCenter() {
      this.$router.push('/admin/user-approval')
    }
  }
}
</script>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

/* 上部布局：1/30 高度 */
.top-header {
  height: calc(100vh / 30);
  min-height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  color: white;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  font-size: 14px;
}

/* 消息预警图标 */
.message-notification {
  cursor: pointer;
  margin-right: 10px;
}

.notification-badge {
  display: inline-block;
}

.message-icon {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.message-icon img {
  width: 18px;
  height: 18px;
  display: block;
}

.message-icon:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.welcome {
  font-weight: 500;
}

.current-date {
  opacity: 0.9;
}

.btn-logout {
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 中间布局：左右分割 */
.main-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧导航菜单：1/10 宽度 */
.sidebar {
  width: calc(100% / 10);
  min-width: 180px;
  max-width: 220px;
  background: white;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
}

.nav-menu {
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 3px solid transparent;
  margin-bottom: 5px;
}

.nav-item:hover {
  background: #f5f7fa;
}

.nav-item.active {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, transparent 100%);
  border-left-color: #667eea;
  color: #667eea;
}

.nav-icon {
  margin-right: 12px;
  width: 24px;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.nav-icon img {
  width: 18px;
  height: 18px;
  display: block;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

.nav-arrow {
  margin-left: auto;
  font-size: 12px;
  transition: transform 0.3s;
}

.nav-arrow.arrow-down {
  transform: rotate(90deg);
}

.nav-item-wrapper {
  margin-bottom: 5px;
}

.system-menu-title {
  position: relative;
}

/* 系统设置二级菜单 */
.system-submenu {
  background: #fafafa;
  padding: 5px 0;
}

.submenu-item {
  display: flex;
  align-items: center;
  padding: 10px 20px 10px 45px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  position: relative;
}

.submenu-item:hover {
  background: #ecf5ff;
  border-left-color: #409eff;
  color: #409eff;
}

.submenu-item.active {
  background: #ecf5ff;
  border-left-color: #409eff;
  color: #409eff;
  font-weight: 500;
}

.submenu-icon {
  margin-right: 10px;
  width: 20px;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.submenu-icon img {
  width: 16px;
  height: 16px;
  display: block;
}

.submenu-text {
  flex: 1;
  font-size: 13px;
}

.submenu-arrow {
  font-size: 12px;
  transition: transform 0.3s;
}

.submenu-arrow.arrow-down {
  transform: rotate(90deg);
}

/* 用户管理三级菜单 */
.third-level-menu {
  background: #f5f7fa;
  padding: 5px 0;
}

.third-level-item {
  display: flex;
  align-items: center;
  padding: 8px 20px 8px 55px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  font-size: 13px;
}

.third-level-item:hover {
  background: #e6f7ff;
  border-left-color: #409eff;
  color: #409eff;
}

.third-level-item.active {
  background: #e6f7ff;
  border-left-color: #409eff;
  color: #409eff;
  font-weight: 500;
}

.third-icon {
  margin-right: 8px;
  color: #409eff;
  font-size: 16px;
}

/* 右侧内容区 */
.content-area {
  flex: 1;
  background: #f5f7fa;
  overflow-y: auto;
  padding: 3px;
}

/* 下部布局：1/50 高度 */
.bottom-footer {
  height: calc(100vh / 50);
  min-height: 35px;
  background: white;
  border-top: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.footer-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #999;
  font-size: 12px;
}
</style>

<template>
  <div class="layout-container">
    <!-- 上部布局：占据屏幕 1/30 高度 -->
    <header class="top-header">
      <div class="header-content">
        <div class="logo">📚 考试系统</div>
        <div class="header-info">
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
            <span class="nav-icon">📊</span>
            <span class="nav-text">驾驶 BI</span>
          </div>

          <div 
            class="nav-item" 
            :class="{ active: currentMenu === 'study' }"
            @click="navigateTo('study')"
          >
            <span class="nav-icon">📚</span>
            <span class="nav-text">学习中心</span>
          </div>

          <div 
            class="nav-item" 
            :class="{ active: currentMenu === 'paper' }"
            @click="navigateTo('paper')"
          >
            <span class="nav-icon">📝</span>
            <span class="nav-text">试卷中心</span>
          </div>

          <div 
            class="nav-item" 
            :class="{ active: currentMenu === 'exam' }"
            @click="navigateTo('exam')"
          >
            <span class="nav-icon">✏️</span>
            <span class="nav-text">考试中心</span>
          </div>

          <div 
            class="nav-item" 
            :class="{ active: currentMenu === 'system' }"
            @click="navigateTo('system')"
          >
            <span class="nav-icon">⚙️</span>
            <span class="nav-text">系统设置</span>
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
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Layout',
  data() {
    return {
      currentMenu: 'bi',
      currentDate: ''
    }
  },
  computed: {
    ...mapState(['user']),
    currentUser() {
      return this.user?.username || '用户'
    }
  },
  mounted() {
    this.updateDate()
    setInterval(this.updateDate, 60000) // 每分钟更新一次
    
    // 根据路由设置当前菜单
    this.setMenuFromRoute()
  },
  watch: {
    '$route'() {
      this.setMenuFromRoute()
    }
  },
  methods: {
    ...mapActions(['logout']),
    
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
      else if (path.includes('/system')) this.currentMenu = 'system'
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

    handleLogout() {
      this.$confirm('确定要退出系统吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.logout()
        this.$message.success('已退出系统')
        this.$router.push('/login')
      }).catch(() => {})
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
  font-size: 20px;
  margin-right: 12px;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

/* 右侧内容区 */
.content-area {
  flex: 1;
  background: #f5f7fa;
  overflow-y: auto;
  padding: 20px;
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

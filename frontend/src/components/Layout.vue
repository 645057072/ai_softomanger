<template>
  <el-container>
    <el-header height="60px" class="header">
      <div class="header-content">
        <div class="logo">考试系统</div>
        <div class="right">
          <el-dropdown>
            <span class="user-info">
              {{ userInfo?.real_name || userInfo?.username }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleProfile">个人中心</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="aside">
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical-demo"
          router
        >
          <el-menu-item index="/">
            <el-icon><home /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/questions">
            <el-icon><document /></el-icon>
            <span>题库管理</span>
          </el-menu-item>
          <el-menu-item index="/papers">
            <el-icon><folder /></el-icon>
            <span>试卷管理</span>
          </el-menu-item>
          <el-menu-item index="/exams">
            <el-icon><timer /></el-icon>
            <span>在线考试</span>
          </el-menu-item>
          <el-menu-item index="/scores">
            <el-icon><trend-charts /></el-icon>
            <span>成绩管理</span>
          </el-menu-item>
          <el-menu-item index="/system" v-if="isAdmin">
            <el-icon><setting /></el-icon>
            <span>系统管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <slot />
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../store'

export default {
  name: 'Layout',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const userStore = useUserStore()
    const activeMenu = ref('/')
    
    const userInfo = computed(() => userStore.userInfo)
    const isAdmin = computed(() => userStore.isAdmin)
    
    onMounted(() => {
      activeMenu.value = route.path
    })
    
    const handleProfile = () => {
      // 个人中心
    }
    
    const handleLogout = () => {
      userStore.logout()
      router.push('/login')
    }
    
    return {
      userInfo,
      isAdmin,
      activeMenu,
      handleProfile,
      handleLogout
    }
  }
}
</script>

<style scoped>
.header {
  background-color: #409EFF;
  color: white;
  line-height: 60px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.aside {
  background-color: #f0f2f5;
  min-height: calc(100vh - 60px);
}

.el-menu-vertical-demo {
  height: 100%;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>

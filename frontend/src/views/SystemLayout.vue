<template>
  <div class="system-layout">
    <!-- 中部左侧系统模块导航 -->
    <div class="system-sidebar">
      <div class="sidebar-header">
        <h3>⚙️ 系统设置</h3>
      </div>
      <div class="sidebar-menu">
        <div class="menu-module" v-for="module in menuModules" :key="module.key">
          <div class="module-title" @click="toggleModule(module.key)">
            <span class="module-icon">{{ module.icon }}</span>
            <span class="module-name">{{ module.name }}</span>
            <span class="module-arrow" :class="{ 'arrow-down': expandedModule === module.key }">▶</span>
          </div>
          <div v-show="expandedModule === module.key" class="module-submenu">
            <div 
              class="submenu-item" 
              v-for="item in module.children" 
              :key="item.path"
              @click="navigateTo(item.path)"
              :class="{ 'active': currentPath === item.path }"
            >
              <span class="submenu-dot">•</span>
              <span>{{ item.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧内容区域 -->
    <div class="system-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'SystemLayout',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const expandedModule = ref(null)
    
    const menuModules = ref([
      {
        key: 'organization',
        name: '组织机构管理',
        icon: '🏢',
        children: [
          { name: '组织机构信息', path: '/admin/organization' }
        ]
      },
      {
        key: 'user',
        name: '用户管理',
        icon: '👥',
        children: [
          { name: '用户注册审批', path: '/admin/user-approval' },
          { name: '用户管理', path: '/admin/user-management' }
        ]
      },
      {
        key: 'role',
        name: '角色管理',
        icon: '🎭',
        children: [
          { name: '角色配置', path: '/admin/role' }
        ]
      },
      {
        key: 'authorization',
        name: '功能授权',
        icon: '🔐',
        children: [
          { name: '权限分配', path: '/admin/authorization' }
        ]
      },
      {
        key: 'data',
        name: '数据管理',
        icon: '📊',
        children: [
          { name: '数据备份与恢复', path: '/admin/data' }
        ]
      }
    ])
    
    const currentPath = computed(() => route.path)
    
    const toggleModule = (moduleKey) => {
      if (expandedModule.value === moduleKey) {
        expandedModule.value = null
      } else {
        expandedModule.value = moduleKey
      }
    }
    
    const navigateTo = (path) => {
      router.push(path)
    }
    
    onMounted(() => {
      // 默认展开第一个模块
      if (menuModules.value.length > 0) {
        expandedModule.value = menuModules.value[0].key
      }
    })
    
    return {
      menuModules,
      expandedModule,
      currentPath,
      toggleModule,
      navigateTo
    }
  }
}
</script>

<style scoped>
.system-layout {
  display: flex;
  height: 100%;
  background: #f5f7fa;
  position: relative;
}

.system-sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 10;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.sidebar-header h3 {
  color: white;
  font-size: 18px;
  margin: 0;
  font-weight: 600;
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.menu-module {
  margin-bottom: 5px;
}

.module-title {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.module-title:hover {
  background: #f5f7fa;
}

.module-title:hover .module-arrow {
  transform: translateX(3px);
}

.module-icon {
  font-size: 20px;
  margin-right: 12px;
}

.module-name {
  flex: 1;
  font-size: 15px;
  color: #333;
  font-weight: 500;
}

.module-arrow {
  font-size: 12px;
  color: #999;
  transition: all 0.3s;
}

.arrow-down {
  transform: rotate(90deg);
}

.module-submenu {
  background: #fafafa;
  padding: 5px 0;
}

.submenu-item {
  display: flex;
  align-items: center;
  padding: 10px 20px 10px 35px;
  cursor: pointer;
  transition: all 0.2s;
  color: #606266;
  font-size: 14px;
  border-left: 3px solid transparent;
}

.submenu-item:hover {
  background: #ecf5ff;
  color: #409eff;
  border-left-color: #409eff;
}

.submenu-item.active {
  background: #ecf5ff;
  color: #409eff;
  border-left-color: #409eff;
  font-weight: 500;
}

.submenu-dot {
  margin-right: 8px;
  color: #409eff;
  font-size: 16px;
}

.system-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
  margin-left: 280px;
}
</style>

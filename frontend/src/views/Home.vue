<template>
  <div class="home-container">
    <!-- 右上角消息预警图标 -->
    <div class="message-notification" @click="goToMessageCenter">
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
        <div class="message-icon">
          <span>🔔</span>
        </div>
      </el-badge>
    </div>
    
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
    
    <!-- 组织机构信息显示 -->
    <div class="organization-info-card" v-if="organizationInfo">
      <div class="org-header">
        <span class="org-icon">🏢</span>
        <h2>{{ organizationInfo.name }}</h2>
      </div>
      <div class="org-content">
        <div class="org-row">
          <span class="org-label">纳税人识别号：</span>
          <span class="org-value">{{ organizationInfo.tax_id || '未设置' }}</span>
        </div>
        <div class="org-row">
          <span class="org-label">注册地址：</span>
          <span class="org-value">{{ organizationInfo.address || '未设置' }}</span>
        </div>
        <div class="org-row">
          <span class="org-label">联系电话：</span>
          <span class="org-value">{{ organizationInfo.phone || '未设置' }}</span>
        </div>
        <div class="org-row">
          <span class="org-label">法定代表人：</span>
          <span class="org-value">{{ organizationInfo.legal_representative || '未设置' }}</span>
        </div>
        <div class="org-row">
          <span class="org-label">所属行业：</span>
          <span class="org-value">{{ organizationInfo.industry || '未设置' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    const organizationInfo = ref(null)
    const unreadCount = ref(0)
    
    const fetchUnreadCount = async () => {
      try {
        const response = await fetch('/api/user-management/pending?per_page=1', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        const result = await response.json()
        if (result.code === 200) {
          unreadCount.value = result.data.total || 0
        }
      } catch (error) {
        console.error('获取未读消息数失败', error)
      }
    }
    
    const goToMessageCenter = () => {
      router.push('/admin/user-approval')
    }
    
    const fetchOrganization = async () => {
      try {
        const response = await fetch('/api/organization?page=1&per_page=1', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        const result = await response.json()
        if (result.code === 200 && result.data.list && result.data.list.length > 0) {
          organizationInfo.value = result.data.list[0]
        }
      } catch (error) {
        console.error('获取组织机构信息失败', error)
      }
    }
    
    onMounted(() => {
      console.log('Home component mounted')
      fetchOrganization()
      fetchUnreadCount()
    })
    
    return {
      organizationInfo,
      unreadCount,
      goToMessageCenter
    }
  }
}
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 100px);
  padding: 20px;
  gap: 30px;
  position: relative;
}

.message-notification {
  position: absolute;
  top: 20px;
  right: 20px;
  cursor: pointer;
  z-index: 100;
}

.notification-badge {
  display: inline-block;
}

.message-icon {
  width: 50px;
  height: 50px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  font-size: 24px;
}

.message-icon:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
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

.organization-info-card {
  background: white;
  border-radius: 20px;
  padding: 30px 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  width: 100%;
}

.org-header {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #667eea;
}

.org-icon {
  font-size: 36px;
  margin-right: 15px;
}

.org-header h2 {
  color: #333;
  font-size: 24px;
  margin: 0;
}

.org-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.org-row {
  display: flex;
  flex-direction: column;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.org-label {
  color: #999;
  font-size: 12px;
  margin-bottom: 5px;
}

.org-value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .org-content {
    grid-template-columns: 1fr;
  }
}
</style>

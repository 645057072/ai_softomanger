import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { normalizeAccessToken } from '../utils/accessToken'

/** 从 localStorage 安全读取用户信息，非法 JSON 时清理缓存，避免整站无法挂载 */
function readStoredUserInfo() {
  const raw = localStorage.getItem('userInfo')
  if (raw == null || raw === '') return null
  try {
    return JSON.parse(raw)
  } catch {
    localStorage.removeItem('userInfo')
    return null
  }
}

// 用户状态管理
export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(readStoredUserInfo())
  
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isTeacher = computed(() => ['admin', 'teacher'].includes(userInfo.value?.role))
  
  function login(newToken, user) {
    const t = normalizeAccessToken(newToken)
    token.value = t
    userInfo.value = user
    localStorage.setItem('token', t)
    localStorage.setItem('userInfo', JSON.stringify(user))
  }
  
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.removeItem('profile_synced_token')
    }
  }
  
  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    isTeacher,
    login,
    logout
  }
})

// 考试状态管理
export const useExamStore = defineStore('exam', () => {
  const currentExam = ref(null)
  const answers = ref({})
  const remainingTime = ref(0)
  const autoSaveTimer = ref(null)
  
  function startAutoSave() {
    if (autoSaveTimer.value) {
      clearInterval(autoSaveTimer.value)
    }
    autoSaveTimer.value = setInterval(() => {
      if (currentExam.value) {
        // 自动保存逻辑
      }
    }, 30000) // 30秒自动保存
  }
  
  function stopAutoSave() {
    if (autoSaveTimer.value) {
      clearInterval(autoSaveTimer.value)
      autoSaveTimer.value = null
    }
  }
  
  function reset() {
    currentExam.value = null
    answers.value = {}
    remainingTime.value = 0
    stopAutoSave()
  }
  
  return {
    currentExam,
    answers,
    remainingTime,
    startAutoSave,
    stopAutoSave,
    reset
  }
})

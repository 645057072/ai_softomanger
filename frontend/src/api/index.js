import axios from 'axios'
import { unref } from 'vue'
import { useUserStore } from '../store'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

/**
 * 从 Pinia 与 localStorage 统一取 Token，避免仅读 localStorage 与 store 不同步导致未带鉴权头。
 * 若曾误存带 Bearer 前缀的字符串，去掉重复前缀。
 */
function getAccessTokenForRequest() {
  let t = ''
  try {
    const s = useUserStore()
    t = unref(s.token) || ''
  } catch (_) {
    t = ''
  }
  if (!t) {
    t = localStorage.getItem('token') || ''
  }
  t = String(t).trim()
  if (/^bearer\s+/i.test(t)) {
    t = t.replace(/^bearer\s+/i, '').trim()
  }
  return t
}

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = getAccessTokenForRequest()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 401 时避免多个并发请求重复清会话、整页跳转导致「闪退」感
let authRedirectLock = false

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response && error.response.status === 401) {
      const url = error.config?.url || ''
      if (error.config?.skipAuthRedirect) {
        return Promise.reject(error)
      }
      if (url.includes('/auth/login') || url.includes('/auth/register')) {
        return Promise.reject(error)
      }
      if (!authRedirectLock) {
        authRedirectLock = true
        try {
          const userStore = useUserStore()
          userStore.logout()
        } catch (_) {
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
        }
        window.location.replace('/login')
      }
    }
    return Promise.reject(error)
  }
)

// 认证相关
export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  refresh: () => api.post('/auth/refresh'),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile', { skipAuthRedirect: true }),
  changePassword: (data) => api.post('/auth/change-password', data)
}

// 用户管理
export const userApi = {
  getList: (params) => api.get('/user/list', { params }),
  getDetail: (id) => api.get(`/user/${id}`),
  create: (data) => api.post('/user/create', data),
  update: (id, data) => api.put(`/user/${id}`, data),
  delete: (id) => api.delete(`/user/${id}`),
  batchImport: (data) => api.post('/user/batch-import', data)
}

// 题目管理
export const questionApi = {
  getList: (params) => api.get('/question/list', { params }),
  getDetail: (id) => api.get(`/question/${id}`),
  create: (data) => api.post('/question/create', data),
  update: (id, data) => api.put(`/question/${id}`, data),
  delete: (id) => api.delete(`/question/${id}`),
  import: (formData) => api.post('/question/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  export: (params) => api.get('/question/export', { params, responseType: 'blob' }),
  getTypes: () => api.get('/question/types'),
  getSubjects: () => api.get('/question/subjects'),
  getStatistics: () => api.get('/question/statistics')
}

// 试卷管理
export const paperApi = {
  getList: (params) => api.get('/paper/list', { params }),
  getDetail: (id) => api.get(`/paper/${id}`),
  create: (data) => api.post('/paper/create', data),
  update: (id, data) => api.put(`/paper/${id}`, data),
  delete: (id) => api.delete(`/paper/${id}`),
  publish: (id) => api.post(`/paper/${id}/publish`),
  generateRandom: (data) => api.post('/paper/generate-random', data),
  addQuestions: (id, data) => api.post(`/paper/${id}/questions`, data),
  getAvailable: () => api.get('/paper/available')
}

// 考试管理
export const examApi = {
  start: (paperId) => api.post(`/exam/start/${paperId}`),
  saveAnswer: (examId, data) => api.post(`/exam/${examId}/save`, data),
  submit: (examId) => api.post(`/exam/${examId}/submit`),
  getStatus: (examId) => api.get(`/exam/${examId}/status`),
  getHistory: (params) => api.get('/exam/history', { params }),
  review: (examId) => api.get(`/exam/${examId}/review`),
  logAction: (examId, data) => api.post(`/exam/${examId}/log`, data)
}

// 成绩管理
export const scoreApi = {
  getList: (params) => api.get('/score/list', { params }),
  getStatistics: (params) => api.get('/score/statistics', { params }),
  getRanking: (params) => api.get('/score/ranking', { params }),
  getMyScores: (params) => api.get('/score/my-scores', { params }),
  export: (params) => api.get('/score/export', { params, responseType: 'blob' }),
  getAnalysis: (params) => api.get('/score/analysis', { params })
}

// 文件上传
export const uploadApi = {
  uploadFile: (formData) => api.post('/upload/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  uploadImage: (formData) => api.post('/upload/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  uploadAvatar: (formData) => api.post('/upload/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 系统管理
export const systemApi = {
  getDashboard: () => api.get('/system/dashboard'),
  getLogs: (params) => api.get('/system/logs', { params }),
  getConfigs: () => api.get('/system/config'),
  updateConfig: (data) => api.post('/system/config', data),
  getExamTypes: () => api.get('/system/exam-types'),
  createExamType: (data) => api.post('/system/exam-types', data),
  updateExamType: (id, data) => api.put(`/system/exam-types/${id}`, data),
  deleteExamType: (id) => api.delete(`/system/exam-types/${id}`),
  getExamSubjects: () => api.get('/system/exam-subjects'),
  createExamSubject: (data) => api.post('/system/exam-subjects', data),
  updateExamSubject: (id, data) => api.put(`/system/exam-subjects/${id}`, data),
  deleteExamSubject: (id) => api.delete(`/system/exam-subjects/${id}`),
  healthCheck: () => api.get('/system/health')
}

// 组织机构管理
export const organizationApi = {
  getList: (params) => api.get('/organization', { params }),
  getDetail: (id) => api.get(`/organization/${id}`),
  create: (data) => api.post('/organization', data),
  update: (id, data) => api.put(`/organization/${id}`, data),
  remove: (id) => api.delete(`/organization/${id}`)
}

// 用户管理（审批/列表）
export const userManagementApi = {
  getPending: (params) => api.get('/user-management/pending', { params }),
  getApproved: (params) => api.get('/user-management/approved', { params }),
  getAll: (params) => api.get('/user-management/all', { params }),
  markRead: (id) => api.post(`/user-management/${id}/mark-read`),
  approve: (id) => api.post(`/user-management/${id}/approve`),
  reject: (id) => api.post(`/user-management/${id}/reject`),
  remove: (id) => api.delete(`/user-management/${id}`),
  update: (id, data) => api.put(`/user-management/${id}`, data)
}

// 在线用户
export const onlineUsersApi = {
  getList: (params) => api.get('/online-users', { params }),
  getDetail: (id) => api.get(`/online-users/${id}`),
  create: (data) => api.post('/online-users', data),
  remove: (id) => api.delete(`/online-users/${id}`),
  update: (id, data) => api.put(`/online-users/${id}`, data)
}

// 业务操作日志
export const bizOperationLogsApi = {
  getList: (params) => api.get('/biz-operation-logs', { params }),
  getDetail: (id) => api.get(`/biz-operation-logs/${id}`),
  create: (data) => api.post('/biz-operation-logs', data),
  update: (id, data) => api.put(`/biz-operation-logs/${id}`, data),
  remove: (id) => api.delete(`/biz-operation-logs/${id}`)
}

// 数据备份 / 恢复
export const dataBackupApi = {
  list: () => api.get('/data-backup'),
  create: () => api.post('/data-backup'),
  remove: (filename) => api.delete('/data-backup', { params: { filename } })
}

export const dataRestoreApi = {
  restore: (data) => api.post('/data-restore', data)
}

export default api

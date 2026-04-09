import axios from 'axios'
import { useUserStore } from '../store'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response && error.response.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关
export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register'),
  refresh: () => api.post('/auth/refresh'),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile'),
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

export default api

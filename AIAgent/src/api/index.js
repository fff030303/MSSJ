import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000', // 实际项目中这里应该配置为后端API的基础URL
  // baseURL: 'http://172.16.3.171:5000',
  timeout: 60*1000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// // 请求拦截器
// api.interceptors.request.use(
//   config => {
//     // 从localStorage获取token并添加到请求头
//     const token = localStorage.getItem('token')
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`
//     }
//     return config
//   },
//   error => {
//     return Promise.reject(error)
//   }
// )

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // if (error.response && error.response.status === 401) {
    //   // 401未授权，清除token并跳转到登录页
    //   localStorage.removeItem('token')
    //   localStorage.removeItem('user')
    //   window.location.href = '/login'
    // }
    return Promise.reject(error)
  }
)

// API服务
export default {
  // 用户认证
  auth: {
    login(credentials) {
      return api.post('/auth/login', credentials)
    },
    register(userData) {
      return api.post('/auth/register', userData)
    },
    logout() {
      return api.post('/auth/logout')
    },
    getProfile() {
      return api.get('/auth/profile')
    }
  },

  // 问题相关
  questions: {
    submit(data) {
      return api.post('/api/chat', { query: data.query, user_id: data.user_id })
    },
    getAnswers(questionId) {
      return api.get(`/questions/${questionId}/answers`)
    }
  },

  // 答案相关
  answers: {
    rate(answerId, rating) {
      return api.post(`/answers/${answerId}/rate`, { rating })
    },
    filter(questionId, filters) {
      return api.post(`/questions/${questionId}/filter`, filters)
    }
  },

  // 历史记录
  history: {
    getAll(params) { // 改为接收params对象
      return api.get('/api/history', { params })
    },
    getById(historyId) {
      return api.get(`/history/${historyId}`)
    },
    delete(historyId) {
      return api.delete(`/history/${historyId}`)
    }
  }
}
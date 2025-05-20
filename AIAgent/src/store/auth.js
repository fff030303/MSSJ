import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token')
  }),

  actions: {
    async login(credentials) {
      try {
        // 硬编码的admin账户登录
        if (credentials.username === 'admin' && credentials.password === '123456') {
          const user = { id: 1, username: 'admin' }
          const token = 'admin-token-' + Math.random().toString(36).substr(2)
          
          this.setUser(user)
          this.setToken(token)
          return { success: true }
        }
        
        // 这里应该连接到实际的API
        // 现在模拟一个成功的请求
        // const response = await axios.post('/api/auth/login', credentials)
        // const { user, token } = response.data
        
        // 模拟数据
        const user = { id: 1, username: credentials.username }
        const token = 'mock-jwt-token-' + Math.random().toString(36).substr(2)
        
        this.setUser(user)
        this.setToken(token)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.message || '登录失败'
        }
      }
    },

    async register(userData) {
      try {
        // 这里应该连接到实际的API
        // 现在模拟一个成功的请求
        // const response = await axios.post('/api/auth/register', userData)
        // const { user, token } = response.data
        
        // 模拟数据
        const user = { id: 1, username: userData.username }
        const token = 'mock-jwt-token-' + Math.random().toString(36).substr(2)
        
        this.setUser(user)
        this.setToken(token)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.message || '注册失败'
        }
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    setUser(user) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },

    setToken(token) {
      this.token = token
      this.isAuthenticated = true
      localStorage.setItem('token', token)
    }
  }
}) 
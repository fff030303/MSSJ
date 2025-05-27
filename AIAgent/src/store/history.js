import {defineStore} from 'pinia'
import api from '../api/index.js'

export const useHistoryStore = defineStore('history', {
  state: () => ({
    conversations: [],
    searchQuery: '',
    dateFilter: {
      start: null,
      end: null
    }
  }),

  getters: {
    // 过滤后的对话历史
    filteredConversations() {
      let filtered = [...this.conversations]
      
      // 按搜索关键词过滤
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(conv => 
          conv.question.toLowerCase().includes(query) ||
          conv.answers.some(ans => ans.content.toLowerCase().includes(query))
        )
      }
      
      // 按日期过滤
      if (this.dateFilter.start) {
        const startDate = new Date(this.dateFilter.start).getTime()
        filtered = filtered.filter(conv => 
          new Date(conv.timestamp).getTime() >= startDate
        )
      }
      
      if (this.dateFilter.end) {
        const endDate = new Date(this.dateFilter.end).getTime()
        filtered = filtered.filter(conv => 
          new Date(conv.timestamp).getTime() <= endDate
        )
      }
      
      // 按时间倒序排列
      return filtered.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )
    }
  },

  actions: {
    // 加载历史记录
    async loadHistory(user_id) {
      try {
        await api.history.getAll({
          user_id: user_id,
          limit: 20,
        }).then(res=>{
          this.conversations = res.history
          this.saveHistory()
        })
      }catch(error){
        console.error('Failed to load history:', error)
      }
      // const savedHistory = localStorage.getItem('conversationHistory')
      // if (savedHistory) {
      //   this.conversations = JSON.parse(savedHistory)
      // }
    },
    
    // 添加新对话到历史
    addConversation(conversation) {
      this.conversations.unshift(conversation)
      this.saveHistory()
    },
    
    // 保存历史记录到本地存储
    saveHistory() {
      localStorage.setItem('conversationHistory', JSON.stringify(this.conversations.slice(0, 100))) // 只保存最近100条
    },
    
    // 清除历史记录
    clearHistory() {
      this.conversations = []
      localStorage.removeItem('conversationHistory')
    },
    
    // 设置搜索查询
    setSearchQuery(query) {
      this.searchQuery = query
    },
    
    // 设置日期过滤器
    setDateFilter(filter) {
      this.dateFilter = filter
    },
    
    // 根据问题ID获取对话
    getConversationById(id) {
      return this.conversations.find(conv => conv.id === id)
    },
    
    // 删除单个对话
    deleteConversation(id) {
      const index = this.conversations.findIndex(conv => conv.id === id)
      if (index !== -1) {
        this.conversations.splice(index, 1)
        this.saveHistory()
      }
    },
  }
}) 
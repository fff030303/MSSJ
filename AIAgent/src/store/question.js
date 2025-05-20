import { defineStore } from 'pinia'
import axios from 'axios'

export const useQuestionStore = defineStore('question', {
  state: () => ({
    currentQuestion: null,
    isLoading: false,
    answers: [],
    history: []
  }),

  actions: {
    async submitQuestion(question) {
      this.isLoading = true
      try {
        // 模拟向多个AI服务提供商发送请求
        // 在实际情况下，这里会调用后端API，后端再分发到不同的AI提供商
        const id = Date.now().toString()
        this.currentQuestion = {
          id,
          content: question,
          timestamp: new Date().toISOString()
        }
        
        // 模拟API请求延迟
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 模拟从不同AI获取的答案
        const mockAnswers = [
          {
            id: '1',
            provider: 'AI提供商A',
            content: `这是AI提供商A对问题"${question}"的回答。`,
            timestamp: new Date().toISOString(),
            questionId: id
          },
          {
            id: '2',
            provider: 'AI提供商B',
            content: `这是AI提供商B对问题"${question}"的详细解答。该问题涉及到的内容可能有多个方面需要考虑。`,
            timestamp: new Date().toISOString(),
            questionId: id
          },
          {
            id: '3',
            provider: 'AI提供商C',
            content: `AI提供商C的答案：${question}是一个很好的问题。从以下几个角度来看待这个问题...`,
            timestamp: new Date().toISOString(),
            questionId: id
          }
        ]
        
        this.answers = mockAnswers
        
        // 添加到历史记录
        this.addToHistory({
          id,
          question,
          answersCount: mockAnswers.length,
          timestamp: new Date().toISOString()
        })
        
        return { success: true, questionId: id }
      } catch (error) {
        console.error('提交问题失败:', error)
        return { success: false, message: '提交问题失败，请稍后重试' }
      } finally {
        this.isLoading = false
      }
    },
    
    addToHistory(historyItem) {
      this.history.unshift(historyItem)
      // 保存到本地存储
      const savedHistory = JSON.parse(localStorage.getItem('questionHistory') || '[]')
      savedHistory.unshift(historyItem)
      localStorage.setItem('questionHistory', JSON.stringify(savedHistory.slice(0, 50))) // 只保留最近50条
    },
    
    loadHistory() {
      const savedHistory = JSON.parse(localStorage.getItem('questionHistory') || '[]')
      this.history = savedHistory
    },
    
    // 根据问题ID获取答案
    getAnswersForQuestion(questionId) {
      return this.answers.filter(answer => answer.questionId === questionId)
    },
    
    // 清空当前问题和答案
    clearCurrent() {
      this.currentQuestion = null
      this.answers = []
    }
  }
}) 
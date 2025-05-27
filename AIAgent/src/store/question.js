import { defineStore } from 'pinia'
import api from '../api/index.js'

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
        const id = Date.now().toString()
        this.currentQuestion = {
          id,
          content: question,
          timestamp: new Date().toISOString()
        }
        
      
        await api.questions.submit(question).then(res=>{
          const spark_answer = res.spark_answer
          const qianfan_answer = res.qianfan_answer
          const doubao_answer = res.doubao_answer
          const question_id = res.question_id
          this.answers = [
            {
              id: '1',
              provider: 'AI提供商A',
              content: spark_answer,
              timestamp: new Date().toISOString(),
              questionId: question_id,
            },
            {
              id: '2',
              provider: 'AI提供商B',
              content: qianfan_answer,
              timestamp: new Date().toISOString(),
              questionId: question_id,
            },
            {
              id: '3',
              provider: 'AI提供商C',
              content: doubao_answer,
              timestamp: new Date().toISOString(),
              questionId: question_id,
            }
          ]
          console.log(this.answers);
          
        })

        
        // 添加到历史记录
        this.addToHistory({
          id,
          question,
          answersCount: this.answers.length, // 改用实际获取的 answers 数组
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
import { defineStore } from 'pinia'
import { useQuestionStore } from './question'

export const useAnswerStore = defineStore('answer', {
  state: () => ({
    // 用户对回答的评分
    ratings: {},
    // 筛选设置
    filterSettings: {
      providers: [], // 筛选特定AI提供商
      minLength: 0,  // 最小长度筛选
      keywords: []   // 关键词筛选
    },
    // 推荐设置
    recommendationSettings: {
      preferredProviders: [], // 偏好的AI提供商
      useContentLength: false, // 是否根据内容长度推荐
      useUserRatings: true     // 是否使用用户评分推荐
    }
  }),

  actions: {
    // 为答案评分
    rateAnswer(answerId, rating) {
      this.ratings[answerId] = rating
      // 保存到本地存储
      localStorage.setItem('answerRatings', JSON.stringify(this.ratings))
    },
    
    // 加载评分记录
    loadRatings() {
      const savedRatings = localStorage.getItem('answerRatings')
      if (savedRatings) {
        this.ratings = JSON.parse(savedRatings)
      }
    },
    
    // 更新筛选设置
    updateFilterSettings(settings) {
      this.filterSettings = { ...this.filterSettings, ...settings }
    },
    
    // 更新推荐设置
    updateRecommendationSettings(settings) {
      this.recommendationSettings = { ...this.recommendationSettings, ...settings }
    },
    
    // 根据筛选条件过滤答案
    filterAnswers(answers) {
      let filtered = [...answers]
      
      // 按提供商筛选
      if (this.filterSettings.providers.length > 0) {
        filtered = filtered.filter(answer => 
          this.filterSettings.providers.includes(answer.provider)
        )
      }
      
      // 按最小长度筛选
      if (this.filterSettings.minLength > 0) {
        filtered = filtered.filter(answer => 
          answer.content.length >= this.filterSettings.minLength
        )
      }
      
      // 按关键词筛选
      if (this.filterSettings.keywords.length > 0) {
        filtered = filtered.filter(answer => 
          this.filterSettings.keywords.some(keyword => 
            answer.content.toLowerCase().includes(keyword.toLowerCase())
          )
        )
      }
      
      return filtered
    },
    
    // 推荐最佳答案
    recommendBestAnswer(answers) {
      if (!answers || answers.length === 0) return null
      
      // 复制数组以免修改原始数据
      let candidates = [...answers]
      
      // 按偏好提供商筛选
      if (this.recommendationSettings.preferredProviders.length > 0) {
        const preferred = candidates.filter(answer => 
          this.recommendationSettings.preferredProviders.includes(answer.provider)
        )
        if (preferred.length > 0) {
          candidates = preferred
        }
      }
      
      // 使用评分筛选
      if (this.recommendationSettings.useUserRatings) {
        const ratedAnswers = candidates.filter(answer => this.ratings[answer.id])
        if (ratedAnswers.length > 0) {
          // 按评分排序
          return ratedAnswers.sort((a, b) => 
            this.ratings[b.id] - this.ratings[a.id]
          )[0]
        }
      }
      
      // 按内容长度筛选
      if (this.recommendationSettings.useContentLength) {
        // 返回最长的答案
        return candidates.sort((a, b) => b.content.length - a.content.length)[0]
      }
      
      // 如果没有其他筛选条件，返回第一个答案
      return candidates[0]
    }
  }
}) 
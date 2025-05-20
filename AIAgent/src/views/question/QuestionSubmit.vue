<template>
  <div class="question-container">
    <div class="chat-header">
      <h2>AI问答聊天</h2>
    </div>

    <!-- AI提供商选择 -->
    <div class="ai-providers-container">
      <div class="ai-providers-title">AI提供商：</div>
      <div class="ai-providers-checkboxes">
        <el-checkbox v-model="providers.chatgpt">ChatGPT</el-checkbox>
        <el-checkbox v-model="providers.claude">Claude</el-checkbox>
        <el-checkbox v-model="providers.gemini">Gemini</el-checkbox>
        <el-checkbox v-model="providers.baidu">Baidu</el-checkbox>
        <el-checkbox v-model="providers.qwen">Qwen</el-checkbox>
      </div>
    </div>

    <!-- 消息展示区域 -->
    <div class="chat-content">
      <div v-if="isLoading" class="loading-message">
        <el-skeleton :rows="3" animated />
        <div class="loading-text">
          <el-icon class="loading-icon"><Loading /></el-icon>
          正在查询AI服务提供商，请稍候...
        </div>
      </div>

      <div v-if="conversation.length === 0" class="empty-conversation">
        <el-empty description="尚无对话，请在下方输入您的问题" />
      </div>

      <div v-else class="message-list">
        <!-- 问题 -->
        <div v-for="(item, index) in conversation" :key="index">
          <!-- 用户问题 -->
          <div v-if="item.type === 'question'" class="question-message">
            <div class="message-header">
              <div class="message-title">问题</div>
              <div class="message-time">{{ formatTime(item.timestamp) }}</div>
            </div>
            <div class="message-content">{{ item.content }}</div>
          </div>

          <!-- AI回答列表 -->
          <div v-if="item.type === 'answers'" class="answers-container">
            <div class="answers-header">
              <div class="answers-title">AI回答</div>
              <div class="answers-tools">
                <el-button-group>
                  <el-button size="small" @click="sortAnswersByTime(item)">按时间排序</el-button>
                  <el-button size="small" @click="sortAnswersByRating(item)">按评分排序</el-button>
                </el-button-group>
              </div>
            </div>

            <!-- 各个AI的回答 -->
            <div v-for="answer in item.answers" :key="answer.id" class="answer-item">
              <div class="answer-header">
                <div class="answer-provider">{{ answer.provider }}</div>
                <div class="answer-time">{{ formatTime(answer.timestamp) }}</div>
              </div>
              <div class="answer-content">{{ answer.content }}</div>
              <div class="answer-footer">
                <el-rate
                  v-model="ratings[answer.id]"
                  @change="rateAnswer(answer.id, $event)"
                  :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                />
                <div class="answer-actions">
                  <el-button size="small" type="primary" plain @click="copyAnswer(answer.content)">复制</el-button>
                  <el-button size="small" type="success" plain>标为最佳</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 问题输入区域 -->
    <div class="question-input-container">
      <el-input
        v-model="questionInput"
        type="textarea"
        :rows="3"
        placeholder="请输入您的问题..."
        :disabled="isLoading"
        @keyup.ctrl.enter="submitQuestion"
      />
      <div class="question-actions">
        <el-button type="primary" @click="submitQuestion" :loading="isLoading" :disabled="!questionInput.trim() || !hasSelectedProvider">
          发送问题
        </el-button>
        <div class="input-tip">按Ctrl+Enter发送</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useQuestionStore } from '@/store/question'
import { useAnswerStore } from '@/store/answer'

const questionStore = useQuestionStore()
const answerStore = useAnswerStore()

// 选择的AI提供商
const providers = reactive({
  chatgpt: true,
  claude: true,
  gemini: true,
  baidu: true,
  qwen: true
})

const hasSelectedProvider = computed(() => {
  return Object.values(providers).some(value => value === true)
})

// 问题输入
const questionInput = ref('')
const isLoading = ref(false)
const ratings = ref({})
const conversation = ref([])

// 加载评分数据和设置
onMounted(() => {
  // 加载用户评分
  answerStore.loadRatings()
  ratings.value = answerStore.ratings
  
  // 加载AI提供商设置
  loadAiSettings()
})

// 加载AI提供商设置
const loadAiSettings = () => {
  try {
    const savedAiSettings = localStorage.getItem('aiSettings')
    if (savedAiSettings) {
      const parsedSettings = JSON.parse(savedAiSettings)
      
      // 更新默认启用的提供商
      if (parsedSettings.defaultProviders && parsedSettings.defaultProviders.length > 0) {
        // 重置所有提供商
        Object.keys(providers).forEach(key => {
          providers[key] = false
        })
        
        // 启用设置中的提供商
        parsedSettings.defaultProviders.forEach(provider => {
          if (providers.hasOwnProperty(provider)) {
            providers[provider] = true
          }
        })
      }
    }
  } catch (error) {
    console.error('加载AI设置失败:', error)
  }
}

// 提交问题
const submitQuestion = async () => {
  if (!questionInput.value.trim() || !hasSelectedProvider.value) return
  
  isLoading.value = true
  
  try {
    // 添加问题到对话
    const questionText = questionInput.value
    const questionItem = {
      type: 'question',
      content: questionText,
      timestamp: new Date().toISOString()
    }
    
    conversation.value.push(questionItem)
    
    // 清空输入
    questionInput.value = ''
    
    // 构造所选的AI提供商列表
    const selectedProviders = []
    for (const [key, value] of Object.entries(providers)) {
      if (value) selectedProviders.push(key)
    }
    
    // 模拟发送到各个AI服务提供商并获取答案
    // 在实际应用中，这里应该通过API发送请求
    
    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 构造模拟回答
    const answersItem = {
      type: 'answers',
      timestamp: new Date().toISOString(),
      answers: selectedProviders.map((provider, index) => ({
        id: Date.now() + '-' + index,
        provider: provider.charAt(0).toUpperCase() + provider.slice(1),
        content: `这是来自${provider}的回答: ${questionText} 是一个很好的问题。这里是${provider}的详细解答...`,
        timestamp: new Date().toISOString()
      }))
    }
    
    // 添加回答到对话
    conversation.value.push(answersItem)
    
    // 添加到历史记录
    const historyItem = {
      id: Date.now().toString(),
      question: questionText,
      answersCount: answersItem.answers.length,
      timestamp: new Date().toISOString()
    }
    
    // 更新历史记录
    questionStore.addToHistory({
      id: historyItem.id,
      question: historyItem.question,
      answersCount: historyItem.answersCount,
      timestamp: historyItem.timestamp
    })
    
  } catch (error) {
    console.error('提交问题错误:', error)
    ElMessage.error('发生错误，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

// 评分答案
const rateAnswer = (answerId, rating) => {
  answerStore.rateAnswer(answerId, rating)
  ElMessage.success('评分已保存')
}

// 复制答案内容
const copyAnswer = (content) => {
  navigator.clipboard.writeText(content).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 按评分排序
const sortAnswersByRating = (item) => {
  item.answers.sort((a, b) => {
    const ratingA = ratings.value[a.id] || 0
    const ratingB = ratings.value[b.id] || 0
    return ratingB - ratingA
  })
  ElMessage.info('已按评分排序')
}

// 按时间排序
const sortAnswersByTime = (item) => {
  item.answers.sort((a, b) => {
    return new Date(a.timestamp) - new Date(b.timestamp)
  })
  ElMessage.info('已按时间排序')
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString()
}
</script>

<style scoped>
.question-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100% !important;
  max-width: none !important;
}

.chat-header {
  padding: 0 0 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.chat-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.ai-providers-container {
  display: flex;
  padding: 20px 0;
  border-bottom: 1px solid #ebeef5;
}

.ai-providers-title {
  white-space: nowrap;
  margin-right: 20px;
  font-weight: 500;
}

.ai-providers-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 15px 0;
  margin-bottom: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.empty-conversation {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 0 15px;
}

.question-message {
  background-color: #ecf5ff;
  padding: 15px;
  border-radius: 8px;
  border-left: 3px solid #409EFF;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.message-title {
  font-weight: 600;
  color: #409EFF;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message-content {
  line-height: 1.5;
  white-space: pre-wrap;
}

.answers-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.answers-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 5px;
}

.answers-title {
  font-weight: 600;
  color: #67c23a;
}

.answer-item {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.answer-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.answer-provider {
  font-weight: 600;
  color: #303133;
}

.answer-time {
  font-size: 12px;
  color: #909399;
}

.answer-content {
  line-height: 1.5;
  margin-bottom: 10px;
  white-space: pre-wrap;
}

.answer-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px dashed #ebeef5;
}

.answer-actions {
  display: flex;
  gap: 10px;
}

.question-input-container {
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 -2px 6px rgba(0, 0, 0, 0.05);
}

.question-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.input-tip {
  font-size: 12px;
  color: #909399;
}

.loading-message {
  padding: 20px;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 15px;
  color: #909399;
}

.loading-icon {
  margin-right: 8px;
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 
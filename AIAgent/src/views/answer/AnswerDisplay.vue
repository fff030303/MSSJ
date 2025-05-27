<template>
  <div class="answer-display-container">
    <div v-if="loading" class="section loading-section">
      <el-skeleton :rows="10" animated />
    </div>
    
    <div v-else-if="error" class="section error-section">
      <el-empty description="获取答案失败" />
      <el-button type="primary" @click="fetchAnswers">重试</el-button>
    </div>
    
    <template v-else>
      <div class="section">
        <div class="question-header">
          <h2 class="section-title">问题详情</h2>
          <el-button size="small" @click="goBack">返回</el-button>
        </div>
        
        <div class="question-info">
          <div class="question-content">
<!--            <strong>问题：</strong> {{ currentQuestion.content }}-->
            <strong>问题：</strong> {{ item.content }}
          </div>
          <div class="question-meta">
            <span>时间：{{ formatTime(item.timestamp) }}</span>
            <span>回答数量：{{ item.answers.length }}</span>
          </div>
        </div>
      </div>

      <!-- 答案筛选 -->
<!--      <div class="section filter-section">-->
<!--        <div class="filter-header">-->
<!--          <h3>答案筛选</h3>-->
<!--          <el-button size="small" @click="resetFilter">重置</el-button>-->
<!--        </div>-->
<!--        -->
<!--        <div class="filter-content">-->
<!--          <el-form :model="filterForm" label-width="100px">-->
<!--            <el-form-item label="AI提供商">-->
<!--              <el-select v-model="filterForm.providers" multiple placeholder="选择AI提供商" style="width: 100%">-->
<!--                <el-option-->
<!--                  v-for="provider in allProviders"-->
<!--                  :key="provider"-->
<!--                  :label="provider"-->
<!--                  :value="provider"-->
<!--                />-->
<!--              </el-select>-->
<!--            </el-form-item>-->
<!--            -->
<!--            <el-form-item label="关键词">-->
<!--              <el-input-->
<!--                v-model="filterForm.keyword"-->
<!--                placeholder="输入关键词"-->
<!--                @keyup.enter="applyFilter"-->
<!--              />-->
<!--            </el-form-item>-->
<!--            -->
<!--            <el-form-item>-->
<!--              <el-button type="primary" @click="applyFilter">应用筛选</el-button>-->
<!--            </el-form-item>-->
<!--          </el-form>-->
<!--        </div>-->
<!--      </div>-->

      <!-- 答案列表 -->
      <div class="section answers-section">
<!--        <div class="answers-header">-->
<!--          <h3>AI回答（{{ displayAnswers.length }}/{{ item.answers.length }}）</h3>-->
<!--          <div class="answers-tools">-->
<!--            <el-button-group>-->
<!--              <el-button size="small" @click="sortByRating">按评分排序</el-button>-->
<!--              <el-button size="small" @click="sortByProvider">按提供商排序</el-button>-->
<!--            </el-button-group>-->
<!--          </div>-->
<!--        </div>-->
<!--        -->
<!--        <div v-if="displayAnswers.length === 0" class="empty-answers">-->
<!--          <el-empty description="没有符合条件的答案" />-->
<!--        </div>-->
        
        <div class="answers-list">
          <el-card v-for="answer in item.answers" class="answer-card">
            <template #header>
              <div class="answer-header">
                <span class="provider">{{ answer.model_name }}</span>
                <div class="answer-actions">
                  <el-rate
                    v-model="ratings[answer.id]"
                    @change="rateAnswer(answer.id, $event)"
                    :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                  />
                </div>
              </div>
            </template>
            
            <div class="answer-content">{{ answer.content }}</div>
          </el-card>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useQuestionStore } from '@/store/question'
import { useAnswerStore } from '@/store/answer'

const route = useRoute()
const router = useRouter()
const questionStore = useQuestionStore()
const answerStore = useAnswerStore()

const questionId = computed(() => route.params.id)
const loading = ref(true)
const error = ref(false)
const currentQuestion = ref(null)
const answers = ref([])
const displayAnswers = ref([])
const ratings = ref({})
const item = ref({})
// 筛选表单
const filterForm = reactive({
  providers: [],
  keyword: ''
})

// 获取所有提供商列表
const allProviders = computed(() => {
  const providers = new Set()
  answers.value.forEach(answer => providers.add(answer.provider))
  // return Array.from(providers)
  return ["豆包","星火","讯飞"]
})

// 加载页面时获取数据
onMounted(async () => {
  if (route.query.conversation) {
    item.value = JSON.parse(route.query.conversation);
    // 使用 item 数据
    console.log('接收到的 item:', item);
  }


  // 加载用户的评分记录
  answerStore.loadRatings()
  ratings.value = answerStore.ratings

  await fetchAnswers()
})

// 获取问题及答案数据
const fetchAnswers = async () => {
  loading.value = true
  error.value = false
  
  try {
    // 在实际应用中，这里应该调用API获取数据
    // 现在我们使用本地存储的数据模拟
    
    // 检查store中是否已有当前问题
    if (questionStore.currentQuestion && questionStore.currentQuestion.id === questionId.value) {
      currentQuestion.value = questionStore.currentQuestion
      answers.value = questionStore.answers
    } else {
      // 模拟从服务器获取数据
      currentQuestion.value = {
        id: questionId.value,
        content: '这是一个样例问题？',
        timestamp: new Date().toISOString()
      }
      
      answers.value = [
        {
          id: '1',
          provider: 'AI提供商A',
          content: '这是AI提供商A的回答。',
          timestamp: new Date().toISOString(),
          questionId: questionId.value
        },
        {
          id: '2',
          provider: 'AI提供商B',
          content: '这是AI提供商B的详细解答。',
          timestamp: new Date().toISOString(),
          questionId: questionId.value
        },
        {
          id: '3',
          provider: 'AI提供商C',
          content: '这是AI提供商C的回答。这个问题有多个角度可以回答...',
          timestamp: new Date().toISOString(),
          questionId: questionId.value
        }
      ]
    }
    
    // 初始显示所有答案
    displayAnswers.value = [...answers.value]
    
  } catch (err) {
    console.error('获取答案失败:', err)
    error.value = true
    ElMessage.error('获取答案数据失败')
  } finally {
    loading.value = false
  }
}

// 评分答案
const rateAnswer = (answerId, rating) => {
  answerStore.rateAnswer(answerId, rating)
}

// 应用筛选
const applyFilter = () => {
  let filtered = [...answers.value]
  
  // 按提供商筛选
  if (filterForm.providers.length > 0) {
    filtered = filtered.filter(answer => 
      filterForm.providers.includes(answer.provider)
    )
  }
  
  // 按关键词筛选
  if (filterForm.keyword) {
    const keyword = filterForm.keyword.toLowerCase()
    filtered = filtered.filter(answer => 
      answer.content.toLowerCase().includes(keyword)
    )
  }
  
  displayAnswers.value = filtered
  
  if (filtered.length === 0) {
    ElMessage.warning('没有符合条件的答案')
  } else {
    ElMessage.success(`筛选完成，共显示 ${filtered.length} 条答案`)
  }
}

// 重置筛选
const resetFilter = () => {
  filterForm.providers = []
  filterForm.keyword = ''
  displayAnswers.value = [...answers.value]
  ElMessage.info('已重置筛选条件')
}

// 按评分排序
const sortByRating = () => {
  displayAnswers.value = [...displayAnswers.value].sort((a, b) => {
    const ratingA = ratings.value[a.id] || 0
    const ratingB = ratings.value[b.id] || 0
    return ratingB - ratingA
  })
  ElMessage.info('已按评分从高到低排序')
}

// 按提供商排序
const sortByProvider = () => {
  displayAnswers.value = [...displayAnswers.value].sort((a, b) => {
    return a.provider.localeCompare(b.provider)
  })
  ElMessage.info('已按提供商名称排序')
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString()
}
</script>

<style scoped>
.section {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.question-header, .filter-header, .answers-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.question-info {
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 4px;
}

.question-content {
  font-size: 16px;
  margin-bottom: 10px;
  line-height: 1.5;
}

.question-meta {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 15px;
}

.answers-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.answer-card {
  margin-bottom: 0;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.provider {
  font-weight: bold;
  font-size: 16px;
}

.answer-content {
  padding: 10px 0;
  line-height: 1.6;
  white-space: pre-line;
}

.loading-section, .error-section, .empty-answers {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.error-section button {
  margin-top: 20px;
}
</style> 
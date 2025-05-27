<template>
  <div class="history-container">
    <div class="history-header">
      <h2>历史对话记录</h2>
      <el-button type="danger" size="small" @click="confirmClearHistory" :disabled="historyList.length === 0">
        清空历史记录
      </el-button>
    </div>

    <!-- 历史记录列表 -->
    <div v-if="loading" class="loading-wrapper">
      <el-skeleton :rows="8" animated />
    </div>
    
    <div v-else-if="historyList.length === 0" class="empty-history">
      <el-empty description="没有历史记录" />
    </div>
    
    <div v-else class="history-list">
      <div v-for="item in historyList" :key="item.id" class="history-item" @click="viewConversation(item)">
        <div class="history-item-content">
          <div class="history-question">{{ item.content }}</div>
          <div class="history-meta">
            <span class="history-time">{{ formatTime(item.answers.get(0).timestamp) }}</span>
            <el-tag size="small" type="info">AI回答: {{ item.answers.get(0).content }}</el-tag>
          </div>
        </div>
        <el-icon class="arrow-icon"><ArrowRight /></el-icon>
      </div>
      
      <!-- 分页 -->
      <div v-if="historyList.length > 0" class="pagination">
        <el-pagination
          :current-page="pagination.currentPage"
          :page-size="pagination.pageSize"
          :total="filteredHistory.length"
          layout="total, prev, pager, next"
          background
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'
import { useHistoryStore } from '@/store/history'
import { useQuestionStore } from '@/store/question'
import { useAnswerStore } from '@/store/answer'
import { useAuthStore } from '@/store/auth'

const questionStore = useQuestionStore()
const answerStore = useAnswerStore()
const userStore = useAuthStore()
const router = useRouter()
const historyStore = useHistoryStore()
const loading = ref(false)

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

// 过滤后的历史记录
const filteredHistory = computed(() => {
  return [...historyStore.conversations].sort((a, b) => {
    return new Date(b.timestamp) - new Date(a.timestamp)
  })
})

// 当前页的历史记录
const historyList = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filteredHistory.value.slice(start, end)
})

// 加载历史记录
onMounted(() => {
  loadHistory()
})

const loadHistory = async () => {
  loading.value = true
    console.log('加载历史记录:', userStore.user.id);
  try {
    await historyStore.loadHistory(userStore.user.id)
    pagination.currentPage = 1
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

// 查看对话
const viewConversation = (item) => {
  router.push(`/home/answer/${item.id}`)
}

// 清空所有历史
const confirmClearHistory = () => {
  ElMessageBox.confirm(
    '确定要清空所有历史记录吗？此操作不可恢复！',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    historyStore.clearHistory()
    ElMessage.success('所有历史记录已清空')
  }).catch(() => {})
}

// 页面变化
const handlePageChange = (page) => {
  pagination.currentPage = page
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString()
}
</script>

<style scoped>
.history-container {
  padding: 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.history-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.loading-wrapper, .empty-history {
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.history-list {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.history-item:hover {
  background-color: #f5f7fa;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item-content {
  flex: 1;
}

.history-question {
  font-size: 16px;
  margin-bottom: 8px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.history-time {
  font-size: 12px;
  color: #909399;
}

.arrow-icon {
  font-size: 18px;
  color: #909399;
}

.pagination {
  padding: 15px;
  text-align: right;
  border-top: 1px solid #ebeef5;
}
</style> 
<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="300px">
        <div class="sidebar">
          <div class="logo-title">多AI回答平台</div>
          <el-menu
            :router="true"
            :default-active="activeMenu"
            class="sidebar-menu"
            background-color="#2c3e50"
            text-color="#b3c0d1"
            active-text-color="#ffffff"
            active-background-color="#34495e"
          >
            <el-menu-item index="/home/question">
              <el-icon><ChatDotRound /></el-icon>
              <span>问答聊天</span>
            </el-menu-item>
            <el-menu-item index="/home/history">
              <el-icon><Clock /></el-icon>
              <span>历史记录</span>
            </el-menu-item>
            <el-menu-item index="/home/settings">
              <el-icon><Setting /></el-icon>
              <span>设置</span>
            </el-menu-item>
          </el-menu>
          
          <div class="user-panel">
            <span class="username">{{ userInfo.username }}</span>
          </div>
        </div>
      </el-aside>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { ChatDotRound, Clock, Setting } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const userInfo = computed(() => {
  return authStore.user || { username: '用户' }
})

const logout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    authStore.logout()
    router.push('/login')
  }).catch(() => {})
}

onMounted(() => {
  // 如果没有用户信息，可以尝试从localStorage获取
  if (!authStore.user && localStorage.getItem('user')) {
    try {
      authStore.setUser(JSON.parse(localStorage.getItem('user')))
    } catch (error) {
      console.error('解析用户信息失败:', error)
    }
  }
})
</script>

<style scoped>
.layout-container {
  height: 100%;
  width: 100% !important;
  max-width: none !important;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.el-container {
  width: 100% !important;
  height: 100%;
  display: flex;
  flex: 1;
}

.el-aside {
  width: 300px !important;
  flex-shrink: 0;
}

.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #2c3e50;
  color: #fff;
  width: 300px;
}

.logo-title {
  font-size: 22px;
  font-weight: bold;
  text-align: center;
  padding: 20px 0;
  margin-bottom: 20px;
  background-color: #273746;
  color: white;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #34495e !important;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #34495e !important;
}

.user-panel {
  padding: 15px;
  text-align: center;
  color: #b3c0d1;
  font-size: 14px;
  background-color: #273746;
}

.username {
  font-weight: bold;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
  height: 100%;
  flex: 1;
  width: calc(100% - 300px) !important;
}
</style> 
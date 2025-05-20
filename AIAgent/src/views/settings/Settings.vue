<template>
  <div class="settings-container">
    <div class="settings-header">
      <h2>系统设置</h2>
    </div>

    <div class="settings-content">
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>AI提供商偏好设置</span>
          </div>
        </template>
        <div class="settings-form">
          <el-form label-position="top" :model="aiSettings">
            <el-form-item label="默认启用的AI提供商">
              <el-checkbox-group v-model="aiSettings.defaultProviders">
                <el-checkbox label="chatgpt">ChatGPT</el-checkbox>
                <el-checkbox label="claude">Claude</el-checkbox>
                <el-checkbox label="gemini">Gemini</el-checkbox>
                <el-checkbox label="baidu">Baidu</el-checkbox>
                <el-checkbox label="qwen">Qwen</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="偏好的AI提供商（用于推荐）">
              <el-select 
                v-model="aiSettings.preferredProviders" 
                multiple 
                placeholder="选择偏好的AI提供商"
                style="width: 100%"
              >
                <el-option label="ChatGPT" value="chatgpt" />
                <el-option label="Claude" value="claude" />
                <el-option label="Gemini" value="gemini" />
                <el-option label="Baidu" value="baidu" />
                <el-option label="Qwen" value="qwen" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </el-card>

      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>界面设置</span>
          </div>
        </template>
        <div class="settings-form">
          <el-form label-position="top" :model="uiSettings">
            <el-form-item label="主题">
              <el-radio-group v-model="uiSettings.theme">
                <el-radio label="light">浅色</el-radio>
                <el-radio label="dark">深色</el-radio>
                <el-radio label="system">跟随系统</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="聊天记录显示数量">
              <el-slider
                v-model="uiSettings.historyLimit"
                :min="5"
                :max="50"
                :step="5"
                show-stops
              />
              <div class="slider-value">{{ uiSettings.historyLimit }} 条</div>
            </el-form-item>
          </el-form>
        </div>
      </el-card>

      <div class="settings-actions">
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
        <el-button @click="resetSettings">恢复默认</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// AI设置
const aiSettings = reactive({
  defaultProviders: ['chatgpt', 'claude', 'gemini'],
  preferredProviders: ['chatgpt']
})

// UI设置
const uiSettings = reactive({
  theme: 'light',
  historyLimit: 20
})

// 加载设置
onMounted(() => {
  loadSettings()
})

// 加载已保存的设置
const loadSettings = () => {
  try {
    const savedAiSettings = localStorage.getItem('aiSettings')
    const savedUiSettings = localStorage.getItem('uiSettings')
    
    if (savedAiSettings) {
      const parsedAiSettings = JSON.parse(savedAiSettings)
      Object.assign(aiSettings, parsedAiSettings)
    }
    
    if (savedUiSettings) {
      const parsedUiSettings = JSON.parse(savedUiSettings)
      Object.assign(uiSettings, parsedUiSettings)
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 保存设置
const saveSettings = () => {
  try {
    localStorage.setItem('aiSettings', JSON.stringify(aiSettings))
    localStorage.setItem('uiSettings', JSON.stringify(uiSettings))
    ElMessage.success('设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  }
}

// 重置设置
const resetSettings = () => {
  // 重置为默认值
  aiSettings.defaultProviders = ['chatgpt', 'claude', 'gemini']
  aiSettings.preferredProviders = ['chatgpt']
  uiSettings.theme = 'light'
  uiSettings.historyLimit = 20
  
  ElMessage.info('已恢复默认设置')
}
</script>

<style scoped>
.settings-container {
  height: 100%;
}

.settings-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.settings-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.settings-card {
  margin-bottom: 0;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.settings-form {
  padding: 10px 0;
}

.slider-value {
  text-align: center;
  margin-top: 10px;
  color: #606266;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style> 
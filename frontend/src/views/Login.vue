<template>
  <div class="login-page">
    <div class="login-card">
      <h1>🐍 贪吃蛇Online</h1>
      <p class="subtitle">多人在线PVP贪吃蛇</p>

      <div class="tab-switch">
        <button
          :class="{ active: mode === 'login' }"
          @click="mode = 'login'"
        >登录</button>
        <button
          :class="{ active: mode === 'register' }"
          @click="mode = 'register'"
        >注册</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label>用户名</label>
          <input
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            maxlength="20"
            required
          />
        </div>
        <div class="field">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            maxlength="50"
            required
          />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '请稍候...' : (mode === 'login' ? '登 录' : '注 册') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import http from '../api/http.js'

const router = useRouter()
const auth = useAuthStore()

const mode = ref('login')
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    const endpoint = mode.value === 'login' ? '/api/login' : '/api/register'
    const res = await http.post(endpoint, {
      username: username.value,
      password: password.value,
    })
    auth.setAuth(res.data.access_token, res.data.username)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}

.login-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 48px 40px;
  width: 400px;
  text-align: center;
}

h1 {
  font-size: 32px;
  margin-bottom: 4px;
}

.subtitle {
  color: #888;
  margin-bottom: 28px;
  font-size: 14px;
}

.tab-switch {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  overflow: hidden;
}

.tab-switch button {
  flex: 1;
  padding: 10px;
  background: transparent;
  color: #888;
  border-radius: 0;
}

.tab-switch button.active {
  background: #16c9f2;
  color: #fff;
}

.field {
  margin-bottom: 16px;
  text-align: left;
}

.field label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  color: #aaa;
}

.field input {
  width: 100%;
}

.error {
  color: #ff6b6b;
  font-size: 13px;
  margin-bottom: 12px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #16c9f2, #0ea5e9);
  color: #fff;
  font-size: 16px;
  margin-top: 8px;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

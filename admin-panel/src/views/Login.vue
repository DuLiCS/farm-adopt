<template>
  <div class="login-page">
    <div class="card">
      <div class="logo">
        <span class="logo-icon">🌱</span>
        <h2>山南记管理后台</h2>
        <p class="subtitle">Admin Login</p>
      </div>

      <div class="form">
        <div class="field">
          <input v-model="username" type="text" placeholder="管理员账号" class="input" />
        </div>
        <div class="field">
          <input v-model="password" type="password" placeholder="密码" class="input" />
        </div>

        <div v-if="error" class="error">{{ error }}</div>

        <button class="btn-primary" :disabled="loading" @click="handleLogin">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

onMounted(() => {
  if (localStorage.getItem('admin_token')) {
    router.replace('/')
  }
  username.value = 'admin' // 默认账号
})

const handleLogin = async () => {
  error.value = ''
  if (!username.value || !password.value) {
    error.value = '请填写账号和密码'
    return
  }

  loading.value = true
  try {
    const res = await api.login(username.value, password.value)
    localStorage.setItem('admin_token', res.access_token)
    localStorage.setItem('admin_role', 'admin')
    setTimeout(() => {
      router.replace('/')
    }, 500)
  } catch (e) {
    error.value = e.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f0;
}
.card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}
.logo {
  text-align: center;
  margin-bottom: 32px;
}
.logo-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}
.logo h2 {
  margin: 0;
  font-size: 24px;
  color: #2d5a27;
}
.subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: #999;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.field {
  display: flex;
  flex-direction: column;
}
.input {
  height: 48px;
  padding: 0 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.input:focus {
  border-color: #2d5a27;
}
.btn-primary {
  height: 48px;
  background: #2d5a27;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 8px;
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #c0392b;
  font-size: 14px;
  text-align: center;
  padding: 8px;
  background: #fdeaea;
  border-radius: 4px;
}
</style>
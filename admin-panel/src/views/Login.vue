<template>
  <div class="login-page">
    <div class="bg-layer"></div>

    <div class="left-panel">
      <div class="brand">
        <div class="brand-logo">🌿</div>
        <div class="brand-name">山南记</div>
        <div class="brand-en">SHANNANJI</div>
        <div class="brand-line"></div>
        <div class="brand-tagline">一棵茶树，一年的来往</div>
        <div class="brand-sub">秦岭南麓 · 陕西汉中西乡</div>
      </div>
      <div class="brand-footer">shannanji.com</div>
    </div>

    <div class="right-panel">
      <div class="form-card">
        <div class="form-title">后台管理</div>
        <div class="form-subtitle">仅限授权人员登录</div>

        <div class="field">
          <label>账号</label>
          <input v-model="username" type="text" placeholder="请输入管理员账号" class="input"
            @keyup.enter="handleLogin" autocomplete="username" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" class="input"
            @keyup.enter="handleLogin" autocomplete="current-password" />
        </div>

        <div v-if="error" class="error">{{ error }}</div>

        <button class="btn-login" :disabled="loading" @click="handleLogin">
          <span v-if="loading" class="loading-dot">···</span>
          <span v-else>进入后台</span>
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
  username.value = 'admin'
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
    setTimeout(() => { router.replace('/') }, 300)
  } catch (e) {
    error.value = e.detail || '账号或密码错误'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;
}

.bg-layer {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1a3d16 0%, #2d5a27 50%, #3d6b32 100%);
}

/* 左侧品牌区 */
.left-panel {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 80px 60px;
}

.brand { color: white; }
.brand-logo { font-size: 64px; margin-bottom: 16px; }
.brand-name { font-size: 48px; font-weight: bold; letter-spacing: 8px; margin-bottom: 4px; }
.brand-en { font-size: 13px; letter-spacing: 6px; opacity: 0.5; margin-bottom: 32px; font-weight: 300; }
.brand-line { width: 40px; height: 2px; background: rgba(255,255,255,0.4); margin-bottom: 28px; }
.brand-tagline { font-size: 18px; opacity: 0.9; margin-bottom: 10px; font-weight: 300; line-height: 1.6; }
.brand-sub { font-size: 13px; opacity: 0.5; letter-spacing: 2px; }

.brand-footer {
  position: absolute;
  bottom: 40px;
  left: 60px;
  font-size: 12px;
  color: rgba(255,255,255,0.3);
  letter-spacing: 2px;
}

/* 右侧表单区 */
.right-panel {
  position: relative;
  z-index: 1;
  width: 420px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255,255,255,0.1);
}

.form-card {
  width: 100%;
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  color: white;
  margin-bottom: 6px;
}
.form-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.45);
  margin-bottom: 36px;
}

.field {
  margin-bottom: 20px;
}
.field label {
  display: block;
  font-size: 12px;
  color: rgba(255,255,255,0.55);
  margin-bottom: 8px;
  letter-spacing: 1px;
}
.input {
  width: 100%;
  height: 46px;
  padding: 0 16px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 8px;
  font-size: 15px;
  color: white;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s, background 0.2s;
}
.input::placeholder { color: rgba(255,255,255,0.3); }
.input:focus {
  border-color: rgba(255,255,255,0.4);
  background: rgba(255,255,255,0.15);
}

.error {
  font-size: 13px;
  color: #ff8a80;
  margin-bottom: 16px;
  padding: 10px 14px;
  background: rgba(255,100,80,0.12);
  border-radius: 6px;
  border: 1px solid rgba(255,100,80,0.2);
}

.btn-login {
  width: 100%;
  height: 46px;
  background: white;
  color: #2d5a27;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
  transition: opacity 0.2s;
  letter-spacing: 2px;
}
.btn-login:hover { opacity: 0.92; }
.btn-login:disabled { opacity: 0.5; cursor: not-allowed; }
.loading-dot { letter-spacing: 4px; }

@media (max-width: 680px) {
  .left-panel { display: none; }
  .right-panel { width: 100%; background: linear-gradient(135deg, #1a3d16, #2d5a27); border-left: none; }
}
</style>

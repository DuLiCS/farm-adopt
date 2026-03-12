<template>
  <div class="login-container">
    <div class="card" style="max-width: 400px; margin: 120px auto; padding: 24px; background: #fff; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
      <div class="logo" style="text-align: center; margin-bottom: 32px;">
        <div style="font-size: 64px; color: #2d5a27;">🌱</div>
        <div style="font-size: 24px; font-weight: bold; margin-top: 16px;">农场管理后台</div>
        <div style="font-size: 14px; color: #999; margin-top: 8px;">Admin Login</div>
      </div>

      <div style="margin-top: 32px;">
        <input
          ref="usernameRef"
          type="text"
          placeholder="管理员账号"
          autocomplete="username"
          v-model="admin_username"
          style="width: 100%; height: 56px; font-size: 18px; padding: 12px 16px; border: 1px solid #ccc; border-radius: 8px; background: #fff; box-sizing: border-box; margin-bottom: 24px;"
        />
        <input
          ref="passwordRef"
          type="password"
          placeholder="密码"
          autocomplete="current-password"
          v-model="admin_password"
          style="width: 100%; height: 56px; font-size: 18px; padding: 12px 16px; border: 1px solid #ccc; border-radius: 8px; background: #fff; box-sizing: border-box;"
        />
      </div>

      <div v-if="error" style="color: #c0392b; font-size: 14px; margin: 16px 0;">
        {{ error }}
      </div>

      <button
        @click="handleLogin"
        :disabled="loading"
        style="width: 100%; margin-top: 32px; height: 56px; background-color: #2d5a27; color: #fff; border: none; border-radius: 999px; font-size: 18px; cursor: pointer;"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminLogin } from '@/api/admin.js'
import { ADMIN_CONFIG } from '@/config.js'

const router = useRouter()
const admin_username = ref('')
const admin_password = ref('')
const error = ref('')
const loading = ref(false)
const usernameRef = ref(null)
const passwordRef = ref(null)

onMounted(() => {
  // 检查是否已有 token
  const token = localStorage.getItem('admin_token')
  if (token) {
    router.replace('/admin/index')
    return
  }
  // 设置默认用户名
  if (ADMIN_CONFIG.username) {
    admin_username.value = ADMIN_CONFIG.username
  }
})

const handleLogin = async () => {
  error.value = ''
  if (!admin_username.value || !admin_password.value) {
    error.value = '请填写账号和密码'
    return
  }

  loading.value = true
  try {
    const res = await adminLogin(admin_username.value, admin_password.value)
    localStorage.setItem('admin_token', res.access_token)
    localStorage.setItem('admin_role', 'admin')
    router.replace('/admin/index')
  } catch (e) {
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

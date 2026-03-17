<template>
  <div class="admin-layout">
    <header class="header">
      <h1>山南记管理后台</h1>
      <nav class="nav">
        <router-link to="/">首页</router-link>
        <router-link to="/targets">认养对象</router-link>
        <router-link to="/orders">订单管理</router-link>
        <router-link to="/updates">发布更新</router-link>
        <router-link to="/update-list">更新列表</router-link>
        <router-link to="/sensor">传感器</router-link>
        <router-link to="/settings">网站设置</router-link>
        <router-link to="/settings">网站设置</router-link>
      </nav>
      <button class="btn-logout" @click="logout">退出</button>
    </header>

    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_role')
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f5f5f0;
}
.header {
  background: #2d5a27;
  color: white;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header h1 {
  margin: 0;
  font-size: 20px;
  flex-shrink: 0;
}
.nav {
  display: flex;
  gap: 16px;
  flex: 1;
}
.nav a {
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.2s;
}
.nav a:hover,
.nav a.router-link-active {
  background: rgba(255,255,255,0.15);
  color: white;
}
.btn-logout {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 14px;
  opacity: 0.8;
}
.btn-logout:hover {
  opacity: 1;
}
.main {
  padding: 24px;
}
</style>
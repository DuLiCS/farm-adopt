<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="sidebar-logo">🌿</span>
        <div class="sidebar-brand-text">
          <div class="sidebar-name">山南记</div>
          <div class="sidebar-role">管理后台</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" exact>
          <span class="nav-icon">◻</span>概览
        </router-link>
        <router-link to="/targets" class="nav-item">
          <span class="nav-icon">🌱</span>认养对象
        </router-link>
        <router-link to="/orders" class="nav-item">
          <span class="nav-icon">📋</span>订单管理
        </router-link>
        <div class="nav-group-label">内容运营</div>
        <router-link to="/updates" class="nav-item">
          <span class="nav-icon">✍️</span>发布更新
        </router-link>
        <router-link to="/update-list" class="nav-item">
          <span class="nav-icon">📰</span>日志管理
        </router-link>
        <div class="nav-group-label">数据与设置</div>
        <router-link to="/sensor" class="nav-item">
          <span class="nav-icon">📡</span>传感器
        </router-link>
        <router-link to="/plans" class="nav-item">
          <span class="nav-icon">🏷️</span>套餐管理
        </router-link>
        <router-link to="/settings" class="nav-item">
          <span class="nav-icon">⚙️</span>网站设置
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="btn-logout" @click="logout">退出登录</button>
      </div>
    </aside>

    <!-- 主内容区 -->
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
  display: flex;
  background: #f5f5f0;
}

/* 侧边栏 */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #1a3d16;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  z-index: 100;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 28px 24px 24px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.sidebar-logo { font-size: 28px; }
.sidebar-name { font-size: 16px; font-weight: bold; color: white; line-height: 1.2; }
.sidebar-role { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 2px; letter-spacing: 1px; }

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
  overflow-y: auto;
}

.nav-group-label {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  letter-spacing: 2px;
  padding: 20px 24px 8px;
  text-transform: uppercase;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 24px;
  font-size: 14px;
  color: rgba(255,255,255,0.65);
  text-decoration: none;
  transition: all 0.15s;
  border-left: 3px solid transparent;
}
.nav-icon { font-size: 15px; width: 20px; text-align: center; flex-shrink: 0; }
.nav-item:hover {
  background: rgba(255,255,255,0.07);
  color: rgba(255,255,255,0.9);
}
.nav-item.router-link-active {
  background: rgba(255,255,255,0.1);
  color: white;
  border-left-color: #7cc47a;
  font-weight: 500;
}

.sidebar-footer {
  padding: 20px 24px;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.btn-logout {
  width: 100%;
  background: none;
  border: 1px solid rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.5);
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}
.btn-logout:hover {
  border-color: rgba(255,255,255,0.3);
  color: rgba(255,255,255,0.8);
}

/* 主内容 */
.main {
  margin-left: 220px;
  flex: 1;
  padding: 32px;
  min-height: 100vh;
  box-sizing: border-box;
}
</style>

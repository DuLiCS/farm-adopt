<template>
  <div class="admin-layout">
    <header class="admin-header" style="background-color: #2d5a27; color: #fff; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="margin: 0; font-size: 20px;">农场管理后台</h1>
      </div>
      <nav>
        <router-link to="/admin/index" style="color: #fff; margin-right: 16px; text-decoration: none;">首页</router-link>
        <router-link to="/admin/targets" style="color: #fff; margin-right: 16px; text-decoration: none;">认养对象</router-link>
        <router-link to="/admin/orders" style="color: #fff; margin-right: 16px; text-decoration: none;">订单管理</router-link>
        <router-link to="/admin/update-form" style="color: #fff; margin-right: 16px; text-decoration: none;">发布更新</router-link>
        <router-link to="/admin/updates" style="color: #fff; margin-right: 16px; text-decoration: none;">更新记录</router-link>
        <a href="#" @click.prevent="logout" style="color: #fff; text-decoration: none;">退出</a>
      </nav>
    </header>
    <main class="admin-content" style="padding: 24px; background: #f5f5f0; min-height: calc(100vh - 64px);">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout',
  methods: {
    logout() {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_role')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f5f5f0;
}
</style>

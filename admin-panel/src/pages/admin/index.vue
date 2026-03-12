<template>
  <div class="container">
    <!-- 数据概览 -->
    <div class="stats-grid" style="display: flex; gap: 16px; margin-bottom: 24px;">
      <div class="stat-card" style="flex: 1; background: #fff; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <div class="stat-value" style="font-size: 32px; font-weight: bold; color: #2d5a27; margin-bottom: 8px;">{{ stats.targetCount }}</div>
        <div class="stat-label" style="font-size: 14px; color: #999;">认养对象</div>
      </div>
      <div class="stat-card" style="flex: 1; background: #fff; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <div class="stat-value" style="font-size: 32px; font-weight: bold; color: #2d5a27; margin-bottom: 8px;">{{ stats.orderCount }}</div>
        <div class="stat-label" style="font-size: 14px; color: #999;">总订单数</div>
      </div>
      <div class="stat-card" style="flex: 1; background: #fff; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <div class="stat-value" style="font-size: 32px; font-weight: bold; color: #2d5a27; margin-bottom: 8px;">{{ stats.monthOrders }}</div>
        <div class="stat-label" style="font-size: 14px; color: #999;">本月新增</div>
      </div>
    </div>

    <!-- 功能菜单 -->
    <div class="menu-section" style="background: #fff; border-radius: 12px; overflow: hidden;">
      <div class="menu-item" style="display: flex; align-items: center; padding: 24px; border-bottom: 1px solid #f0f0f0; cursor: pointer;" @click="goToTargets">
        <div class="menu-icon" style="width: 64px; height: 64px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 32px; margin-right: 16px; background-color: #e8f5e9;">🌿</div>
        <div class="menu-content" style="flex: 1;">
          <div class="menu-title" style="font-size: 18px; font-weight: 500; color: #333; margin-bottom: 4px;">认养对象管理</div>
          <div class="menu-desc" style="font-size: 14px; color: #999;">查看和管理认养地块</div>
        </div>
        <div class="menu-arrow" style="font-size: 24px; color: #bbb;">›</div>
      </div>

      <div class="menu-item" style="display: flex; align-items: center; padding: 24px; border-bottom: 1px solid #f0f0f0; cursor: pointer;" @click="goToOrders">
        <div class="menu-icon" style="width: 64px; height: 64px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 32px; margin-right: 16px; background-color: #fff3e0;">📦</div>
        <div class="menu-content" style="flex: 1;">
          <div class="menu-title" style="font-size: 18px; font-weight: 500; color: #333; margin-bottom: 4px;">订单管理</div>
          <div class="menu-desc" style="font-size: 14px; color: #999;">查看和创建订单</div>
        </div>
        <div class="menu-arrow" style="font-size: 24px; color: #bbb;">›</div>
      </div>

      <div class="menu-item" style="display: flex; align-items: center; padding: 24px; cursor: pointer;" @click="goToUpdateForm">
        <div class="menu-icon" style="width: 64px; height: 64px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 32px; margin-right: 16px; background-color: #e3f2fd;">📝</div>
        <div class="menu-content" style="flex: 1;">
          <div class="menu-title" style="font-size: 18px; font-weight: 500; color: #333; margin-bottom: 4px;">发布更新</div>
          <div class="menu-desc" style="font-size: 14px; color: #999;">发布农场动态和图片</div>
        </div>
        <div class="menu-arrow" style="font-size: 24px; color: #bbb;">›</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAdminTargets, getAdminOrders } from '@/api/admin.js'

const router = useRouter()
const stats = ref({
  targetCount: 0,
  orderCount: 0,
  monthOrders: 0
})
const loading = ref(false)

const checkAuth = () => {
  const token = localStorage.getItem('admin_token')
  if (!token) {
    router.replace('/login')
  }
}

const loadStats = async () => {
  loading.value = true
  try {
    const [targetsRes, ordersRes] = await Promise.all([
      getAdminTargets(),
      getAdminOrders()
    ])
    stats.value.targetCount = targetsRes.length
    stats.value.orderCount = ordersRes.length

    // 本月新增
    const now = new Date()
    const thisMonth = now.getMonth()
    const thisYear = now.getFullYear()
    stats.value.monthOrders = ordersRes.filter(order => {
      const orderDate = new Date(order.created_at)
      return orderDate.getMonth() === thisMonth && orderDate.getFullYear() === thisYear
    }).length
  } catch (e) {
    console.error('加载统计数据失败:', e)
    alert('加载失败')
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_role')
  router.replace('/login')
}

const goToTargets = () => {
  router.push('/admin/targets')
}
const goToOrders = () => {
  router.push('/admin/orders')
}
const goToUpdateForm = () => {
  router.push('/admin/update-form')
}

onMounted(() => {
  checkAuth()
  loadStats()
})
</script>

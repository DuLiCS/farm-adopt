<template>
  <view class="container">
    <!-- 顶部导航栏 -->
    <view class="header">
      <text class="title">管理后台</text>
      <view class="logout-btn" @click="handleLogout">退出</view>
    </view>

    <!-- 数据概览 -->
    <view class="stats-grid">
      <view class="stat-card">
        <text class="stat-value">{{ stats.targetCount }}</text>
        <text class="stat-label">认养对象</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ stats.orderCount }}</text>
        <text class="stat-label">总订单数</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ stats.monthOrders }}</text>
        <text class="stat-label">本月新增</text>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-item" @click="goToTargets">
        <view class="menu-icon" style="background-color: #e8f5e9;">🌿</view>
        <view class="menu-content">
          <text class="menu-title">认养对象管理</text>
          <text class="menu-desc">查看和管理认养地块</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @click="goToOrders">
        <view class="menu-icon" style="background-color: #fff3e0;">📦</view>
        <view class="menu-content">
          <text class="menu-title">订单管理</text>
          <text class="menu-desc">查看和创建订单</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @click="goToUpdateForm">
        <view class="menu-icon" style="background-color: #e3f2fd;">📝</view>
        <view class="menu-content">
          <text class="menu-title">发布更新</text>
          <text class="menu-desc">发布农场动态和图片</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getAdminTargets, getAdminOrders } from '@/api/admin.js'

export default {
  data() {
    return {
      stats: {
        targetCount: 0,
        orderCount: 0,
        monthOrders: 0
      },
      loading: false
    }
  },
  onLoad() {
    this.checkAuth()
    this.loadStats()
  },
  onShow() {
    this.loadStats()
  },
  methods: {
    checkAuth() {
      const token = uni.getStorageSync('admin_token')
      if (!token) {
        uni.redirectTo({ url: '/pages/admin/login' })
      }
    },
    async loadStats() {
      this.loading = true
      try {
        // 并行加载数据
        const [targetsRes, ordersRes] = await Promise.all([
          getAdminTargets(),
          getAdminOrders()
        ])
        this.stats.targetCount = targetsRes.length
        this.stats.orderCount = ordersRes.length
        
        // 计算本月新增订单
        const now = new Date()
        const thisMonth = now.getMonth()
        const thisYear = now.getFullYear()
        this.stats.monthOrders = ordersRes.filter(order => {
          const orderDate = new Date(order.created_at)
          return orderDate.getMonth() === thisMonth && orderDate.getFullYear() === thisYear
        }).length
      } catch (e) {
        console.error('加载统计数据失败:', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    handleLogout() {
      uni.removeStorageSync('admin_token')
      uni.removeStorageSync('admin_role')
      uni.reLaunch({ url: '/pages/admin/login' })
    },
    goToTargets() {
      uni.navigateTo({ url: '/pages/admin/targets' })
    },
    goToOrders() {
      uni.navigateTo({ url: '/pages/admin/orders' })
    },
    goToUpdateForm() {
      uni.navigateTo({ url: '/pages/admin/update-form' })
    }
  }
}
</script>

<style scoped>
.container { padding: 24px; min-height: 100vh; box-sizing: border-box; background-color: #f5f5f0; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.title { font-size: 32rpx; font-weight: bold; color: #333; }
.logout-btn { color: #2d5a27; font-size: 28rpx; cursor: pointer; }

.stats-grid { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { flex: 1; background: #fff; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.stat-value { display: block; font-size: 48rpx; font-weight: bold; color: #2d5a27; margin-bottom: 8rpx; }
.stat-label { font-size: 24rpx; color: #999; }

.menu-section { background: #fff; border-radius: 12px; overflow: hidden; }
.menu-item { display: flex; align-items: center; padding: 24px; border-bottom: 1px solid #f0f0f0; cursor: pointer; }
.menu-item:last-child { border-bottom: none; }
.menu-icon { width: 64rpx; height: 64rpx; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 32rpx; margin-right: 16px; }
.menu-content { flex: 1; }
.menu-title { display: block; font-size: 30rpx; font-weight: 500; color: #333; margin-bottom: 4rpx; }
.menu-desc { font-size: 24rpx; color: #999; }
.menu-arrow { font-size: 48rpx; color: #bbb; }
</style>

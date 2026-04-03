<template>
  <div class="dashboard">
    <h2>数据概览</h2>
    <div class="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.activeOrders }}</div>
        <div class="stat-label">守候中订单</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.orderCount }}</div>
        <div class="stat-label">总订单数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.monthOrders }}</div>
        <div class="stat-label">本月新增</div>
      </div>
      <div class="stat-card highlight">
        <div class="stat-value">¥{{ stats.totalRevenue }}</div>
        <div class="stat-label">累计收入（元）</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.availableTargets }}</div>
        <div class="stat-label">待认养对象</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.pendingDrafts }}</div>
        <div class="stat-label">待审核日志</div>
      </div>
    </div>

    <div class="recent-section" v-if="recentOrders.length">
      <h3>最近订单</h3>
      <table class="recent-table">
        <thead>
          <tr><th>用户</th><th>对象</th><th>套餐</th><th>状态</th><th>时间</th></tr>
        </thead>
        <tbody>
          <tr v-for="o in recentOrders" :key="o.id">
            <td>{{ o.user?.phone || '-' }}</td>
            <td>{{ o.target?.code || '-' }}</td>
            <td>{{ o.plan_type }}</td>
            <td><span :class="'badge-' + o.status">{{ statusLabel(o.status) }}</span></td>
            <td>{{ formatDate(o.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import { API_BASE } from '../config.js'

const stats = ref({
  activeOrders: 0, orderCount: 0, monthOrders: 0,
  totalRevenue: 0, availableTargets: 0, pendingDrafts: 0
})
const recentOrders = ref([])

const statusLabel = (s) => ({ active: '进行中', expired: '已过期', cancelled: '已取消' }[s] || s)
const formatDate = (d) => d ? d.substring(0, 10) : '-'

onMounted(async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const [targets, orders, draftsRes] = await Promise.all([
      api.getTargets(),
      api.getOrders(),
      fetch(`${API_BASE}/admin/updates/drafts`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json())
    ])

    const now = new Date()
    const thisMonth = now.getMonth()
    const thisYear = now.getFullYear()

    stats.value.orderCount = orders.length
    stats.value.activeOrders = orders.filter(o => o.status === 'active').length
    stats.value.monthOrders = orders.filter(o => {
      const d = new Date(o.created_at)
      return d.getMonth() === thisMonth && d.getFullYear() === thisYear
    }).length
    stats.value.totalRevenue = Math.round(
      orders.filter(o => o.status !== 'cancelled')
        .reduce((sum, o) => sum + (Number(o.price) || 0), 0)
    )
    stats.value.availableTargets = targets.filter(t => t.current_status === 'active').length
    stats.value.pendingDrafts = Array.isArray(draftsRes) ? draftsRes.length : 0

    recentOrders.value = [...orders]
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5)
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.dashboard h2 { margin: 0 0 24px; font-size: 20px; color: #333; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 32px; }
.stat-card { background: white; border-radius: 12px; padding: 24px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.stat-card.highlight { background: linear-gradient(135deg, #2d5a27, #4a7c3f); }
.stat-card.highlight .stat-value, .stat-card.highlight .stat-label { color: white; }
.stat-value { font-size: 32px; font-weight: bold; color: #2d5a27; }
.stat-label { font-size: 13px; color: #999; margin-top: 8px; }
.recent-section h3 { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 16px; }
.recent-table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.recent-table th, .recent-table td { padding: 10px 16px; text-align: left; font-size: 14px; border-bottom: 1px solid #f0f0f0; }
.recent-table th { background: #f5f5f0; font-weight: 500; color: #666; }
.recent-table tr:last-child td { border-bottom: none; }
.badge-active { background: #e6f7e6; color: #2d5a27; padding: 2px 10px; border-radius: 999px; font-size: 12px; }
.badge-expired { background: #fde8e8; color: #c0392b; padding: 2px 10px; border-radius: 999px; font-size: 12px; }
.badge-cancelled { background: #f5f5f5; color: #999; padding: 2px 10px; border-radius: 999px; font-size: 12px; }
</style>
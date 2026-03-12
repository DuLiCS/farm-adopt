<template>
  <div class="dashboard">
    <h2>数据概览</h2>
    <div class="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.targetCount }}</div>
        <div class="stat-label">山南对象</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.orderCount }}</div>
        <div class="stat-label">总订单数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.monthOrders }}</div>
        <div class="stat-label">本月新增</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.recentUpdates }}</div>
        <div class="stat-label">最近更新</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const stats = ref({
  targetCount: 0,
  orderCount: 0,
  monthOrders: 0,
  recentUpdates: 0
})

onMounted(async () => {
  try {
    const [targets, orders, updates] = await Promise.all([
      api.getTargets(),
      api.getOrders(),
      api.getUpdates()
    ])

    stats.value.targetCount = targets.length
    stats.value.orderCount = orders.length

    const now = new Date()
    const thisMonth = now.getMonth()
    const thisYear = now.getFullYear()
    stats.value.monthOrders = orders.filter(o => {
      const d = new Date(o.created_at)
      return d.getMonth() === thisMonth && d.getFullYear() === thisYear
    }).length

    stats.value.recentUpdates = updates.length
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.dashboard h2 {
  margin: 0 0 24px;
  font-size: 20px;
  color: #333;
}
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #2d5a27;
}
.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}
</style>
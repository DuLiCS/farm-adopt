<template>
  <div class="update-list-page">
    <h2>更新记录列表</h2>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="updates.length === 0" class="empty">暂无更新记录</div>
    <div v-else class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>认养对象</th>
            <th>类型</th>
            <th>描述摘要</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in updates" :key="u.id">
            <td>{{ u.target?.code || u.target_id }}</td>
            <td>{{ logTypeLabel(u.log_type) }}</td>
            <td class="desc-col">{{ truncate(u.description, 50) }}</td>
            <td>{{ formatDate(u.updated_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const updates = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    updates.value = await api.getUpdates()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

const logTypeLabel = (t) => ({
  daily: '日常',
  solar_term: '节气',
  harvest: '收获',
  delivery: '配送'
}[t] || t)

const truncate = (str, len) => {
  if (!str) return '-'
  return str.length > len ? str.substring(0, len) + '...' : str
}

const formatDate = (d) => {
  if (!d) return '-'
  return d.replace('T', ' ').substring(0, 19)
}
</script>

<style scoped>
.update-list-page {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
h2 { margin: 0 0 16px; font-size: 18px; }
.loading, .empty { text-align: center; padding: 40px; color: #999; }
.table { width: 100%; border-collapse: collapse; }
.th, .td { padding: 12px 16px; text-align: left; font-size: 14px; }
.th { background: #f5f5f5; font-weight: 600; color: #666; border-bottom: 1px solid #eee; }
.td { border-bottom: 1px solid #f0f0f0; }
.tr:last-child .td { border-bottom: none; }
.desc-col { max-width: 300px; }
</style>
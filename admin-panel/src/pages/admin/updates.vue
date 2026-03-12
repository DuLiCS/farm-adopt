<template>
  <div class="container">
    <div class="header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <div class="title" style="font-size: 24px; font-weight: bold; color: #333;">更新记录</div>
    </div>

    <div v-if="loading" style="text-align: center; padding: 60px 0; color: #999;">加载中...</div>
    <div v-else-if="updates.length === 0" style="text-align: center; padding: 60px 0; color: #999;">暂无更新记录</div>

    <div v-else class="updates-list" style="display: flex; flex-direction: column; gap: 16px;">
      <div v-for="update in updates" :key="update.id" class="update-card" style="background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <div class="update-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div class="target-info" style="font-weight: bold; color: #2d5a27;">
            对象：{{ getTargetCode(update.target_id) }}
          </div>
          <div class="update-meta" style="font-size: 12px; color: #999;">
            {{ formatDate(update.created_at) }} · {{ getLogTypeLabel(update.log_type) }}
          </div>
        </div>
        <div class="update-description" style="margin-bottom: 12px; line-height: 1.6; color: #333;">
          {{ update.description }}
        </div>
        <div v-if="update.image_urls && update.image_urls.length" class="update-images" style="display: flex; flex-wrap: wrap; gap: 8px;">
          <img v-for="(url, idx) in update.image_urls" :key="idx" :src="url" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px;" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAdminUpdates } from '@/api/admin.js'
import { getAdminTargets } from '@/api/admin.js'

const router = useRouter()
const updates = ref([])
const targets = ref([])
const loading = ref(false)

const checkAuth = () => {
  const role = localStorage.getItem('admin_role')
  if (role !== 'admin') router.replace('/login')
}

const loadData = async () => {
  loading.value = true
  try {
    const [updatesRes, targetsRes] = await Promise.all([
      getAdminUpdates(),
      getAdminTargets()
    ])
    updates.value = updatesRes.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    targets.value = targetsRes
  } catch (e) {
    console.error('加载失败:', e)
    alert('加载失败')
  } finally {
    loading.value = false
  }
}

const getTargetCode = (targetId) => {
  const t = targets.value.find(tt => tt.id === targetId)
  return t ? t.code : '-'
}
const getLogTypeLabel = (type) => {
  const labels = { daily: '日常更新', solar_term: '节气记录', harvest: '收获通知', delivery: '配送通知' }
  return labels[type] || type
}
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.split('T')[0]
}

onMounted(() => {
  checkAuth()
  loadData()
})
</script>

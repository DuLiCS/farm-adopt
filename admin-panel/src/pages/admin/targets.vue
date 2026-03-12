<template>
  <div class="container">
    <!-- 顶部导航 -->
    <div class="header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <div class="title" style="font-size: 24px; font-weight: bold; color: #333;">认养对象管理</div>
      <button class="btn-add" style="background-color: #2d5a27; color: #fff; border: none; border-radius: 8px; padding: 8px 24px; font-size: 16px; cursor: pointer;" @click="showAddModal">新增</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading" style="text-align: center; padding: 60px 0; color: #999; font-size: 16px;">加载中...</div>

    <!-- 空状态 -->
    <div v-else-if="targets.length === 0" class="empty" style="text-align: center; padding: 60px 0; color: #999; font-size: 16px;">暂无认养对象</div>

    <!-- 表格 -->
    <div v-else class="table-container" style="background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
      <div class="table-header" style="display: flex; background-color: #f5f5f5; padding: 16px; font-weight: bold; font-size: 14px; color: #666; border-bottom: 1px solid #eee;">
        <div class="col-code" style="width: 20%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">编号</div>
        <div class="col-type" style="width: 20%;">类型</div>
        <div class="col-status" style="width: 20%;">状态</div>
        <div class="col-location" style="width: 40%;">位置</div>
      </div>
      <div class="table-body" style="max-height: 800px; overflow-y: auto;">
        <div v-for="item in targets" :key="item.id" class="table-row" style="display: flex; padding: 16px; border-bottom: 1px solid #f0f0f0; font-size: 14px;">
          <div class="col-code" style="width: 20%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ item.code }}</div>
          <div class="col-type" style="width: 20%;">{{ getTypeLabel(item.type) }}</div>
          <div class="col-status" style="width: 20%;" :style="{ color: getStatusColor(item.current_status) }">{{ getStatusLabel(item.current_status) }}</div>
          <div class="col-location" style="width: 40%;">{{ item.location_desc || '-' }}</div>
        </div>
      </div>
    </div>

    <!-- 新增弹窗 -->
    <div v-if="showModal" class="modal-overlay" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;" @click="hideAddModal">
      <div class="modal-content" style="width: 80%; max-width: 600px; background: #fff; border-radius: 16px; padding: 24px; max-height: 90vh; overflow-y: auto;" @click.stop>
        <div class="modal-title" style="font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 24px; color: #333;">新增认养对象</div>
        <div class="form-group" style="margin-bottom: 20px;">
          <label class="label" style="display: block; font-size: 16px; color: #666; margin-bottom: 8px;">编号 *</label>
          <input class="input" type="text" v-model="form.code" placeholder="如: TEA-001" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 16px; background: #fff; box-sizing: border-box;" />
        </div>
        <div class="form-group" style="margin-bottom: 20px;">
          <label class="label" style="display: block; font-size: 16px; color: #666; margin-bottom: 8px;">类型 *</label>
          <select v-model="form.type" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 16px; background: #fff; box-sizing: border-box;" @change="onTypeChange">
            <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom: 20px;">
          <label class="label" style="display: block; font-size: 16px; color: #666; margin-bottom: 8px;">状态</label>
          <select v-model="form.current_status" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 16px; background: #fff; box-sizing: border-box;" @change="onStatusChange">
            <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom: 20px;">
          <label class="label" style="display: block; font-size: 16px; color: #666; margin-bottom: 8px;">位置描述</label>
          <input class="input" type="text" v-model="form.location_desc" placeholder="如: 大棚A区-01号" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 16px; background: #fff; box-sizing: border-box;" />
        </div>
        <div class="form-group" style="margin-bottom: 20px;">
          <label class="label" style="display: block; font-size: 16px; color: #666; margin-bottom: 8px;">摄像头ID</label>
          <input class="input" type="text" v-model="form.camera_id" placeholder="可选" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 16px; background: #fff; box-sizing: border-box;" />
        </div>
        <div v-if="error" class="error-msg" style="color: #c0392b; font-size: 14px; margin-bottom: 16px; text-align: center;">{{ error }}</div>
        <div class="modal-actions" style="display: flex; gap: 12px; margin-top: 24px;">
          <button class="btn-cancel" style="flex: 1; border: none; border-radius: 8px; padding: 12px; font-size: 16px; background: #f0f0f0; color: #666; cursor: pointer;" @click="hideAddModal">取消</button>
          <button class="btn-confirm" style="flex: 1; border: none; border-radius: 8px; padding: 12px; font-size: 16px; background: #2d5a27; color: #fff; cursor: pointer;" @click="handleSubmit">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAdminTargets, createAdminTarget } from '@/api/admin.js'

const router = useRouter()
const targets = ref([])
const loading = ref(false)
const showModal = ref(false)
const form = ref({
  code: '',
  type: 'tea',
  current_status: 'active',
  location_desc: '',
  camera_id: ''
})
const error = ref('')

const typeOptions = [
  { label: '茶饮 (tea)', value: 'tea' },
  { label: '水培 (hydroponic)', value: 'hydroponic' }
]
const statusOptions = [
  { label: '可认养 (active)', value: 'active' },
  { label: '维护中 (maintenance)', value: 'maintenance' },
  { label: '已收获 (harvested)', value: 'harvested' },
  { label: '不可用 (unavailable)', value: 'unavailable' }
]

const checkAuth = () => {
  const role = localStorage.getItem('admin_role')
  if (role !== 'admin') {
    router.replace('/login')
  }
}

const loadTargets = async () => {
  loading.value = true
  try {
    const res = await getAdminTargets()
    targets.value = res
  } catch (e) {
    console.error('加载认养对象失败:', e)
    alert('加载失败')
  } finally {
    loading.value = false
  }
}

const getTypeLabel = (type) => {
  const opt = typeOptions.find(o => o.value === type)
  return opt ? opt.label : type
}
const getStatusLabel = (status) => {
  const opt = statusOptions.find(o => o.value === status)
  return opt ? opt.label : status
}
const getStatusColor = (status) => {
  const colors = {
    active: '#4caf50',
    maintenance: '#ff9800',
    harvested: '#2196f3',
    unavailable: '#f44336'
  }
  return colors[status] || '#333'
}
const onTypeChange = (e) => {
  form.value.type = e.target.value
}
const onStatusChange = (e) => {
  form.value.current_status = e.target.value
}
const showAddModal = () => {
  form.value = { code: '', type: 'tea', current_status: 'active', location_desc: '', camera_id: '' }
  error.value = ''
  showModal.value = true
}
const hideAddModal = () => {
  showModal.value = false
}
const handleSubmit = async () => {
  if (!form.value.code) {
    error.value = '请输入编号'
    return
  }
  if (!form.value.type) {
    error.value = '请选择类型'
    return
  }

  loading.value = true
  try {
    await createAdminTarget(form.value)
    alert('创建成功')
    hideAddModal()
    await loadTargets()
  } catch (e) {
    error.value = e.message || '创建失败'
    alert(error.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkAuth()
  loadTargets()
})
</script>

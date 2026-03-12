<template>
  <div class="container">
    <div class="header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <div class="title" style="font-size: 24px; font-weight: bold; color: #333;">订单管理</div>
      <button style="background-color: #2d5a27; color: #fff; border: none; border-radius: 8px; padding: 8px 24px; font-size: 16px; cursor: pointer;" @click="showAddModal">手动创建</button>
    </div>

    <div v-if="loading" style="text-align: center; padding: 60px 0; color: #999;">加载中...</div>
    <div v-else-if="orders.length === 0" style="text-align: center; padding: 60px 0; color: #999;">暂无订单</div>

    <div v-else class="table-container" style="background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
      <div class="table-header" style="display: flex; background: #f5f5f5; padding: 16px; font-weight: bold; font-size: 14px; color: #666; border-bottom: 1px solid #eee;">
        <div class="col-phone" style="width: 20%;">手机号</div>
        <div class="col-target" style="width: 20%;">认养对象</div>
        <div class="col-plan" style="width: 20%;">套餐</div>
        <div class="col-expire" style="width: 20%;">到期日</div>
        <div class="col-status" style="width: 20%;">状态</div>
      </div>
      <div class="table-body" style="max-height: 800px; overflow-y: auto;">
        <div v-for="order in orders" :key="order.id" class="table-row" style="display: flex; padding: 16px; border-bottom: 1px solid #f0f0f0; font-size: 14px;">
          <div class="col-phone" style="width: 20%;">{{ order.user?.phone || '-' }}</div>
          <div class="col-target" style="width: 20%;">{{ order.target?.code || '-' }}</div>
          <div class="col-plan" style="width: 20%;">{{ getPlanLabel(order.plan_type) }}</div>
          <div class="col-expire" style="width: 20%;">{{ formatDate(order.expire_date) }}</div>
          <div class="col-status" style="width: 20%;" :style="{ color: getStatusColor(order.status) }">{{ getStatusLabel(order.status) }}</div>
        </div>
      </div>
    </div>

    <!-- 新增订单弹窗 -->
    <div v-if="showModal" class="modal-overlay" style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;" @click="hideAddModal">
      <div class="modal-content" style="width: 90%; max-width: 600px; background: #fff; border-radius: 12px; padding: 24px; max-height: 90vh; overflow-y: auto;" @click.stop>
        <h3 style="margin: 0 0 16px; font-size: 18px;">手动创建订单</h3>
        <div style="margin-bottom: 16px;">
          <label style="display: block; margin-bottom: 8px; font-size: 14px; color: #666;">用户 *</label>
          <select v-model="form.user_id" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; box-sizing: border-box;">
            <option value="">请选择用户</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.phone }} ({{ u.nickname || '未命名' }})</option>
          </select>
        </div>
        <div style="margin-bottom: 16px;">
          <label style="display: block; margin-bottom: 8px; font-size: 14px; color: #666;">认养对象 *</label>
          <select v-model="form.target_id" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; box-sizing: border-box;">
            <option value="">请选择对象</option>
            <option v-for="t in targets" :key="t.id" :value="t.id">{{ t.code }} - {{ t.location_desc }}</option>
          </select>
        </div>
        <div style="margin-bottom: 16px;">
          <label style="display: block; margin-bottom: 8px; font-size: 14px; color: #666;">套餐类型 *</label>
          <select v-model="form.plan_type" @change="updatePrice" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; box-sizing: border-box;">
            <option value="trial">体验套餐 (trial)</option>
            <option value="season">季度套餐 (season)</option>
            <option value="annual">年度套餐 (annual)</option>
          </select>
        </div>
        <div style="margin-bottom: 16px;">
          <label style="display: block; margin-bottom: 8px; font-size: 14px; color: #666;">到期日期 *</label>
          <input type="date" v-model="form.expire_date" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; box-sizing: border-box;" />
        </div>
        <div v-if="error" style="color: #c0392b; font-size: 14px; margin-bottom: 16px;">{{ error }}</div>
        <div style="display: flex; gap: 12px;">
          <button style="flex: 1; background: #f0f0f0; border: none; border-radius: 8px; padding: 12px; cursor: pointer;" @click="hideAddModal">取消</button>
          <button style="flex: 1; background: #2d5a27; color: #fff; border: none; border-radius: 8px; padding: 12px; cursor: pointer;" @click="handleSubmit">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAdminOrders, getAdminTargets, getAdminUsers, createAdminOrder } from '@/api/admin.js'

const router = useRouter()
const orders = ref([])
const targets = ref([])
const users = ref([])
const loading = ref(false)
const showModal = ref(false)
const form = ref({
  user_id: '',
  target_id: '',
  plan_type: 'basic',
  price: 666,
  expire_date: ''
})
const error = ref('')

const checkAuth = () => {
  const role = localStorage.getItem('admin_role')
  if (role !== 'admin') router.replace('/login')
}

const loadData = async () => {
  loading.value = true
  try {
    let ordersRes, targetsRes, usersRes
    try {
      ordersRes = await getAdminOrders()
    } catch (e) {
      console.error('getAdminOrders failed:', e)
      ordersRes = []
    }
    try {
      targetsRes = await getAdminTargets()
    } catch (e) {
      console.error('getAdminTargets failed:', e)
      targetsRes = []
    }
    try {
      usersRes = await getAdminUsers()
    } catch (e) {
      console.error('getAdminUsers failed:', e)
      usersRes = []
    }
    console.log('Loaded:', { orders: ordersRes, targets: targetsRes, users: usersRes })
    orders.value = ordersRes
    targets.value = targetsRes
    users.value = usersRes
  } finally {
    loading.value = false
  }
}

const getTargetCode = (target) => {
  const t = targets.value.find(tt => tt.id === target?.id || tt.id === target)
  return t ? t.code : '-'
}
const getPlanLabel = (plan) => {
  const labels = { trial: '体验套餐', season: '季度套餐', annual: '年度套餐' }
  return labels[plan] || plan
}
const getStatusLabel = (status) => {
  const labels = { active: '生效中', expired: '已过期', cancelled: '已取消' }
  return labels[status] || status
}
const getStatusColor = (status) => {
  const colors = { active: '#4caf50', expired: '#999', cancelled: '#f44336' }
  return colors[status] || '#333'
}
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.split('T')[0]
}

const PLANS = {
  trial: 99,
  season: 666,
  annual: 1888
}

const updatePrice = () => {
  form.value.price = PLANS[form.value.plan_type] || 666
}

const showAddModal = () => {
  form.value = { user_id: '', target_id: '', plan_type: 'basic', expire_date: '', price: PLANS.basic }
  error.value = ''
  showModal.value = true
}
const hideAddModal = () => {
  showModal.value = false
}

const handleSubmit = async () => {
  if (!form.value.user_id || !form.value.target_id || !form.value.expire_date) {
    error.value = '请填写所有必填字段'
    return
  }
  loading.value = true
  try {
    // 找到选择的用户手机号
    const selectedUser = users.value.find(u => u.id === parseInt(form.value.user_id))
    if (!selectedUser) {
      error.value = '请选择有效的用户'
      return
    }
    const payload = {
      user_phone: selectedUser.phone,
      target_id: parseInt(form.value.target_id, 10),
      plan_type: form.value.plan_type,
      price: form.value.price,
      expire_date: form.value.expire_date
    }
    await createAdminOrder(payload)
    alert('创建成功')
    hideAddModal()
    await loadData()
  } catch (e) {
    error.value = e.message || '创建失败'
    alert(error.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkAuth()
  loadData()
})
</script>

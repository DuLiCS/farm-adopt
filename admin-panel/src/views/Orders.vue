<template>
  <div class="orders-page">
    <h2>订单管理</h2>
    <button class="btn-add" @click="showModal = true">手动创建</button>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="orders.length === 0" class="empty">暂无订单</div>
    <div v-else class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>用户手机</th>
            <th>山南对象</th>
            <th>套餐</th>
            <th>到期日</th>
            <th>收货人</th>
            <th>手机</th>
            <th>收货地址</th>
            <th>备注</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in orders" :key="o.id">
            <td>{{ o.user?.phone || o.user_id }}</td>
            <td>{{ o.target?.code || o.target_id }}</td>
            <td>{{ planLabel(o.plan_type) }}</td>
            <td>{{ formatDate(o.expire_date) }}</td>
            <td :style="{ color: statusColor(o.status) }">{{ statusLabel(o.status) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增订单弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click="showModal = false">
      <div class="modal" @click.stop>
        <h3>手动创建订单</h3>
        <div class="form-group">
          <label>用户 *</label>
          <select v-model="form.user_phone">
            <option value="">请选择用户</option>
            <option v-for="u in users" :key="u.id" :value="u.phone">
              {{ u.phone }} {{ u.nickname ? '(' + u.nickname + ')' : '' }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>山南对象 *</label>
          <select v-model="form.target_id">
            <option value="">请选择</option>
            <option v-for="t in targets" :key="t.id" :value="t.id">{{ t.code }} - {{ t.type }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>套餐类型 *</label>
          <select v-model="form.plan_type" @change="onPlanChange">
            <option value="trial">体验套餐 - 99元</option>
            <option value="season">季度套餐 - 666元</option>
            <option value="annual">年度套餐 - 1888元</option>
          </select>
        </div>
        <div class="form-group">
          <label>价格 (元) *</label>
          <input v-model.number="form.price" type="number" disabled />
        </div>
        <div class="form-group">
          <label>到期日 *</label>
          <input v-model="form.expire_date" type="date" />
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div class="actions">
          <button @click="showModal = false">取消</button>
          <button class="btn-primary" @click="handleSubmit">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const orders = ref([])
const targets = ref([])
const users = ref([])
const loading = ref(false)
const showModal = ref(false)
const form = ref({
  user_phone: '',
  target_id: '',
  plan_type: 'season',
  price: 666,
  expire_date: ''
})
const error = ref('')

const PLANS = { trial: 99, season: 666, annual: 1888 }

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const [ordersRes, targetsRes, usersRes] = await Promise.all([
      api.getOrders(),
      api.getTargets(),
      api.getUsers()
    ])
    orders.value = ordersRes
    targets.value = targetsRes
    users.value = usersRes
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const planLabel = (p) => ({ trial: '体验套餐', season: '季度套餐', annual: '年度套餐' }[p] || p)
const statusLabel = (s) => ({ active: '进行中', expired: '已过期', cancelled: '已取消' }[s] || s)
const statusColor = (s) => ({ active: '#4caf50', expired: '#f44336', cancelled: '#999' }[s] || '#333')
const formatDate = (d) => d ? d.substring(0, 10) : '-'

const onPlanChange = () => {
  form.value.price = PLANS[form.value.plan_type] || 0
  if (form.value.target_id) {
    const today = new Date()
    let expire = new Date()
    if (form.value.plan_type === 'trial') expire.setMonth(today.getMonth() + 1)
    else if (form.value.plan_type === 'season') expire.setMonth(today.getMonth() + 3)
    else expire.setFullYear(today.getFullYear() + 1)
    form.value.expire_date = expire.toISOString().substring(0, 10)
  }
}

const handleSubmit = async () => {
  error.value = ''
  if (!form.value.user_phone) { error.value = '请选择用户'; return }
  if (!form.value.target_id) { error.value = '请选择山南对象'; return }
  if (!form.value.expire_date) { error.value = '请选择到期日'; return }

  loading.value = true
  try {
    await api.createOrder({
      user_phone: form.value.user_phone,
      target_id: Number(form.value.target_id),
      plan_type: form.value.plan_type,
      price: form.value.price,
      expire_date: form.value.expire_date
    })
    showModal.value = false
    form.value = { user_phone: '', target_id: '', plan_type: 'season', price: 666, expire_date: '' }
    await loadData()
  } catch (e) {
    error.value = e.detail || '创建失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.orders-page {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
h2 { margin: 0 0 16px; font-size: 18px; }
.btn-add {
  background: #2d5a27;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 16px;
}
.loading, .empty { text-align: center; padding: 40px; color: #999; }
.table { width: 100%; border-collapse: collapse; }
.th, .td { padding: 12px 16px; text-align: left; font-size: 14px; }
.th { background: #f5f5f5; font-weight: 600; color: #666; border-bottom: 1px solid #eee; }
.td { border-bottom: 1px solid #f0f0f0; }
.tr:last-child .td { border-bottom: none; }

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
}
.modal h3 { margin: 0 0 16px; font-size: 18px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 14px; color: #666; }
.form-group input, .form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.error { color: #c0392b; font-size: 14px; margin-bottom: 12px; }
.actions { display: flex; gap: 12px; margin-top: 16px; }
.actions button { flex: 1; padding: 10px; border: none; border-radius: 6px; cursor: pointer; }
.actions button:first-child { background: #f0f0f0; color: #666; }
.actions .btn-primary { background: #2d5a27; color: white; }
</style>
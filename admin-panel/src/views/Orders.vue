<template>
  <div class="orders-page">
    <h2>订单管理</h2>
    <button class="btn-add" @click="openCreate">手动创建</button>

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
            <th>收货地址</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in orders" :key="o.id">
            <td>{{ o.user?.phone || o.user_id }}</td>
            <td>{{ o.target?.code || o.target_id }}</td>
            <td>{{ planLabel(o.plan_type) }}</td>
            <td>{{ formatDate(o.expire_date) }}</td>
            <td>{{ o.receiver_name || '-' }}</td>
            <td class="addr-col">{{ o.receiver_address || '-' }}</td>
            <td><span :class="'status-badge status-' + o.status">{{ statusLabel(o.status) }}</span></td>
            <td>
              <button class="btn-sm" @click="openEdit(o)">编辑</button>
            </td>
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
            <option v-for="t in targets" :key="t.id" :value="t.id">{{ t.code }} - {{ t.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>套餐 *</label>
          <select v-model="form.plan_key" @change="onPlanChange">
            <option value="">请选择套餐</option>
            <option v-for="p in plans" :key="p.plan_key" :value="p.plan_key">
              {{ p.name }} — ¥{{ (p.price / 100).toFixed(0) }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>价格 (元)</label>
          <input v-model.number="form.price" type="number" />
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

    <!-- 编辑订单弹窗 -->
    <div v-if="editOrder" class="modal-overlay" @click="editOrder = null">
      <div class="modal" @click.stop>
        <h3>编辑订单 #{{ editOrder.id }}</h3>
        <div class="form-group">
          <label>状态</label>
          <select v-model="editForm.status">
            <option value="active">进行中</option>
            <option value="expired">已过期</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>
        <div class="form-group">
          <label>到期日</label>
          <input v-model="editForm.expire_date" type="date" />
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div class="actions">
          <button @click="editOrder = null">取消</button>
          <button class="btn-primary" @click="handleEditSubmit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import { API_BASE } from '../config.js'

const orders = ref([])
const targets = ref([])
const users = ref([])
const plans = ref([])
const loading = ref(false)
const showModal = ref(false)
const editOrder = ref(null)
const form = ref({ user_phone: '', target_id: '', plan_key: '', price: 0, expire_date: '' })
const editForm = ref({ status: '', expire_date: '' })
const error = ref('')

onMounted(() => { loadData() })

const loadData = async () => {
  loading.value = true
  try {
    const [ordersRes, targetsRes, usersRes, plansRes] = await Promise.all([
      api.getOrders(),
      api.getTargets(),
      api.getUsers(),
      fetch(`${API_BASE}/api/plans/all`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` }
      }).then(r => r.json())
    ])
    orders.value = ordersRes
    targets.value = targetsRes
    users.value = usersRes
    plans.value = Array.isArray(plansRes) ? plansRes : []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const planLabel = (p) => {
  const found = plans.value.find(pl => pl.plan_key === p)
  if (found) return found.name
  const legacy = { trial: '体验套餐', season: '季度套餐', annual: '年度套餐',
    tea_basic: '茶树基础档', tea_standard: '茶树标准档', plant_basic: '植物季度' }
  return legacy[p] || p
}
const statusLabel = (s) => ({ active: '进行中', expired: '已过期', cancelled: '已取消' }[s] || s)
const formatDate = (d) => d ? d.substring(0, 10) : '-'

const openCreate = () => {
  error.value = ''
  form.value = { user_phone: '', target_id: '', plan_key: '', price: 0, expire_date: '' }
  showModal.value = true
}

const onPlanChange = () => {
  const plan = plans.value.find(p => p.plan_key === form.value.plan_key)
  if (plan) {
    form.value.price = plan.price / 100
    const today = new Date()
    let expire = new Date()
    if (plan.plan_key.includes('standard') || plan.plan_key === 'annual') {
      expire.setFullYear(today.getFullYear() + 1)
    } else {
      expire.setMonth(today.getMonth() + 3)
    }
    form.value.expire_date = expire.toISOString().substring(0, 10)
  }
}

const handleSubmit = async () => {
  error.value = ''
  if (!form.value.user_phone) { error.value = '请选择用户'; return }
  if (!form.value.target_id) { error.value = '请选择山南对象'; return }
  if (!form.value.plan_key) { error.value = '请选择套餐'; return }
  if (!form.value.expire_date) { error.value = '请填写到期日'; return }

  loading.value = true
  try {
    await api.createOrder({
      user_phone: form.value.user_phone,
      target_id: Number(form.value.target_id),
      plan_type: form.value.plan_key,
      price: Math.round(form.value.price * 100),
      expire_date: form.value.expire_date
    })
    showModal.value = false
    await loadData()
  } catch (e) {
    error.value = e.detail || '创建失败'
  } finally {
    loading.value = false
  }
}

const openEdit = (order) => {
  error.value = ''
  editOrder.value = order
  editForm.value = {
    status: order.status,
    expire_date: formatDate(order.expire_date)
  }
}

const handleEditSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    await api.updateOrder(editOrder.value.id, {
      status: editForm.value.status,
      expire_date: editForm.value.expire_date
    })
    editOrder.value = null
    await loadData()
  } catch (e) {
    error.value = e.detail || '保存失败'
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
.table th, .table td { padding: 10px 14px; text-align: left; font-size: 14px; border-bottom: 1px solid #f0f0f0; }
.table th { background: #f5f5f5; font-weight: 600; color: #666; border-bottom: 1px solid #eee; }
.table tr:last-child td { border-bottom: none; }
.addr-col { max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.status-badge { padding: 3px 10px; border-radius: 999px; font-size: 12px; }
.status-active { background: #e6f7e6; color: #2d5a27; }
.status-expired { background: #fde8e8; color: #c0392b; }
.status-cancelled { background: #f5f5f5; color: #999; }

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
.btn-sm { padding: 4px 12px; border-radius: 4px; border: 1px solid #ddd; cursor: pointer; font-size: 12px; background: #fff; }
.btn-sm:hover { background: #f5f5f5; }
</style>
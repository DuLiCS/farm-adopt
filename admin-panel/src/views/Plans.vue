<template>
  <div class="page">
    <div class="page-header">
      <h2>套餐管理</h2>
      <button class="btn-primary" @click="openCreate">+ 新增套餐</button>
    </div>

    <table class="table">
      <thead>
        <tr>
          <th>排序</th>
          <th>名称</th>
          <th>分类</th>
          <th>价格</th>
          <th>库存</th>
          <th>已售</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="plan in plans" :key="plan.id">
          <td>
            <input type="number" v-model.number="plan.sort_order" style="width:60px"
              @change="saveSort(plan)" />
          </td>
          <td>{{ plan.name }}</td>
          <td>{{ categoryLabel(plan.category) }}</td>
          <td>¥{{ (plan.price / 100).toFixed(0) }}</td>
          <td>{{ plan.stock === -1 ? "不限" : plan.stock }}</td>
          <td>{{ plan.sold_count }}</td>
          <td>
            <span :class="plan.is_active ? 'badge-on' : 'badge-off'">
              {{ plan.is_active ? "上架" : "下架" }}
            </span>
          </td>
          <td class="actions">
            <button class="btn-sm" @click="openEdit(plan)">编辑</button>
            <button class="btn-sm btn-danger" @click="toggleActive(plan)">
              {{ plan.is_active ? "下架" : "上架" }}
            </button>
            <button class="btn-sm btn-danger" @click="deletePlan(plan)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editingId ? "编辑套餐" : "新增套餐" }}</h3>
        <div class="form-group">
          <label>套餐标识（唯一key）</label>
          <input v-model="form.plan_key" :disabled="!!editingId" placeholder="如 tea_basic" />
        </div>
        <div class="form-group">
          <label>名称</label>
          <input v-model="form.name" />
        </div>
        <div class="form-group">
          <label>分类</label>
          <select v-model="form.category">
            <option value="tea">茶树</option>
            <option value="plant">植物</option>
            <option value="egg">鸡蛋</option>
            <option value="other">其他</option>
          </select>
        </div>
        <div class="form-group">
          <label>价格（元）</label>
          <input type="number" v-model.number="form.price_yuan" />
        </div>
        <div class="form-group">
          <label>一句话简介</label>
          <input v-model="form.description" />
        </div>
        <div class="form-group">
          <label>套餐详情（支持HTML富文本）</label>
          <textarea v-model="form.details" rows="6" placeholder="<ul><li>内容</li></ul>" />
        </div>
        <div class="form-group">
          <label>卡片标签（每行一个）</label>
          <textarea v-model="form.benefits_text" rows="3" placeholder="🌱 全年节气更新" />
        </div>
        <div class="form-group">
          <label>排序（数字越小越靠前）</label>
          <input type="number" v-model.number="form.sort_order" />
        </div>
        <div class="form-group">
          <label>库存（-1表示不限量）</label>
          <input type="number" v-model.number="form.stock" />
        </div>
        <div class="form-group">
          <label>状态</label>
          <select v-model="form.is_active">
            <option :value="true">上架</option>
            <option :value="false">下架</option>
          </select>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="submitForm">保存</button>
          <button class="btn-outline" @click="closeModal">取消</button>
        </div>
      </div>
    </div>
    <!-- 确认弹窗 -->
    <ConfirmModal
      :show="confirmState.show"
      :title="confirmState.title"
      :message="confirmState.message"
      confirmText="删除"
      :danger="true"
      @confirm="confirmState.resolve(true); confirmState.show = false"
      @cancel="confirmState.resolve(false); confirmState.show = false"
    />
    <AppToast :show="toast.show" :message="toast.message" :type="toast.type" />
  </div>
</template>

<script>
import { API_BASE } from '../config.js'
import ConfirmModal from '../components/ConfirmModal.vue'
import AppToast from '../components/AppToast.vue'

export default {
  components: { ConfirmModal, AppToast },
  data() {
    return {
      plans: [],
      showModal: false,
      editingId: null,
      confirmState: { show: false, title: '', message: '', resolve: null },
      toast: { show: false, message: '', type: 'success' },
      form: {
        plan_key: '',
        name: '',
        category: 'tea',
        price_yuan: 0,
        description: '',
        details: '',
        benefits_text: '',
        sort_order: 0,
        stock: -1,
        is_active: true
      }
    }
  },
  mounted() {
    this.fetchPlans()
  },
  methods: {
    token() {
      return localStorage.getItem('admin_token')
    },
    async fetchPlans() {
      const res = await fetch(`${API_BASE}/api/plans/all`, {
        headers: { Authorization: `Bearer ${this.token()}` }
      })
      this.plans = await res.json()
    },
    categoryLabel(cat) {
      return { tea: '茶树', plant: '植物', egg: '鸡蛋', other: '其他' }[cat] || cat
    },
    openCreate() {
      this.editingId = null
      this.form = {
        plan_key: '', name: '', category: 'tea',
        price_yuan: 0, description: '', details: '',
        benefits_text: '', sort_order: 0, stock: -1, is_active: true
      }
      this.showModal = true
    },
    openEdit(plan) {
      this.editingId = plan.id
      this.form = {
        plan_key: plan.plan_key,
        name: plan.name,
        category: plan.category,
        price_yuan: plan.price / 100,
        description: plan.description || '',
        details: plan.details || '',
        benefits_text: (plan.benefits || []).join('\n'),
        sort_order: plan.sort_order,
        stock: plan.stock,
        is_active: plan.is_active
      }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    async submitForm() {
      const body = {
        plan_key: this.form.plan_key,
        name: this.form.name,
        category: this.form.category,
        price: Math.round(this.form.price_yuan * 100),
        description: this.form.description,
        details: this.form.details,
        benefits: this.form.benefits_text.split('\n').map(s => s.trim()).filter(Boolean),
        sort_order: this.form.sort_order,
        stock: this.form.stock,
        is_active: this.form.is_active
      }
      const url = this.editingId
        ? `${API_BASE}/api/plans/${this.editingId}`
        : `${API_BASE}/api/plans`
      const method = this.editingId ? 'PUT' : 'POST'
      await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${this.token()}` },
        body: JSON.stringify(body)
      })
      this.closeModal()
      this.fetchPlans()
      this.showToast(this.editingId ? '保存成功' : '套餐已创建')
    },
    async toggleActive(plan) {
      await fetch(`${API_BASE}/api/plans/${plan.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${this.token()}` },
        body: JSON.stringify({ is_active: !plan.is_active })
      })
      this.fetchPlans()
    },
    async deletePlan(plan) {
      const confirmed = await new Promise(resolve => {
        this.confirmState = {
          show: true,
          title: `删除「${plan.name}」？`,
          message: '删除后无法恢复，已售订单不受影响',
          resolve
        }
      })
      if (!confirmed) return
      await fetch(`${API_BASE}/api/plans/${plan.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${this.token()}` }
      })
      this.showToast('已删除')
      this.fetchPlans()
    },
    showToast(message, type = 'success') {
      this.toast = { show: true, message, type }
      setTimeout(() => { this.toast.show = false }, 2500)
    },
    async saveSort(plan) {
      await fetch(`${API_BASE}/api/plans/${plan.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${this.token()}` },
        body: JSON.stringify({ sort_order: plan.sort_order })
      })
    }
  }
}
</script>

<style scoped>
.page { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-header h2 { margin: 0; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 10px 12px; border-bottom: 1px solid #eee; text-align: left; font-size: 14px; }
.table th { background: #f9f9f9; font-weight: 600; }
.actions { display: flex; gap: 8px; }
.badge-on { background: #e6f7e6; color: #2d5a27; padding: 2px 10px; border-radius: 999px; font-size: 12px; }
.badge-off { background: #f5f5f5; color: #999; padding: 2px 10px; border-radius: 999px; font-size: 12px; }
.btn-primary { background: #2d5a27; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-outline { background: #fff; color: #2d5a27; border: 1px solid #2d5a27; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-sm { padding: 4px 12px; border-radius: 4px; border: 1px solid #ddd; cursor: pointer; font-size: 12px; background: #fff; }
.btn-danger { color: #e53e3e; border-color: #e53e3e; }
.modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:999; }
.modal { background: #fff; border-radius: 12px; padding: 32px; width: 560px; max-height: 85vh; overflow-y: auto; }
.modal h3 { margin: 0 0 24px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; color: #666; margin-bottom: 6px; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; box-sizing: border-box; }
.modal-footer { display: flex; gap: 12px; margin-top: 24px; }
</style>

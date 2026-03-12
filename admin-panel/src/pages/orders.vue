<template>
  <view class="container">
    <!-- 顶部导航 -->
    <view class="header">
      <text class="title">订单管理</text>
      <button class="btn-add" @click="showAddModal">手动创建</button>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading">加载中...</view>

    <!-- 空状态 -->
    <view v-else-if="orders.length === 0" class="empty">
      <text>暂无订单</text>
    </view>

    <!-- 表格 -->
    <view v-else class="table-container">
      <view class="table-header">
        <text class="col-phone">手机号</text>
        <text class="col-target">认养对象</text>
        <text class="col-plan">套餐</text>
        <text class="col-expire">到期日</text>
        <text class="col-status">状态</text>
      </view>
      <scroll-view scroll-y class="table-body">
        <view v-for="order in orders" :key="order.id" class="table-row">
          <text class="col-phone">{{ getOrderUser(order) }}</text>
          <text class="col-target">{{ getTargetCode(order) }}</text>
          <text class="col-plan">{{ getPlanLabel(order.plan_type) }}</text>
          <text class="col-expire">{{ formatDate(order.expire_date) }}</text>
          <text class="col-status" :style="{ color: getStatusColor(order.status) }">
            {{ getStatusLabel(order.status) }}
          </text>
        </view>
      </scroll-view>
    </view>
  </view>

  <!-- 新增订单弹窗 -->
  <view v-if="showModal" class="modal-overlay" @click="hideAddModal">
    <view class="modal-content" @click.stop>
      <view class="modal-title">手动创建订单</view>
      
      <view class="form-group">
        <text class="label">用户手机号 *</text>
        <input class="input" v-model="form.user_phone" placeholder="请输入用户手机号" />
      </view>

      <view class="form-group">
        <text class="label">认养对象 *</text>
        <picker v-model="form.target_id" :range="targetOptions" range-key="label" @change="onTargetChange">
          <view class="picker">{{ getSelectedTargetLabel() || '请选择认养对象' }}</view>
        </picker>
      </view>

      <view class="form-group">
        <text class="label">套餐类型 *</text>
        <picker v-model="form.plan_type" :range="planOptions" range-key="label" @change="onPlanChange">
          <view class="picker">{{ getPlanLabel(form.plan_type) || '请选择套餐' }}</view>
        </picker>
      </view>

      <view class="form-group">
        <text class="label">价格 (元) *</text>
        <input class="input" v-model="form.price" type="digit" placeholder="自动计算，不可修改" disabled />
      </view>

      <view class="form-group">
        <text class="label">到期日 *</text>
        <picker v-model="form.expire_date" mode="date">
          <view class="picker">{{ form.expire_date || '请选择到期日' }}</view>
        </picker>
      </view>

      <view v-if="error" class="error-msg">{{ error }}</view>
      <view class="modal-actions">
        <button class="btn-cancel" @click="hideAddModal">取消</button>
        <button class="btn-confirm" @click="handleSubmit">确定</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getAdminOrders, createAdminOrder } from '@/api/admin.js'
import { getAdminTargets } from '@/api/admin.js'
import { PLANS } from '@/config.js'

export default {
  data() {
    return {
      orders: [],
      targets: [],
      loading: false,
      showModal: false,
      form: {
        user_phone: '',
        target_id: null,
        plan_type: 'season',
        price: 0,
        expire_date: ''
      },
      error: '',
      targetOptions: [],
      planOptions: [
        { label: '季度套餐 - 666元', value: 'season', price: 666 },
        { label: '年度套餐 - 1888元', value: 'annual', price: 1888 },
        { label: '体验套餐 - 99元', value: 'trial', price: 99 }
      ]
    }
  },
  onLoad() {
    this.checkAuth()
    this.loadData()
  },
  onShow() {
    this.loadData()
  },
  methods: {
    checkAuth() {
      const role = uni.getStorageSync('admin_role')
      if (role !== 'admin') {
        uni.redirectTo({ url: '/pages/admin/login' })
      }
    },
    async loadData() {
      this.loading = true
      try {
        const [ordersRes, targetsRes] = await Promise.all([
          getAdminOrders(),
          getAdminTargets()
        ])
        this.orders = ordersRes
        this.targets = targetsRes
        // 准备认养对象选项
        this.targetOptions = this.targets.map(t => ({
          label: `${t.code} - ${t.type} (${t.current_status})`,
          value: t.id,
          status: t.current_status
        }))
      } catch (e) {
        console.error('加载数据失败:', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    getOrderUser(order) {
      // 这里需要关联查询用户信息，暂时返回占位
      return `用户ID: ${order.user_id || '待定'}`
    },
    getTargetCode(order) {
      const target = this.targets.find(t => t.id === order.target_id)
      return target ? target.code : '未知'
    },
    getPlanLabel(planType) {
      const plan = this.planOptions.find(p => p.value === planType)
      return plan ? plan.label.split(' - ')[0] : planType
    },
    getStatusLabel(status) {
      const labels = {
        active: '进行中',
        expired: '已过期',
        cancelled: '已取消'
      }
      return labels[status] || status
    },
    getStatusColor(status) {
      const colors = {
        active: '#4caf50',
        expired: '#f44336',
        cancelled: '#999'
      }
      return colors[status] || '#333'
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return dateStr
    },
    onTargetChange(e) {
      const targetId = this.targetOptions[e.detail.value].value
      this.form.target_id = targetId
      
      // 检查对象状态
      const target = this.targets.find(t => t.id === targetId)
      if (target && target.current_status !== 'active') {
        uni.showToast({ title: '该对象暂不可认养', icon: 'none' })
        this.form.target_id = null
        return
      }
      
      // 自动设置价格
      const plan = this.planOptions.find(p => p.value === this.form.plan_type)
      if (plan) {
        this.form.price = plan.price
      }
      
      // 计算默认到期日
      this.calculateExpireDate()
    },
    onPlanChange(e) {
      const plan = this.planOptions[e.detail.value]
      this.form.plan_type = plan.value
      this.form.price = plan.price
      this.calculateExpireDate()
    },
    calculateExpireDate() {
      if (!this.form.target_id) return
      const today = new Date()
      let expireDate = new Date()
      if (this.form.plan_type === 'trial') {
        expireDate.setMonth(today.getMonth() + 1)
      } else if (this.form.plan_type === 'season') {
        expireDate.setMonth(today.getMonth() + 3)
      } else if (this.form.plan_type === 'annual') {
        expireDate.setFullYear(today.getFullYear() + 1)
      }
      this.form.expire_date = this.formatDateISO(expireDate)
    },
    formatDateISO(date) {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },
    getSelectedTargetLabel() {
      if (!this.form.target_id) return ''
      const opt = this.targetOptions.find(o => o.value === this.form.target_id)
      return opt ? opt.label : ''
    },
    showAddModal() {
      this.form = {
        user_phone: '',
        target_id: null,
        plan_type: 'season',
        price: 0,
        expire_date: ''
      }
      this.error = ''
      this.showModal = true
    },
    hideAddModal() {
      this.showModal = false
    },
    async handleSubmit() {
      if (!this.form.user_phone) {
        this.error = '请输入用户手机号'
        return
      }
      if (!this.form.target_id) {
        this.error = '请选择认养对象'
        return
      }
      if (!this.form.plan_type) {
        this.error = '请选择套餐类型'
        return
      }
      if (!this.form.expire_date) {
        this.error = '请选择到期日'
        return
      }
      if (!this.form.price || this.form.price <= 0) {
        this.error = '价格必须大于0'
        return
      }

      this.loading = true
      try {
        await createAdminOrder({
          user_phone: this.form.user_phone,
          target_id: this.form.target_id,
          plan_type: this.form.plan_type,
          price: this.form.price,
          expire_date: this.form.expire_date
        })
        uni.showToast({ title: '订单创建成功', icon: 'success' })
        this.hideAddModal()
        this.loadData()
      } catch (e) {
        this.error = e.message || '创建失败'
        uni.showToast({ title: this.error, icon: 'none' })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.container { padding: 24px; min-height: 100vh; box-sizing: border-box; background-color: #f5f5f0; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.title { font-size: 32rpx; font-weight: bold; color: #333; }
.btn-add { background-color: #2d5a27; color: #fff; border: none; border-radius: 8px; padding: 8px 24px; font-size: 28rpx; }
.loading, .empty { text-align: center; padding: 60px 0; color: #999; font-size: 28rpx; }

.table-container { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.table-header { display: flex; background-color: #f5f5f5; padding: 16px; font-weight: bold; font-size: 24rpx; color: #666; border-bottom: 1px solid #eee; }
.table-body { max-height: 800rpx; }
.table-row { display: flex; padding: 16px; border-bottom: 1px solid #f0f0f0; font-size: 24rpx; align-items: center; }
.table-row:last-child { border-bottom: none; }
.col-phone { width: 18%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-target { width: 18%; }
.col-plan { width: 18%; }
.col-expire { width: 18%; }
.col-status { width: 18%; text-align: center; }

/* 弹窗 */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { width: 85%; max-width: 650rpx; background: #fff; border-radius: 16px; padding: 24px; max-height: 90vh; overflow-y: auto; }
.modal-title { font-size: 32rpx; font-weight: bold; text-align: center; margin-bottom: 24px; color: #333; }
.form-group { margin-bottom: 20px; }
.label { display: block; font-size: 28rpx; color: #666; margin-bottom: 8px; }
.input, .picker { width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 28rpx; background: #fff; min-height: 40px; box-sizing: border-box; }
.picker { line-height: 40px; }
.input:disabled { background: #f5f5f5; color: #999; }
.error-msg { color: #c0392b; font-size: 24rpx; margin-bottom: 16px; text-align: center; }
.modal-actions { display: flex; gap: 12px; margin-top: 24px; }
.btn-cancel, .btn-confirm { flex: 1; border: none; border-radius: 8px; padding: 12px; font-size: 28rpx; }
.btn-cancel { background: #f0f0f0; color: #666; }
.btn-confirm { background: #2d5a27; color: #fff; }
</style>

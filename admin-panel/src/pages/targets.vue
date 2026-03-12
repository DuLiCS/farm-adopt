<template>
  <view class="container">
    <!-- 顶部导航 -->
    <view class="header">
      <text class="title">认养对象管理</text>
      <button class="btn-add" @click="showAddModal">新增</button>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading">加载中...</view>

    <!-- 空状态 -->
    <view v-else-if="targets.length === 0" class="empty">
      <text>暂无认养对象</text>
    </view>

    <!-- 表格 -->
    <view v-else class="table-container">
      <view class="table-header">
        <text class="col-code">编号</text>
        <text class="col-type">类型</text>
        <text class="col-status">状态</text>
        <text class="col-location">位置</text>
      </view>
      <scroll-view scroll-y class="table-body">
        <view v-for="item in targets" :key="item.id" class="table-row">
          <text class="col-code">{{ item.code }}</text>
          <text class="col-type">{{ getTypeLabel(item.type) }}</text>
          <text class="col-status" :style="{ color: getStatusColor(item.current_status) }">
            {{ getStatusLabel(item.current_status) }}
          </text>
          <text class="col-location">{{ item.location_desc || '-' }}</text>
        </view>
      </scroll-view>
    </view>
  </view>

  <!-- 新增弹窗 -->
  <view v-if="showModal" class="modal-overlay" @click="hideAddModal">
    <view class="modal-content" @click.stop>
      <view class="modal-title">新增认养对象</view>
      <view class="form-group">
        <text class="label">编号 *</text>
        <input class="input" v-model="form.code" placeholder="如: TEA-001" />
      </view>
      <view class="form-group">
        <text class="label">类型 *</text>
        <picker v-model="form.type" :range="typeOptions" range-key="label" @change="onTypeChange">
          <view class="picker">{{ getTypeLabel(form.type) || '请选择类型' }}</view>
        </picker>
      </view>
      <view class="form-group">
        <text class="label">状态</text>
        <picker v-model="form.current_status" :range="statusOptions" range-key="label" @change="onStatusChange">
          <view class="picker">{{ getStatusLabel(form.current_status) || '请选择状态' }}</view>
        </picker>
      </view>
      <view class="form-group">
        <text class="label">位置描述</text>
        <input class="input" v-model="form.location_desc" placeholder="如: 大棚A区-01号" />
      </view>
      <view class="form-group">
        <text class="label">摄像头ID</text>
        <input class="input" v-model="form.camera_id" placeholder="可选" />
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
import { getAdminTargets, createAdminTarget } from '@/api/admin.js'
import { TargetType, TargetStatus } from '@/models/adopt_target.js' // 假设备份的枚举

export default {
  data() {
    return {
      targets: [],
      loading: false,
      showModal: false,
      form: {
        code: '',
        type: 'tea',
        current_status: 'active',
        location_desc: '',
        camera_id: ''
      },
      error: '',
      typeOptions: [
        { label: '茶饮 (tea)', value: 'tea' },
        { label: '水培 (hydroponic)', value: 'hydroponic' }
      ],
      statusOptions: [
        { label: '可认养 (active)', value: 'active' },
        { label: '维护中 (maintenance)', value: 'maintenance' },
        { label: '已收获 (harvested)', value: 'harvested' },
        { label: '不可用 (unavailable)', value: 'unavailable' }
      ]
    }
  },
  onLoad() {
    this.checkAuth()
    this.loadTargets()
  },
  onShow() {
    this.loadTargets()
  },
  methods: {
    checkAuth() {
      const role = uni.getStorageSync('admin_role')
      if (role !== 'admin') {
        uni.redirectTo({ url: '/pages/admin/login' })
      }
    },
    async loadTargets() {
      this.loading = true
      try {
        const res = await getAdminTargets()
        this.targets = res
      } catch (e) {
        console.error('加载认养对象失败:', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    getTypeLabel(type) {
      const opt = this.typeOptions.find(o => o.value === type)
      return opt ? opt.label : type
    },
    getStatusLabel(status) {
      const opt = this.statusOptions.find(o => o.value === status)
      return opt ? opt.label : status
    },
    getStatusColor(status) {
      const colors = {
        active: '#4caf50',
        maintenance: '#ff9800',
        harvested: '#2196f3',
        unavailable: '#f44336'
      }
      return colors[status] || '#333'
    },
    onTypeChange(e) {
      this.form.type = this.typeOptions[e.detail.value].value
    },
    onStatusChange(e) {
      this.form.current_status = this.statusOptions[e.detail.value].value
    },
    showAddModal() {
      this.form = { code: '', type: 'tea', current_status: 'active', location_desc: '', camera_id: '' }
      this.error = ''
      this.showModal = true
    },
    hideAddModal() {
      this.showModal = false
    },
    async handleSubmit() {
      if (!this.form.code) {
        this.error = '请输入编号'
        return
      }
      if (!this.form.type) {
        this.error = '请选择类型'
        return
      }
      
      this.loading = true
      try {
        await createAdminTarget(this.form)
        uni.showToast({ title: '创建成功', icon: 'success' })
        this.hideAddModal()
        this.loadTargets()
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
.table-header { display: flex; background-color: #f5f5f5; padding: 16px; font-weight: bold; font-size: 26rpx; color: #666; border-bottom: 1px solid #eee; }
.table-body { max-height: 800rpx; }
.table-row { display: flex; padding: 16px; border-bottom: 1px solid #f0f0f0; font-size: 26rpx; }
.table-row:last-child { border-bottom: none; }
.col-code { width: 20%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-type { width: 20%; }
.col-status { width: 20%; }
.col-location { width: 40%; }

/* 弹窗 */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { width: 80%; max-width: 600rpx; background: #fff; border-radius: 16px; padding: 24px; max-height: 90vh; overflow-y: auto; }
.modal-title { font-size: 32rpx; font-weight: bold; text-align: center; margin-bottom: 24px; color: #333; }
.form-group { margin-bottom: 20px; }
.label { display: block; font-size: 28rpx; color: #666; margin-bottom: 8px; }
.input, .picker { width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 28rpx; background: #fff; min-height: 40px; box-sizing: border-box; }
.picker { line-height: 40px; }
.error-msg { color: #c0392b; font-size: 24rpx; margin-bottom: 16px; text-align: center; }
.modal-actions { display: flex; gap: 12px; margin-top: 24px; }
.btn-cancel, .btn-confirm { flex: 1; border: none; border-radius: 8px; padding: 12px; font-size: 28rpx; }
.btn-cancel { background: #f0f0f0; color: #666; }
.btn-confirm { background: #2d5a27; color: #fff; }
</style>

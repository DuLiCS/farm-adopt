<template>
  <view class="container">
    <!-- 顶部导航 -->
    <view class="header">
      <text class="title">发布更新</text>
      <button class="btn-submit" @click="handleSubmit" :disabled="submitting">发布</button>
    </view>

    <view class="form">
      <view class="form-section">
        <view class="section-title">认养对象</view>
        <picker v-model="form.target_id" :range="targetOptions" range-key="label" @change="onTargetChange">
          <view class="picker-display">
            {{ getSelectedTargetLabel() || '请选择认养对象' }}
          </view>
        </picker>
      </view>

      <view class="form-section">
        <view class="section-title">更新类型 *</view>
        <view class="radio-group">
          <view 
            v-for="type in logTypeOptions" 
            :key="type.value"
            class="radio-item"
            :class="{ active: form.log_type === type.value }"
            @click="form.log_type = type.value"
          >
            <text>{{ type.label }}</text>
          </view>
        </view>
      </view>

      <view class="form-section">
        <view class="section-title">描述 *</view>
        <textarea 
          class="textarea" 
          v-model="form.description" 
          placeholder="请填写更新描述，如：今日浇水情况、生长状态等"
          maxlength="500"
        />
        <view class="char-count">{{ form.description.length }}/500</view>
      </view>

      <view class="form-section">
        <view class="section-title">图片URLs</view>
        <view class="url-input-wrapper">
          <input 
            class="url-input" 
            v-model="currentImageUrl" 
            placeholder="输入图片URL，回车添加"
            @confirm="addImageUrl"
          />
          <button class="btn-add-url" @click="addImageUrl">添加</button>
        </view>
        <view v-if="form.image_urls && form.image_urls.length" class="image-list">
          <view v-for="(url, index) in form.image_urls" :key="index" class="image-tag">
            <text>{{ url }}</text>
            <text class="remove-btn" @click="removeImageUrl(index)">×</text>
          </view>
        </view>
        <view class="hint">每张图片应为有效的URL，可添加多张</view>
      </view>
    </view>

    <!-- 预览区域 -->
    <view v-if="form.target_id || form.description" class="preview-section">
      <view class="section-title">预览</view>
      <view class="preview-card">
        <view class="preview-target">认养对象：{{ getSelectedTargetLabel() }}</view>
        <view class="preview-type">类型：{{ getLogTypeLabel(form.log_type) }}</view>
        <view class="preview-desc">{{ form.description || '暂无描述' }}</view>
        <view v-if="form.image_urls && form.image_urls.length" class="preview-images">
          <text class="preview-images-title">图片（{{ form.image_urls.length }}张）：</text>
          <view class="preview-image-list">
            <text v-for="(url, idx) in form.image_urls" :key="idx" class="preview-image-url">{{ url }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { createUpdate } from '@/api/admin.js'
import { getAdminTargets } from '@/api/admin.js'
import { LogType } from '@/models/update_log.js'

export default {
  data() {
    return {
      targets: [],
      targetOptions: [],
      logTypeOptions: [
        { label: '日常更新', value: 'daily' },
        { label: '节气记录', value: 'solar_term' },
        { label: '收获通知', value: 'harvest' },
        { label: '配送通知', value: 'delivery' }
      ],
      form: {
        target_id: null,
        log_type: 'daily',
        description: '',
        image_urls: []
      },
      currentImageUrl: '',
      submitting: false
    }
  },
  onLoad() {
    this.checkAuth()
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
      try {
        const res = await getAdminTargets()
        this.targets = res
        this.targetOptions = this.targets.map(t => ({
          label: `${t.code} - ${t.type}`,
          value: t.id
        }))
      } catch (e) {
        console.error('加载认养对象失败:', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    onTargetChange(e) {
      this.form.target_id = this.targetOptions[e.detail.value].value
    },
    getSelectedTargetLabel() {
      if (!this.form.target_id) return ''
      const opt = this.targetOptions.find(o => o.value === this.form.target_id)
      return opt ? opt.label : ''
    },
    getLogTypeLabel(type) {
      const opt = this.logTypeOptions.find(o => o.value === type)
      return opt ? opt.label : type
    },
    addImageUrl() {
      const url = this.currentImageUrl.trim()
      if (!url) return
      if (!this.isValidUrl(url)) {
        uni.showToast({ title: '请输入有效的URL', icon: 'none' })
        return
      }
      if (!this.form.image_urls) {
        this.form.image_urls = []
      }
      this.form.image_urls.push(url)
      this.currentImageUrl = ''
    },
    isValidUrl(url) {
      try {
        new URL(url)
        return true
      } catch {
        return false
      }
    },
    removeImageUrl(index) {
      this.form.image_urls.splice(index, 1)
    },
    async handleSubmit() {
      if (!this.form.target_id) {
        uni.showToast({ title: '请选择认养对象', icon: 'none' })
        return
      }
      if (!this.form.description.trim()) {
        uni.showToast({ title: '请填写描述', icon: 'none' })
        return
      }
      if (!this.form.log_type) {
        uni.showToast({ title: '请选择更新类型', icon: 'none' })
        return
      }

      this.submitting = true
      try {
        await createUpdate({
          target_id: this.form.target_id,
          log_type: this.form.log_type,
          description: this.form.description.trim(),
          image_urls: this.form.image_urls || []
        })
        uni.showToast({ title: '发布成功', icon: 'success' })
        // 清空表单
        this.form = {
          target_id: null,
          log_type: 'daily',
          description: '',
          image_urls: []
        }
        this.currentImageUrl = ''
      } catch (e) {
        console.error('发布失败:', e)
        uni.showToast({ title: e.message || '发布失败', icon: 'none' })
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.container { padding: 0; min-height: 100vh; box-sizing: border-box; background-color: #f5f5f0; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: #fff; border-bottom: 1px solid #eee; }
.title { font-size: 32rpx; font-weight: bold; color: #333; }
.btn-submit { background-color: #2d5a27; color: #fff; border: none; border-radius: 8px; padding: 8px 32px; font-size: 28rpx; }
.btn-submit[disabled] { background-color: #ccc; }

.form { padding: 24px; margin-bottom: 16px; }
.form-section { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.section-title { font-size: 28rpx; font-weight: 500; color: #333; margin-bottom: 12px; }
.picker-display { border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 28rpx; background: #fff; color: #333; min-height: 40px; display: flex; align-items: center; }
.radio-group { display: flex; flex-wrap: wrap; gap: 12px; }
.radio-item { padding: 8px 16px; border: 1px solid #2d5a27; border-radius: 16px; font-size: 26rpx; color: #2d5a27; }
.radio-item.active { background-color: #2d5a27; color: #fff; }
.textarea { border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 28rpx; background: #fff; min-height: 200rpx; width: 100%; box-sizing: border-box; }
.char-count { text-align: right; font-size: 24rpx; color: #999; margin-top: 8px; }
.url-input-wrapper { display: flex; gap: 8px; }
.url-input { flex: 1; border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 28rpx; background: #fff; }
.btn-add-url { background-color: #2d5a27; color: #fff; border: none; border-radius: 8px; padding: 8px 24px; font-size: 26rpx; white-space: nowrap; }
.image-list { margin-top: 12px; }
.image-tag { display: inline-flex; align-items: center; background: #f0f0f0; border-radius: 6px; padding: 6px 12px; margin: 4px 6px 4px 0; font-size: 24rpx; }
.remove-btn { margin-left: 8px; color: #c0392b; font-weight: bold; cursor: pointer; }
.hint { font-size: 24rpx; color: #999; margin-top: 8px; }

.preview-section { padding: 0 24px 24px; }
.preview-card { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.preview-target, .preview-type, .preview-desc { font-size: 26rpx; margin-bottom: 8px; color: #333; }
.preview-target { color: #2d5a27; font-weight: 500; }
.preview-desc { white-space: pre-wrap; line-height: 1.6; }
.preview-images { margin-top: 12px; }
.preview-images-title { font-size: 26rpx; color: #666; margin-bottom: 8px; display: block; }
.preview-image-list { display: flex; flex-direction: column; gap: 8px; }
.preview-image-url { font-size: 24rpx; color: #999; word-break: break-all; line-height: 1.4; }
</style>

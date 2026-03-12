<template>
  <div class="container" style="padding: 0; min-height: 100vh; background: #f5f5f0;">
    <div class="header" style="display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: #fff; border-bottom: 1px solid #eee;">
      <div class="title" style="font-size: 20px; font-weight: bold; color: #333;">发布更新</div>
      <button class="btn-submit" style="background-color: #2d5a27; color: #fff; border: none; border-radius: 8px; padding: 8px 32px; font-size: 16px; cursor: pointer;" @click="handleSubmit" :disabled="submitting">发布</button>
    </div>

    <div class="form" style="padding: 24px; margin-bottom: 16px;">
      <div class="form-section" style="background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <div class="section-title" style="font-size: 16px; font-weight: 500; color: #333; margin-bottom: 12px;">认养对象</div>
        <select v-model="form.target_id" style="width: 100%; border: 1px solid #eee; border-radius: 8px; padding: 12px; box-sizing: border-box;" @change="onTargetChange">
          <option value="">请选择认养对象</option>
          <option v-for="opt in targetOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>

      <div class="form-section" style="background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
        <div class="section-title" style="font-size: 16px; font-weight: 500; color: #333; margin-bottom: 12px;">更新类型 *</div>
        <div class="radio-group" style="display: flex; flex-wrap: wrap; gap: 12px;">
          <div v-for="type in logTypeOptions" :key="type.value" class="radio-item" :class="{ active: form.log_type === type.value }" style="padding: 8px 16px; border: 1px solid #2d5a27; border-radius: 16px; font-size: 14px; color: #2d5a27; cursor: pointer;" @click="form.log_type = type.value">
            {{ type.label }}
          </div>
        </div>
      </div>

      <div class="form-section" style="background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
        <div class="section-title" style="font-size: 16px; font-weight: 500; color: #333; margin-bottom: 12px;">描述 *</div>
        <textarea class="textarea" v-model="form.description" placeholder="请填写更新描述，如：今日浇水情况、生长状态等" maxlength="500" style="border: 1px solid #eee; border-radius: 8px; padding: 12px; font-size: 16px; background: #fff; min-height: 120px; width: 100%; box-sizing: border-box;"></textarea>
        <div class="char-count" style="text-align: right; font-size: 14px; color: #999; margin-top: 8px;">{{ form.description.length }}/500</div>
      </div>

      <div class="form-section" style="background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
        <div class="section-title" style="font-size: 16px; font-weight: 500; color: #333; margin-bottom: 12px;">图片URLs</div>
        <div class="url-input-wrapper" style="display: flex; gap: 8px; margin-bottom: 12px;">
          <input class="url-input" type="text" v-model="currentImageUrl" placeholder="输入图片URL，回车添加" @keyup.enter="addImageUrl" style="flex: 1; border: 1px solid #eee; border-radius: 8px; padding: 12px; box-sizing: border-box;" />
          <button class="btn-add-url" style="background-color: #2d5a27; color: #fff; border: none; border-radius: 8px; padding: 8px 24px; font-size: 14px; cursor: pointer;" @click="addImageUrl">添加</button>
        </div>
        <div v-if="form.image_urls && form.image_urls.length" class="image-list">
          <div v-for="(url, index) in form.image_urls" :key="index" class="image-tag" style="display: inline-flex; align-items: center; background: #f0f0f0; border-radius: 6px; padding: 6px 12px; margin: 4px 6px 4px 0; font-size: 12px;">
            {{ url }}
            <span class="remove-btn" style="margin-left: 8px; color: #c0392b; font-weight: bold; cursor: pointer;" @click="removeImageUrl(index)">×</span>
          </div>
        </div>
        <div class="hint" style="font-size: 12px; color: #999; margin-top: 8px;">每张图片应为有效的URL，可添加多张</div>
      </div>
    </div>

    <!-- 预览区域 -->
    <div v-if="form.target_id || form.description" class="preview-section" style="padding: 0 24px 24px;">
      <div class="preview-card" style="background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <div class="section-title" style="font-size: 16px; font-weight: 500; color: #333; margin-bottom: 12px;">预览</div>
        <div class="preview-target" style="font-size: 14px; margin-bottom: 8px; color: #2d5a27; font-weight: 500;">认养对象：{{ getSelectedTargetLabel() }}</div>
        <div class="preview-type" style="font-size: 14px; margin-bottom: 8px; color: #666;">类型：{{ getLogTypeLabel(form.log_type) }}</div>
        <div class="preview-desc" style="font-size: 14px; margin-bottom: 8px; color: #333; white-space: pre-wrap; line-height: 1.6;">{{ form.description || '暂无描述' }}</div>
        <div v-if="form.image_urls && form.image_urls.length" class="preview-images" style="margin-top: 12px;">
          <span class="preview-images-title" style="font-size: 14px; color: #666; margin-bottom: 8px; display: block;">图片（{{ form.image_urls.length }}张）：</span>
          <div class="preview-image-list" style="display: flex; flex-direction: column; gap: 8px;">
            <span v-for="(url, idx) in form.image_urls" :key="idx" class="preview-image-url" style="font-size: 12px; color: #999; word-break: break-all; line-height: 1.4;">{{ url }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAdminTargets, createUpdate } from '@/api/admin.js'

const router = useRouter()
const targets = ref([])
const targetOptions = ref([])
const logTypeOptions = [
  { label: '日常更新', value: 'daily' },
  { label: '节气记录', value: 'solar_term' },
  { label: '收获通知', value: 'harvest' },
  { label: '配送通知', value: 'delivery' }
]
const form = ref({
  target_id: '',
  log_type: 'daily',
  description: '',
  image_urls: []
})
const currentImageUrl = ref('')
const submitting = ref(false)

const checkAuth = () => {
  const role = localStorage.getItem('admin_role')
  if (role !== 'admin') router.replace('/login')
}

const loadTargets = async () => {
  try {
    const res = await getAdminTargets()
    targets.value = res
    targetOptions.value = res.map(t => ({ label: `${t.code} - ${t.type}`, value: t.id }))
  } catch (e) {
    console.error('加载认养对象失败:', e)
    alert('加载失败')
  }
}

const onTargetChange = (e) => {
  form.value.target_id = e.target.value
}
const getSelectedTargetLabel = () => {
  if (!form.value.target_id) return ''
  const opt = targetOptions.value.find(o => o.value === form.value.target_id)
  return opt ? opt.label : ''
}
const getLogTypeLabel = (type) => {
  const opt = logTypeOptions.find(o => o.value === type)
  return opt ? opt.label : type
}
const addImageUrl = () => {
  const url = currentImageUrl.value.trim()
  if (!url) return
  if (!isValidUrl(url)) {
    alert('请输入有效的URL')
    return
  }
  if (!form.value.image_urls) form.value.image_urls = []
  form.value.image_urls.push(url)
  currentImageUrl.value = ''
}
const isValidUrl = (url) => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}
const removeImageUrl = (index) => {
  form.value.image_urls.splice(index, 1)
}
const handleSubmit = async () => {
  if (!form.value.target_id) {
    alert('请选择认养对象')
    return
  }
  if (!form.value.description.trim()) {
    alert('请填写描述')
    return
  }

  submitting.value = true
  try {
    await createUpdate({
      target_id: form.value.target_id,
      log_type: form.value.log_type,
      description: form.value.description.trim(),
      image_urls: form.value.image_urls || []
    })
    alert('发布成功')
    form.value = { target_id: '', log_type: 'daily', description: '', image_urls: [] }
    currentImageUrl.value = ''
  } catch (e) {
    alert(e.message || '发布失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  checkAuth()
  loadTargets()
})
</script>

<template>
  <div class="update-form-page">
    <h2>发布更新</h2>
    <div class="form-card">
      <div class="form-group">
        <label>认养对象 *</label>
        <select v-model="form.target_id">
          <option value="">请选择</option>
          <option v-for="t in targets" :key="t.id" :value="t.id">{{ t.code }} - {{ t.type }}</option>
        </select>
      </div>

      <div class="form-group">
        <label>更新类型 *</label>
        <div class="radio-group">
          <button
            v-for="type in logTypeOptions"
            :key="type.value"
            :class="{ active: form.log_type === type.value }"
            @click="form.log_type = type.value"
          >{{ type.label }}</button>
        </div>
      </div>

      <div class="form-group">
        <label>描述 *</label>
        <textarea v-model="form.description" placeholder="请填写更新描述" maxlength="500" rows="6"></textarea>
        <div class="char-count">{{ form.description.length }}/500</div>
      </div>

      <div class="form-group">
        <label>图片</label>
        <div class="img-upload-row">
          <input type="file" ref="fileInput" accept="image/*" multiple @change="handleFileUpload" style="display:none" />
          <button type="button" class="btn-upload" @click="$refs.fileInput.click()" :disabled="uploading">
            {{ uploading ? '上传中...' : '📷 上传图片' }}
          </button>
          <span class="upload-or">或</span>
          <div class="url-input-row">
            <input v-model="currentUrl" placeholder="粘贴图片URL，回车添加" @keyup.enter="addUrl" />
            <button type="button" @click="addUrl">添加</button>
          </div>
        </div>
        <div v-if="form.image_urls?.length" class="img-preview-list">
          <div v-for="(url, idx) in form.image_urls" :key="idx" class="img-preview-item">
            <img :src="url" class="img-thumb" />
            <span class="remove" @click="removeUrl(idx)">×</span>
          </div>
        </div>
      </div>

      <button class="btn-submit" :disabled="submitting" @click="handleSubmit">
        {{ submitting ? '发布中...' : '发布' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const targets = ref([])
const submitting = ref(false)
const uploading = ref(false)
const currentUrl = ref('')
const fileInput = ref(null)
const form = ref({
  target_id: '',
  log_type: 'daily',
  description: '',
  image_urls: []
})

const logTypeOptions = [
  { label: '日常更新', value: 'daily' },
  { label: '节气记录', value: 'solar_term' },
  { label: '收获通知', value: 'harvest' },
  { label: '配送通知', value: 'delivery' }
]

onMounted(() => {
  api.getTargets().then(data => targets.value = data).catch(console.error)
})

const addUrl = () => {
  const url = currentUrl.value.trim()
  if (!url) return
  try {
    new URL(url)
    if (!form.value.image_urls) form.value.image_urls = []
    form.value.image_urls.push(url)
    currentUrl.value = ''
  } catch {
    alert('请输入有效的 URL')
  }
}

const removeUrl = (idx) => {
  form.value.image_urls.splice(idx, 1)
}

const handleFileUpload = async (event) => {
  const files = Array.from(event.target.files)
  if (!files.length) return
  uploading.value = true
  try {
    for (const file of files) {
      const result = await api.uploadImage(file)
      if (result.url) {
        if (!form.value.image_urls) form.value.image_urls = []
        // uploadImage returns relative path like /static/images/xxx.jpg
        // convert to absolute if needed
        const url = result.url.startsWith('http') ? result.url : window.location.origin + result.url
        form.value.image_urls.push(url)
      }
    }
  } catch (e) {
    alert(e.detail || '上传失败')
  } finally {
    uploading.value = false
    event.target.value = ''
  }
}

const handleSubmit = async () => {
  if (!form.value.target_id) { alert('请选择认养对象'); return }
  if (!form.value.description.trim()) { alert('请填写描述'); return }
  if (!form.value.log_type) { alert('请选择更新类型'); return }

  submitting.value = true
  try {
    await api.createUpdate({
      target_id: Number(form.value.target_id),
      log_type: form.value.log_type,
      description: form.value.description.trim(),
      image_urls: form.value.image_urls || []
    })
    alert('发布成功')
    form.value = { target_id: '', log_type: 'daily', description: '', image_urls: [] }
    currentUrl.value = ''
  } catch (e) {
    alert(e.detail || '发布失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.update-form-page {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
h2 { margin: 0 0 16px; font-size: 18px; }
.form-card { max-width: 600px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-size: 14px; color: #666; }
.form-group select, .form-group input, .form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-group textarea { min-height: 120px; resize: vertical; }
.char-count { text-align: right; font-size: 12px; color: #999; margin-top: 4px; }

.radio-group { display: flex; flex-wrap: wrap; gap: 8px; }
.radio-group button {
  padding: 8px 16px;
  border: 1px solid #2d5a27;
  border-radius: 16px;
  background: white;
  color: #2d5a27;
  cursor: pointer;
  font-size: 14px;
}
.radio-group button.active { background: #2d5a27; color: white; }

.url-input-row { display: flex; gap: 8px; }
.url-input-row input { flex: 1; }
.url-input-row button {
  padding: 8px 16px;
  background: #2d5a27;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.img-upload-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.btn-upload {
  background: #f0f0f0; color: #333; border: 1px solid #ddd;
  padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px; white-space: nowrap;
}
.btn-upload:hover { background: #e0e0e0; }
.btn-upload:disabled { opacity: 0.6; cursor: not-allowed; }
.upload-or { font-size: 13px; color: #bbb; flex-shrink: 0; }
.img-preview-list { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 8px; }
.img-preview-item { position: relative; }
.img-thumb { width: 80px; height: 60px; object-fit: cover; border-radius: 6px; display: block; }
.img-preview-item .remove {
  position: absolute; top: -6px; right: -6px;
  background: #c0392b; color: white; border-radius: 50%;
  width: 18px; height: 18px; display: flex; align-items: center; justify-content: center;
  font-size: 12px; cursor: pointer; line-height: 1;
}

.btn-submit {
  width: 100%;
  padding: 12px;
  background: #2d5a27;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 16px;
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
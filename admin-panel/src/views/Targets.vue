<template>
  <div class="targets-page">
    <h2>山南对象管理</h2>
    <button class="btn-add" @click="openCreateModal">新增</button>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="targets.length === 0" class="empty">暂无山南对象</div>
    <div v-else class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>封面</th>
            <th>编号</th>
            <th>类型</th>
            <th>名称</th>
            <th>位置</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in targets" :key="t.id">
            <td>
              <img v-if="t.cover_image" :src="getImageUrl(t.cover_image)" class="cover-thumb" />
              <span v-else class="no-cover">无</span>
            </td>
            <td>{{ t.code }}</td>
            <td>{{ t.type === 'tea' ? '茶树' : '无土栽培' }}</td>
            <td>{{ t.name }}</td>
            <td>{{ t.location_desc || '-' }}</td>
            <td :style="{ color: statusColor(t.current_status) }">{{ statusLabel(t.current_status) }}</td>
            <td>
              <button class="btn-edit" @click="openEditModal(t)">编辑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <h3>{{ isEditing ? '编辑山南对象' : '新增山南对象' }}</h3>

        <div class="form-group">
          <label>编号 *</label>
          <input v-model="form.code" placeholder="如: TEA-001" :disabled="isEditing" />
        </div>

        <div class="form-group">
          <label>类型 *</label>
          <select v-model="form.type" :disabled="isEditing">
            <option value="tea">茶树</option>
            <option value="hydroponic">无土栽培</option>
          </select>
        </div>

        <div class="form-group">
          <label>名称 *</label>
          <input v-model="form.name" placeholder="如: 云雾茶树·01号" />
        </div>

        <div class="form-group">
          <label>位置描述</label>
          <input v-model="form.location_desc" placeholder="如: 汉中·西乡" />
        </div>

        <div class="form-group">
          <label>描述</label>
          <textarea v-model="form.description" placeholder="简要描述..." rows="3"></textarea>
        </div>

        <div class="form-group">
          <label>价格 - 基础档</label>
          <input type="number" v-model="form.price_basic" placeholder="599" />
        </div>

        <div class="form-group">
          <label>价格 - 标准档</label>
          <input type="number" v-model="form.price_standard" placeholder="999" />
        </div>

        <div class="form-group">
          <label>状态</label>
          <select v-model="form.current_status">
            <option value="active">可认养</option>
            <option value="maintenance">维护中</option>
            <option value="harvested">已收获</option>
            <option value="unavailable">不可用</option>
          </select>
        </div>

        <div class="form-group">
          <label>封面图</label>
          <div v-if="form.cover_image" class="cover-preview">
            <img :src="getImageUrl(form.cover_image)" class="cover-preview-img" />
            <button type="button" class="btn-remove-cover" @click="form.cover_image = ''">删除</button>
          </div>
          <input type="file" ref="fileInput" accept="image/*" @change="handleFileSelect" style="display: none;" />
          <button type="button" class="btn-upload" @click="$refs.fileInput.click()">上传图片</button>
          <div v-if="uploading" class="uploading">上传中...</div>
        </div>

        <div v-if="error" class="error">{{ error }}</div>
        <div class="actions">
          <button @click="closeModal">取消</button>
          <button class="btn-primary" @click="handleSubmit">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { API_BASE } from '../config.js'
import { ref, onMounted } from 'vue'
import { api } from '../api'

const targets = ref([])
const loading = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const uploading = ref(false)
const error = ref('')
const fileInput = ref(null)

const defaultForm = {
  code: '',
  type: 'tea',
  name: '',
  location_desc: '',
  description: '',
  price_basic: null,
  price_standard: null,
  current_status: 'active',
  cover_image: ''
}

const form = ref({ ...defaultForm })

onMounted(() => {
  loadTargets()
})

const loadTargets = async () => {
  loading.value = true
  try {
    targets.value = await api.getTargets()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const getImageUrl = (path) => {
  if (!path) return ''
  // 相对路径转为完整 URL
  if (path.startsWith('http')) return path
  if (path.startsWith('/static/')) return path
  return API_BASE + path
}

const statusLabel = (s) => ({
  active: '可认养',
  maintenance: '维护中',
  harvested: '已收获',
  unavailable: '不可用'
}[s] || s)

const statusColor = (s) => ({
  active: '#4caf50',
  maintenance: '#ff9800',
  harvested: '#2196f3',
  unavailable: '#f44336'
}[s] || '#333')

const openCreateModal = () => {
  isEditing.value = false
  form.value = { ...defaultForm }
  error.value = ''
  showModal.value = true
}

const openEditModal = (target) => {
  isEditing.value = true
  form.value = {
    code: target.code,
    type: target.type,
    name: target.name,
    location_desc: target.location_desc || '',
    description: target.description || '',
    price_basic: target.price_basic,
    price_standard: target.price_standard,
    current_status: target.current_status,
    cover_image: target.cover_image || ''
  }
  form.value.targetId = target.id
  error.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  form.value = { ...defaultForm }
  error.value = ''
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件类型
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['jpg', 'jpeg', 'png', 'webp'].includes(ext)) {
    error.value = '只支持 jpg/png/webp 格式'
    return
  }

  uploading.value = true
  error.value = ''
  try {
    const result = await api.uploadImage(file)
    form.value.cover_image = result.url
  } catch (e) {
    error.value = e.detail || '上传失败'
  } finally {
    uploading.value = false
    // 清空 input 以允许重复选择同一文件
    event.target.value = ''
  }
}

const handleSubmit = async () => {
  error.value = ''
  if (!form.value.code) {
    error.value = '请输入编号'
    return
  }

  loading.value = true
  try {
    if (isEditing.value) {
      // 编辑模式：更新封面图（如果有变更）
      const targetId = form.value.targetId
      if (form.value.cover_image) {
        await api.updateTargetCover(targetId, form.value.cover_image)
      }
      // TODO: 更新其他字段（目前只实现了封面图更新）
    } else {
      // 新增模式
      await api.createTarget({
        ...form.value,
        price_basic: form.value.price_basic || null,
        price_standard: form.value.price_standard || null
      })
    }
    showModal.value = false
    form.value = { ...defaultForm }
    await loadTargets()
  } catch (e) {
    error.value = e.detail || (isEditing.value ? '更新失败' : '创建失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.targets-page {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
h2 {
  margin: 0 0 16px;
  font-size: 18px;
}
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
.btn-edit {
  background: #4a7c3f;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
.table {
  width: 100%;
  border-collapse: collapse;
}
.th, .td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
}
.th {
  background: #f5f5f5;
  font-weight: 600;
  color: #666;
  border-bottom: 1px solid #eee;
}
.td {
  border-bottom: 1px solid #f0f0f0;
}
.tr:last-child .td {
  border-bottom: none;
}
.cover-thumb {
  width: 60px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
}
.no-cover {
  color: #999;
  font-size: 12px;
}

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
  max-height: 90vh;
  overflow-y: auto;
}
.modal h3 {
  margin: 0 0 16px;
  font-size: 18px;
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #666;
}
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-group textarea {
  resize: vertical;
  min-height: 80px;
}
.cover-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}
.cover-preview-img {
  width: 100px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}
.btn-remove-cover {
  background: #c0392b;
  color: white;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.btn-upload {
  background: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}
.btn-upload:hover {
  background: #e0e0e0;
}
.uploading {
  margin-top: 8px;
  color: #666;
  font-size: 14px;
}
.error {
  color: #c0392b;
  font-size: 14px;
  margin-bottom: 12px;
}
.actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
.actions button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.actions button:first-child {
  background: #f0f0f0;
  color: #666;
}
.actions .btn-primary {
  background: #2d5a27;
  color: white;
}
</style>

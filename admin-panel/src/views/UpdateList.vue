<template>
 <div class="update-list-page">
 <div class="page-header">
 <h2 class="page-title">日志管理</h2>
 <div class="tab-group">
 <button :class="{ active: tab === 'drafts' }" @click="tab = 'drafts'; loadData()">
 待审核 <span class="badge" v-if="drafts.length">{{ drafts.length }}</span>
 </button>
 <button :class="{ active: tab === 'published' }" @click="tab = 'published'; loadData()">已发布</button>
 </div>
 </div>

 <div v-if="loading" class="empty">加载中...</div>

 <!-- 草稿列表 -->
 <div v-else-if="tab === 'drafts'">
 <div v-if="drafts.length === 0" class="empty">暂无待审核草稿</div>
 <div class="draft-list" v-else>
 <div class="draft-card" v-for="d in drafts" :key="d.id">
 <div class="draft-header">
 <div class="draft-source">
 <span class="badge-auto" v-if="d.source === 'auto'">🤖 自动生成</span>
 <span class="badge-manual" v-else>✍️ 手动</span>
 </div>
 <div class="draft-time">{{ formatDate(d.updated_at) }}</div>
 </div>
 <div class="draft-title" v-if="d.title">{{ d.title }}</div>
 <div class="draft-desc">{{ d.description }}</div>
 <div class="draft-meta">
 认养对象ID: {{ d.target_id }} · {{ logTypeLabel(d.log_type) }}
 </div>
 <div class="draft-actions">
 <button class="btn-publish" @click="publish(d.id)">发布</button>
 <button class="btn-edit" @click="startEdit(d)">编辑</button>
 </div>
 </div>
 </div>
 </div>

 <!-- 已发布列表 -->
 <div v-else>
 <div v-if="published.length === 0" class="empty">暂无已发布日志</div>
 <table v-else class="table">
 <thead>
 <tr>
 <th>标题/描述</th>
 <th>类型</th>
 <th>来源</th>
 <th>认养对象</th>
 <th>时间</th>
 </tr>
 </thead>
 <tbody>
 <tr v-for="u in published" :key="u.id">
 <td class="desc-col">{{ u.title || truncate(u.description, 40) }}</td>
 <td>{{ logTypeLabel(u.log_type) }}</td>
 <td>{{ u.source === 'auto' ? '🤖 自动' : '✍️ 手动' }}</td>
 <td>{{ u.target?.code || u.target_id }}</td>
 <td>{{ formatDate(u.updated_at) }}</td>
 </tr>
 </tbody>
 </table>
 </div>

 <!-- 编辑弹窗 -->
 <div class="modal-mask" v-if="editItem" @click.self="editItem = null">
 <div class="modal">
 <div class="modal-title">编辑日志</div>
 <div class="form-group">
 <label>标题（可选）</label>
 <input v-model="editItem.title" class="form-input" placeholder="如：谷雨·第一批明前茶" />
 </div>
 <div class="form-group">
 <label>正文</label>
 <textarea v-model="editItem.description" class="form-textarea" rows="5"></textarea>
 </div>
 <div class="modal-actions">
 <button class="btn-publish" @click="saveEdit">保存</button>
 <button class="btn-cancel" @click="editItem = null">取消</button>
 </div>
 </div>
 </div>
 </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { api } from "../api"

const tab = ref("drafts")
const drafts = ref([])
const published = ref([])
const loading = ref(false)
const editItem = ref(null)
import { API_BASE as API } from '../config.js'

async function loadData() {
 loading.value = true
 try {
 if (tab.value === "drafts") {
 const token = localStorage.getItem("admin_token")
 const res = await fetch(`${API}/admin/updates/drafts`, {
 headers: { Authorization: `Bearer ${token}` }
 })
 drafts.value = await res.json()
 } else {
 published.value = await api.getUpdates()
 }
 } catch (e) {
 console.error(e)
 } finally {
 loading.value = false
 }
}

async function publish(id) {
 const token = localStorage.getItem("admin_token")
 await fetch(`${API}/admin/updates/${id}/publish`, {
 method: "POST",
 headers: { Authorization: `Bearer ${token}` }
 })
 await loadData()
}

function startEdit(item) {
 editItem.value = { ...item }
}

async function saveEdit() {
 const token = localStorage.getItem("admin_token")
 await fetch(`${API}/admin/updates/${editItem.value.id}`, {
 method: "PUT",
 headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
 body: JSON.stringify({ title: editItem.value.title, description: editItem.value.description })
 })
 editItem.value = null
 await loadData()
}

const logTypeLabel = (t) => ({ daily: "日常", solar_term: "节气", harvest: "收获", delivery: "配送" }[t] || t)
const truncate = (str, len) => !str ? "-" : str.length > len ? str.substring(0, len) + "..." : str
const formatDate = (d) => !d ? "-" : d.replace("T", " ").substring(0, 16)

onMounted(loadData)
</script>

<style scoped>
.update-list-page { max-width: 900px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: bold; color: #2d5a27; margin: 0; }
.tab-group { display: flex; gap: 8px; }
.tab-group button { border: 1px solid #ddd; background: white; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; color: #666; position: relative; }
.tab-group button.active { background: #2d5a27; color: white; border-color: #2d5a27; }
.badge { background: #e74c3c; color: white; border-radius: 999px; padding: 1px 6px; font-size: 11px; margin-left: 6px; }
.empty { text-align: center; padding: 60px; color: #ccc; font-size: 15px; background: white; border-radius: 12px; }
.draft-list { display: flex; flex-direction: column; gap: 16px; }
.draft-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.draft-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.badge-auto { background: #e8f4fd; color: #1976d2; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
.badge-manual { background: #f5f5f0; color: #666; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
.draft-time { font-size: 12px; color: #bbb; }
.draft-title { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 8px; }
.draft-desc { font-size: 14px; color: #555; line-height: 1.6; margin-bottom: 12px; }
.draft-meta { font-size: 12px; color: #999; margin-bottom: 16px; }
.draft-actions { display: flex; gap: 10px; }
.btn-publish { background: #2d5a27; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-edit { background: white; color: #2d5a27; border: 1px solid #2d5a27; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-cancel { background: white; color: #999; border: 1px solid #ddd; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
th { background: #f5f5f0; color: #666; padding: 12px 16px; text-align: left; font-weight: 500; font-size: 13px; }
td { padding: 12px 16px; border-bottom: 1px solid #f0f0f0; font-size: 14px; color: #333; }
tr:last-child td { border-bottom: none; }
.desc-col { max-width: 280px; }
.modal-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: white; border-radius: 12px; padding: 32px; width: 500px; max-width: 90vw; }
.modal-title { font-size: 18px; font-weight: bold; color: #2d5a27; margin-bottom: 24px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 14px; color: #555; margin-bottom: 8px; }
.form-input { width: 100%; border: 1px solid #ddd; border-radius: 6px; padding: 10px 12px; font-size: 14px; box-sizing: border-box; }
.form-textarea { width: 100%; border: 1px solid #ddd; border-radius: 6px; padding: 10px 12px; font-size: 14px; box-sizing: border-box; resize: vertical; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }
</style>

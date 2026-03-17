<template>
 <div class="sensor-page">
 <h2 class="page-title">传感器数据</h2>

 <div class="latest-card">
 <div class="latest-title">🌿 当前实况</div>
 <div v-if="latest" class="latest-grid">
 <div class="latest-item">
 <div class="latest-value">{{ latest.temperature !== null ? latest.temperature + "°C" : "--" }}</div>
 <div class="latest-label">温度</div>
 </div>
 <div class="latest-item">
 <div class="latest-value">{{ latest.humidity !== null ? latest.humidity + "%" : "--" }}</div>
 <div class="latest-label">湿度</div>
 </div>
 <div class="latest-item">
 <div class="latest-value">{{ latest.soil_moisture !== null ? latest.soil_moisture + "%" : "--" }}</div>
 <div class="latest-label">土壤湿度</div>
 </div>
 </div>
 <div v-else class="no-data">暂无数据</div>
 <div class="latest-time" v-if="latest">更新于 {{ updateText }}</div>
 </div>

 <div class="history-card">
 <div class="history-header">
 <div class="history-title">📊 历史记录</div>
 <div class="tab-group">
 <button :class="{ active: hours === 24 }" @click="switchHours(24)">24小时</button>
 <button :class="{ active: hours === 168 }" @click="switchHours(168)">7天</button>
 <button :class="{ active: hours === 720 }" @click="switchHours(720)">30天</button>
 </div>
 </div>
 <div class="table-wrap">
 <table v-if="history.length">
 <thead>
 <tr>
 <th>时间</th>
 <th>温度(°C)</th>
 <th>湿度(%)</th>
 <th>土壤湿度(%)</th>
 </tr>
 </thead>
 <tbody>
 <tr v-for="row in pagedHistory" :key="row.recorded_at">
 <td>{{ formatTime(row.recorded_at) }}</td>
 <td>{{ row.temperature !== null ? row.temperature : "--" }}</td>
 <td>{{ row.humidity !== null ? row.humidity : "--" }}</td>
 <td>{{ row.soil_moisture !== null ? row.soil_moisture : "--" }}</td>
 </tr>
 </tbody>
 </table>
 <div v-else class="no-data">暂无数据</div>
 <div class="pagination" v-if="totalPages > 1">
 <button :disabled="page === 1" @click="page--">上一页</button>
 <span>{{ page }} / {{ totalPages }}</span>
 <button :disabled="page === totalPages" @click="page++">下一页</button>
 </div>
 </div>
 </div>
 </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"

const latest = ref(null)
const history = ref([])
const hours = ref(24)
const page = ref(1)
const pageSize = 20
const totalPages = computed(() => Math.ceil(history.value.length / pageSize))
const pagedHistory = computed(() => {
 const start = (page.value - 1) * pageSize
 return history.value.slice(start, start + pageSize)
})
const API = "https://shannanji.com"
const DEVICE_ID = "esp32-farm-01"

const updateText = computed(() => {
 if (!latest.value || !latest.value.recorded_at) return ""
 const now = new Date()
 const recorded = new Date(latest.value.recorded_at + "Z")
 const diffMin = Math.floor((now - recorded) / 60000)
 if (diffMin < 1) return "刚刚"
 if (diffMin < 60) return diffMin + "分钟前"
 const diffHour = Math.floor(diffMin / 60)
 if (diffHour < 24) return diffHour + "小时前"
 return Math.floor(diffHour / 24) + "天前"
})

async function loadLatest() {
 const res = await fetch(`${API}/api/sensor/latest?device_id=${DEVICE_ID}`)
 const data = await res.json()
 if (data.temperature !== undefined) latest.value = data
}

async function loadHistory() {
 const res = await fetch(`${API}/api/sensor/history?device_id=${DEVICE_ID}&hours=${hours.value}`)
 const data = await res.json()
 history.value = (data.data || []).reverse()
}

function switchHours(h) {
 hours.value = h
 page.value = 1
 loadHistory()
}

function formatTime(t) {
 const dt = new Date(t + "Z")
 return dt.getFullYear() + "-" +
 String(dt.getMonth()+1).padStart(2,"0") + "-" +
 String(dt.getDate()).padStart(2,"0") + " " +
 String(dt.getHours()).padStart(2,"0") + ":" +
 String(dt.getMinutes()).padStart(2,"0")
}

onMounted(() => {
 loadLatest()
 loadHistory()
})
</script>

<style scoped>
.sensor-page { max-width: 900px; }
.page-title { font-size: 22px; font-weight: bold; color: #2d5a27; margin-bottom: 24px; }
.latest-card, .history-card { background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.latest-title, .history-title { font-size: 16px; font-weight: 600; color: #2d5a27; margin-bottom: 20px; }
.latest-grid { display: flex; gap: 40px; }
.latest-item { text-align: center; }
.latest-value { font-size: 32px; font-weight: bold; color: #333; }
.latest-label { font-size: 13px; color: #999; margin-top: 4px; }
.latest-time { font-size: 12px; color: #bbb; margin-top: 16px; text-align: right; }
.history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.tab-group { display: flex; gap: 8px; }
.tab-group button { border: 1px solid #ddd; background: white; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; color: #666; }
.tab-group button.active { background: #2d5a27; color: white; border-color: #2d5a27; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { background: #f5f5f0; color: #666; padding: 10px 16px; text-align: left; font-weight: 500; }
td { padding: 10px 16px; border-bottom: 1px solid #f0f0f0; color: #333; }
tr:hover td { background: #fafaf8; }
.no-data { color: #ccc; text-align: center; padding: 40px; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; }
.pagination button { border: 1px solid #ddd; background: white; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination span { font-size: 14px; color: #666; }
</style>

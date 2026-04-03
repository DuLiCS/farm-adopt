<template>
  <div class="settings-page">
    <h2>网站设置</h2>
    <div class="section-card">
      <h3>首页 Banner 图片</h3>
      <div class="banner-preview-wrap" v-if="settings.banner_image">
        <img :src="serverUrl + settings.banner_image" class="banner-preview" />
        <button class="btn-danger-sm" @click="clearBanner">移除图片</button>
      </div>
      <div class="upload-area" v-else>
        <p class="upload-hint">📷 暂无 Banner 图片，点击上传</p>
      </div>
      <div class="upload-row">
        <input type="file" ref="fileInput" accept="image/*" @change="onFileChange" style="display:none" />
        <button class="btn-primary" @click="$refs.fileInput.click()" :disabled="uploading">
          {{ uploading ? "上传中..." : "上传 Banner 图" }}
        </button>
        <span class="upload-tip">建议 750×400px，JPG/PNG，≤2MB</span>
      </div>
    </div>
    <div class="section-card">
      <h3>Banner 文案</h3>
      <div class="form-row">
        <label>主标题</label>
        <input v-model="settings.banner_title" class="form-input" />
      </div>
      <div class="form-row">
        <label>副标题</label>
        <input v-model="settings.banner_sub" class="form-input" />
      </div>
      <button class="btn-primary" @click="saveSettings" :disabled="saving">
        {{ saving ? "保存中..." : "保存文案" }}
      </button>
    </div>
  <AppToast :show="toast.show" :message="toast.message" :type="toast.type" />
  </div>
</template>

<script>
import { API_BASE as SERVER_URL } from '../config.js'
import AppToast from '../components/AppToast.vue'
export default {
  name: "Settings",
  components: { AppToast },
  data() {
    return {
      serverUrl: SERVER_URL,
      settings: { banner_image: "", banner_title: "", banner_sub: "" },
      uploading: false,
      saving: false,
      toast: { show: false, message: '', type: 'success' }
    }
  },
  async mounted() {
    const res = await fetch(SERVER_URL + "/api/settings")
    this.settings = await res.json()
  },
  methods: {
    showToast(message, type = 'success') {
      this.toast = { show: true, message, type }
      setTimeout(() => { this.toast.show = false }, 2500)
    },
    async onFileChange(e) {
      const file = e.target.files[0]
      if (!file) return
      this.uploading = true
      try {
        const token = localStorage.getItem("admin_token")
        const fd = new FormData()
        fd.append("file", file)
        const res = await fetch(SERVER_URL + "/admin/upload", {
          method: "POST",
          headers: { Authorization: "Bearer " + token },
          body: fd
        })
        const data = await res.json()
        if (data.url) {
          this.settings.banner_image = data.url
          await this._save()
          this.showToast('Banner 已更新')
        } else {
          this.showToast('上传失败：' + (data.detail || '未知错误'), 'error')
        }
      } catch (e) {
        this.showToast('上传失败：' + e.message, 'error')
      } finally {
        this.uploading = false
        this.$refs.fileInput.value = ""
      }
    },
    async _save() {
      const token = localStorage.getItem("admin_token")
      await fetch(SERVER_URL + "/api/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
        body: JSON.stringify(this.settings)
      })
    },
    async saveSettings() {
      this.saving = true
      try { await this._save(); this.showToast('保存成功') }
      catch (e) { this.showToast('保存失败：' + e.message, 'error') }
      finally { this.saving = false }
    },
    async clearBanner() {
      this.settings.banner_image = ""
      await this._save()
      this.showToast('Banner 已移除')
    }
  }
}
</script>

<style scoped>
.settings-page { max-width: 800px; margin: 0 auto; padding: 24px; }
h2 { font-size: 22px; font-weight: bold; margin-bottom: 24px; color: #2d5a27; }
.section-card { background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #333; }
.banner-preview { width: 100%; max-height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 12px; display: block; }
.banner-preview-wrap { margin-bottom: 16px; }
.upload-area { border: 2px dashed #ddd; border-radius: 8px; padding: 40px; text-align: center; margin-bottom: 16px; }
.upload-hint { color: #999; font-size: 14px; margin: 0; }
.upload-row { display: flex; align-items: center; gap: 16px; }
.upload-tip { font-size: 13px; color: #999; }
.form-row { margin-bottom: 16px; }
.form-row label { display: block; font-size: 14px; color: #666; margin-bottom: 6px; }
.form-input { width: 100%; border: 1px solid #e0e0e0; border-radius: 8px; padding: 10px 12px; font-size: 14px; box-sizing: border-box; }
.btn-primary { background: #2d5a27; color: white; border: none; border-radius: 8px; padding: 10px 24px; font-size: 14px; cursor: pointer; }
.btn-primary:disabled { background: #999; cursor: not-allowed; }
.btn-danger-sm { background: #e74c3c; color: white; border: none; border-radius: 6px; padding: 6px 14px; font-size: 13px; cursor: pointer; }
</style>

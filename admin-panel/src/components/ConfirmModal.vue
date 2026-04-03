<template>
  <Teleport to="body">
    <div v-if="show" class="confirm-overlay" @click.self="$emit('cancel')">
      <div class="confirm-box">
        <div class="confirm-title">{{ title }}</div>
        <div v-if="message" class="confirm-msg">{{ message }}</div>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="$emit('cancel')">取消</button>
          <button class="btn-confirm" :class="{ danger: danger }" @click="$emit('confirm')">{{ confirmText || '确认' }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: Boolean,
  title: String,
  message: String,
  confirmText: String,
  danger: Boolean
})
defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999;
}
.confirm-box {
  background: white; border-radius: 12px; padding: 28px 32px;
  width: 340px; box-shadow: 0 8px 40px rgba(0,0,0,0.15);
}
.confirm-title { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 10px; }
.confirm-msg { font-size: 14px; color: #666; margin-bottom: 24px; line-height: 1.6; }
.confirm-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; }
.btn-cancel {
  padding: 8px 20px; border: 1px solid #ddd; border-radius: 6px;
  background: white; color: #666; cursor: pointer; font-size: 14px;
}
.btn-cancel:hover { background: #f5f5f5; }
.btn-confirm {
  padding: 8px 20px; border: none; border-radius: 6px;
  background: #2d5a27; color: white; cursor: pointer; font-size: 14px;
}
.btn-confirm.danger { background: #e53e3e; }
.btn-confirm:hover { opacity: 0.9; }
</style>

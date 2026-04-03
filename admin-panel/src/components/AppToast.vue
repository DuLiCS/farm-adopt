<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="show" class="app-toast" :class="type">{{ message }}</div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  show: Boolean,
  message: String,
  type: { type: String, default: 'success' }
})
</script>

<style scoped>
.app-toast {
  position: fixed; top: 24px; left: 50%; transform: translateX(-50%);
  padding: 12px 24px; border-radius: 8px; font-size: 14px; font-weight: 500;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12); z-index: 9999; white-space: nowrap;
}
.app-toast.success { background: #2d5a27; color: white; }
.app-toast.error { background: #e53e3e; color: white; }
.app-toast.info { background: #333; color: white; }
.toast-enter-active, .toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(-12px); }
</style>

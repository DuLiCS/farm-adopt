import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/admin-panel/',
  server: {
    host: '0.0.0.0',
    port: 5174,
    proxy: {
      '/auth': { target: 'http://localhost:8000', changeOrigin: true },
      '/admin': { target: 'http://localhost:8000', changeOrigin: true },
      '/plaza': { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
})

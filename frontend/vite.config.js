import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/ssh-gcp-costing/',
  plugins: [react()],
  server: {
    // Dev proxy — forwards API calls to backend
    proxy: {
      '/ssh-gcp-costing-backend': {
        target: process.env.VITE_API_URL || 'http://localhost:9006',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ssh-gcp-costing-backend/, ''),
      }
    }
  }
})

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  envDir: '../',
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8008',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: '../dist',
    sourcemap: false,
  },
  define: {
    // Expose env vars to the app
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
})

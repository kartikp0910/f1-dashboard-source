import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'spa-root-rewrite',
      configureServer(server) {
        server.middlewares.use((request, _response, next) => {
          if (request.url === '/') request.url = '/index.html'
          next()
        })
      }
    }
  ],
  appType: 'spa',
  server: {
    port: 4173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})

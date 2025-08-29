import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import svgr from 'vite-plugin-svgr'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    svgr()
  ],
  build: {
    assetsInlineLimit: 100000000 // Set to a very high number to inline all assets (eg.: images) (base64) rather than load them as separate files
  }
})

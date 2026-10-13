import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Relative asset paths, so the same build works at any URL
  // (GitHub Pages serves it under /Casalia/).
  base: './',
})

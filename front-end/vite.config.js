import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
    server: {
        port: 3008,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8069',  // Use port 8062 here
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ''),
            },
        },
    },
    plugins: [vue()],
});


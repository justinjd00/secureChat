import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

console.log(process.env)

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    define: {
        'process.env': process.env
    },
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },

    server: {
        port: 3000,
        '^/api': {
            target: `${process.env.SERVER_ADDRESS ?? 'http://localhost'}:${process.env.SERVER_PORT ?? '8080'}`,
            ws: true,
            changeOrigin: true,
        },
    },
});

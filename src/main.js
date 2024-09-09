import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router';  // Importiere den Router

const app = createApp(App);
app.use(router);                // Nutze den Router in der App
app.mount('#app');

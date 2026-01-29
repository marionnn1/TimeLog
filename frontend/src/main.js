import './assets/main.css' // 1. Estilos de Tailwind

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router' // 2. Ahora sí encontrará este archivo

const app = createApp(App)

app.use(createPinia())
app.use(router) // 3. Activamos el router

app.mount('#app')
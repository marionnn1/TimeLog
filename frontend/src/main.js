import './assets/main.css' 

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router' 
import { msalInstance } from './auth/AuthConfig' 

async function startApp() {
    try {
        await msalInstance.initialize()
    } catch (error) {
        console.error("Error inicializando MSAL:", error)
    }

    const app = createApp(App)

    app.use(createPinia())
    app.use(router) 

    app.mount('#app')
}

startApp()
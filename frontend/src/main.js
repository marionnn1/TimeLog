import './assets/main.css' 
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router' 
import { msalInstance } from './auth/AuthConfig'

const app = createApp(App)

msalInstance.initialize().then(() => {
    app.use(createPinia())
    app.use(router) 
    app.mount('#app')
}).catch(e => console.error("Error inicializando MSAL", e))
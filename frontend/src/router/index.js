import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        // Aquí es donde definiremos tus páginas (Login, Home, etc.)
        // De momento lo dejamos vacío para que arranque.
    ]
})

export default router
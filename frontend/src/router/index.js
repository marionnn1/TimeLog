import { createRouter, createWebHistory } from 'vue-router'

// 1. Importamos las vistas
import DashboardView from '../views/DashboardView.vue'
import ProjectsView from '../views/ProjectsView.vue'
import ImputacionesView from '../views/ImputacionesView.vue' // <--- NUEVO IMPORT

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard' // Redirección inicial
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView // Vista Semanal (Excel style)
    },
    {
      path: '/imputaciones',
      name: 'imputaciones',
      component: ImputacionesView // Vista Mensual (Histórico) <--- NUEVA RUTA
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectsView
    }
  ]
})

export default router
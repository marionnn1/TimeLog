import { createRouter, createWebHistory } from 'vue-router'

// 1. Importamos los archivos que acabas de crear
import DashboardView from '../views/DashboardView.vue'
import ProjectsView from '../views/ProjectsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard' // Si entran a la raíz, los mandamos al dashboard
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectsView
    }
  ]
})

export default router
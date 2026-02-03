import { createRouter, createWebHistory } from 'vue-router'

// 1. Importamos las vistas
import DashboardView from '../views/DashboardView.vue'
import ProjectsView from '../views/ProjectsView.vue'
import ImputacionesView from '../views/ImputacionesView.vue' // <--- NUEVO IMPORT
import AdminUsersView from '../views/admin/AdminUsersView.vue'
import AdminProjectsView from '@/views/admin/AdminProjectsView.vue'
import AdminAnnouncementsView from '../views/admin/AdminAnnouncementsView.vue'
import AdminAuditView from '../views/admin/AdminAuditView.vue'
import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import AdminTicketsView from '../views/admin/AdminTicketsView.vue'

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
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: AdminUsersView,
      meta: { requiresAuth: true, role: 'admin' }
    },

    {
      path: '/admin/users',
      component: AdminUsersView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/projects-manager',
      component: AdminProjectsView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/announcements',
      component: AdminAnnouncementsView,
      meta: { requiresAuth: true, role: 'admin' }
    },

    {
      path: '/admin/audit',
      component: AdminAuditView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: AdminDashboardView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/tickets',
      name: 'admin-tickets',
      component: AdminTicketsView,
      meta: { requiresAuth: true, role: 'admin' }
    }
  ]
})

export default router
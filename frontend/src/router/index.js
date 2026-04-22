import { createRouter, createWebHistory } from 'vue-router'
import { msalInstance } from '../auth/AuthConfig'

import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ImputacionesView from '../views/ImputacionesView.vue'
import GlobalCalendarView from '../views/GlobalCalendarView.vue'
import MyProjectsView from '../views/MyProjectsView.vue'

// Vistas de Admin
import AdminUsersView from '../views/admin/AdminUsersView.vue'
import AdminProjectsView from '@/views/admin/AdminProjectsView.vue'
import AdminAuditView from '../views/admin/AdminAuditView.vue'
import AdminDashboardView from '../views/admin/AdminDashboardView.vue'

// Vistas de Manager
import ManagerAnalyticsView from '../views/manager/ManagerAnalyticsView.vue'
import ManagerClosingView from '../views/manager/ManagerClosingView.vue'
import ProjectsView from '../views/manager/ProjectsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { layout: 'empty' } },
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/imputaciones', name: 'imputaciones', component: ImputacionesView, meta: { requiresAuth: true } },
    { path: '/calendario-global', name: 'calendario-global', component: GlobalCalendarView, meta: { requiresAuth: true } },
    { path: '/my-projects', name: 'my-projects', component: MyProjectsView, meta: { requiresAuth: true } },
    { path: '/admin/dashboard', name: 'admin-dashboard', component: AdminDashboardView, meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/admin/users', name: 'admin-users', component: AdminUsersView, meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/admin/projects-manager', name: 'admin-projects', component: AdminProjectsView, meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/admin/audit', name: 'admin-audit', component: AdminAuditView, meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/manager/analitica', name: 'manager-analytics', component: ManagerAnalyticsView, meta: { requiresAuth: true, roles: ['admin', 'jp', 'manager'] } },
    { path: '/manager/cierre', name: 'manager-closing', component: ManagerClosingView, meta: { requiresAuth: true, roles: ['admin', 'jp', 'manager'] } },
    { path: '/manager/projects', name: 'manager-projects', component: ProjectsView, meta: { requiresAuth: true, roles: ['admin', 'jp', 'manager'] } }
  ]
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  if (to.path === '/login' && isAuthenticated) {
    return next('/')
  }

  // Lógica de validación de roles robusta
  if (to.meta.roles && to.meta.roles.length > 0) {
    try {
      const activeAccount = msalInstance.getAllAccounts()[0]
      const rolesAzure = activeAccount?.idTokenClaims?.roles || ['tecnico']
      const userRoles = rolesAzure.map(r => r.toLowerCase())

      const tienePermiso = to.meta.roles.some(rolPermitido =>
        userRoles.includes(rolPermitido.toLowerCase())
      )

      if (!tienePermiso) {
        console.warn(`Bloqueo de seguridad: Acceso denegado a '${to.path}' para roles: ${userRoles}`)
        return next('/dashboard') // Redirigir a zona común en lugar de bucle
      }
    } catch (error) {
      console.error('Error verificando roles:', error)
      return next('/dashboard')
    }
  }

  next()
})

export default router
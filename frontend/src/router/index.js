import { createRouter, createWebHistory } from 'vue-router'

// 1. Importamos las vistas
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ImputacionesView from '../views/ImputacionesView.vue'
import GlobalCalendarView from '../views/GlobalCalendarView.vue'

// Vistas de Admin
import AdminUsersView from '../views/admin/AdminUsersView.vue'
import AdminProjectsView from '@/views/admin/AdminProjectsView.vue'
import AdminAuditView from '../views/admin/AdminAuditView.vue'
import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import AdminTicketsView from '../views/admin/AdminTicketsView.vue' // <--- NUEVA VISTA

// Vistas de Manager
import ManagerValidationView from '../views/manager/ManagerValidationView.vue'
import ManagerClosingView from '../views/manager/ManagerClosingView.vue'
import ManagerAnalyticsView from '../views/manager/ManagerAnalyticsView.vue'
import ProjectsView from '../views/manager/ProjectsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // --- RUTA PÚBLICA: LOGIN ---
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { layout: 'empty' } 
    },

    // --- REDIRECCIÓN INICIAL ---
    {
      path: '/',
      redirect: '/dashboard'
    },

    // --- RUTAS COMUNES (PROTEGIDAS) ---
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/imputaciones',
      name: 'imputaciones',
      component: ImputacionesView,
      meta: { requiresAuth: true }
    },
    {
      path: '/calendario-global',
      name: 'calendario-global',
      component: GlobalCalendarView,
      meta: { requiresAuth: true }
    },

    // --- RUTAS ADMIN ---
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: AdminDashboardView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: AdminUsersView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/projects-manager',
      name: 'admin-projects',
      component: AdminProjectsView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/audit',
      name: 'admin-audit',
      component: AdminAuditView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/tickets', // <--- NUEVA RUTA DE TICKETS
      name: 'admin-tickets',
      component: AdminTicketsView,
      meta: { requiresAuth: true, role: 'admin' }
    },

    // --- RUTAS MANAGER ---
    {
      path: '/manager/projects',
      name: 'manager-projects',
      component: ProjectsView,
      meta: { requiresAuth: true, role: 'manager' }
    },
    {
      path: '/manager/validaciones',
      name: 'manager-validaciones',
      component: ManagerValidationView,
      meta: { requiresAuth: true, role: 'manager' }
    },
    {
      path: '/manager/cierre',
      name: 'manager-cierre',
      component: ManagerClosingView,
      meta: { requiresAuth: true, role: 'manager' }
    },
    {
      path: '/manager/analitica',
      name: 'manager-analitica',
      component: ManagerAnalyticsView,
      meta: { requiresAuth: true, role: 'manager' }
    },
  ]
})


router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } 
  else if (to.path === '/login' && isAuthenticated) {
    next('/')
  } 
  else {
    next()
  }
})

export default router
import { createRouter, createWebHistory } from 'vue-router'


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
import AdminTicketsView from '../views/admin/AdminTicketsView.vue' 

// Vistas de Manager
import ManagerAnalyticsView from '../views/manager/ManagerAnalyticsView.vue'
import ManagerClosingView from '../views/manager/ManagerClosingView.vue'
import ProjectsView from '../views/manager/ProjectsView.vue' 
import ManagerValidationView from '../views/manager/ManagerValidationView.vue'

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
    {
      path: '/my-projects',
      name: 'my-projects',
      component: MyProjectsView,
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
      path: '/admin/tickets', 
      name: 'admin-tickets',
      component: AdminTicketsView,
      meta: { requiresAuth: true, role: 'admin' }
    },

    // --- RUTAS MANAGER ---
    {
      path: '/manager/analitica', 
      name: 'manager-analytics',
      component: ManagerAnalyticsView
    },
    {
      path: '/manager/cierre', 
      name: 'manager-closing',
      component: ManagerClosingView
    },
    {
      path: '/manager/projects', 
      name: 'manager-projects',
      component: ProjectsView
    },
    {
      path: '/manager/validaciones', 
      name: 'manager-validation',
      component: ManagerValidationView
    }
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

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  
  if (to.path !== '/login' && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
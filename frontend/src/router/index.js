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

    // --- RUTAS COMUNES (PROTEGIDAS - Todos los roles) ---
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
      meta: { requiresAuth: true, roles: ['admin'] }
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: AdminUsersView,
      meta: { requiresAuth: true, roles: ['admin'] }
    },
    {
      path: '/admin/projects-manager',
      name: 'admin-projects',
      component: AdminProjectsView,
      meta: { requiresAuth: true, roles: ['admin'] }
    },
    {
      path: '/admin/audit',
      name: 'admin-audit',
      component: AdminAuditView,
      meta: { requiresAuth: true, roles: ['admin'] }
    },
    {
      path: '/admin/tickets', 
      name: 'admin-tickets',
      component: AdminTicketsView,
      meta: { requiresAuth: true, roles: ['admin'] }
    },

    // --- RUTAS MANAGER ---
    {
      path: '/manager/analitica', 
      name: 'manager-analytics',
      component: ManagerAnalyticsView,
      meta: { requiresAuth: true, roles: ['admin', 'jp', 'manager'] }
    },
    {
      path: '/manager/cierre', 
      name: 'manager-closing',
      component: ManagerClosingView,
      meta: { requiresAuth: true, roles: ['admin', 'jp', 'manager'] }
    },
    {
      path: '/manager/projects', 
      name: 'manager-projects',
      component: ProjectsView,
      meta: { requiresAuth: true, roles: ['admin', 'jp', 'manager'] }
    },
    {
      path: '/manager/validaciones', 
      name: 'manager-validation',
      component: ManagerValidationView,
      meta: { requiresAuth: true, roles: ['admin', 'jp', 'manager'] }
    }
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

  if (to.meta.roles) {
    try {
      const savedState = localStorage.getItem('timeLog_state')
      let userRole = 'tecnico'
      
      if (savedState) {
        const parsedState = JSON.parse(savedState)
        
        userRole = parsedState.currentUser?.rol?.toLowerCase() || 'tecnico'
      }

      if (!to.meta.roles.includes(userRole)) {
        console.warn(`Bloqueo de seguridad: El rol '${userRole}' intentó acceder a '${to.path}'`)
        return next('/dashboard')
      }
    } catch (error) {
      console.error('Error verificando roles en el router:', error)
      return next('/dashboard')
    }
  }

  next()
})

export default router
<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../composables/useAuth'
import { useDataStore } from '../../stores/dataStore'
import {
  LayoutDashboard, Clock, FolderKanban, FileBarChart, LogOut, ShieldCheck, Calendar,
  CheckCircle, Users, Briefcase, History, Activity, AlertOctagon
} from 'lucide-vue-next'

const router = useRouter()
const store = useDataStore()
const { logout } = useAuth()

const currentUser = computed(() => store.getCurrentUser())
const rolActual = computed(() => currentUser.value?.rol || 'user')

// Lógica de permisos para mostrar/ocultar secciones
const esAdmin = computed(() => rolActual.value === 'admin')
const esJefe = computed(() => rolActual.value === 'manager' || rolActual.value === 'admin' || rolActual.value === 'jp')

const claseLink = "flex items-center gap-3 px-3 py-2.5 rounded-r-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group cursor-pointer border-l-4 border-transparent whitespace-nowrap"
const claseIcono = "w-5 h-5 text-slate-400 group-hover:text-primary transition shrink-0"

const handleLogout = async () => {
  // 1. Limpiamos la persistencia local del selector de cuentas
  localStorage.removeItem('isAuthenticated')

  // 2. Reseteamos el usuario en el store global
  store.setCurrentUser(null)

  // 3. Intentamos el logout de Microsoft si está configurado
  try {
    if (logout) await logout()
  } catch (e) {
    console.log("Cerrando sesión local (MSAL no disponible)")
  }

  // 4. Redirigimos al selector de usuarios
  router.push('/login')
}
</script>

<template>
  <aside
    class="w-64 min-w-[16rem] shrink-0 bg-slate-900 text-white min-h-screen flex flex-col border-r border-slate-800 font-sans transition-all duration-300">

    <div class="h-16 flex items-center justify-center border-b border-slate-800 bg-slate-950 shadow-sm shrink-0">
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <ShieldCheck class="w-5 h-5 text-primary" />
          <h1 class="text-lg font-bold tracking-wide text-white">TimeLog</h1>
        </div>
        <div class="h-4 w-px bg-slate-700"></div>
        <img src="/logo_inetum.png" alt="Logo" class="h-4 w-auto object-contain mt-1.5" />
      </div>
    </div>

    <nav class="flex-1 px-3 py-6 space-y-1 overflow-y-auto overflow-x-hidden no-scrollbar">

      <div class="px-3 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest truncate">Personal</div>

      <router-link to="/dashboard" :class="claseLink">
        <LayoutDashboard :class="claseIcono" />
        <span class="text-sm font-medium truncate">Dashboard Semanal</span>
      </router-link>

      <router-link to="/imputaciones" :class="claseLink">
        <Clock :class="claseIcono" />
        <span class="text-sm font-medium truncate">Mis Imputaciones</span>
      </router-link>

      <router-link to="/calendario-global" :class="claseLink">
        <Calendar :class="claseIcono" />
        <span class="text-sm font-medium truncate">Calendario Global</span>
      </router-link>

      <router-link to="/my-projects" :class="claseLink">
        <FolderKanban :class="claseIcono" />
        <span class="text-sm font-medium truncate">Mis Proyectos</span>
      </router-link>

      <template v-if="esJefe">
        <div class="px-3 mt-8 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest truncate">
          Gestión Equipo
        </div>
        <router-link to="/manager/validaciones" :class="claseLink">
          <CheckCircle :class="claseIcono" />
          <span class="text-sm font-medium truncate">Validar Horas</span>
        </router-link>
        <router-link to="/manager/cierre" :class="claseLink">
          <FileBarChart :class="claseIcono" />
          <span class="text-sm font-medium truncate">Cierre Mensual</span>
        </router-link>
        <router-link to="/manager/projects" :class="claseLink">
          <FolderKanban :class="claseIcono" />
          <span class="text-sm font-medium truncate">Ver Proyectos</span>
        </router-link>
        <router-link to="/manager/analitica" :class="claseLink">
          <Activity :class="claseIcono" />
          <span class="text-sm font-medium truncate">Analítica Equipo</span>
        </router-link>
      </template>

      <template v-if="esAdmin">
        <div class="px-3 mt-8 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest truncate">
          Administración
        </div>
        <router-link to="/admin/dashboard" :class="claseLink">
          <Activity :class="claseIcono" />
          <span class="text-sm font-medium truncate">Centro de Control</span>
        </router-link>
        <router-link to="/admin/users" :class="claseLink">
          <Users :class="claseIcono" />
          <span class="text-sm font-medium truncate">Usuarios</span>
        </router-link>
        <router-link to="/admin/projects-manager" :class="claseLink">
          <Briefcase :class="claseIcono" />
          <span class="text-sm font-medium truncate">Gestión Proyectos</span>
        </router-link>

        <router-link to="/admin/tickets" :class="claseLink">
          <AlertOctagon :class="claseIcono" />
          <span class="text-sm font-medium truncate">Tickets Soporte</span>
        </router-link>

        <router-link to="/admin/audit" :class="claseLink">
          <History :class="claseIcono" />
          <span class="text-sm font-medium truncate">Historial / Logs</span>
        </router-link>
      </template>

    </nav>

    <div class="p-4 border-t border-slate-800 bg-slate-950 shrink-0">
      <div class="flex items-center gap-3 mb-4 pl-1" v-if="currentUser">
        <div
          class="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm text-white shadow-lg relative bg-primary shrink-0 transition-transform hover:scale-105">
          {{ currentUser.iniciales || 'U' }}
          <div v-if="esAdmin"
            class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-slate-900">
          </div>
        </div>
        <div class="overflow-hidden">
          <p class="text-sm font-bold text-white truncate">{{ currentUser.nombre || 'Usuario' }}</p>
          <p class="text-[10px] text-slate-400 truncate uppercase font-black tracking-tighter">{{ currentUser.rol }}</p>
        </div>
      </div>

      <button @click="handleLogout"
        class="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-red-400 hover:bg-slate-900 rounded-lg transition text-xs font-bold uppercase tracking-wider group border border-transparent hover:border-red-900/30">
        <LogOut class="w-4 h-4 group-hover:text-red-400 transition-colors" />
        <span>Cerrar Sesión</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.router-link-active {
  @apply bg-slate-800 text-white border-primary;
}

.router-link-active svg {
  @apply text-primary;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
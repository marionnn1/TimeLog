<script setup>
import { computed } from 'vue'
import {
  // Iconos Generales
  LayoutDashboard, Clock, FolderKanban, FileBarChart, LogOut, ShieldCheck, Calendar, // <--- AÑADIDO CALENDAR
  // Iconos de Gestión (JP)
  CheckCircle,
  Users, Briefcase, Megaphone, History, Ticket, Activity
} from 'lucide-vue-next'


const rolActual = 'admin'

const usuario = {
  nombre: 'Mario León',
  rol: rolActual === 'admin' ? 'Administrador' : (rolActual === 'jp' ? 'Jefe de Proyecto' : 'Técnico Junior'),
  iniciales: 'ML'
}

const esAdmin = computed(() => rolActual === 'admin')
const esJefe = computed(() => rolActual === 'jp' || rolActual === 'admin')

const claseLink = "flex items-center gap-3 px-3 py-2.5 rounded-r-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group cursor-pointer border-l-4 border-transparent whitespace-nowrap"
const claseIcono = "w-5 h-5 text-slate-400 group-hover:text-primary transition shrink-0"
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
        <img src="/logo_inetum.png" alt="Logo" class="h-4 w-auto object-contain opacity-100 mt-1.5" />
      </div>
    </div>

    <nav class="flex-1 px-3 py-6 space-y-1 overflow-y-auto overflow-x-hidden scrollbar-thin scrollbar-thumb-slate-700">

      <div class="px-3 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest truncate">Personal</div>

      <router-link to="/" :class="claseLink">
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

        <router-link to="/manager/proyectos" :class="claseLink">
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

        <router-link to="/admin/audit" :class="claseLink">
          <History :class="claseIcono" />
          <span class="text-sm font-medium truncate">Historial / Logs</span>
        </router-link>
      </template>

    </nav>

    <div class="p-4 border-t border-slate-800 bg-slate-950 shrink-0">
      <div class="flex items-center gap-3 mb-4 pl-1">
        <div class="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm text-white shadow-lg relative bg-primary shrink-0">
          {{ usuario.iniciales }}
          <div v-if="esAdmin"
            class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-slate-900"
            title="Admin">
          </div>
          <div v-else-if="esJefe"
            class="absolute -top-1 -right-1 w-3 h-3 bg-amber-500 rounded-full border-2 border-slate-900"
            title="JP">
          </div>
        </div>
        <div class="overflow-hidden">
          <p class="text-sm font-bold text-white truncate">{{ usuario.nombre }}</p>
          <p class="text-xs text-slate-400 truncate uppercase">{{ usuario.rol }}</p>
        </div>
      </div>

      <button
        class="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-red-400 hover:bg-slate-900 rounded-lg transition text-xs font-bold uppercase tracking-wider">
        <LogOut class="w-4 h-4" />
        <span>Cerrar Sesión</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
/* Solo cambiamos el color del borde y fondo al estar activo */
.router-link-active {
  @apply bg-slate-800 text-white border-primary;
}

.router-link-active svg {
  @apply text-primary;
}
</style>
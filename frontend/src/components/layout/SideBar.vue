<script setup>
import { computed } from 'vue'
import { 
  // Iconos Generales
  LayoutDashboard, Clock, FolderKanban, FileBarChart, LogOut, ShieldCheck,
  // Iconos de Gestión (JP)
  CheckCircle, 
  // Iconos de Admin
  Users, Briefcase, Megaphone, History, Ticket, Activity
} from 'lucide-vue-next'

// --- CONFIGURACIÓN DE ROL ---
// Cambia esto a 'admin', 'jp' o 'user' para probar los menús
const rolActual = 'admin' 

const usuario = {
  nombre: 'Mario León',
  rol: rolActual === 'admin' ? 'Administrador' : (rolActual === 'jp' ? 'Jefe de Proyecto' : 'Técnico Junior'),
  iniciales: 'ML'
}

const esAdmin = computed(() => rolActual === 'admin')
const esJefe = computed(() => rolActual === 'jp' || rolActual === 'admin') 

// Estilos reutilizables (para evitar problemas con @apply)
const claseLink = "flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group cursor-pointer"
const claseIcono = "w-5 h-5 text-slate-400 group-hover:text-[#26AA9B] transition"
</script>

<template>
  <aside class="w-64 bg-slate-900 text-white min-h-screen flex flex-col border-r border-slate-800 font-sans">
    
    <div class="h-16 flex items-center justify-center border-b border-slate-800 bg-slate-950 shadow-sm">
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <ShieldCheck class="w-5 h-5 text-[#26AA9B]" />
          <h1 class="text-lg font-bold tracking-wide text-white">TimeLog</h1>
        </div>
        <div class="h-4 w-px bg-slate-700"></div>
        <img src="/logo_inetum.png" alt="Inetum" class="h-4 w-auto object-contain opacity-100 mt-1.5" />
      </div>
    </div>

    <nav class="flex-1 px-3 py-6 space-y-1 overflow-y-auto">
      
      <div class="px-3 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest">Personal</div>
      
      <router-link to="/" :class="claseLink">
        <LayoutDashboard :class="claseIcono" />
        <span class="text-sm font-medium">Dashboard Semanal</span>
      </router-link>
      
      <router-link to="/imputaciones" :class="claseLink">
        <Clock :class="claseIcono" />
        <span class="text-sm font-medium">Mis Imputaciones</span>
      </router-link>

      <template v-if="esJefe">
        <div class="px-3 mt-8 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest">Gestión Equipo</div>
        
        <router-link to="/validaciones" :class="claseLink">
          <CheckCircle :class="claseIcono" />
          <span class="text-sm font-medium">Validar Horas</span>
        </router-link>

        <router-link to="/projects" :class="claseLink">
          <FolderKanban :class="claseIcono" />
          <span class="text-sm font-medium">Ver Proyectos</span>
        </router-link>

        <router-link to="/reports" :class="claseLink">
          <FileBarChart :class="claseIcono" />
          <span class="text-sm font-medium">Reportes</span>
        </router-link>
      </template>

      <template v-if="esAdmin">
        <div class="px-3 mt-8 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest">Administración</div>

        <router-link to="/admin/dashboard" :class="claseLink">
          <Activity :class="claseIcono" />
          <span class="text-sm font-medium">Centro de Control</span>
        </router-link>

        <router-link to="/admin/tickets" :class="claseLink">
          <Ticket :class="claseIcono" />
          <span class="text-sm font-medium">Incidencias</span>
        </router-link>

        <div class="h-px bg-slate-800 my-2 mx-3"></div> <router-link to="/admin/users" :class="claseLink">
          <Users :class="claseIcono" />
          <span class="text-sm font-medium">Usuarios</span>
        </router-link>
        
        <router-link to="/admin/projects-manager" :class="claseLink">
          <Briefcase :class="claseIcono" />
          <span class="text-sm font-medium">Gestión Proyectos</span>
        </router-link>

        <router-link to="/admin/announcements" :class="claseLink">
          <Megaphone :class="claseIcono" />
          <span class="text-sm font-medium">Anuncios</span>
        </router-link>

        <router-link to="/admin/audit" :class="claseLink">
          <History :class="claseIcono" />
          <span class="text-sm font-medium">Historial / Logs</span>
        </router-link>
      </template>

    </nav>

    <div class="p-4 border-t border-slate-800 bg-slate-950">
      <div class="flex items-center gap-3 mb-4 pl-1">
        <div class="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm text-white shadow-lg relative"
             style="background-color: #26AA9B;">
          {{ usuario.iniciales }}
          <div v-if="esAdmin" class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-slate-900" title="Admin"></div>
          <div v-else-if="esJefe" class="absolute -top-1 -right-1 w-3 h-3 bg-amber-500 rounded-full border-2 border-slate-900" title="JP"></div>
        </div>
        <div class="overflow-hidden">
          <p class="text-sm font-bold text-white truncate">{{ usuario.nombre }}</p>
          <p class="text-xs text-slate-400 truncate uppercase">{{ usuario.rol }}</p>
        </div>
      </div>

      <button class="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-red-400 hover:bg-slate-900 rounded-lg transition text-xs font-bold uppercase tracking-wider">
        <LogOut class="w-4 h-4" />
        <span>Cerrar Sesión</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
/* Estilos para el enlace activo */
.router-link-active {
  background-color: rgb(30 41 59); /* slate-800 */
  color: white;
  border-left: 3px solid #26AA9B; 
}
/* Forzamos el color del icono activo */
.router-link-active svg {
  color: #26AA9B !important; 
}
</style>
<script setup>
import {
    LayoutDashboard,
    Clock,
    FolderKanban,
    FileBarChart,
    LogOut,
    ShieldCheck,
    User // Icono de usuario
} from 'lucide-vue-next'

// Datos del usuario (Simulados, luego vendrán del Login/Entra ID)
const usuario = {
    nombre: 'Mario León', // Nombre del ejemplo del PDF
    rol: 'Técnico Junior',
    iniciales: 'ML'
}
</script>

<template>
    <aside class="w-64 bg-slate-900 text-white min-h-screen flex flex-col border-r border-slate-800 font-sans">
        <div class="h-16 flex items-center px-6 border-b border-slate-800 bg-slate-950 shadow-sm">
            <ShieldCheck class="w-6 h-6 text-[#26AA9B] mr-3" />
            <h1 class="text-lg font-bold tracking-wide">TimeLog</h1>
        </div>

        <nav class="flex-1 px-3 py-6 space-y-1">
            <div class="px-3 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest">Personal</div>

            <router-link to="/"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group">
                <LayoutDashboard class="w-5 h-5 text-slate-400 group-hover:text-[#26AA9B] transition" />
                <span class="text-sm font-medium">Dashboard Semanal</span>
            </router-link>

            <router-link to="/imputaciones"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group">
                <Clock class="w-5 h-5 text-slate-400 group-hover:text-[#26AA9B] transition" />
                <span class="text-sm font-medium">Mis Imputaciones</span>
            </router-link>

            <div class="px-3 mt-8 mb-2 text-xs font-bold text-slate-500 uppercase tracking-widest">Gestión</div>

            <router-link to="/projects"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group">
                <FolderKanban class="w-5 h-5 text-slate-400 group-hover:text-[#26AA9B] transition" />
                <span class="text-sm font-medium">Proyectos</span>
            </router-link>

            <router-link to="/reports"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group">
                <FileBarChart class="w-5 h-5 text-slate-400 group-hover:text-[#26AA9B] transition" />
                <span class="text-sm font-medium">Reportes</span>
            </router-link>
        </nav>

        <div class="p-4 border-t border-slate-800 bg-slate-950">

            <div class="flex items-center gap-3 mb-4 pl-1">
                <div class="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm text-white shadow-lg"
                    style="background-color: #26AA9B;">
                    {{ usuario.iniciales }}
                </div>
                <div class="overflow-hidden">
                    <p class="text-sm font-bold text-white truncate">{{ usuario.nombre }}</p>
                    <p class="text-xs text-slate-400 truncate">{{ usuario.rol }}</p>
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
.router-link-active {
    background-color: rgb(30 41 59);
    color: white;
    border-left: 3px solid #26AA9B;
}

.router-link-active svg {
    color: #26AA9B;
}
</style>
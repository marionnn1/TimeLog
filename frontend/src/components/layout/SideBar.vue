<script setup>
// Importamos los iconos profesionales
import {
    LayoutDashboard,
    Clock,
    FolderKanban,
    FileBarChart,
    LogOut,
    ShieldCheck
} from 'lucide-vue-next'
</script>

<template>
    <aside class="w-64 bg-slate-900 text-white min-h-screen flex flex-col border-r border-slate-800">
        <div class="h-16 flex items-center px-6 border-b border-slate-800 bg-slate-950">
            <ShieldCheck class="w-6 h-6 text-blue-500 mr-3" />
            <h1 class="text-lg font-bold tracking-wide">TimeLog</h1>
        </div>

        <nav class="flex-1 px-3 py-6 space-y-1">

            <div class="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Personal
            </div>

            <router-link to="/"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group">
                <LayoutDashboard class="w-5 h-5 text-slate-400 group-hover:text-white transition" />
                <span class="text-sm font-medium">Dashboard</span>
            </router-link>

            <router-link to="/imputaciones"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group">
                <Clock class="w-5 h-5 text-slate-400 group-hover:text-white transition" />
                <span class="text-sm font-medium">Mis Imputaciones</span>
            </router-link>

            <div class="px-3 mt-8 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Gestión
            </div>

            <router-link to="/projects"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group">
                <FolderKanban class="w-5 h-5 text-slate-400 group-hover:text-white transition" />
                <span class="text-sm font-medium">Proyectos</span>
            </router-link>

            <router-link to="/reports"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition group">
                <FileBarChart class="w-5 h-5 text-slate-400 group-hover:text-white transition" />
                <span class="text-sm font-medium">Reportes</span>
            </router-link>

        </nav>

        <div class="p-4 border-t border-slate-800 bg-slate-950">
            <button
                class="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-red-400 hover:bg-slate-900 rounded-lg transition text-sm font-medium">
                <LogOut class="w-5 h-5" />
                <span>Cerrar Sesión</span>
            </button>
        </div>
    </aside>
</template>

<style scoped>
/* Estilo activo automático de Vue Router */
.router-link-active {
    background-color: rgb(30 41 59);
    /* bg-slate-800 */
    color: white;
}

.router-link-active svg {
    color: rgb(59 130 246);
    /* text-blue-500 */
}
</style>
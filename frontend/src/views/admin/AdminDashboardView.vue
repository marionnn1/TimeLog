<script setup>
import { computed } from 'vue'
import { Users, FolderOpen, Ticket, Activity, CheckCircle, AlertCircle } from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()
const stats = computed(() => store.getStats())
</script>

<template>
    <div class="h-full p-6 bg-gray-50 flex flex-col gap-6 font-sans overflow-y-auto">

        <div>
            <h1 class="text-2xl font-bold text-[#232D4B]">Centro de Control</h1>
            <p class="text-sm text-gray-500">Visión general del estado del sistema y soporte.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

            <div
                class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between hover:border-[#26AA9B] transition group">
                <div>
                    <p class="text-xs font-bold text-gray-400 uppercase tracking-wider">Usuarios Totales</p>
                    <p class="text-3xl font-bold text-[#232D4B] mt-1">{{ stats.totalUsuarios }}</p>
                </div>
                <div class="p-3 rounded-full bg-blue-50 text-blue-600 group-hover:bg-blue-100 transition">
                    <Users class="w-6 h-6" />
                </div>
            </div>

            <div
                class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between hover:border-[#26AA9B] transition group">
                <div>
                    <p class="text-xs font-bold text-gray-400 uppercase tracking-wider">Proyectos Activos</p>
                    <p class="text-3xl font-bold text-[#232D4B] mt-1">{{ stats.proyectosActivos }}</p>
                </div>
                <div class="p-3 rounded-full bg-emerald-50 text-emerald-600 group-hover:bg-emerald-100 transition">
                    <FolderOpen class="w-6 h-6" />
                </div>
            </div>

            <div
                class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between hover:border-amber-400 transition group relative overflow-hidden">
                <div class="absolute right-0 top-0 w-16 h-16 bg-amber-400/10 rounded-bl-full"></div>
                <div>
                    <p class="text-xs font-bold text-gray-400 uppercase tracking-wider">Tickets Pendientes</p>
                    <p class="text-3xl font-bold text-amber-600 mt-1">{{ stats.ticketsPendientes }}</p>
                    <p class="text-xs text-gray-400 mt-1">de {{ stats.ticketsTotales }} totales</p>
                </div>
                <div class="p-3 rounded-full bg-amber-50 text-amber-600 group-hover:bg-amber-100 transition z-10">
                    <Ticket class="w-6 h-6" />
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
            <div
                class="lg:col-span-2 bg-[#1e293b] rounded-xl p-6 text-white shadow-lg relative overflow-hidden flex flex-col justify-between">
                <div
                    class="absolute top-0 right-0 p-40 bg-[#26AA9B] rounded-full blur-[100px] opacity-10 pointer-events-none">
                </div>

                <div class="flex justify-between items-start relative z-10">
                    <div>
                        <h3 class="font-bold text-lg flex items-center gap-2">
                            <Activity class="w-5 h-5 text-[#26AA9B]" /> Monitor de Sistema
                        </h3>
                        <p class="text-slate-400 text-sm">Rendimiento en tiempo real</p>
                    </div>
                    <span
                        class="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full text-xs font-bold border border-emerald-500/50 flex items-center gap-2 animate-pulse">
                        Operativo
                    </span>
                </div>

                <div class="grid grid-cols-3 gap-4 mt-8 relative z-10">
                    <div class="bg-white/5 p-4 rounded-lg border border-white/10">
                        <p class="text-xs text-slate-400 mb-1">Base de Datos</p>
                        <div class="text-xl font-mono font-bold text-white">Conectada</div>
                    </div>
                    <div class="bg-white/5 p-4 rounded-lg border border-white/10">
                        <p class="text-xs text-slate-400 mb-1">Latencia API</p>
                        <div class="text-xl font-mono font-bold text-[#26AA9B]">24ms</div>
                    </div>
                    <div class="bg-white/5 p-4 rounded-lg border border-white/10">
                        <p class="text-xs text-slate-400 mb-1">Último Backup</p>
                        <div class="text-xl font-mono font-bold text-white">04:00 AM</div>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm flex flex-col gap-3">
                <h3 class="font-bold text-gray-700 text-sm uppercase mb-2">Acciones Rápidas</h3>
                <button
                    class="w-full text-left p-3 rounded-lg bg-gray-50 hover:bg-gray-100 flex items-center gap-3 transition text-sm font-medium text-gray-600">
                    <div class="w-2 h-2 rounded-full bg-[#26AA9B]"></div> Nuevo Comunicado Global
                </button>
                <button
                    class="w-full text-left p-3 rounded-lg bg-gray-50 hover:bg-gray-100 flex items-center gap-3 transition text-sm font-medium text-gray-600">
                    <div class="w-2 h-2 rounded-full bg-blue-500"></div> Exportar Logs de Auditoría
                </button>
                <button
                    class="w-full text-left p-3 rounded-lg bg-gray-50 hover:bg-gray-100 flex items-center gap-3 transition text-sm font-medium text-gray-600">
                    <div class="w-2 h-2 rounded-full bg-amber-500"></div> Revisar Tickets Críticos
                </button>
            </div>
        </div>
    </div>
</template>
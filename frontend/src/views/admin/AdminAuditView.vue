<script setup>
import { ref, computed } from 'vue'
import { History, Search, ShieldAlert } from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()

// --- ESTADO ---
const logs = computed(() => store.getLogs())
const busqueda = ref('')
const filtroGravedad = ref('todos')

// --- LÓGICA DE FILTRADO ---
const logsFiltrados = computed(() => {
    return logs.value.filter(log => {
        const textoBusqueda = busqueda.value.toLowerCase()
        
        const coincideTexto = 
            log.actor.toLowerCase().includes(textoBusqueda) ||
            log.accion.toLowerCase().includes(textoBusqueda) ||
            log.detalle.toLowerCase().includes(textoBusqueda)

        const coincideFiltro = filtroGravedad.value === 'todos' || log.gravedad === filtroGravedad.value

        return coincideTexto && coincideFiltro
    })
})

// --- ESTILOS ---
const obtenerEstiloBadge = (gravedad) => {
    if (gravedad === 'danger')  return 'bg-red-100 text-red-700 border-red-200'
    if (gravedad === 'warning') return 'bg-amber-100 text-amber-700 border-amber-200'
    if (gravedad === 'system')  return 'bg-slate-100 text-slate-700 border-slate-200'
    
    return 'bg-blue-50 text-blue-700 border-blue-200'
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto">

        <div>
            <h1 class="text-2xl font-bold text-[#232D4B] flex items-center gap-2">
                <History class="w-6 h-6 text-[#26AA9B]" /> Auditoría e Historial
            </h1>
            <p class="text-sm text-gray-500 mt-1">Registro centralizado de eventos.</p>
        </div>

        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center">
            
            <div class="relative w-full md:w-96">
                <Search class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                <input 
                    v-model="busqueda" 
                    type="text" 
                    placeholder="Buscar por usuario, acción..."
                    class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm focus:border-[#26AA9B] outline-none transition"
                >
            </div>

            <div class="flex gap-2 bg-gray-100 p-1 rounded-lg">
                <button 
                    @click="filtroGravedad = 'todos'"
                    class="px-3 py-1.5 rounded-md text-xs font-bold transition"
                    :class="filtroGravedad === 'todos' ? 'bg-white shadow text-[#232D4B]' : 'text-gray-500'">
                    Todos
                </button>
                <button 
                    @click="filtroGravedad = 'danger'"
                    class="px-3 py-1.5 rounded-md text-xs font-bold transition"
                    :class="filtroGravedad === 'danger' ? 'bg-white shadow text-red-600' : 'text-gray-500'">
                    Críticos
                </button>
                <button 
                    @click="filtroGravedad = 'warning'"
                    class="px-3 py-1.5 rounded-md text-xs font-bold transition"
                    :class="filtroGravedad === 'warning' ? 'bg-white shadow text-amber-600' : 'text-gray-500'">
                    Alertas
                </button>
                <button 
                    @click="filtroGravedad = 'info'"
                    class="px-3 py-1.5 rounded-md text-xs font-bold transition"
                    :class="filtroGravedad === 'info' ? 'bg-white shadow text-blue-600' : 'text-gray-500'">
                    Info
                </button>
            </div>
        </div>

        <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden flex-1">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 text-xs uppercase tracking-wider text-slate-500 border-b border-gray-200">
                            <th class="px-6 py-3 font-bold">Fecha</th>
                            <th class="px-6 py-3 font-bold">Actor</th>
                            <th class="px-6 py-3 font-bold">Acción</th>
                            <th class="px-6 py-3 font-bold">Detalle</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 text-sm">
                        <tr v-for="log in logsFiltrados" :key="log.id" class="hover:bg-slate-50 transition">
                            <td class="px-6 py-4 font-mono text-slate-500 text-xs whitespace-nowrap">
                                {{ log.fecha }}
                            </td>
                            
                            <td class="px-6 py-4 font-bold text-[#232D4B]">
                                {{ log.actor }}
                            </td>
                            
                            <td class="px-6 py-4">
                                <span 
                                    class="px-2 py-1 rounded-md text-[10px] font-black uppercase tracking-widest border"
                                    :class="obtenerEstiloBadge(log.gravedad)">
                                    {{ log.accion }}
                                </span>
                            </td>
                            
                            <td class="px-6 py-4 text-slate-600 font-medium">
                                {{ log.detalle }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div v-if="logsFiltrados.length === 0" class="p-12 text-center text-gray-400">
                <ShieldAlert class="w-12 h-12 mx-auto mb-3 opacity-20" />
                <p class="font-medium">No se encontraron registros.</p>
            </div>
        </div>
    </div>
</template>
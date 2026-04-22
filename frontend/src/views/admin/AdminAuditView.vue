<script setup>
import { ref, computed, onMounted } from 'vue'
import { History, Search, ShieldAlert, Loader2, Filter, AlertTriangle } from 'lucide-vue-next'
import AdminAPI from '../../services/AdminAPI'
import ToastNotification from '@/components/common/ToastNotification.vue'

const logs = ref([])
const cargando = ref(true)
const busqueda = ref('')
const filtroGravedad = ref('todos')
const filtroCategoria = ref('todas') 

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null
const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => { toast.value.show = false }, 3000)
}

const cargarLogs = async () => {
    try {
        cargando.value = true
        const json = await AdminAPI.getAuditoria()
        if (json.status === 'success') {
            logs.value = json.data
        } else {
            showToast("No se pudieron cargar los logs de auditoría", "error")
        }
    } catch (error) {
        showToast("Error de conexión al cargar el historial", "error")
    } finally {
        cargando.value = false
    }
}

onMounted(cargarLogs)

const getCategoriaDeLog = (log) => {
    const accion = (log.accion || '').toLowerCase()
    const detalle = (log.detalle || '').toLowerCase()

    if (accion.includes('usuario') || accion.includes('baja lógica') || (accion.includes('borrado físico') && detalle.includes('usuario'))) {
        return 'usuarios'
    }
    if (accion.includes('cliente')) {
        return 'clientes'
    }
    if (accion.includes('proyecto') || accion.includes('cambio estado') || (accion.includes('borrado físico') && detalle.includes('proyecto'))) {
        return 'proyectos'
    }
    if (accion.includes('cierre') || accion.includes('reapertura')) {
        return 'cierres'
    }
    if (accion.includes('edición de horas') || accion.includes('corrección') || detalle.includes('horas')) {
        return 'horas'
    }
    
    return 'otras'
}

const logsFiltrados = computed(() => {
    return logs.value.filter(log => {
        const txt = busqueda.value.toLowerCase()
        const matchTxt = log.actor.toLowerCase().includes(txt) || 
                         log.accion.toLowerCase().includes(txt) || 
                         log.detalle.toLowerCase().includes(txt)
                         
        const matchGravedad = filtroGravedad.value === 'todos' || log.gravedad === filtroGravedad.value
        const matchCategoria = filtroCategoria.value === 'todas' || getCategoriaDeLog(log) === filtroCategoria.value

        return matchTxt && matchGravedad && matchCategoria
    })
})

// NUEVO: ESTILO POR CATEGORÍA
const obtenerEstiloAccion = (log) => {
    const categoria = getCategoriaDeLog(log);
    switch (categoria) {
        case 'usuarios':  return 'bg-purple-100 text-purple-700 border-purple-300';
        case 'clientes':  return 'bg-pink-100 text-pink-700 border-pink-300';
        case 'proyectos': return 'bg-emerald-100 text-emerald-700 border-emerald-300';
        case 'cierres':   return 'bg-orange-100 text-orange-700 border-orange-300';
        case 'horas':     return 'bg-cyan-100 text-cyan-700 border-cyan-300';
        default:          return 'bg-slate-100 text-slate-700 border-slate-300';
    }
}

// NUEVO: PUNTO DE COLOR PARA LA GRAVEDAD
const obtenerColorGravedad = (gravedad) => {
    if (gravedad === 'danger')  return 'bg-red-500 shadow-[0_0_5px_rgba(239,68,68,0.6)]'
    if (gravedad === 'warning') return 'bg-amber-500 shadow-[0_0_5px_rgba(245,158,11,0.6)]'
    if (gravedad === 'info')    return 'bg-blue-500 shadow-[0_0_5px_rgba(59,130,246,0.6)]'
    return 'bg-slate-400'
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto relative pb-10">
        <div>
            <h1 class="text-2xl font-bold text-[#232D4B] flex items-center gap-2">
                <History class="w-6 h-6 text-[#26AA9B]" /> Auditoría e Historial
            </h1>
            <p class="text-sm text-slate-500 mt-1">Registro de actividad administrativa y eventos del sistema.</p>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col gap-5 shrink-0">
            
            <div class="relative w-full">
                <Search class="absolute left-4 top-3.5 w-4 h-4 text-gray-400" />
                <input v-model="busqueda" type="text" placeholder="Buscar por usuario, acción o detalle..." 
                       class="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:border-[#26AA9B] focus:ring-4 focus:ring-[#26AA9B]/10 outline-none transition-all">
            </div>

            <div class="flex flex-col xl:flex-row justify-between gap-5">
                
                <div class="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1 w-full xl:w-auto">
                    <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mr-2 shrink-0 flex items-center gap-1"><Filter class="w-3 h-3"/> Área</span>
                    
                    <button @click="filtroCategoria = 'todas'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroCategoria === 'todas' ? 'bg-slate-800 text-white border-slate-800 shadow-md' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Todas
                    </button>
                    <button @click="filtroCategoria = 'usuarios'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroCategoria === 'usuarios' ? 'bg-purple-100 text-purple-700 border-purple-300 shadow-sm' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Usuarios
                    </button>
                    <button @click="filtroCategoria = 'clientes'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroCategoria === 'clientes' ? 'bg-pink-100 text-pink-700 border-pink-300 shadow-sm' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Clientes
                    </button>
                    <button @click="filtroCategoria = 'proyectos'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroCategoria === 'proyectos' ? 'bg-emerald-100 text-emerald-700 border-emerald-300 shadow-sm' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Proyectos
                    </button>
                    <button @click="filtroCategoria = 'cierres'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroCategoria === 'cierres' ? 'bg-orange-100 text-orange-700 border-orange-300 shadow-sm' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Cierres
                    </button>
                    <button @click="filtroCategoria = 'horas'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroCategoria === 'horas' ? 'bg-cyan-100 text-cyan-700 border-cyan-300 shadow-sm' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Horas
                    </button>
                </div>

                <div class="hidden xl:block w-px h-8 bg-gray-200"></div>

                <div class="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1 w-full xl:w-auto shrink-0">
                    <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mr-2 shrink-0 flex items-center gap-1"><AlertTriangle class="w-3 h-3"/> Nivel</span>
                    
                    <button @click="filtroGravedad = 'todos'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroGravedad === 'todos' ? 'bg-slate-800 text-white border-slate-800 shadow-md' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Todos
                    </button>
                    <button @click="filtroGravedad = 'danger'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroGravedad === 'danger' ? 'bg-red-500 text-white border-red-600 shadow-md' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Críticos
                    </button>
                    <button @click="filtroGravedad = 'warning'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroGravedad === 'warning' ? 'bg-amber-500 text-white border-amber-600 shadow-md' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Alertas
                    </button>
                    <button @click="filtroGravedad = 'info'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 border" 
                            :class="filtroGravedad === 'info' ? 'bg-blue-500 text-white border-blue-600 shadow-md' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
                        Info
                    </button>
                </div>

            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden flex-1 relative min-h-[400px]">
            <div v-if="cargando" class="absolute inset-0 flex items-center justify-center bg-white/80 z-10">
                <Loader2 class="w-8 h-8 text-[#26AA9B] animate-spin" />
            </div>

            <div class="overflow-x-auto h-full scrollbar-thin">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 text-xs uppercase text-slate-500 border-b border-gray-200">
                            <th class="px-6 py-4 font-bold tracking-wider">Fecha</th>
                            <th class="px-6 py-4 font-bold tracking-wider">Actor</th>
                            <th class="px-6 py-4 font-bold tracking-wider">Acción</th>
                            <th class="px-6 py-4 font-bold tracking-wider">Detalle</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 text-sm">
                        <tr v-for="log in logsFiltrados" :key="log.id" class="hover:bg-slate-50 transition-colors">
                            <td class="px-6 py-4 font-mono text-slate-500 text-xs whitespace-nowrap">{{ log.fecha }}</td>
                            <td class="px-6 py-4 font-bold text-[#232D4B] whitespace-nowrap">{{ log.actor }}</td>
                            
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center gap-2">
                                    <div class="w-2 h-2 rounded-full" :class="obtenerColorGravedad(log.gravedad)" :title="log.gravedad"></div>
                                    <span class="px-2.5 py-1 rounded-md text-[10px] font-black uppercase border" :class="obtenerEstiloAccion(log)">
                                        {{ log.accion }}
                                    </span>
                                </div>
                            </td>
                            
                            <td class="px-6 py-4 text-slate-600 leading-relaxed min-w-[300px]">{{ log.detalle }}</td>
                        </tr>
                    </tbody>
                </table>
                
                <div v-if="!cargando && logsFiltrados.length === 0" class="flex flex-col items-center justify-center h-64 text-gray-400">
                    <ShieldAlert class="w-12 h-12 mb-3 opacity-20" />
                    <p class="font-medium text-slate-500">No se encontraron registros que coincidan con tus filtros.</p>
                    <button @click="busqueda=''; filtroCategoria='todas'; filtroGravedad='todos'" class="mt-4 text-sm text-blue-600 font-bold hover:underline">
                        Limpiar filtros
                    </button>
                </div>
            </div>
        </div>

        <ToastNotification
            :show="toast.show"
            :message="toast.message"
            :type="toast.type"
            @close="toast.show = false"
        />
    </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
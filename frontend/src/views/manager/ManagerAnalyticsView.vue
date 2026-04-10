<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import ManagerAPI from '../../services/ManagerAPI'
import {
    Users, Activity, FileSpreadsheet, Briefcase, Building2
} from 'lucide-vue-next'
import ToastNotification from '../../components/common/ToastNotification.vue'

const hoy = new Date()
const anioActual = hoy.getFullYear()
const mesActualNum = String(hoy.getMonth() + 1).padStart(2, '0')
const mesActual = `${anioActual}-${mesActualNum}`

const mesAnalisis = ref(mesActual)
const isLoading = ref(false)

const totalHorasReales = ref(0)
const totalCapacidadEquipo = ref(0) 
const jerarquiaClientes = ref([]) 
const cargaEmpleados = ref([])

const vistaActual = ref('proyectos') 

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => { toast.value.show = false }, 3000)
}

const fetchAnalyticsData = async () => {
    isLoading.value = true
    try {
        const response = await ManagerAPI.getAnalytics(mesAnalisis.value)
        const data = response.data?.data || response.data
        
        totalHorasReales.value = data.totalHorasImputadas || 0
        totalCapacidadEquipo.value = data.totalCapacidadTeorica || 0 
        jerarquiaClientes.value = data.clientesStats || [] 
        cargaEmpleados.value = data.cargaEmpleados || []
    } catch (error) {
        showToast("Error al conectar con el servidor", "error")
    } finally {
        isLoading.value = false
    }
}

onMounted(fetchAnalyticsData)
watch(mesAnalisis, fetchAnalyticsData)

const mediaHorasEquipo = computed(() => {
    if (cargaEmpleados.value.length === 0) return 0
    return Math.round(totalHorasReales.value / cargaEmpleados.value.length)
})

const empleadosAltaActividad = computed(() => cargaEmpleados.value.filter(e => e.horas > (e.capacidad || 160)).length)

const getBarColor = (horas, capacidad) => {
    const umbral = capacidad || 160
    if (horas > umbral) return 'bg-rose-500' 
    return 'bg-emerald-500' 
}

const exportarReporte = () => {
    const headers = ['Empleado', 'Rol', 'Horas Imputadas', 'Objetivo del Mes']
    const rows = cargaEmpleados.value.map(emp => [emp.nombre, emp.rol, emp.horas, emp.capacidad])
    const csvContent = [headers.join(';'), ...rows.map(row => row.join(';'))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `reporte_horas_${mesAnalisis.value}.csv`
    link.click()
    showToast('Reporte descargado correctamente', 'success')
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-slate-50 p-8 gap-8 overflow-y-auto">

        <div class="flex flex-col md:flex-row justify-between items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div>
                <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-3">
                    <Activity class="w-8 h-8 text-emerald-600" /> Analítica y Control
                </h1>
                <p class="text-slate-500 text-sm mt-1">Visión global de la actividad del equipo para {{ mesAnalisis }}</p>
            </div>
            <div class="flex items-center gap-3">
                <input type="month" v-model="mesAnalisis" class="px-4 py-2 border border-slate-300 rounded-lg font-bold text-slate-700 focus:ring-2 focus:ring-emerald-500 outline-none">
                <button @click="exportarReporte" class="flex items-center gap-2 bg-slate-800 hover:bg-slate-900 text-white px-5 py-2.5 rounded-lg font-bold text-sm transition">
                    <FileSpreadsheet class="w-4 h-4" /> Exportar CSV
                </button>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-l-indigo-500">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Total Horas Imputadas</p>
                <div class="flex items-baseline gap-2 mt-2">
                    <h3 class="text-4xl font-extrabold text-slate-800">{{ totalHorasReales }}h</h3>
                    <span class="text-sm font-bold text-slate-400">/ {{ totalCapacidadEquipo }}h teóricas</span>
                </div>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-l-emerald-500">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Media por Empleado</p>
                <h3 class="text-4xl font-extrabold text-slate-800 mt-2">{{ mediaHorasEquipo }}h</h3>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-l-rose-500">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Exceso Horas (Horas Extra)</p>
                <h3 class="text-4xl font-extrabold text-slate-800 mt-2">{{ empleadosAltaActividad }} <span class="text-sm font-medium text-slate-500">empleados</span></h3>
            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex-1 flex flex-col">
            
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4 border-b border-slate-100 pb-4">
                <h3 class="font-bold text-slate-800 flex items-center gap-2">
                    <component :is="vistaActual === 'proyectos' ? Briefcase : Users" class="w-5 h-5 text-slate-400" />
                    {{ vistaActual === 'proyectos' ? 'Esfuerzo por Cliente y Proyecto' : 'Desglose Individual y Control' }}
                </h3>
                
                <div class="flex bg-slate-100 p-1 rounded-xl">
                    <button @click="vistaActual = 'proyectos'"
                        :class="vistaActual === 'proyectos' ? 'bg-white shadow-sm text-emerald-600 font-bold' : 'text-slate-500 hover:text-slate-700'"
                        class="px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2">
                        <Briefcase class="w-4 h-4" /> Ver Proyectos
                    </button>
                    <button @click="vistaActual = 'usuarios'"
                        :class="vistaActual === 'usuarios' ? 'bg-white shadow-sm text-emerald-600 font-bold' : 'text-slate-500 hover:text-slate-700'"
                        class="px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2">
                        <Users class="w-4 h-4" /> Ver Empleados
                    </button>
                </div>
            </div>
            
            <div v-if="isLoading" class="flex flex-col items-center justify-center py-10 opacity-50 flex-1">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500 mb-4"></div>
                <p class="text-sm text-slate-500">Calculando analítica del mes...</p>
            </div>

            <div v-else class="flex-1">
                
                <div v-if="vistaActual === 'proyectos'" class="space-y-8">
                    <div v-for="cliente in jerarquiaClientes" :key="cliente.cliente" class="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
                        <div class="bg-slate-50 border-b border-slate-200 p-5 flex justify-between items-center">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600">
                                    <Building2 class="w-5 h-5" />
                                </div>
                                <div>
                                    <h2 class="text-xl font-bold text-slate-800">{{ cliente.cliente }}</h2>
                                    <p class="text-xs text-slate-500 font-medium">{{ cliente.proyectos.length }} proyectos con actividad este mes</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <span class="text-2xl font-black text-indigo-600">{{ cliente.horas_totales }}<span class="text-sm font-medium text-indigo-400 ml-1">h</span></span>
                                <span class="text-[10px] text-slate-400 block uppercase tracking-widest font-bold">Total Facturable</span>
                            </div>
                        </div>

                        <div class="p-5 grid grid-cols-1 xl:grid-cols-2 gap-6 bg-white">
                            <div v-for="proj in cliente.proyectos" :key="proj.nombre" class="flex flex-col bg-white border border-slate-200 rounded-xl shadow-sm hover:border-emerald-300 transition-colors overflow-hidden">
                                <div class="bg-white p-4 border-b border-slate-100 flex justify-between items-center">
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600 shrink-0">
                                            <Briefcase class="w-4 h-4" />
                                        </div>
                                        <span class="font-bold text-slate-700 text-base truncate" :title="proj.nombre">{{ proj.nombre }}</span>
                                    </div>
                                    <div class="bg-emerald-50 px-3 py-1 rounded-lg border border-emerald-100 shrink-0">
                                        <span class="font-bold text-emerald-700">{{ proj.horas_totales }}h</span>
                                    </div>
                                </div>

                                <div class="flex flex-col gap-1 p-3 bg-slate-50/50 flex-1 max-h-[300px] overflow-y-auto scrollbar-thin">
                                    <div v-for="user in proj.usuarios" :key="user.usuario_id" class="flex items-center justify-between p-2.5 bg-white rounded-lg border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                                        <div class="flex items-center gap-3 min-w-0">
                                            
                                            <img v-if="user.foto" :src="'data:image/jpeg;base64,' + user.foto" alt="Avatar" class="w-8 h-8 rounded-full object-cover border border-slate-200 shadow-sm shrink-0" />
                                            <div v-else class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-600 shrink-0">
                                                {{ user.avatar }}
                                            </div>

                                            <div class="truncate">
                                                <span class="text-sm font-bold text-slate-700 block truncate">{{ user.nombre }}</span>
                                                <span class="text-[10px] text-slate-400 uppercase tracking-wider">{{ user.rol }}</span>
                                            </div>
                                        </div>
                                        <div class="flex items-center gap-3 shrink-0 ml-2">
                                            <div class="flex flex-col items-end">
                                                <span class="font-mono font-bold text-slate-800">{{ user.horas }}h</span>
                                                <span class="text-[10px] font-bold text-emerald-600">{{ Math.round((user.horas / (proj.horas_totales || 1)) * 100) }}%</span>
                                            </div>
                                            <div class="w-12 h-1.5 bg-slate-100 rounded-full overflow-hidden hidden sm:block">
                                                <div class="h-full bg-emerald-400" :style="{ width: `${Math.round((user.horas / (proj.horas_totales || 1)) * 100)}%` }"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div v-for="emp in cargaEmpleados" :key="emp.nombre" class="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition">
                        
                        <div class="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                            <div class="flex items-center gap-3">
                                
                                <img v-if="emp.foto" :src="'data:image/jpeg;base64,' + emp.foto" alt="Avatar" class="w-10 h-10 rounded-full object-cover border border-slate-200 shadow-sm shrink-0" />
                                <div v-else class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-sm font-bold text-indigo-700 shrink-0">
                                    {{ emp.avatar }}
                                </div>

                                <div>
                                    <span class="font-bold text-slate-800 block text-lg">{{ emp.nombre }}</span>
                                    <span class="text-xs font-medium text-slate-500 uppercase tracking-wider">{{ emp.rol }}</span>
                                </div>
                            </div>
                            <div class="text-right flex flex-col items-end">
                                <div class="flex items-baseline gap-1">
                                    <span class="text-xl font-black" :class="emp.horas > emp.capacidad ? 'text-rose-600' : 'text-slate-800'">
                                        {{ emp.horas }}h
                                    </span>
                                    <span class="text-xs font-bold text-slate-400">/ {{ emp.capacidad }}h</span>
                                </div>
                                <span class="text-[10px] font-bold px-2 py-0.5 rounded-md mt-1 uppercase" 
                                      :class="emp.horas > emp.capacidad ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'">
                                    {{ Math.round((emp.horas / (emp.capacidad || 1)) * 100) }}% Ocupación
                                </span>
                            </div>
                        </div>

                        <div class="w-full h-1.5 bg-slate-100">
                            <div class="h-full transition-all duration-1000" 
                                :class="getBarColor(emp.horas, emp.capacidad)" 
                                :style="`width: ${Math.min((emp.horas / (emp.capacidad || 1)) * 100, 100)}%`">
                            </div>
                        </div>

                        <div class="p-4">
                            <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-3">Distribución del Esfuerzo</p>
                            
                            <div v-if="emp.desglose_clientes && emp.desglose_clientes.length > 0" class="flex flex-col gap-5">
                                <div v-for="grupo in emp.desglose_clientes" :key="grupo.cliente" class="flex flex-col gap-2">
                                    
                                    <div class="flex items-center gap-2 pb-1 border-b border-slate-100">
                                        <Building2 class="w-3.5 h-3.5 text-slate-400" />
                                        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-widest truncate" :title="grupo.cliente">{{ grupo.cliente }}</span>
                                        <span class="text-[10px] text-slate-400 ml-auto whitespace-nowrap">{{ grupo.horas_totales }}h en total</span>
                                    </div>
                                    
                                    <div v-for="proj in grupo.proyectos" :key="proj.nombre" class="flex justify-between items-center bg-white border border-slate-100 p-2.5 rounded-lg hover:border-indigo-200 shadow-sm transition-colors">
                                        <div class="flex items-center gap-3 min-w-0">
                                            <div class="w-7 h-7 rounded bg-slate-50 border border-slate-100 flex items-center justify-center shrink-0">
                                                <Briefcase class="w-3.5 h-3.5 text-indigo-500" />
                                            </div>
                                            <span class="text-sm font-bold text-slate-700 truncate max-w-[160px] xl:max-w-[200px]" :title="proj.nombre">{{ proj.nombre }}</span>
                                        </div>

                                        <div class="flex items-center gap-3 shrink-0 ml-2">
                                            <div class="flex flex-col items-end">
                                                <span class="font-mono font-bold text-slate-800">{{ proj.horas }}h</span>
                                                <span class="text-[10px] font-bold text-indigo-600">{{ Math.round((proj.horas / (emp.horas || 1)) * 100) }}%</span>
                                            </div>
                                            <div class="w-12 h-1.5 bg-slate-100 rounded-full overflow-hidden hidden sm:block">
                                                <div class="h-full bg-indigo-400" :style="{ width: `${Math.round((proj.horas / (emp.horas || 1)) * 100)}%` }"></div>
                                            </div>
                                        </div>
                                    </div>

                                </div>
                            </div>
                            
                            <div v-else class="text-sm text-slate-400 italic text-center py-4 bg-slate-50 rounded-lg border border-slate-100 border-dashed">
                                Sin imputaciones a proyectos
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="!isLoading && (vistaActual === 'usuarios' && cargaEmpleados.length === 0) || (vistaActual === 'proyectos' && jerarquiaClientes.length === 0)" class="text-center py-10 text-slate-400">
                    No hay datos registrados en el sistema para este periodo.
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
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import ManagerAPI from '../../services/ManagerAPI'
import {
    Users, Activity, FileSpreadsheet
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
const proyectosStats = ref([])
const cargaEmpleados = ref([])

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
        proyectosStats.value = data.proyectosStats || []
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
    if (horas < (umbral * 0.5)) return 'bg-amber-400' 
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
                    <Activity class="w-8 h-8 text-emerald-600" /> Control de Horas Reales
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

        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex-1">
            <h3 class="font-bold text-slate-800 mb-6 flex items-center gap-2">
                <Users class="w-5 h-5 text-slate-400" /> Desglose Individual por Proyectos
            </h3>
            
            <div v-if="isLoading" class="flex flex-col items-center justify-center py-10 opacity-50">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500 mb-4"></div>
                <p class="text-sm text-slate-500">Calculando horas teóricas del mes...</p>
            </div>

            <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-x-12 gap-y-8">
                <div v-for="emp in cargaEmpleados" :key="emp.nombre" class="flex flex-col gap-3 p-4 border border-slate-100 rounded-xl hover:shadow-md transition">
                    <div class="flex justify-between items-center">
                        <div class="flex items-center gap-3">
                            <div class="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600">
                                {{ emp.avatar }}
                            </div>
                            <div>
                                <span class="font-bold text-slate-700 block">{{ emp.nombre }}</span>
                                <span class="text-xs text-slate-400">{{ emp.rol }}</span>
                            </div>
                        </div>
                        <div class="text-right flex flex-col">
                            <div>
                                <span class="font-mono font-bold" :class="emp.horas > emp.capacidad ? 'text-rose-600' : 'text-slate-800'">
                                    {{ emp.horas }}h
                                </span>
                                <span class="font-mono text-xs font-bold text-slate-400"> / {{ emp.capacidad }}h</span>
                            </div>
                            <span class="text-[10px] font-bold mt-1 uppercase" :class="emp.horas >= emp.capacidad ? 'text-emerald-500' : 'text-amber-500'">
                                {{ Math.round((emp.horas / (emp.capacidad || 1)) * 100) }}% Ocupación
                            </span>
                        </div>
                    </div>

                    <div class="flex flex-wrap gap-2 mt-2">
                        <div v-for="proj in emp.desglose_proyectos" :key="proj.proyecto" 
                             class="flex items-center gap-1 bg-slate-100 px-2 py-1 rounded-md text-xs font-medium text-slate-600 border border-slate-200">
                            <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
                            <span class="truncate max-w-[120px]" :title="proj.proyecto">{{ proj.proyecto }}</span>
                            <span class="font-bold ml-1">{{ proj.horas }}h</span>
                        </div>
                        <div v-if="!emp.desglose_proyectos || emp.desglose_proyectos.length === 0" class="text-xs text-slate-400 italic">
                            Sin imputaciones a proyectos
                        </div>
                    </div>
                    
                    <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden mt-1">
                        <div class="h-full transition-all duration-1000" 
                             :class="getBarColor(emp.horas, emp.capacidad)" 
                             :style="`width: ${Math.min((emp.horas / (emp.capacidad || 1)) * 100, 100)}%`">
                        </div>
                    </div>
                </div>
            </div>
            
            <div v-if="!isLoading && cargaEmpleados.length === 0" class="text-center py-10 text-slate-400">
                No hay empleados activos.
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
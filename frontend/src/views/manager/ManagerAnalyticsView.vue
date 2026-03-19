<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import ManagerAPI from '../../services/ManagerAPI'
import {
    PieChart, BarChart3, Users, Activity, Download,
    Calendar, Clock, ArrowUpRight, AlertCircle, FileSpreadsheet
} from 'lucide-vue-next'

const mesAnalisis = ref('2026-02')
const isLoading = ref(false)

const totalHorasReales = ref(0)
const proyectosStats = ref([])
const cargaEmpleados = ref([])

const toast = ref({ show: false, message: '', type: 'success' })

const fetchAnalyticsData = async () => {
    isLoading.value = true
    try {
        const response = await ManagerAPI.getAnalytics(mesAnalisis.value)
        const data = response.data
        totalHorasReales.value = data.totalHorasImputadas || 0
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

const empleadosAltaActividad = computed(() => cargaEmpleados.value.filter(e => e.horas > 160).length)

const getBarColor = (horas) => {
    if (horas > 160) return 'bg-rose-500'
    if (horas < 80) return 'bg-amber-400'
    return 'bg-emerald-500'
}

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    setTimeout(() => toast.value.show = false, 3000)
}

const exportarReporte = () => {
    const headers = ['Empleado', 'Rol', 'Horas Imputadas']
    const rows = cargaEmpleados.value.map(emp => [emp.nombre, emp.rol, emp.horas])
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
                <h3 class="text-4xl font-extrabold text-slate-800 mt-2">{{ totalHorasReales }}h</h3>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-l-emerald-500">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Media por Empleado</p>
                <h3 class="text-4xl font-extrabold text-slate-800 mt-2">{{ mediaHorasEquipo }}h</h3>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-l-rose-500">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Alta Actividad (>160h)</p>
                <h3 class="text-4xl font-extrabold text-slate-800 mt-2">{{ empleadosAltaActividad }}</h3>
            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex-1">
            <h3 class="font-bold text-slate-800 mb-6 flex items-center gap-2">
                <Users class="w-5 h-5 text-slate-400" /> Desglose Individual
            </h3>
            
            <div class="space-y-6">
                <div v-for="emp in cargaEmpleados" :key="emp.nombre" class="flex flex-col gap-2">
                    <div class="flex justify-between items-center">
                        <div class="flex items-center gap-3">
                            <div class="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600">{{ emp.avatar }}</div>
                            <span class="font-bold text-slate-700">{{ emp.nombre }}</span>
                        </div>
                        <span class="font-mono font-bold text-slate-800">{{ emp.horas }}h</span>
                    </div>
                    <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div class="h-full transition-all duration-1000" 
                             :class="getBarColor(emp.horas)" 
                             :style="`width: ${Math.min((emp.horas / 170) * 100, 100)}%`">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="toast.show" class="fixed bottom-6 right-6 bg-slate-800 text-white px-6 py-3 rounded-lg shadow-xl font-bold animate-in slide-in-from-right">
            {{ toast.message }}
        </div>
    </div>
</template>
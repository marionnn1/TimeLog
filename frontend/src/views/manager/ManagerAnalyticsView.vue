<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../../stores/dataStore'
import {
    PieChart, BarChart3, AlertCircle, Users, Activity, Download,
    Calendar, Battery, ArrowUpRight, ArrowDownRight, Clock,
    AlertTriangle, CheckCircle2, X
} from 'lucide-vue-next'

const store = useDataStore()

const mesAnalisis = ref('2026-02')

const totalHorasImputadas = 1450
const totalCapacidadTeorica = 1600

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

const diasCriticos = computed(() => {
    const todasAusencias = store.getAusencias()
    const ausenciasDelMes = todasAusencias.filter(a => a.date.startsWith(mesAnalisis.value))

    const conteoPorDia = {}
    ausenciasDelMes.forEach(a => {
        conteoPorDia[a.date] = (conteoPorDia[a.date] || 0) + 1
    })

    const LIMITE_ALERTA = 3
    return Object.entries(conteoPorDia)
        .filter(([fecha, cantidad]) => cantidad >= LIMITE_ALERTA)
        .map(([fecha, cantidad]) => ({
            fecha,
            cantidad,
            fechaFormat: new Date(fecha).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' })
        }))
        .sort((a, b) => new Date(a.fecha) - new Date(b.fecha))
})

const proyectosStats = ref([
    { nombre: 'Santander', horas: 600, color: 'bg-red-600', contributors: ['ML', 'AR', 'PS'] },
    { nombre: 'Mapfre', horas: 300, color: 'bg-red-500', contributors: ['LG'] },
    { nombre: 'Inditex', horas: 400, color: 'bg-zinc-800', contributors: ['CM', 'ML'] },
    { nombre: 'Interno', horas: 150, color: 'bg-blue-500', contributors: ['Todos'] },
])

const cargaEmpleados = ref([
    { nombre: 'Mario León', horas: 175, capacidad: 160, rol: 'Dev', avatar: 'ML', trend: 'up' },
    { nombre: 'Ana Ruiz', horas: 160, capacidad: 160, rol: 'QA', avatar: 'AR', trend: 'equal' },
    { nombre: 'Pedro Sola', horas: 150, capacidad: 160, rol: 'Junior', avatar: 'PS', trend: 'down' },
    { nombre: 'Laura G.', horas: 120, capacidad: 160, rol: 'Manager', avatar: 'LG', trend: 'equal' },
    { nombre: 'Carlos M.', horas: 40, capacidad: 160, rol: 'Dev', avatar: 'CM', trend: 'down' },
])

const getPorcentaje = (horas) => Math.round((horas / totalHorasImputadas) * 100)
const getWidth = (horas) => `${Math.min((horas / 180) * 100, 100)}%`
const getBarColor = (horas, capacidad) => {
    const ratio = horas / capacidad
    if (ratio > 1.0) return 'bg-rose-500'
    if (ratio < 0.5) return 'bg-amber-400'
    return 'bg-emerald-500'
}

const empleadosExcedidos = computed(() => cargaEmpleados.value.filter(e => e.horas > e.capacidad).length)
const horasLibres = computed(() => totalCapacidadTeorica - totalHorasImputadas)
const porcentajeOcupacionGlobal = computed(() => Math.round((totalHorasImputadas / totalCapacidadTeorica) * 100))

const exportarReporte = () => {
    const headers = ['Empleado', 'Rol', 'Horas Imputadas', 'Capacidad', 'Estado']
    const rows = cargaEmpleados.value.map(emp => {
        let estado = 'Correcto'
        if (emp.horas > emp.capacidad) estado = 'Exceso'
        else if (emp.horas < emp.capacidad * 0.5) estado = 'Baja Ocupación'
        return [emp.nombre, emp.rol, emp.horas, emp.capacidad, estado]
    })
 
    const csvContent = [
        headers.join(';'),
        ...rows.map(row => row.join(';'))
    ].join('\n')
  
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `reporte_carga_${mesAnalisis.value}.csv`)
    document.body.appendChild(link)
    
    link.click()
    document.body.removeChild(link)

    showToast(`Reporte generado: reporte_carga_${mesAnalisis.value}.csv`, 'success')
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto relative">

        <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div>
                <h1 class="h1-title flex items-center gap-2">
                    <Activity class="w-8 h-8 text-primary" /> Analítica de Equipo
                </h1>
                <p class="subtitle">Control de carga, disponibilidad y riesgos.</p>
            </div>

            <div class="flex items-center gap-3 bg-white p-1.5 rounded-xl border border-gray-200 shadow-sm">
                <div class="flex items-center px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-100">
                    <Calendar class="w-4 h-4 text-gray-500 mr-2" />
                    <input type="month" v-model="mesAnalisis"
                        class="bg-transparent border-none outline-none text-sm font-bold text-dark">
                </div>
                <div class="h-6 w-px bg-gray-200"></div>
                <button @click="exportarReporte"
                    class="btn-ghost text-xs font-bold uppercase tracking-wide flex items-center gap-2">
                    <Download class="w-4 h-4" /> Exportar
                </button>
            </div>
        </div>

        <div v-if="diasCriticos.length > 0"
            class="bg-[#FFFBEB] border-l-4 border-amber-400 p-4 rounded-r-lg shadow-sm flex items-start gap-4 animate-in slide-in-from-top-2">

            <div class="p-2 bg-amber-100 rounded-full text-amber-600 shrink-0">
                <AlertTriangle class="w-6 h-6" />
            </div>

            <div class="flex-1">
                <h3 class="text-amber-900 font-bold text-sm uppercase tracking-wide mb-1">
                    Aviso de Disponibilidad
                </h3>
                <p class="text-amber-800 text-sm mb-3 leading-relaxed">
                    Se ha detectado una alta concurrencia de vacaciones (<strong>3 o más personas</strong>) en las
                    siguientes fechas.
                    Revisa la planificación para evitar cuellos de botella.
                </p>

                <div class="flex flex-wrap gap-2">
                    <div v-for="dia in diasCriticos" :key="dia.fecha"
                        class="bg-white border border-amber-200 text-amber-800 px-3 py-1 rounded-md text-xs font-bold flex items-center gap-2 shadow-sm">
                        <Calendar class="w-3 h-3 text-amber-500" />
                        {{ dia.fechaFormat }}:
                        <span class="bg-amber-100 px-1.5 rounded text-amber-900 border border-amber-200">
                            {{ dia.cantidad }} Ausentes
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="card p-5 border-l-4 border-l-blue-500 flex flex-col justify-between">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Horas Imputadas</p>
                        <h3 class="text-3xl font-bold text-dark mt-1">{{ totalHorasImputadas }}h</h3>
                    </div>
                    <div class="p-2 bg-blue-50 text-blue-600 rounded-lg">
                        <Clock class="w-5 h-5" />
                    </div>
                </div>
                <div
                    class="mt-4 flex items-center gap-2 text-xs font-medium text-emerald-600 bg-emerald-50 w-fit px-2 py-1 rounded">
                    <ArrowUpRight class="w-3 h-3" /> +12% vs mes anterior
                </div>
            </div>

            <div class="card p-5 border-l-4 border-l-emerald-500 flex flex-col justify-between">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Ocupación Total</p>
                        <h3 class="text-3xl font-bold text-dark mt-1">{{ porcentajeOcupacionGlobal }}%</h3>
                    </div>
                    <div class="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
                        <Users class="w-5 h-5" />
                    </div>
                </div>
                <div class="w-full bg-gray-100 h-1.5 rounded-full mt-4 overflow-hidden">
                    <div class="bg-emerald-500 h-full" :style="`width: ${porcentajeOcupacionGlobal}%`"></div>
                </div>
            </div>

            <div class="card p-5 border-l-4 border-l-rose-500 flex flex-col justify-between">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Exceso de Jornada</p>
                        <h3 class="text-3xl font-bold mt-1"
                            :class="empleadosExcedidos > 0 ? 'text-rose-600' : 'text-dark'">
                            {{ empleadosExcedidos }} <span class="text-sm font-normal text-gray-500">empleados</span>
                        </h3>
                    </div>
                    <div class="p-2 bg-rose-50 text-rose-600 rounded-lg">
                        <AlertCircle class="w-5 h-5" />
                    </div>
                </div>
                <p class="mt-2 text-xs text-gray-500">Han superado sus horas teóricas este mes.</p>
            </div>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 flex-1 min-h-0">

            <div class="card flex flex-col xl:col-span-2 overflow-hidden">
                <div class="flex items-center justify-between mb-6 border-b border-gray-100 pb-4">
                    <div class="flex items-center gap-2">
                        <BarChart3 class="w-5 h-5 text-gray-400" />
                        <h3 class="font-bold text-dark">Detalle de Horas por Empleado</h3>
                    </div>
                    <span class="badge bg-gray-100 text-gray-500 border-gray-200">Top 5</span>
                </div>

                <div class="flex-1 overflow-y-auto pr-2 space-y-6">
                    <div v-for="emp in cargaEmpleados" :key="emp.nombre" class="group">
                        <div class="flex justify-between items-center mb-2">
                            <div class="flex items-center gap-3">
                                <div
                                    class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 font-bold text-xs flex items-center justify-center border border-slate-200">
                                    {{ emp.avatar }}
                                </div>
                                <div>
                                    <p class="text-sm font-bold text-dark leading-none">{{ emp.nombre }}</p>
                                    <p class="text-[10px] text-gray-400 uppercase font-bold mt-0.5">{{ emp.rol }}</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="text-sm font-bold"
                                    :class="emp.horas > emp.capacidad ? 'text-rose-600' : 'text-dark'">
                                    {{ emp.horas }}h <span class="text-gray-400 font-normal">/ {{ emp.capacidad
                                        }}h</span>
                                </div>
                            </div>
                        </div>
                        <div class="relative w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                            <div class="absolute top-0 left-0 h-full rounded-full transition-all duration-1000"
                                :class="getBarColor(emp.horas, emp.capacidad)" :style="`width: ${getWidth(emp.horas)}`">
                            </div>
                            <div class="absolute top-0 bottom-0 w-0.5 bg-white z-10" style="left: 88%"></div>
                        </div>
                        <div class="flex justify-between items-center mt-1">
                            <div v-if="emp.horas > emp.capacidad"
                                class="text-[10px] text-rose-500 font-bold flex items-center gap-1 animate-pulse">
                                <AlertCircle class="w-3 h-3" /> Excede jornada (+{{ emp.horas - emp.capacidad }}h)
                            </div>
                            <div v-else-if="emp.horas < emp.capacidad * 0.5"
                                class="text-[10px] text-amber-500 font-bold">Baja ocupación</div>
                            <div v-else class="text-[10px] text-emerald-600 font-bold">Carga correcta</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex flex-col gap-6">
                <div class="card flex flex-col flex-1">
                    <div class="flex items-center gap-2 mb-4 border-b border-gray-100 pb-4">
                        <PieChart class="w-5 h-5 text-gray-400" />
                        <h3 class="font-bold text-dark">Impacto por Proyecto</h3>
                    </div>
                    <div class="flex-1 overflow-y-auto space-y-4">
                        <div v-for="item in proyectosStats" :key="item.nombre"
                            class="p-3 rounded-xl border border-gray-100 bg-gray-50/50">
                            <div class="flex justify-between items-center mb-2">
                                <div class="flex items-center gap-2">
                                    <div class="w-2 h-2 rounded-full" :class="item.color"></div>
                                    <span class="font-bold text-sm text-dark">{{ item.nombre }}</span>
                                </div>
                                <span class="text-xs font-bold text-gray-600">{{ getPorcentaje(item.horas) }}%</span>
                            </div>
                            <div class="w-full h-1.5 bg-gray-200 rounded-full mb-3 overflow-hidden">
                                <div class="h-full rounded-full" :class="item.color"
                                    :style="`width: ${getPorcentaje(item.horas)}%`"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card p-4 bg-slate-900 text-white border-none relative overflow-hidden">
                    <div class="relative z-10">
                        <div class="flex items-center gap-2 mb-3">
                            <Battery class="w-4 h-4 text-emerald-400" />
                            <h3 class="font-bold text-sm">Disponibilidad del Equipo</h3>
                        </div>
                        <div class="flex items-end gap-2 mb-1">
                            <span class="text-2xl font-bold text-white">{{ horasLibres }}h</span>
                            <span class="text-xs text-slate-400 mb-1">libres este mes</span>
                        </div>
                        <div class="w-full bg-slate-700 h-2 rounded-full mt-3 overflow-hidden">
                            <div class="bg-emerald-500 h-full" :style="`width: ${100 - porcentajeOcupacionGlobal}%`">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <transition enter-active-class="transform ease-out duration-300 transition" enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2" enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="toast.show" class="absolute bottom-6 right-6 z-50 flex items-center w-full max-w-xs p-4 space-x-3 text-gray-500 bg-white rounded-lg shadow-lg border border-gray-100" role="alert">
                <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg" :class="toast.type === 'success' ? 'text-green-500 bg-green-100' : 'text-red-500 bg-red-100'">
                    <component :is="toast.type === 'success' ? CheckCircle2 : AlertCircle" class="w-5 h-5"/>
                </div>
                <div class="ml-3 text-sm font-bold text-gray-800">{{ toast.message }}</div>
                <button @click="toast.show = false" type="button" class="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 items-center justify-center">
                    <X class="w-4 h-4"/>
                </button>
            </div>
        </transition>

    </div>
</template>
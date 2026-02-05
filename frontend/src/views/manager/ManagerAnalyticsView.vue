<script setup>
import { ref, computed } from 'vue'
import { 
    PieChart, BarChart3, AlertCircle, Users, Activity, Download, 
    Calendar, Battery, ArrowUpRight, ArrowDownRight, Clock
} from 'lucide-vue-next'

// --- ESTADO ---
const mesAnalisis = ref('2026-02') 

// --- DATOS MOCK ---
const totalHorasImputadas = 1450 
const totalCapacidadTeorica = 1600 // 10 personas x 160h

// Distribución por Proyecto
const proyectosStats = ref([
    { 
        nombre: 'Santander', horas: 600, color: 'bg-red-600', 
        contributors: ['ML', 'AR', 'PS'] 
    },
    { 
        nombre: 'Mapfre', horas: 300, color: 'bg-red-500', 
        contributors: ['LG'] 
    }, 
    { 
        nombre: 'Inditex', horas: 400, color: 'bg-zinc-800', 
        contributors: ['CM', 'ML'] 
    },
    { 
        nombre: 'Interno', horas: 150, color: 'bg-blue-500', 
        contributors: ['Todos'] 
    },
])

// Carga por Empleado
const cargaEmpleados = ref([
    { nombre: 'Mario León', horas: 175, capacidad: 160, rol: 'Dev', avatar: 'ML', trend: 'up' }, 
    { nombre: 'Ana Ruiz', horas: 160, capacidad: 160, rol: 'QA', avatar: 'AR', trend: 'equal' },
    { nombre: 'Pedro Sola', horas: 150, capacidad: 160, rol: 'Junior', avatar: 'PS', trend: 'down' },
    { nombre: 'Laura G.', horas: 120, capacidad: 160, rol: 'Manager', avatar: 'LG', trend: 'equal' }, 
    { nombre: 'Carlos M.', horas: 40, capacidad: 160, rol: 'Dev', avatar: 'CM', trend: 'down' }, 
])

// --- CÁLCULOS ---
const getPorcentaje = (horas) => Math.round((horas / totalHorasImputadas) * 100)

const getBarColor = (horas, capacidad) => {
    const ratio = horas / capacidad
    if (ratio > 1.0) return 'bg-rose-500' // Se pasó
    if (ratio < 0.5) return 'bg-amber-400' // Muy poco
    return 'bg-emerald-500' 
}

const getWidth = (horas) => {
    return `${Math.min((horas / 180) * 100, 100)}%`
}

// KPI: Empleados que se han pasado de horas
const empleadosExcedidos = computed(() => cargaEmpleados.value.filter(e => e.horas > e.capacidad).length)

// KPI: Capacidad Restante (Bolsa de horas libres del equipo)
const horasLibres = computed(() => totalCapacidadTeorica - totalHorasImputadas)
const porcentajeOcupacionGlobal = computed(() => Math.round((totalHorasImputadas / totalCapacidadTeorica) * 100))

// --- EXPORTACIÓN ---
const exportarReporte = () => {
    alert(`Generando PDF para el periodo: ${mesAnalisis.value}...`)
}
</script>

<template>
  <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto">
    
    <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
            <h1 class="h1-title flex items-center gap-2">
                <Activity class="w-8 h-8 text-primary" /> Analítica de Equipo
            </h1>
            <p class="subtitle">Control de carga de trabajo y horas imputadas.</p>
        </div>
        
        <div class="flex items-center gap-3 bg-white p-1.5 rounded-xl border border-gray-200 shadow-sm">
            <div class="flex items-center px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-100">
                <Calendar class="w-4 h-4 text-gray-500 mr-2" />
                <input type="month" v-model="mesAnalisis" class="bg-transparent border-none outline-none text-sm font-bold text-dark">
            </div>
            <div class="h-6 w-px bg-gray-200"></div>
            <button @click="exportarReporte" class="btn-ghost text-xs font-bold uppercase tracking-wide flex items-center gap-2">
                <Download class="w-4 h-4" /> Exportar
            </button>
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
            <div class="mt-4 flex items-center gap-2 text-xs font-medium text-emerald-600 bg-emerald-50 w-fit px-2 py-1 rounded">
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
                    <h3 class="text-3xl font-bold mt-1" :class="empleadosExcedidos > 0 ? 'text-rose-600' : 'text-dark'">
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
                            <div class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 font-bold text-xs flex items-center justify-center border border-slate-200">
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
                                {{ emp.horas }}h <span class="text-gray-400 font-normal">/ {{ emp.capacidad }}h</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="relative w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                        <div class="absolute top-0 left-0 h-full rounded-full transition-all duration-1000"
                             :class="getBarColor(emp.horas, emp.capacidad)"
                             :style="`width: ${getWidth(emp.horas)}`">
                        </div>
                        <div class="absolute top-0 bottom-0 w-0.5 bg-white z-10" style="left: 88%"></div> 
                    </div>

                    <div class="flex justify-between items-center mt-1">
                        <div v-if="emp.horas > emp.capacidad" class="text-[10px] text-rose-500 font-bold flex items-center gap-1 animate-pulse">
                            <AlertCircle class="w-3 h-3" /> Excede jornada (+{{ emp.horas - emp.capacidad }}h)
                        </div>
                        <div v-else-if="emp.horas < emp.capacidad * 0.5" class="text-[10px] text-amber-500 font-bold">
                            Baja ocupación
                        </div>
                        <div v-else class="text-[10px] text-emerald-600 font-bold">Carga correcta</div>

                        <div class="text-[10px] text-gray-400 flex items-center gap-1" v-if="emp.trend !== 'equal'">
                            <span v-if="emp.trend === 'up'" class="text-red-400 flex items-center">Subiendo <ArrowUpRight class="w-3 h-3"/></span>
                            <span v-if="emp.trend === 'down'" class="text-emerald-400 flex items-center">Bajando <ArrowDownRight class="w-3 h-3"/></span>
                        </div>
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
                         class="p-3 rounded-xl border border-gray-100 bg-gray-50/50 hover:bg-white hover:shadow-sm hover:border-gray-200 transition group">
                        
                        <div class="flex justify-between items-center mb-2">
                            <div class="flex items-center gap-2">
                                <div class="w-2 h-2 rounded-full" :class="item.color"></div>
                                <span class="font-bold text-sm text-dark">{{ item.nombre }}</span>
                            </div>
                            <span class="text-xs font-bold text-gray-600">{{ getPorcentaje(item.horas) }}%</span>
                        </div>

                        <div class="w-full h-1.5 bg-gray-200 rounded-full mb-3 overflow-hidden">
                            <div class="h-full rounded-full" :class="item.color" :style="`width: ${getPorcentaje(item.horas)}%`"></div>
                        </div>

                        <div class="flex items-center justify-between">
                            <div class="flex -space-x-1.5 overflow-hidden">
                                <div v-for="(av, i) in item.contributors" :key="i" 
                                     class="inline-block h-5 w-5 rounded-full ring-2 ring-white bg-slate-200 text-[8px] font-bold flex items-center justify-center text-slate-600">
                                    {{ av }}
                                </div>
                            </div>
                            <span class="text-[10px] text-gray-400 font-mono">{{ item.horas }}h</span>
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
                    
                    <p class="text-[10px] text-slate-400 leading-relaxed">
                        El equipo ha consumido el <b>{{ porcentajeOcupacionGlobal }}%</b> de su capacidad teórica ({{ totalCapacidadTeorica }}h).
                    </p>

                    <div class="w-full bg-slate-700 h-2 rounded-full mt-3 overflow-hidden">
                        <div class="bg-emerald-500 h-full" :style="`width: ${100 - porcentajeOcupacionGlobal}%`"></div>
                    </div>
                    <p class="text-[9px] text-right mt-1 text-emerald-400 font-bold">Espacio disponible</p>
                </div>
            </div>

        </div>

    </div>
  </div>
</template>
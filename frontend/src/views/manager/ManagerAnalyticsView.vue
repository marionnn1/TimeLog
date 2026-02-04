<script setup>
import { ref, computed } from 'vue'
import {
    PieChart, BarChart3, TrendingUp, Users, Activity, Download
} from 'lucide-vue-next'

// --- DATOS MOCK (Equipo de 10 personas) ---
// Total horas del mes del equipo
const totalHorasEquipo = 1450

// Distribución por Proyecto
const proyectosStats = ref([
    { nombre: 'Santander', horas: 600, color: 'bg-red-500' },
    { nombre: 'Mapfre', horas: 300, color: 'bg-red-600' }, // Mapfre suele ser rojo también, usamos tono distinto
    { nombre: 'Inditex', horas: 400, color: 'bg-zinc-800' },
    { nombre: 'Interno', horas: 150, color: 'bg-blue-500' },
])

// Carga por Empleado (Top 5 para no saturar)
const cargaEmpleados = ref([
    { nombre: 'Mario León', horas: 175, capacidad: 160, rol: 'Dev' }, // Overworked
    { nombre: 'Ana Ruiz', horas: 160, capacidad: 160, rol: 'QA' },
    { nombre: 'Pedro Sola', horas: 150, capacidad: 160, rol: 'Junior' },
    { nombre: 'Laura G.', horas: 120, capacidad: 160, rol: 'Manager' }, // Menos carga técnica
    { nombre: 'Carlos M.', horas: 40, capacidad: 160, rol: 'Dev' }, // ¿Baja o vacaciones?
])

// --- CÁLCULOS ---
const getPorcentaje = (horas) => Math.round((horas / totalHorasEquipo) * 100)

const getBarColor = (horas, capacidad) => {
    const ratio = horas / capacidad
    if (ratio > 1.05) return 'bg-rose-500' // Rojo: Quemado
    if (ratio < 0.5) return 'bg-amber-400' // Amarillo: Infrautilizado
    return 'bg-emerald-500' // Verde: Óptimo
}

const getWidth = (horas, max) => {
    // Escala relativa al máximo (aprox 180h)
    return `${Math.min((horas / 180) * 100, 100)}%`
}

const exportarReporte = () => {
    alert("📄 Generando PDF con el resumen de actividad del equipo...")
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto">

        <div class="flex justify-between items-end">
            <div>
                <h1 class="h1-title flex items-center gap-2">
                    <Activity class="w-8 h-8 text-primary" /> Analítica de Esfuerzo
                </h1>
                <p class="subtitle">Visión global de dónde invierte su tiempo el equipo.</p>
            </div>

            <button @click="exportarReporte" class="btn-secondary flex items-center gap-2">
                <Download class="w-4 h-4" /> Descargar Reporte Mensual
            </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="card flex items-center gap-4 border-l-4 border-l-blue-500">
                <div class="p-3 bg-blue-50 rounded-full text-blue-600">
                    <Clock class="w-6 h-6" />
                </div>
                <div>
                    <p class="text-xs font-bold text-gray-400 uppercase">Horas Totales (Mes)</p>
                    <h3 class="text-2xl font-bold text-dark">{{ totalHorasEquipo }}h</h3>
                </div>
            </div>

            <div class="card flex items-center gap-4 border-l-4 border-l-emerald-500">
                <div class="p-3 bg-emerald-50 rounded-full text-emerald-600">
                    <Users class="w-6 h-6" />
                </div>
                <div>
                    <p class="text-xs font-bold text-gray-400 uppercase">Ocupación Media</p>
                    <h3 class="text-2xl font-bold text-dark">92%</h3>
                </div>
            </div>

            <div class="card flex items-center gap-4 border-l-4 border-l-purple-500">
                <div class="p-3 bg-purple-50 rounded-full text-purple-600">
                    <TrendingUp class="w-6 h-6" />
                </div>
                <div>
                    <p class="text-xs font-bold text-gray-400 uppercase">Productividad</p>
                    <h3 class="text-2xl font-bold text-dark">+5% <span class="text-xs font-normal text-gray-400">vs mes
                            pasado</span></h3>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">

            <div class="card flex flex-col">
                <div class="flex items-center gap-2 mb-6 border-b border-gray-100 pb-4">
                    <PieChart class="w-5 h-5 text-gray-400" />
                    <h3 class="font-bold text-dark">Distribución del Tiempo</h3>
                </div>

                <div class="flex-1 flex flex-col justify-center gap-6">
                    <div class="w-full h-8 rounded-full flex overflow-hidden shadow-inner">
                        <div v-for="item in proyectosStats" :key="item.nombre"
                            class="h-full flex items-center justify-center text-[10px] font-bold text-white transition-all hover:opacity-90 cursor-help relative group"
                            :class="item.color" :style="`width: ${getPorcentaje(item.horas)}%`">
                            <span class="hidden md:block">{{ getPorcentaje(item.horas) }}%</span>

                            <div
                                class="absolute bottom-full mb-2 bg-gray-800 text-white px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition text-xs whitespace-nowrap z-10">
                                {{ item.nombre }}: {{ item.horas }}h
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div v-for="item in proyectosStats" :key="item.nombre"
                            class="flex items-center justify-between p-2 rounded hover:bg-gray-50 transition">
                            <div class="flex items-center gap-2">
                                <div class="w-3 h-3 rounded-full shadow-sm" :class="item.color"></div>
                                <span class="font-bold text-sm text-gray-700">{{ item.nombre }}</span>
                            </div>
                            <span class="text-sm font-mono text-gray-500">{{ item.horas }}h</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card flex flex-col">
                <div class="flex items-center gap-2 mb-4 border-b border-gray-100 pb-4">
                    <BarChart3 class="w-5 h-5 text-gray-400" />
                    <h3 class="font-bold text-dark">Carga de Trabajo Individual</h3>
                </div>

                <div class="space-y-5 overflow-y-auto pr-2">
                    <div v-for="emp in cargaEmpleados" :key="emp.nombre">
                        <div class="flex justify-between items-end mb-1">
                            <div class="flex items-center gap-2">
                                <span class="text-sm font-bold text-dark">{{ emp.nombre }}</span>
                                <span class="text-[10px] uppercase text-gray-400 bg-gray-100 px-1.5 rounded">{{ emp.rol
                                    }}</span>
                            </div>
                            <div class="text-xs font-bold"
                                :class="emp.horas > emp.capacidad ? 'text-rose-500' : (emp.horas < emp.capacidad * 0.5 ? 'text-amber-500' : 'text-emerald-600')">
                                {{ emp.horas }} / {{ emp.capacidad }}h
                            </div>
                        </div>

                        <div class="w-full bg-gray-100 h-2.5 rounded-full overflow-hidden flex items-center">
                            <div class="h-full rounded-full transition-all duration-1000"
                                :class="getBarColor(emp.horas, emp.capacidad)" :style="`width: ${getWidth(emp.horas)}`">
                            </div>
                        </div>

                        <p v-if="emp.horas > emp.capacidad"
                            class="text-[10px] text-rose-500 mt-1 font-bold flex items-center gap-1">
                            ⚠️ Sobrecarga detectada (+{{ emp.horas - emp.capacidad }}h)
                        </p>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, markRaw } from 'vue'
// Importamos los iconos específicos para las tarjetas
import {
    CalendarCheck,
    Activity,
    Clock,
    AlertCircle,
    Plus
} from 'lucide-vue-next'

const cargando = ref(true)

// Usamos markRaw para guardar el icono como objeto, no como texto
const kpis = ref([
    { id: 'cumplimiento', titulo: '% Cumplimiento', valor: '-', color: 'bg-blue-600', icon: markRaw(CalendarCheck) },
    { id: 'utilizacion', titulo: '% Utilización', valor: '-', color: 'bg-emerald-600', icon: markRaw(Activity) },
    { id: 'horas_totales', titulo: 'Horas (Mes)', valor: '-', color: 'bg-indigo-600', icon: markRaw(Clock) },
    { id: 'pendientes', titulo: 'Días Pendientes', valor: '-', color: 'bg-amber-500', icon: markRaw(AlertCircle) },
])

const imputacionesRecientes = ref([])

const cargarDatos = async () => {
    try {
        cargando.value = true
        // Simulación de carga
        setTimeout(() => { cargando.value = false }, 500)
    } catch (error) {
        console.error(error)
        cargando.value = false
    }
}

onMounted(() => {
    cargarDatos()
})
</script>

<template>
    <div>
        <div class="flex justify-between items-center mb-8">
            <div>
                <h1 class="text-2xl font-bold text-slate-900">Panel de Control</h1>
                <p class="text-slate-500 text-sm mt-1">Resumen mensual de actividad</p>
            </div>

            <button
                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg shadow-sm hover:shadow transition flex items-center gap-2 text-sm font-medium">
                <Plus class="w-4 h-4" />
                Imputar Horas
            </button>
        </div>

        <div v-if="cargando" class="flex justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>

        <div v-else>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">

                <div v-for="kpi in kpis" :key="kpi.id"
                    class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-start">
                    <div :class="`p-3 rounded-lg text-white mr-4 shadow-sm ${kpi.color}`">
                        <component :is="kpi.icon" class="w-6 h-6" />
                    </div>

                    <div>
                        <p class="text-slate-500 text-xs font-semibold uppercase tracking-wide mb-1">{{ kpi.titulo }}
                        </p>
                        <p class="text-2xl font-bold text-slate-800">{{ kpi.valor }}</p>
                    </div>
                </div>

            </div>

            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div class="px-6 py-4 border-b border-slate-200">
                    <h2 class="text-base font-bold text-slate-800">Últimas Imputaciones</h2>
                </div>

                <div class="p-8 text-center">
                    <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 mb-3">
                        <Clock class="w-6 h-6 text-slate-400" />
                    </div>
                    <h3 class="text-sm font-medium text-slate-900">No hay actividad reciente</h3>
                    <p class="text-sm text-slate-500 mt-1">Tus imputaciones de horas aparecerán aquí.</p>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import {
    ChevronLeft,
    ChevronRight,
    FileText,
    Plus,
    Calendar as CalendarIcon,
    Ban // Icono de prohibido para el fin de semana
} from 'lucide-vue-next'

// --- LÓGICA DE FECHAS ---
const fechaActual = ref(new Date())
const hoy = new Date()

const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

const anioActual = computed(() => fechaActual.value.getFullYear())
const mesActualIndex = computed(() => fechaActual.value.getMonth())
const nombreMes = computed(() => meses[mesActualIndex.value])

const diasEnBlanco = computed(() => {
    const primerDia = new Date(anioActual.value, mesActualIndex.value, 1).getDay()
    return primerDia === 0 ? 6 : primerDia - 1
})

const diasDelMes = computed(() => {
    return new Date(anioActual.value, mesActualIndex.value + 1, 0).getDate()
})

// Detectar Sábados y Domingos
const esFinDeSemana = (dia) => {
    const fecha = new Date(anioActual.value, mesActualIndex.value, dia)
    const diaSemana = fecha.getDay()
    return diaSemana === 0 || diaSemana === 6
}

// Navegación
const mesAnterior = () => fechaActual.value = new Date(anioActual.value, mesActualIndex.value - 1, 1)
const mesSiguiente = () => fechaActual.value = new Date(anioActual.value, mesActualIndex.value + 1, 1)
const irAHoy = () => fechaActual.value = new Date()

// --- DATOS MOCK ---
const imputaciones = ref([
    { dia: 5, proyecto: 'Banco Santander', horas: 8, descripcion: 'Auditoría', color: 'bg-blue-50 text-[#232D4B] border-blue-100' },
    { dia: 6, proyecto: 'Mapfre', horas: 4, descripcion: 'Reunión', color: 'bg-emerald-50 text-emerald-800 border-emerald-100' },
    { dia: 6, proyecto: 'Interno', horas: 4, descripcion: 'Formación', color: 'bg-gray-50 text-gray-700 border-gray-200' },
    { dia: 12, proyecto: 'Inditex', horas: 8.5, descripcion: 'Despliegue', color: 'bg-purple-50 text-purple-800 border-purple-100' },
])

const getImputacionesPorDia = (dia) => imputaciones.value.filter(imp => imp.dia === dia)
const getTotalHoras = (dia) => getImputacionesPorDia(dia).reduce((acc, curr) => acc + curr.horas, 0)
const esHoy = (dia) => dia === hoy.getDate() && mesActualIndex.value === hoy.getMonth() && anioActual.value === hoy.getFullYear()

</script>

<template>
    <div class="h-full flex flex-col font-sans">

        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center gap-4">
                <h1 class="text-3xl font-bold capitalize flex items-center gap-2" style="color: #232D4B;">
                    <CalendarIcon class="w-8 h-8 opacity-80" />
                    {{ nombreMes }} <span class="font-light opacity-60">{{ anioActual }}</span>
                </h1>

                <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200 ml-6">
                    <button @click="mesAnterior"
                        class="p-2 hover:bg-gray-50 text-gray-600 rounded-l-lg border-r border-gray-200 transition">
                        <ChevronLeft class="w-5 h-5" />
                    </button>
                    <button @click="irAHoy"
                        class="px-4 py-2 text-sm font-bold tracking-wide hover:bg-gray-50 transition"
                        style="color: #232D4B;">
                        HOY
                    </button>
                    <button @click="mesSiguiente"
                        class="p-2 hover:bg-gray-50 text-gray-600 rounded-r-lg border-l border-gray-200 transition">
                        <ChevronRight class="w-5 h-5" />
                    </button>
                </div>
            </div>

            <button
                class="text-white px-5 py-2.5 rounded-lg shadow-md hover:shadow-lg transition transform hover:-translate-y-0.5 flex items-center gap-2 text-sm font-bold tracking-wide"
                style="background-color: #26AA9B;">
                <Plus class="w-5 h-5" />
                NUEVA IMPUTACIÓN
            </button>
        </div>

        <div class="bg-white rounded-xl shadow-lg border border-gray-200 flex-1 flex flex-col overflow-hidden">

            <div class="grid grid-cols-7 border-b border-gray-200" style="background-color: #F8FAFC;">
                <div v-for="(dia, index) in diasSemana" :key="dia"
                    class="py-4 text-center text-xs font-bold uppercase tracking-widest"
                    :style="{ color: index >= 5 ? '#94a3b8' : '#232D4B' }">
                    {{ dia }}
                </div>
            </div>

            <div class="grid grid-cols-7 flex-1 auto-rows-fr bg-gray-50">

                <div v-for="blank in diasEnBlanco" :key="`blank-${blank}`"
                    class="bg-white border-b border-r border-gray-100 opacity-50"></div>

                <div v-for="dia in diasDelMes" :key="dia"
                    class="min-h-[120px] p-2 border-b border-r border-gray-100 transition relative group flex flex-col gap-1"
                    :class="esFinDeSemana(dia) ? 'cursor-not-allowed weekend-pattern' : 'hover:bg-white bg-white cursor-pointer'">

                    <div v-if="esFinDeSemana(dia)"
                        class="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none">
                        <Ban class="w-12 h-12 text-gray-400" />
                    </div>

                    <div class="flex justify-between items-start mb-2 relative z-10">
                        <span
                            class="text-sm font-bold w-8 h-8 flex items-center justify-center rounded-full transition-colors"
                            :style="esHoy(dia) ? 'background-color: #232D4B; color: white; box-shadow: 0 4px 6px -1px rgba(35, 45, 75, 0.4);' : (esFinDeSemana(dia) ? 'color: #cbd5e1;' : 'color: #475569;')">
                            {{ dia }}
                        </span>

                        <span v-if="getTotalHoras(dia) > 0"
                            class="text-xs font-bold px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                            {{ getTotalHoras(dia) }}h
                        </span>
                    </div>

                    <div v-for="(item, idx) in getImputacionesPorDia(dia)" :key="idx"
                        class="text-xs p-2 rounded-md border mb-1 truncate flex items-center justify-between shadow-sm relative z-10 hover:opacity-80 transition"
                        :class="item.color">
                        <span class="truncate font-semibold">{{ item.proyecto }}</span>
                        <FileText v-if="item.descripcion" class="w-3 h-3 opacity-60 flex-shrink-0 ml-1" />
                    </div>

                    <div v-if="!esFinDeSemana(dia)"
                        class="absolute bottom-3 right-3 opacity-0 group-hover:opacity-100 transition transform scale-90 hover:scale-100 z-20">
                        <button class="text-white p-2 rounded-full shadow-lg transition hover:rotate-90"
                            style="background-color: #26AA9B;">
                            <Plus class="w-4 h-4" />
                        </button>
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Patrón agresivo para el fin de semana */
.weekend-pattern {
    background-color: #f1f5f9;
    /* Slate 100 de fondo base */
    background-image: repeating-linear-gradient(45deg,
            #e2e8f0,
            #e2e8f0 1px,
            #f1f5f9 1px,
            #f1f5f9 10px);
}
</style>
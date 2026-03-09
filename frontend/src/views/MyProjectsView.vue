<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { 
    Calendar, Clock, LayoutGrid, Loader2, FolderKanban, BarChart, Download
} from 'lucide-vue-next'

const store = useDataStore()
const datos = ref(null)
const cargando = ref(true)

// Estado del filtro
const mesActual = new Date().getMonth() + 1
const anioActual = new Date().getFullYear()
const mesSeleccionado = ref(mesActual)
const anioSeleccionado = ref(anioActual)

const meses = [
    { v: 1, n: 'Enero' }, { v: 2, n: 'Febrero' }, { v: 3, n: 'Marzo' },
    { v: 4, n: 'Abril' }, { v: 5, n: 'Mayo' }, { v: 6, n: 'Junio' },
    { v: 7, n: 'Julio' }, { v: 8, n: 'Agosto' }, { v: 9, n: 'Septiembre' },
    { v: 10, n: 'Octubre' }, { v: 11, n: 'Noviembre' }, { v: 12, n: 'Diciembre' }
]

const cargarData = async () => {
    cargando.value = true
    const user = store.getCurrentUser()
    if (!user) return
    
    try {
        const res = await fetch(`http://localhost:5000/api/myprojects/analitica-mensual?usuario_id=${user.id}&mes=${mesSeleccionado.value}&anio=${anioSeleccionado.value}`)
        const json = await res.json()
        datos.value = json.data
    } catch (e) {
        console.error(e)
    } finally {
        cargando.value = false
    }
}

watch([mesSeleccionado, anioSeleccionado], cargarData)
onMounted(cargarData)

// Cálculos para la tabla
const totalMes = computed(() => datos.value?.totales?.mes_real || 1)
const getPorcentaje = (horas) => Math.round((horas / totalMes.value) * 100)

// Función para exportar a CSV
const exportarCSV = () => {
    if (!datos.value || !datos.value.proyectos.length) return

    // Definir cabeceras
    const headers = ['Proyecto', 'Cliente', 'Horas Invertidas', 'Impacto (%)']
    
    // Mapear los datos de los proyectos asegurando que los textos van entre comillas (por si llevan comas)
    const rows = datos.value.proyectos.map(p => {
        return [
            `"${p.proyecto}"`,
            `"${p.cliente}"`,
            p.real,
            getPorcentaje(p.real)
        ].join(';')
    })

    // Fila de totales
    rows.push(`"TOTAL MENSUAL","",${datos.value.totales.mes_real},100`)

    // Generar el archivo
    const csvContent = [headers.join(';'), ...rows].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    
    // Crear enlace oculto y forzar descarga
    const link = document.createElement('a')
    link.setAttribute('href', url)
    const mesNombre = meses.find(m => m.v === mesSeleccionado.value).n
    link.setAttribute('download', `Dedicacion_${mesNombre}_${anioSeleccionado.value}.csv`)
    document.body.appendChild(link)
    
    link.click()
    document.body.removeChild(link)
}
</script>

<template>
  <div class="p-6 md:p-8 bg-slate-50 min-h-screen h-full overflow-y-auto pb-24 font-sans text-slate-800">
    
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white border border-slate-200 rounded-lg flex items-center justify-center shadow-sm">
                <LayoutGrid class="w-5 h-5 text-primary" />
            </div>
            <div>
                <h1 class="text-xl font-bold leading-none">Mis Proyectos</h1>
                <p class="text-slate-500 text-xs mt-1">Análisis de tiempo invertido por proyecto</p>
            </div>
        </div>

        <div class="flex flex-wrap items-center gap-3">
            <div class="flex items-center gap-2 bg-white px-2 py-1.5 rounded-lg border border-slate-200 shadow-sm">
                <Calendar class="w-4 h-4 text-slate-400 ml-2" />
                <select v-model="mesSeleccionado" class="bg-transparent font-semibold text-sm text-slate-700 outline-none px-2 cursor-pointer">
                    <option v-for="m in meses" :key="m.v" :value="m.v">{{ m.n }}</option>
                </select>
                <div class="w-px h-4 bg-slate-200"></div>
                <select v-model="anioSeleccionado" class="bg-transparent font-semibold text-sm text-slate-700 outline-none px-2 cursor-pointer">
                    <option :value="2026">2026</option>
                    <option :value="2025">2025</option>
                </select>
            </div>

            <button 
                @click="exportarCSV" 
                :disabled="!datos || datos.proyectos.length === 0"
                class="flex items-center gap-2 bg-white px-4 py-2 rounded-lg border border-slate-200 shadow-sm text-sm font-bold text-slate-600 hover:text-primary hover:border-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <Download class="w-4 h-4" /> Exportar CSV
            </button>
        </div>
    </div>

    <div v-if="cargando" class="flex flex-col items-center justify-center py-20">
        <Loader2 class="animate-spin text-primary w-8 h-8 mb-4" />
        <p class="text-xs font-bold uppercase tracking-widest text-slate-400">Recopilando datos...</p>
    </div>

    <div v-else-if="datos" class="space-y-6 max-w-7xl mx-auto">
        
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            
            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex items-center gap-4">
                <div class="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 shrink-0">
                    <Clock class="w-6 h-6" />
                </div>
                <div>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Total Mes</p>
                    <p class="text-2xl font-black text-slate-800">{{ datos.totales.mes_real }} <span class="text-sm font-medium text-slate-500">horas</span></p>
                </div>
            </div>

            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex items-center gap-4">
                <div class="w-12 h-12 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-600 shrink-0">
                    <BarChart class="w-6 h-6" />
                </div>
                <div>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Acumulado Anual</p>
                    <p class="text-2xl font-black text-slate-800">{{ datos.totales.ano_acumulado }} <span class="text-sm font-medium text-slate-500">horas</span></p>
                </div>
            </div>

            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex items-center gap-4">
                <div class="w-12 h-12 rounded-full bg-purple-50 flex items-center justify-center text-purple-600 shrink-0">
                    <FolderKanban class="w-6 h-6" />
                </div>
                <div>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Proyectos Activos</p>
                    <p class="text-2xl font-black text-slate-800">{{ datos.proyectos.length }} <span class="text-sm font-medium text-slate-500">este mes</span></p>
                </div>
            </div>

        </div>

        <div class="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            <div class="px-5 py-4 border-b border-slate-100 bg-slate-50/50">
                <h2 class="font-bold text-sm text-slate-800">Desglose de Imputaciones</h2>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-white border-b border-slate-200 text-[10px] uppercase tracking-widest text-slate-400">
                            <th class="px-6 py-3 font-bold w-1/2">Proyecto / Cliente</th>
                            <th class="px-6 py-3 font-bold text-right">Horas Invertidas</th>
                            <th class="px-6 py-3 font-bold w-1/3">Impacto del Mes</th>
                        </tr>
                    </thead>
                    
                    <tbody v-if="datos.proyectos.length > 0" class="divide-y divide-slate-100 text-sm">
                        <tr v-for="p in datos.proyectos" :key="p.proyecto" class="hover:bg-slate-50/80 transition-colors">
                            
                            <td class="px-6 py-4">
                                <p class="font-bold text-slate-800">{{ p.proyecto }}</p>
                                <p class="text-xs text-slate-500 mt-0.5">{{ p.cliente }}</p>
                            </td>
                            
                            <td class="px-6 py-4 text-right">
                                <span class="inline-block px-3 py-1 bg-slate-100 text-slate-700 font-bold rounded border border-slate-200">
                                    {{ p.real }} h
                                </span>
                            </td>
                            
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3">
                                    <div class="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                                        <div class="h-full bg-primary rounded-full" :style="{ width: getPorcentaje(p.real) + '%' }"></div>
                                    </div>
                                    <span class="text-xs font-bold text-slate-600 w-8 text-right">{{ getPorcentaje(p.real) }}%</span>
                                </div>
                            </td>
                            
                        </tr>
                    </tbody>
                    
                    <tbody v-else>
                        <tr>
                            <td colspan="3" class="px-6 py-12 text-center">
                                <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-50 mb-3">
                                    <FolderKanban class="w-6 h-6 text-slate-300" />
                                </div>
                                <p class="text-sm font-bold text-slate-600">Sin actividad registrada</p>
                                <p class="text-xs text-slate-400 mt-1">No tienes horas imputadas en {{ meses[mesSeleccionado-1].n }} de {{ anioSeleccionado }}.</p>
                            </td>
                        </tr>
                    </tbody>
                    
                    <tfoot v-if="datos.proyectos.length > 0" class="bg-slate-50/50 border-t border-slate-200">
                        <tr>
                            <td class="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-widest text-right">Total</td>
                            <td class="px-6 py-3 text-right">
                                <span class="font-black text-primary text-base">{{ datos.totales.mes_real }} h</span>
                            </td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
        
    </div>
  </div>
</template>
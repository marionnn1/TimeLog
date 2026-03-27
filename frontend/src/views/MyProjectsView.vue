<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import MyProjectsAPI from '../services/MyProjectsAPI'
import {
    Calendar, Clock, LayoutGrid, Loader2, FolderKanban, BarChart, FileText, Briefcase
} from 'lucide-vue-next'

const store = useDataStore()
const datos = ref(null)
const cargando = ref(true)

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
        const json = await MyProjectsAPI.getAnaliticaMensual(user.id, mesSeleccionado.value, anioSeleccionado.value)
        if (json.status === 'success') datos.value = json.data
    } catch (e) {
        console.error(e)
    } finally {
        cargando.value = false
    }
}

watch([mesSeleccionado, anioSeleccionado], cargarData)
onMounted(cargarData)

const totalMes = computed(() => datos.value?.totales?.mes_real || 1)
const getPorcentaje = (horas) => Math.round((horas / totalMes.value) * 100)

const clientesAgrupados = computed(() => {
    if (!datos.value || !datos.value.proyectos) return {}

    const grupos = {}
    datos.value.proyectos.forEach(p => {
        const nombreCliente = p.cliente || 'Sin Cliente asignado'
        if (!grupos[nombreCliente]) {
            grupos[nombreCliente] = {
                nombre: nombreCliente,
                proyectos: [],
                totalHoras: 0
            }
        }
        grupos[nombreCliente].proyectos.push(p)
        grupos[nombreCliente].totalHoras += p.real
    })

    return Object.keys(grupos).sort().reduce((obj, key) => {
        obj[key] = grupos[key]
        return obj
    }, {})
})

const exportarCSV = () => {
    if (!datos.value || !datos.value.proyectos.length) return

    const headers = ['Cliente', 'Proyecto', 'Horas Invertidas', 'Impacto (%)']

    const proyectosOrdenados = [...datos.value.proyectos].sort((a, b) => a.cliente.localeCompare(b.cliente))

    const rows = proyectosOrdenados.map(p => [
        `"${p.cliente}"`,
        `"${p.proyecto}"`,
        `"${p.real.toString().replace('.', ',')}"`,
        `"${getPorcentaje(p.real).toString().replace('.', ',')}"`
    ].join(';'))

    rows.push(`"TOTAL MENSUAL","", "${datos.value.totales.mes_real.toString().replace('.', ',')}", "100"`)

    const csvContent = [headers.join(';'), ...rows].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
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
    <div class="absolute inset-0 overflow-y-auto bg-slate-50 font-sans p-6 md:p-8 pb-24 text-slate-800">

        <div class="max-w-[1600px] mx-auto w-full">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <div class="flex items-center gap-3">
                    <div
                        class="w-10 h-10 bg-white border border-slate-200 rounded-lg flex items-center justify-center shadow-sm">
                        <LayoutGrid class="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h1 class="text-xl font-bold leading-none">Mis Proyectos</h1>
                        <p class="text-slate-500 text-xs mt-1">Análisis de tiempo invertido estructurado por cliente</p>
                    </div>
                </div>

                <div class="flex flex-wrap items-center gap-3">
                    <div
                        class="flex items-center gap-1 bg-white px-3 py-2 rounded-lg border border-slate-200 shadow-sm">
                        <Calendar class="w-4 h-4 text-slate-400 mr-1" />

                        <select v-model="mesSeleccionado"
                            class="bg-transparent font-bold text-sm text-slate-700 outline-none border-none focus:ring-0 focus:border-transparent cursor-pointer appearance-none pr-5 relative"
                            style="background-image: url('data:image/svg+xml;utf8,<svg fill=%22none%22 stroke=%22%2394a3b8%22 viewBox=%220 0 24 24%22 xmlns=%22http://www.w3.org/2000/svg%22><path stroke-linecap=%22round%22 stroke-linejoin=%22round%22 stroke-width=%222%22 d=%22M19 9l-7 7-7-7%22></path></svg>'); background-repeat: no-repeat; background-position: right center; background-size: 12px;">
                            <option v-for="m in meses" :key="m.v" :value="m.v">{{ m.n }}</option>
                        </select>

                        <div class="w-px h-4 bg-slate-200 mx-1"></div>

                        <select v-model="anioSeleccionado"
                            class="bg-transparent font-bold text-sm text-slate-700 outline-none border-none focus:ring-0 focus:border-transparent cursor-pointer appearance-none pr-5 relative"
                            style="background-image: url('data:image/svg+xml;utf8,<svg fill=%22none%22 stroke=%22%2394a3b8%22 viewBox=%220 0 24 24%22 xmlns=%22http://www.w3.org/2000/svg%22><path stroke-linecap=%22round%22 stroke-linejoin=%22round%22 stroke-width=%222%22 d=%22M19 9l-7 7-7-7%22></path></svg>'); background-repeat: no-repeat; background-position: right center; background-size: 12px;">
                            <option :value="2026">2026</option>
                            <option :value="2025">2025</option>
                        </select>
                    </div>

                    <button @click="exportarCSV" :disabled="!datos || datos.proyectos.length === 0"
                        class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
                        <FileText class="w-4 h-4" /> Exportar
                    </button>
                </div>
            </div>

            <div v-if="cargando" class="flex flex-col items-center justify-center py-20">
                <Loader2 class="animate-spin text-primary w-8 h-8 mb-4" />
                <p class="text-xs font-bold uppercase tracking-widest text-slate-400">Recopilando datos...</p>
            </div>

            <div v-else-if="datos" class="space-y-6">

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex items-center gap-4">
                        <div
                            class="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 shrink-0">
                            <Clock class="w-6 h-6" />
                        </div>
                        <div>
                            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Total Mes</p>
                            <p class="text-2xl font-black text-slate-800">{{ datos.totales.mes_real }} <span
                                    class="text-sm font-medium text-slate-500">horas</span></p>
                        </div>
                    </div>

                    <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex items-center gap-4">
                        <div
                            class="w-12 h-12 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-600 shrink-0">
                            <BarChart class="w-6 h-6" />
                        </div>
                        <div>
                            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Acumulado Anual
                            </p>
                            <p class="text-2xl font-black text-slate-800">{{ datos.totales.ano_acumulado }} <span
                                    class="text-sm font-medium text-slate-500">horas</span></p>
                        </div>
                    </div>

                    <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex items-center gap-4">
                        <div
                            class="w-12 h-12 rounded-full bg-purple-50 flex items-center justify-center text-purple-600 shrink-0">
                            <FolderKanban class="w-6 h-6" />
                        </div>
                        <div>
                            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Proyectos Activos
                            </p>
                            <p class="text-2xl font-black text-slate-800">{{ datos.proyectos.length }} <span
                                    class="text-sm font-medium text-slate-500">este mes</span></p>
                        </div>
                    </div>
                </div>

                <div v-if="Object.keys(clientesAgrupados).length === 0"
                    class="bg-white border border-slate-200 rounded-xl shadow-sm p-12 text-center">
                    <div
                        class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-50 mb-4 border border-slate-100">
                        <FolderKanban class="w-8 h-8 text-slate-300" />
                    </div>
                    <p class="text-lg font-bold text-slate-700">Sin actividad registrada</p>
                    <p class="text-sm text-slate-500 mt-2">No tienes horas imputadas en {{ meses[mesSeleccionado - 1].n }}
                        de {{ anioSeleccionado }}.</p>
                </div>

                <div class="space-y-6">
                    <div v-for="(datosCliente, clienteNombre) in clientesAgrupados" :key="clienteNombre"
                        class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">

                        <div class="px-6 py-4 border-b border-slate-100 bg-[#f8fafc] flex justify-between items-center">
                            <div class="flex items-center gap-3">
                                <div
                                    class="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600">
                                    <Briefcase class="w-4 h-4" />
                                </div>
                                <h2 class="font-bold text-lg text-slate-800">{{ clienteNombre }}</h2>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="text-xs font-bold text-slate-500 uppercase tracking-widest">Total en
                                    cliente:</span>
                                <span
                                    class="bg-white text-blue-700 border border-blue-200 font-bold px-3 py-1 rounded-full text-sm shadow-sm">
                                    {{ datosCliente.totalHoras }} h
                                </span>
                            </div>
                        </div>

                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse">
                                <thead>
                                    <tr
                                        class="bg-white border-b border-slate-100 text-[10px] uppercase tracking-widest text-slate-400">
                                        <th class="px-6 py-3 font-bold w-1/2">Nombre del Proyecto</th>
                                        <th class="px-6 py-3 font-bold text-right w-1/4">Horas Invertidas</th>
                                        <th class="px-6 py-3 font-bold w-1/4">Impacto del Mes</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-50 text-sm">
                                    <tr v-for="p in datosCliente.proyectos" :key="p.proyecto"
                                        class="hover:bg-slate-50/50 transition-colors">
                                        <td class="px-6 py-4">
                                            <div class="flex items-center gap-2">
                                                <p class="font-bold text-slate-700">{{ p.proyecto }}</p>
                                                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase border"
                                                    :class="{
                                                        'bg-emerald-50 text-emerald-600 border-emerald-200': p.estado === 'Activo',
                                                        'bg-amber-50 text-amber-600 border-amber-200': p.estado === 'Cerrado',
                                                        'bg-orange-50 text-orange-600 border-orange-200': p.estado === 'Inactivo',
                                                        'bg-slate-50 text-slate-500 border-slate-200': !p.estado || p.estado === 'Desconocido'
                                                    }">
                                                    {{ p.estado || 'Desconocido' }}
                                                </span>
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 text-right">
                                            <span
                                                class="inline-block px-3 py-1 bg-slate-100 text-slate-700 font-bold rounded-md border border-slate-200">
                                                {{ p.real }} h
                                            </span>
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="flex items-center gap-3">
                                                <div class="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                                                    <div class="h-full bg-primary rounded-full"
                                                        :style="{ width: getPorcentaje(p.real) + '%' }"></div>
                                                </div>
                                                <span class="text-xs font-bold text-slate-600 w-8 text-right">{{
                                                    getPorcentaje(p.real) }}%</span>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>
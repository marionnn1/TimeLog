<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
    ChevronLeft, ChevronRight, Plus, Trash2, Save, Building2, Info, AlertTriangle, X, RotateCcw
} from 'lucide-vue-next'

const route = useRoute()

// --- DÍAS ESPECIALES ---
const diasEspeciales = [
    { dia: 12, mes: 1, tipo: 'festivo', label: 'Festivo' },
    { dia: 16, mes: 1, tipo: 'vacaciones', label: 'Vacaciones' },
    { dia: 20, mes: 1, tipo: 'asuntos_propios', label: 'Asuntos P.' },
    { dia: 27, mes: 1, tipo: 'libre_disposicion', label: 'Libre Disp.' }
]

const getTipoDia = (date) => {
    const especial = diasEspeciales.find(d =>
        d.dia === date.getDate() && d.mes === date.getMonth() && date.getFullYear() === 2026
    )
    return especial ? especial.tipo : null
}
const getLabelDia = (date) => {
    const especial = diasEspeciales.find(d =>
        d.dia === date.getDate() && d.mes === date.getMonth() && date.getFullYear() === 2026
    )
    return especial ? especial.label : null
}

const MAX_HORAS_DIARIAS = 8.5
const MAX_HORAS_SEMANALES = 40.5
const clientesDisponibles = ['Banco Santander', 'Mapfre', 'Inditex', 'BBVA', 'Naturgy']
const proyectosDisponibles = ['Auditoría Backend', 'Migración Cloud', 'Desarrollo Frontend', 'Mantenimiento Legacy', 'Consultoría de Seguridad']

const mostrarModal = ref(false)
const nuevoRegistro = ref({ cliente: '', proyecto: '' })
const fechaActual = ref(new Date())
const diaSeleccionado = ref(new Date().getDate())

onMounted(() => {
    if (route.query.fecha) {
        const fechaUrl = new Date(route.query.fecha)
        if (!isNaN(fechaUrl.getTime())) {
            fechaActual.value = fechaUrl
            diaSeleccionado.value = fechaUrl.getDate()
        }
    }
})

const getLunesSemana = (fecha) => {
    const d = new Date(fecha)
    const dia = d.getDay()
    const diff = d.getDate() - dia + (dia === 0 ? -6 : 1)
    return new Date(d.setDate(diff))
}
const lunesActual = computed(() => getLunesSemana(fechaActual.value))
const diasSemana = computed(() => {
    const dias = []
    for (let i = 0; i < 7; i++) {
        const d = new Date(lunesActual.value)
        d.setDate(lunesActual.value.getDate() + i)
        dias.push(new Date(d))
    }
    return dias
})

const nombresDias = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']
const formatoFechaCabecera = (fecha) => fecha.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
const esFinDeSemana = (date) => { const d = date.getDay(); return d === 0 || d === 6 }

const esHoy = (date) => {
    const hoy = new Date()
    return date.getDate() === hoy.getDate() && date.getMonth() === hoy.getMonth() && date.getFullYear() === hoy.getFullYear()
}

// --- LÓGICA DE BLOQUEO ACTUALIZADA ---
const esEditable = (date) => {
    const hoy = new Date()
    hoy.setHours(0, 0, 0, 0)
    const fechaComparar = new Date(date)
    fechaComparar.setHours(0, 0, 0, 0)

    // 1. Bloquear días pasados
    if (fechaComparar < hoy) return false

    // 2. BLOQUEO TOTAL: Si existe CUALQUIER tipo de día especial, devuelve false
    const tipo = getTipoDia(date)
    if (tipo) return false

    return true
}

// Helper para saber si es pasado PERO no es especial (para ponerlo gris normal)
const esPasadoNormal = (date) => {
    const hoy = new Date()
    hoy.setHours(0, 0, 0, 0)
    const fechaComparar = new Date(date)
    fechaComparar.setHours(0, 0, 0, 0)
    return fechaComparar < hoy && !getTipoDia(date)
}

const esSeleccionado = (date) => date.getDate() === diaSeleccionado.value && date.getMonth() === fechaActual.value.getMonth()
const semanaAnterior = () => { const d = new Date(fechaActual.value); d.setDate(d.getDate() - 7); fechaActual.value = d }
const semanaSiguiente = () => { const d = new Date(fechaActual.value); d.setDate(d.getDate() + 7); fechaActual.value = d }
const seleccionarDia = (date) => { diaSeleccionado.value = date.getDate() }
const irAHoy = () => { fechaActual.value = new Date(); diaSeleccionado.value = new Date().getDate() }

const textoBotonCentral = computed(() => {
    const hoy = new Date()
    const seleccion = new Date(fechaActual.value)
    seleccion.setDate(diaSeleccionado.value)
    if (seleccion.getDate() === hoy.getDate() && seleccion.getMonth() === hoy.getMonth()) return 'HOY'
    const diaSemana = nombresDias[seleccion.getDay() === 0 ? 6 : seleccion.getDay() - 1]
    return `${diaSemana} ${diaSeleccionado.value}`
})

const filas = ref([
    { id: 1, cliente: 'Banco Santander', proyecto: 'Auditoría Backend', horas: [8, 8, 8, 8, 4, 0, 0], seleccionado: false },
    { id: 2, cliente: 'Mapfre', proyecto: 'Migración Cloud', horas: [0, 0, 0, 0, 4, 0, 0], seleccionado: false }
])

const totalFila = (fila) => fila.horas.reduce((acc, h) => acc + (parseFloat(h) || 0), 0)
const totalDia = (index) => filas.value.reduce((acc, f) => acc + (parseFloat(f.horas[index]) || 0), 0)
const totalSemanal = computed(() => filas.value.reduce((acc, f) => acc + totalFila(f), 0))
const excedeLimiteDiario = (index) => totalDia(index) > MAX_HORAS_DIARIAS
const excedeLimiteSemanal = computed(() => totalSemanal.value > MAX_HORAS_SEMANALES)

const abrirModal = () => { nuevoRegistro.value = { cliente: '', proyecto: '' }; mostrarModal.value = true }
const cerrarModal = () => { mostrarModal.value = false }
const confirmarAnadirLinea = () => {
    if (!nuevoRegistro.value.cliente || !nuevoRegistro.value.proyecto) return
    filas.value.push({ id: Date.now(), cliente: nuevoRegistro.value.cliente, proyecto: nuevoRegistro.value.proyecto, horas: [0, 0, 0, 0, 0, 0, 0], seleccionado: false })
    cerrarModal()
}
const borrarLineas = () => filas.value = filas.value.filter(f => !f.seleccionado)
const guardarCambios = () => {
    if (excedeLimiteSemanal.value) return alert('Límite semanal excedido')
    alert('✅ Imputaciones guardadas')
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-4 gap-6 relative">

        <div class="flex flex-col gap-3">
            <div class="flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <h1 class="h1-title capitalize">
                        {{ formatoFechaCabecera(lunesActual) }}
                    </h1>
                    <span class="text-sm font-medium text-gray-400 px-2 border-l border-gray-300">
                        Semana {{ lunesActual.getDate() }} - {{ new Date(lunesActual.getTime() + 6 * 24 * 60 * 60 *
                        1000).getDate() }}
                    </span>
                </div>

                <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200">
                    <button @click="semanaAnterior" class="p-2 hover:bg-gray-50 text-gray-600 border-r border-gray-200">
                        <ChevronLeft class="w-5 h-5" />
                    </button>
                    <button @click="irAHoy"
                        class="px-4 py-2 text-sm font-bold uppercase tracking-wide hover:bg-gray-50 flex items-center gap-2 min-w-[100px] justify-center text-dark">
                        <span v-if="textoBotonCentral !== 'HOY'" class="opacity-50">
                            <RotateCcw class="w-3 h-3" />
                        </span> {{ textoBotonCentral }}
                    </button>
                    <button @click="semanaSiguiente"
                        class="p-2 hover:bg-gray-50 text-gray-600 border-l border-gray-200">
                        <ChevronRight class="w-5 h-5" />
                    </button>
                </div>
            </div>

            <div class="grid grid-cols-7 gap-3 h-32">
                <div v-for="(fecha, index) in diasSemana" :key="index" @click="seleccionarDia(fecha)"
                    class="relative rounded-xl border shadow-sm flex flex-col items-center justify-between p-3 transition-all cursor-pointer group"
                    :class="[
                        esFinDeSemana(fecha) ? 'bg-slate-100 border-slate-200' : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-md',
                        // REFACTORIZADO: ring-primary border-primary
                        esSeleccionado(fecha) ? 'ring-2 ring-offset-2 ring-primary border-primary' : '',
                        esHoy(fecha) ? 'bg-blue-50/50' : '',

                        getTipoDia(fecha) === 'festivo' ? 'bg-rose-50 border-rose-100' : '',
                        getTipoDia(fecha) === 'vacaciones' ? 'bg-teal-50 border-teal-100' : '',
                        getTipoDia(fecha) === 'libre_disposicion' ? 'bg-amber-50 border-amber-100' : '',
                        getTipoDia(fecha) === 'asuntos_propios' ? 'bg-violet-50 border-violet-100' : '',

                        excedeLimiteDiario(index) ? 'border-red-400 bg-red-50' : ''
                    ]"
                    :style="esFinDeSemana(fecha) ? 'background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.03) 10px, rgba(0,0,0,0.03) 20px);' : ''">

                    <span class="text-xs font-bold uppercase tracking-widest"
                        :class="esHoy(fecha) ? 'text-primary' : 'text-gray-400'">{{ nombresDias[index] }}</span>
                    <span class="text-2xl font-bold"
                        :class="esHoy(fecha) ? 'text-dark' : (esFinDeSemana(fecha) ? 'text-gray-400' : 'text-gray-700')">{{
                            fecha.getDate() }}</span>

                    <div v-if="getTipoDia(fecha)" class="mt-1">
                        <span class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded shadow-sm" :class="{
                            'bg-rose-100 text-rose-600': getTipoDia(fecha) === 'festivo',
                            'bg-teal-100 text-teal-600': getTipoDia(fecha) === 'vacaciones',
                            'bg-amber-100 text-amber-600': getTipoDia(fecha) === 'libre_disposicion',
                            'bg-violet-100 text-violet-600': getTipoDia(fecha) === 'asuntos_propios'
                        }">
                            {{ getLabelDia(fecha) }}
                        </span>
                    </div>
                    <div v-else-if="totalDia(index) > 0" class="px-2 py-0.5 rounded-full text-xs font-bold"
                        :class="excedeLimiteDiario(index) ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-dark'">{{
                            totalDia(index) }}h</div>
                    <div v-else class="h-5"></div>

                    <div v-if="esHoy(fecha)" class="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary"></div>
                </div>
            </div>

            <div class="flex items-center gap-6 mt-1 text-xs text-gray-600">
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-white border border-gray-200"></div><span>Laborable</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-rose-300"></div><span>Festivo</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-teal-300"></div><span>Vacaciones</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-blue-200 relative">
                        <div class="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-primary"></div>
                    </div><span>Hoy</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-amber-300"></div><span>Libre Disp.</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-violet-300"></div><span>Asuntos P.</span>
                </div>
            </div>
        </div>

        <div class="card flex-1 flex flex-col overflow-hidden p-0">
            <div class="flex justify-between items-center px-6 py-4 border-b border-gray-200 bg-gray-50/50">
                <h2 class="font-bold text-sm uppercase tracking-wider text-dark flex items-center gap-2">
                    <Info class="w-4 h-4 text-primary" /> Detalle de Imputaciones
                </h2>
                <div class="flex gap-3">
                    <button @click="borrarLineas"
                        class="flex items-center gap-2 px-3 py-1.5 text-xs font-bold text-red-600 hover:bg-red-50 rounded border border-transparent hover:border-red-100 transition uppercase">
                        <Trash2 class="w-3 h-3" /> Borrar
                    </button>
                    <button @click="abrirModal"
                        class="flex items-center gap-2 px-4 py-1.5 text-xs font-bold text-white rounded shadow-md transition hover:shadow-lg uppercase tracking-wide bg-primary">
                        <Plus class="w-4 h-4" /> Añadir Línea
                    </button>
                </div>
            </div>

            <div class="overflow-x-auto flex-1">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-white text-xs uppercase tracking-wider border-b-2 border-gray-100 text-dark">
                            <th class="p-3 w-8 text-center"></th>
                            <th class="p-3 font-bold w-1/4">Cliente</th>
                            <th class="p-3 font-bold w-1/3">Proyecto</th>
                            <th v-for="(fecha, i) in diasSemana" :key="i" class="p-2 text-center w-14"
                                :class="[esFinDeSemana(fecha) ? 'bg-slate-50 text-gray-400' : '', excedeLimiteDiario(i) ? 'bg-red-50 text-red-600 font-bold' : '']">
                                <div class="flex flex-col items-center">
                                    <span>{{ nombresDias[i] }}</span>
                                    <span class="text-[10px] opacity-60 font-medium">{{ fecha.getDate() }}</span>
                                </div>
                            </th>
                            <th class="p-3 font-bold text-center w-16">Total</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-gray-700 divide-y divide-gray-50">
                        <tr v-for="fila in filas" :key="fila.id" class="hover:bg-blue-50/20 transition group">
                            <td class="p-3 text-center"><input type="checkbox" v-model="fila.seleccionado"
                                    class="rounded border-gray-300 text-primary focus:ring-primary"></td>
                            <td class="p-2">
                                <div
                                    class="flex items-center gap-2 border border-transparent hover:border-gray-200 rounded px-2 py-1 bg-transparent hover:bg-white transition">
                                    <Building2 class="w-3 h-3 text-gray-400" /><input v-model="fila.cliente"
                                        class="w-full bg-transparent outline-none text-gray-700 font-medium placeholder-gray-400 text-xs">
                                </div>
                            </td>
                            <td class="p-2"><input v-model="fila.proyecto"
                                    class="w-full border border-transparent hover:border-gray-200 rounded px-2 py-1 bg-transparent hover:bg-white outline-none transition placeholder-gray-400 text-xs">
                            </td>

                            <td v-for="(hora, index) in fila.horas" :key="index" class="p-1 text-center" :class="[
                                esFinDeSemana(diasSemana[index]) ? 'bg-slate-50' : '',
                                getTipoDia(diasSemana[index]) === 'festivo' ? 'bg-rose-50' : '',
                                getTipoDia(diasSemana[index]) === 'vacaciones' ? 'bg-teal-50' : '',
                                getTipoDia(diasSemana[index]) === 'libre_disposicion' ? 'bg-amber-50' : '',
                                getTipoDia(diasSemana[index]) === 'asuntos_propios' ? 'bg-violet-50' : '',
                            ]">

                                <input type="number" min="0" max="24" step="0.5" v-model="fila.horas[index]"
                                    :disabled="!esEditable(diasSemana[index])"
                                    class="w-full text-center p-0 py-1 rounded border transition font-medium bg-transparent text-sm disabled:cursor-not-allowed appearance-none"
                                    :class="{
                                        'text-primary font-bold border-transparent hover:border-gray-300 focus:border-primary focus:ring-1 focus:ring-primary': esEditable(diasSemana[index]) && fila.horas[index] > 0,
                                        'text-gray-300 border-transparent hover:border-gray-300': esEditable(diasSemana[index]) && fila.horas[index] == 0,
                                        'bg-gray-100 text-gray-400': esPasadoNormal(diasSemana[index]),
                                        'bg-rose-50 text-rose-400 placeholder-rose-300': getTipoDia(diasSemana[index]) === 'festivo',
                                        'bg-teal-50 text-teal-400 placeholder-teal-300': getTipoDia(diasSemana[index]) === 'vacaciones',
                                        'bg-amber-50 text-amber-400 placeholder-amber-300': getTipoDia(diasSemana[index]) === 'libre_disposicion',
                                        'bg-violet-50 text-violet-400 placeholder-violet-300': getTipoDia(diasSemana[index]) === 'asuntos_propios',
                                    }" :placeholder="getTipoDia(diasSemana[index]) ? '—' : ''">
                            </td>
                            <td class="p-3 text-center font-bold text-dark bg-gray-50 text-sm">{{ totalFila(fila) }}
                            </td>
                        </tr>
                    </tbody>
                    <tfoot class="bg-gray-50 border-t border-gray-200 text-xs font-bold text-dark">
                        <tr>
                            <td colspan="3" class="p-3 text-right uppercase">Total Diario:</td>
                            <td v-for="(dia, index) in diasSemana" :key="index" class="p-2 text-center"
                                :class="excedeLimiteDiario(index) ? 'bg-red-100' : ''"><span
                                    :class="[excedeLimiteDiario(index) ? 'text-red-600 font-extrabold' : (totalDia(index) > 0 ? 'text-primary' : 'text-gray-400')]">{{
                                        totalDia(index) }}</span></td>
                            <td class="p-3 text-center border-l border-blue-100 text-sm transition-colors"
                                :class="excedeLimiteSemanal ? 'bg-red-600 text-white' : 'bg-blue-50 text-blue-900'">{{
                                    totalSemanal }} / {{ MAX_HORAS_SEMANALES }}</td>
                        </tr>
                    </tfoot>
                </table>
            </div>

            <div class="p-3 bg-gray-50 border-t border-gray-200 flex justify-end">
                <button @click="guardarCambios" :disabled="excedeLimiteSemanal"
                    class="flex items-center gap-2 px-6 py-2 text-white font-bold rounded shadow-md transition text-xs uppercase tracking-wider disabled:opacity-50 disabled:cursor-not-allowed"
                    :class="excedeLimiteSemanal ? 'bg-gray-400' : 'bg-dark hover:shadow-lg'">
                    <Save class="w-4 h-4" /> Guardar Imputaciones
                </button>
            </div>
        </div>

        <div v-if="mostrarModal"
            class="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
            <div
                class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
                <div class="bg-slate-50 border-b border-gray-100 px-6 py-4 flex justify-between items-center">
                    <h3 class="text-lg font-bold text-dark">Nueva Imputación</h3>
                    <button @click="cerrarModal" class="text-gray-400 hover:text-red-500 transition">
                        <X class="w-5 h-5" />
                    </button>
                </div>
                <div class="p-6 space-y-4">
                    <div>
                        <label class="label-std">Cliente</label>
                        <div class="relative">
                            <select v-model="nuevoRegistro.cliente"
                                class="w-full border border-gray-200 rounded-lg p-2.5 text-sm text-gray-700 focus:ring-2 focus:ring-primary focus:border-primary outline-none appearance-none bg-white">
                                <option value="" disabled selected>Selecciona un cliente...</option>
                                <option v-for="c in clientesDisponibles" :key="c" :value="c">{{ c }}</option>
                            </select>
                            <div class="absolute right-3 top-3 pointer-events-none text-gray-400">▼</div>
                        </div>
                    </div>
                    <div>
                        <label class="label-std">Proyecto / Tarea</label>
                        <div class="relative">
                            <select v-model="nuevoRegistro.proyecto"
                                class="w-full border border-gray-200 rounded-lg p-2.5 text-sm text-gray-700 focus:ring-2 focus:ring-primary focus:border-primary outline-none appearance-none bg-white">
                                <option value="" disabled selected>Selecciona un proyecto...</option>
                                <option v-for="p in proyectosDisponibles" :key="p" :value="p">{{ p }}</option>
                            </select>
                            <div class="absolute right-3 top-3 pointer-events-none text-gray-400">▼</div>
                        </div>
                    </div>
                </div>
                <div class="px-6 py-4 bg-gray-50 flex justify-end gap-3 border-t border-gray-100">
                    <button @click="cerrarModal"
                        class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 transition">Cancelar</button>
                    <button @click="confirmarAnadirLinea"
                        class="px-6 py-2 text-sm font-bold text-white rounded-lg shadow transition transform active:scale-95 bg-primary">Añadir
                        a la Tabla</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Eliminar flechas del input number */
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
</style>
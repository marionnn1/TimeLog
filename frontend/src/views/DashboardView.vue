<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '../stores/dataStore' // <--- 1. IMPORTAR STORE
import {
    ChevronLeft, ChevronRight, Plus, Trash2, Save, Building2, Info, X, RotateCcw
} from 'lucide-vue-next'

const route = useRoute()
const store = useDataStore() // <--- 2. USAR STORE

// --- GESTIÓN DE FECHAS DESDE EL STORE ---
const getInfoDia = (date) => {
    // Ajuste zona horaria para coincidir con el string del store (YYYY-MM-DD)
    const offset = date.getTimezoneOffset() * 60000
    const isoDate = new Date(date.getTime() - offset).toISOString().split('T')[0]
    
    // Consultamos al store
    const ausencia = store.getAusenciaPorFecha(isoDate, store.getCurrentUser().id)
    
    if (!ausencia) return null
    
    return {
        // Mapeamos 'asuntos' del store a 'asuntos_propios' que usa tu template original
        tipo: ausencia.type === 'asuntos' ? 'asuntos_propios' : ausencia.type,
        label: ausencia.type === 'asuntos' ? 'Asuntos P.' : (ausencia.type.charAt(0).toUpperCase() + ausencia.type.slice(1))
    }
}

const getTipoDia = (date) => getInfoDia(date)?.tipo
const getLabelDia = (date) => getInfoDia(date)?.label

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
    } else {
        fechaActual.value = new Date() 
        diaSeleccionado.value = fechaActual.value.getDate()
    }
})

// --- FECHAS Y SEMANAS ---
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

// --- CÁLCULO DE LÍMITES ---
const esJornadaVerano = (date) => {
    const mes = date.getMonth()
    return mes === 6 || mes === 7
}

const getMaxHorasDia = (date) => {
    if (getTipoDia(date)) return 0 // Si hay vacación en Store, 0 horas
    if (date.getDay() === 0 || date.getDay() === 6) return 0 
    if (esJornadaVerano(date)) return 7.0
    if (date.getDay() === 5) return 6.5
    return 8.5
}

// LÓGICA MODIFICADA: Si es pasado y está vacío, no cuenta para el total
const getMaxHorasSemana = () => {
    const hoy = new Date()
    hoy.setHours(0,0,0,0)

    return diasSemana.value.reduce((total, fecha, index) => {
        const maxHorasDia = getMaxHorasDia(fecha)
        const horasImputadas = totalDia(index)
        
        const fechaDia = new Date(fecha)
        fechaDia.setHours(0,0,0,0)

        // Si es pasado, horas 0 y NO es un día especial (vacaciones), no suma deuda
        if (fechaDia < hoy && horasImputadas === 0 && !getTipoDia(fecha)) {
            return total 
        }

        return total + maxHorasDia
    }, 0)
}

// UTILS
const nombresDias = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']
const formatoFechaCabecera = (fecha) => fecha.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
const esFinDeSemana = (date) => { const d = date.getDay(); return d === 0 || d === 6 }

const esHoy = (date) => {
    const hoy = new Date()
    return date.getDate() === hoy.getDate() && date.getMonth() === hoy.getMonth() && date.getFullYear() === hoy.getFullYear()
}

const esEditable = (date) => {
    const hoy = new Date()
    hoy.setHours(0, 0, 0, 0)
    const fechaComparar = new Date(date)
    fechaComparar.setHours(0, 0, 0, 0)

    if (esFinDeSemana(date)) return false 
    if (fechaComparar < hoy) return false 
    if (getTipoDia(date)) return false // Bloqueado si hay dato en Store
    
    return true
}

const esPasadoNormal = (date) => {
    const hoy = new Date()
    hoy.setHours(0, 0, 0, 0)
    const fechaComparar = new Date(date)
    fechaComparar.setHours(0, 0, 0, 0)
    return fechaComparar < hoy && !getTipoDia(date) && !esFinDeSemana(date)
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

// --- DATOS TABLA ---
const filas = ref([
    { id: 1, cliente: 'Banco Santander', proyecto: 'Auditoría Backend', horas: [0, 0, 8.5, 0, 6.5, 0, 0], seleccionado: false },
    { id: 2, cliente: 'Mapfre', proyecto: 'Migración Cloud', horas: [0, 0, 0, 0, 0, 0, 0], seleccionado: false }
])

watch(lunesActual, () => {
    filas.value.forEach(fila => {
        fila.horas = [0, 0, 0, 0, 0, 0, 0]
    })
})

const handleFocus = (event) => {
    if (event.target.value == 0) event.target.value = ''
}
const handleBlur = (event, fila, index) => {
    if (event.target.value === '') fila.horas[index] = 0
}

const totalFila = (fila) => fila.horas.reduce((acc, h) => acc + (parseFloat(h) || 0), 0)
const totalDia = (index) => filas.value.reduce((acc, f) => {
    const val = parseFloat(f.horas[index])
    return acc + (isNaN(val) ? 0 : val)
}, 0)
const totalSemanal = computed(() => filas.value.reduce((acc, f) => acc + totalFila(f), 0))

// Validaciones
const excedeLimiteDiario = (index) => {
    const fechaDia = diasSemana.value[index]
    const maxHoras = getMaxHorasDia(fechaDia)
    if (maxHoras === 0) return false 
    return totalDia(index) > maxHoras
}

const excedeLimiteSemanal = computed(() => totalSemanal.value > getMaxHorasSemana())

const hayErrores = computed(() => {
    if (excedeLimiteSemanal.value) return true
    for (let i = 0; i < 7; i++) {
        if (excedeLimiteDiario(i)) return true
    }
    return false
})

const abrirModal = () => { nuevoRegistro.value = { cliente: '', proyecto: '' }; mostrarModal.value = true }
const cerrarModal = () => { mostrarModal.value = false }
const confirmarAnadirLinea = () => {
    if (!nuevoRegistro.value.cliente || !nuevoRegistro.value.proyecto) return
    filas.value.push({ id: Date.now(), cliente: nuevoRegistro.value.cliente, proyecto: nuevoRegistro.value.proyecto, horas: [0, 0, 0, 0, 0, 0, 0], seleccionado: false })
    cerrarModal()
}
const borrarLineas = () => filas.value = filas.value.filter(f => !f.seleccionado)
const guardarCambios = () => {
    if (hayErrores.value) return alert('Por favor corrige los días en rojo antes de guardar.')
    alert('✅ Imputaciones guardadas correctamente')
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
                        Semana {{ lunesActual.getDate() }} - {{ new Date(lunesActual.getTime() + 6 * 24 * 60 * 60 * 1000).getDate() }}
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
                        esSeleccionado(fecha) ? 'ring-2 ring-offset-2 ring-primary border-primary' : '',
                        esHoy(fecha) ? 'bg-blue-50/50' : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-md',
                        esFinDeSemana(fecha) ? 'bg-slate-100 border-slate-200 cursor-default' : '',
                        excedeLimiteDiario(index) ? 'border-red-500 bg-red-50' : ''
                    ]"
                    :style="esFinDeSemana(fecha) ? 'background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.03) 10px, rgba(0,0,0,0.03) 20px);' : ''">

                    <span class="text-xs font-bold uppercase tracking-widest"
                        :class="esHoy(fecha) ? 'text-primary' : 'text-gray-400'">{{ nombresDias[index] }}</span>
                    <span class="text-2xl font-bold"
                        :class="esHoy(fecha) ? 'text-dark' : (esFinDeSemana(fecha) ? 'text-gray-400' : 'text-gray-700')">{{
                        fecha.getDate() }}</span>

                    <div v-if="getTipoDia(fecha)" class="mt-1">
                        <span class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded shadow-sm" :class="{
                            'bg-orange-100 text-orange-700': getTipoDia(fecha) === 'festivo',
                            'bg-emerald-100 text-emerald-700': getTipoDia(fecha) === 'vacaciones',
                            'bg-blue-100 text-blue-700': getTipoDia(fecha) === 'asuntos_propios'
                        }">
                            {{ getLabelDia(fecha) }}
                        </span>
                    </div>

                    <div v-else-if="totalDia(index) > 0" class="px-2 py-0.5 rounded-full text-xs font-bold relative group/tooltip"
                        :class="excedeLimiteDiario(index) ? 'bg-red-100 text-red-700 animate-pulse' : 'bg-blue-100 text-dark'">
                        {{ totalDia(index) }}h
                        
                        <span v-if="excedeLimiteDiario(index)" class="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-max bg-red-800 text-white text-[10px] px-2 py-1 rounded shadow-lg z-50">
                            Máx permitido: {{ getMaxHorasDia(fecha) }}h
                        </span>
                    </div>
                    <div v-else class="h-5"></div>

                    <div v-if="esHoy(fecha)" class="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary"></div>
                </div>
            </div>

            <div class="flex items-center gap-6 mt-1 text-xs text-gray-600">
                <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-white border border-gray-200"></div><span>Laborable</span></div>
                <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-orange-500"></div><span>Festivo</span></div>
                <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-emerald-500"></div><span>Vacaciones</span></div>
                <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-blue-500"></div><span>Asuntos P.</span></div>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-blue-200 relative"><div class="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-primary"></div></div><span>Hoy</span>
                </div>
            </div>
        </div>

        <div class="card flex-1 flex flex-col overflow-hidden p-0">
            <div class="flex justify-between items-center px-6 py-4 border-b border-gray-200 bg-gray-50/50">
                <h2 class="font-bold text-sm uppercase tracking-wider text-dark flex items-center gap-2">
                    <Info class="w-4 h-4 text-primary" /> Detalle de Imputaciones
                </h2>
                <div class="flex gap-3">
                    <button @click="borrarLineas" class="flex items-center gap-2 px-3 py-1.5 text-xs font-bold text-red-600 hover:bg-red-50 rounded border border-transparent hover:border-red-100 transition uppercase">
                        <Trash2 class="w-3 h-3" /> Borrar
                    </button>
                    <button @click="abrirModal" class="btn-primary">
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
                                :class="[
                                    esFinDeSemana(fecha) ? 'bg-slate-50 text-gray-400' : '',
                                    excedeLimiteDiario(i) ? 'bg-red-50 text-red-600 font-bold' : ''
                                ]">
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
                                <div class="flex items-center gap-2 border border-transparent hover:border-gray-200 rounded px-2 py-1 bg-transparent hover:bg-white transition">
                                    <Building2 class="w-3 h-3 text-gray-400" /><input v-model="fila.cliente"
                                        class="w-full bg-transparent outline-none text-gray-700 font-medium placeholder-gray-400 text-xs">
                                </div>
                            </td>
                            <td class="p-2"><input v-model="fila.proyecto"
                                    class="w-full border border-transparent hover:border-gray-200 rounded px-2 py-1 bg-transparent hover:bg-white outline-none transition placeholder-gray-400 text-xs">
                            </td>

                            <td v-for="(hora, index) in fila.horas" :key="index" class="p-1 text-center" :class="[
                                esFinDeSemana(diasSemana[index]) ? 'bg-slate-50' : '',
                                // 5. COLORES DE FONDO DE CELDA
                                getTipoDia(diasSemana[index]) === 'festivo' ? 'bg-orange-50' : '',
                                getTipoDia(diasSemana[index]) === 'vacaciones' ? 'bg-emerald-50' : '',
                                getTipoDia(diasSemana[index]) === 'asuntos_propios' ? 'bg-blue-50' : '',
                            ]">
                                
                                <input type="number" min="0" max="24" step="0.5" 
                                    v-model="fila.horas[index]"
                                    @focus="handleFocus" 
                                    @blur="(e) => handleBlur(e, fila, index)"
                                    :disabled="!esEditable(diasSemana[index])"
                                    class="w-full text-center p-0 py-1 rounded transition font-medium text-sm disabled:cursor-not-allowed appearance-none"
                                    :class="{
                                        'text-primary font-bold border border-transparent hover:border-gray-300 focus:border-primary focus:ring-1 focus:ring-primary bg-transparent': esEditable(diasSemana[index]) && fila.horas[index] > 0,
                                        'bg-white border border-gray-200 hover:border-[#1F8C7F] hover:bg-teal-50/20 text-[#1F8C7F] shadow-sm cursor-pointer font-bold': esEditable(diasSemana[index]) && fila.horas[index] == 0,
                                        'bg-gray-100 text-gray-400 border-transparent': esPasadoNormal(diasSemana[index]) || esFinDeSemana(diasSemana[index]),
                                        
                                        // 6. COLORES DE INPUT Y TEXTO
                                        'bg-orange-50 text-orange-600 border-transparent font-bold placeholder-orange-300': getTipoDia(diasSemana[index]) === 'festivo',
                                        'bg-emerald-50 text-emerald-600 border-transparent font-bold placeholder-emerald-300': getTipoDia(diasSemana[index]) === 'vacaciones',
                                        'bg-blue-50 text-blue-600 border-transparent font-bold placeholder-blue-300': getTipoDia(diasSemana[index]) === 'asuntos_propios',

                                        'border border-red-300 bg-red-50 text-red-600 font-extrabold shadow-none': esEditable(diasSemana[index]) && excedeLimiteDiario(index)
                                    }" :placeholder="getTipoDia(diasSemana[index]) || (esFinDeSemana(diasSemana[index]) ? '' : '0')">
                                    
                                    <div v-if="getTipoDia(diasSemana[index])" class="text-[9px] text-center uppercase font-bold opacity-60">
                                        {{ getLabelDia(diasSemana[index]).substring(0,3) }}
                                    </div>
                            </td>
                            <td class="p-3 text-center font-bold text-dark bg-gray-50 text-sm">{{ totalFila(fila) }}</td>
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
                                totalSemanal }} / {{ getMaxHorasSemana() }}</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <div class="p-3 bg-gray-50 border-t border-gray-200 flex justify-end gap-3 items-center">
                <p v-if="hayErrores" class="text-xs font-bold text-red-600 flex items-center gap-1 animate-pulse">
                    <X class="w-4 h-4"/> Corrige el exceso de horas para guardar
                </p>
                <button @click="guardarCambios" :disabled="hayErrores"
                    class="flex items-center gap-2 px-6 py-2 text-white font-bold rounded shadow-md transition text-xs uppercase tracking-wider disabled:opacity-50 disabled:cursor-not-allowed"
                    :class="hayErrores ? 'bg-gray-400' : 'bg-dark hover:shadow-lg'">
                    <Save class="w-4 h-4" /> Guardar Imputaciones
                </button>
            </div>
        </div>

        <div v-if="mostrarModal"
            class="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
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
                    <button @click="cerrarModal" class="btn-secondary">Cancelar</button>
                    <button @click="confirmarAnadirLinea" class="btn-primary">Añadir a la Tabla</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
</style>
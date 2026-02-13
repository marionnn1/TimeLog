<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { 
    Calendar as CalendarIcon, ChevronLeft, ChevronRight, 
    AlertTriangle, UserPlus, X, Check, Palmtree, MapPin, Briefcase,
    AlertCircle, CheckCircle2, Trash2
} from 'lucide-vue-next'

const store = useDataStore()
const currentUser = store.getCurrentUser() 

// --- SISTEMA DE NOTIFICACIONES (TOAST) ---
const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

// --- SISTEMA DE CONFIRMACIÓN ---
const confirmState = ref({ show: false, title: '', message: '', type: 'neutral', action: null })

const solicitarConfirmacion = (title, message, type, callback) => {
    confirmState.value = { show: true, title, message, type, action: callback }
}

const ejecutarConfirmacion = () => {
    if (confirmState.value.action) confirmState.value.action()
    confirmState.value.show = false
}

// --- FECHA Y CALENDARIO ---
const currentDate = ref(new Date())
const year = computed(() => currentDate.value.getFullYear())
const month = computed(() => currentDate.value.getMonth())
const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

// --- CONEXIÓN DE DATOS (LEER DEL STORE) ---
const getAusenciasDia = (isoDate) => store.getAusenciasEquipoPorFecha(isoDate)
const getMiAusencia = (isoDate) => store.getAusenciaPorFecha(isoDate, currentUser.id)

// --- MODAL ---
const mostrarModal = ref(false)
const form = ref({
    fechaInicio: '',
    fechaFin: '',
    tipo: 'vacaciones', 
})

// --- ESTILOS VISUALES ---
const getEstiloTipo = (tipo) => {
    switch(tipo) {
        case 'vacaciones': return 'bg-emerald-100 text-emerald-700 border-emerald-200'
        case 'festivo': return 'bg-orange-100 text-orange-700 border-orange-200' 
        case 'asuntos': return 'bg-blue-100 text-blue-700 border-blue-200'
        default: return 'bg-gray-100'
    }
}

const getIconoTipo = (tipo) => {
    switch(tipo) {
        case 'vacaciones': return Palmtree
        case 'festivo': return MapPin
        case 'asuntos': return Briefcase
    }
}

// --- CÁLCULOS CALENDARIO ---
const daysInMonth = computed(() => {
    const days = new Date(year.value, month.value + 1, 0).getDate()
    return Array.from({ length: days }, (_, i) => {
        const d = new Date(year.value, month.value, i + 1)
        const offset = d.getTimezoneOffset() * 60000
        const isoDate = new Date(d.getTime() - offset).toISOString().split('T')[0]
        
        return {
            dateObj: d, dayNum: i + 1, isoDate: isoDate,
            isWeekend: d.getDay() === 0 || d.getDay() === 6
        }
    })
})

const startPadding = computed(() => {
    const firstDay = new Date(year.value, month.value, 1).getDay()
    return firstDay === 0 ? 6 : firstDay - 1 
})

// --- ACCIONES ---

const abrirModal = (day) => {
    if (day.isWeekend) return

    const existing = getMiAusencia(day.isoDate)
    if (existing) {
        solicitarConfirmacion(
            'Eliminar Ausencia',
            `¿Estás seguro de eliminar tu ${existing.type} del día ${day.dayNum}?`,
            'danger',
            () => {
                store.removeAusencia(day.isoDate, currentUser.id)
                showToast('Ausencia eliminada correctamente', 'success')
            }
        )
        return
    }

    form.value = {
        fechaInicio: day.isoDate,
        fechaFin: day.isoDate, 
        tipo: 'vacaciones'
    }
    mostrarModal.value = true
}

const procesarSolicitud = (diasSolicitados) => {
    diasSolicitados.forEach(date => {
        store.addAusencia({
            date: date,
            userId: currentUser.id,
            nombre: currentUser.nombre,
            iniciales: currentUser.iniciales,
            type: form.value.tipo
        })
    })
    mostrarModal.value = false
    showToast('Solicitud registrada con éxito', 'success')
}

const confirmarSolicitud = () => {
    const start = new Date(form.value.fechaInicio)
    const end = new Date(form.value.fechaFin)
    const diasSolicitados = []

    for(let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        if (d.getDay() !== 0 && d.getDay() !== 6) {
            const offset = d.getTimezoneOffset() * 60000
            const iso = new Date(d.getTime() - offset).toISOString().split('T')[0]
            diasSolicitados.push(iso)
        }
    }

    if (diasSolicitados.length === 0) {
        showToast("Selecciona al menos un día laborable.", "error")
        return
    }

    let alertaJefe = false
    diasSolicitados.forEach(date => {
        const total = getAusenciasDia(date).length
        if (total >= 3) alertaJefe = true
    })

    if (alertaJefe) {
        solicitarConfirmacion(
            'Alta Demanda Detectada',
            'Algunos días seleccionados ya tienen a 3 o más compañeros fuera. Se notificará al Jefe de Proyecto. ¿Continuar?',
            'warning',
            () => procesarSolicitud(diasSolicitados)
        )
        return
    }

    procesarSolicitud(diasSolicitados)
}


const prevMonth = () => currentDate.value = new Date(year.value, month.value - 1, 1)
const nextMonth = () => currentDate.value = new Date(year.value, month.value + 1, 1)
</script>

<template>
  <div class="h-full flex flex-col font-sans p-6 bg-slate-50 overflow-y-auto relative">
    
    <div class="flex justify-between items-center mb-6">
        <div>
            <h1 class="h1-title flex items-center gap-2">
                <CalendarIcon class="w-8 h-8 text-slate-400" /> 
                Calendario Global
            </h1>
            <p class="subtitle">Coordina tus días libres con el resto del equipo.</p>
        </div>

        <div class="flex gap-4 text-xs items-center bg-white px-4 py-2 rounded-lg border border-slate-200 shadow-sm">
            <div class="flex items-center gap-1.5 font-medium text-emerald-700">
                <div class="w-2 h-2 rounded-full bg-emerald-500"></div> Vacaciones
            </div>
            <div class="flex items-center gap-1.5 font-medium text-orange-700">
                <div class="w-2 h-2 rounded-full bg-orange-500"></div> Festivo Local
            </div>
            <div class="flex items-center gap-1.5 font-medium text-blue-700">
                <div class="w-2 h-2 rounded-full bg-blue-500"></div> Asuntos P.
            </div>
        </div>
    </div>

    <div class="flex items-center justify-between bg-white p-4 rounded-t-xl border border-slate-200 border-b-0">
        <button @click="prevMonth" class="btn-ghost hover:bg-slate-100"><ChevronLeft/></button>
        <h2 class="text-xl font-bold text-slate-800 capitalize">{{ monthNames[month] }} {{ year }}</h2>
        <button @click="nextMonth" class="btn-ghost hover:bg-slate-100"><ChevronRight/></button>
    </div>

    <div class="bg-white rounded-b-xl border border-slate-200 shadow-sm overflow-hidden select-none">
        
        <div class="grid grid-cols-7 bg-slate-50 border-b border-slate-200 text-center py-3">
            <div v-for="d in ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']" :key="d" 
                 class="text-xs font-bold text-slate-400 uppercase tracking-wider">
                {{ d }}
            </div>
        </div>

        <div class="grid grid-cols-7 auto-rows-fr">
            <div v-for="p in startPadding" :key="'pad-'+p" class="bg-slate-50/50 border-b border-r border-slate-100 min-h-[140px]"></div>

            <div v-for="day in daysInMonth" :key="day.isoDate" 
                 @click="abrirModal(day)"
                 class="relative border-b border-r border-slate-100 min-h-[140px] p-2 transition-all group hover:bg-slate-50 cursor-pointer"
                 :class="{ 'bg-slate-50': day.isWeekend, 'bg-white': !day.isWeekend }">
                
                <div class="flex justify-between items-start mb-1">
                    <span class="text-sm font-bold" 
                          :class="day.isoDate === new Date().toISOString().split('T')[0] ? 'bg-slate-900 text-white w-6 h-6 rounded-full flex items-center justify-center' : 'text-slate-700'">
                        {{ day.dayNum }}
                    </span>
                    
                    <div v-if="!day.isWeekend && getAusenciasDia(day.isoDate).length >= 3" 
                         class="text-rose-500 animate-pulse" title="Alta concurrencia">
                        <AlertTriangle class="w-4 h-4" />
                    </div>
                </div>

                <div v-if="getMiAusencia(day.isoDate)" 
                     class="mb-2 p-1.5 rounded-md border text-xs font-bold flex items-center gap-1.5 animate-in zoom-in-95"
                     :class="getEstiloTipo(getMiAusencia(day.isoDate).type)">
                    <component :is="getIconoTipo(getMiAusencia(day.isoDate).type)" class="w-3 h-3" />
                    <span class="capitalize">{{ getMiAusencia(day.isoDate).type }}</span>
                </div>

                <div class="flex flex-wrap gap-1 content-start">
                    <div v-for="aus in getAusenciasDia(day.isoDate)" :key="aus.userId">
                        <div v-if="aus.userId !== currentUser.id" 
                             class="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-bold border border-white shadow-sm ring-1 ring-white"
                             :class="{
                                 'bg-emerald-200 text-emerald-800': aus.type === 'vacaciones',
                                 'bg-orange-200 text-orange-800': aus.type === 'festivo',
                                 'bg-blue-200 text-blue-800': aus.type === 'asuntos'
                             }"
                             :title="`${aus.nombre} (${aus.type})`">
                            {{ aus.iniciales }}
                        </div>
                    </div>
                </div>

                <div v-if="!day.isWeekend && !getMiAusencia(day.isoDate)" 
                     class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-slate-50/30">
                    <div class="bg-white rounded-full p-2 shadow-sm border border-slate-200 text-slate-400">
                        <UserPlus class="w-5 h-5" />
                    </div>
                </div>

            </div>
        </div>
    </div>

    <div v-if="mostrarModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl p-6 animate-in zoom-in-95">
            
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-bold text-slate-800">Solicitar Días</h3>
                <button @click="mostrarModal=false" class="text-slate-400 hover:text-slate-600"><X class="w-6 h-6"/></button>
            </div>

            <div class="space-y-6">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="label-std">Desde</label>
                        <input type="date" v-model="form.fechaInicio" class="input-std font-bold text-slate-700">
                    </div>
                    <div>
                        <label class="label-std">Hasta</label>
                        <input type="date" v-model="form.fechaFin" class="input-std font-bold text-slate-700">
                    </div>
                </div>

                <div>
                    <label class="label-std mb-2">Motivo de la Ausencia</label>
                    <div class="grid grid-cols-3 gap-2">
                        <div @click="form.tipo = 'vacaciones'" 
                             class="cursor-pointer border rounded-xl p-3 flex flex-col items-center gap-2 transition-all"
                             :class="form.tipo === 'vacaciones' ? 'border-emerald-500 bg-emerald-50 text-emerald-700 ring-1 ring-emerald-500' : 'border-slate-200 hover:border-slate-300 text-slate-500'">
                            <Palmtree class="w-6 h-6" />
                            <span class="text-[10px] font-bold uppercase">Vacaciones</span>
                        </div>
                        <div @click="form.tipo = 'festivo'" 
                             class="cursor-pointer border rounded-xl p-3 flex flex-col items-center gap-2 transition-all"
                             :class="form.tipo === 'festivo' ? 'border-orange-500 bg-orange-50 text-orange-700 ring-1 ring-orange-500' : 'border-slate-200 hover:border-slate-300 text-slate-500'">
                            <MapPin class="w-6 h-6" />
                            <span class="text-[10px] font-bold uppercase">Festivo Local</span>
                        </div>
                        <div @click="form.tipo = 'asuntos'" 
                             class="cursor-pointer border rounded-xl p-3 flex flex-col items-center gap-2 transition-all"
                             :class="form.tipo === 'asuntos' ? 'border-blue-500 bg-blue-50 text-blue-700 ring-1 ring-blue-500' : 'border-slate-200 hover:border-slate-300 text-slate-500'">
                            <Briefcase class="w-6 h-6" />
                            <span class="text-[10px] font-bold uppercase">Asuntos P.</span>
                        </div>
                    </div>
                </div>

                <button @click="confirmarSolicitud" class="w-full btn-primary py-3 justify-center text-base">
                    <Check class="w-5 h-5 mr-2"/> Confirmar Solicitud
                </button>
            </div>
        </div>
    </div>

    <div v-if="confirmState.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
        <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
            <div class="flex flex-col items-center text-center gap-3">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2"
                     :class="confirmState.type === 'danger' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'">
                    <component :is="confirmState.type === 'danger' ? Trash2 : AlertTriangle" class="w-6 h-6" />
                </div>
                <h3 class="text-lg font-bold text-slate-900">{{ confirmState.title }}</h3>
                <p class="text-sm text-slate-500 leading-relaxed">{{ confirmState.message }}</p>
                
                <div class="flex gap-3 w-full mt-4">
                    <button @click="confirmState.show = false" class="btn-secondary flex-1 justify-center">Cancelar</button>
                    <button @click="ejecutarConfirmacion" 
                            class="flex-1 justify-center btn-primary"
                            :class="confirmState.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : 'bg-amber-600 hover:bg-amber-700'">
                        Confirmar
                    </button>
                </div>
            </div>
        </div>
    </div>

    <transition enter-active-class="transform ease-out duration-300 transition" enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2" enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="toast.show" class="absolute bottom-6 right-6 z-50 flex items-center w-full max-w-xs p-4 space-x-3 text-gray-500 bg-white rounded-lg shadow-lg border border-gray-100">
            <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg" :class="toast.type === 'success' ? 'text-green-500 bg-green-100' : 'text-red-500 bg-red-100'">
                <component :is="toast.type === 'success' ? CheckCircle2 : AlertCircle" class="w-5 h-5"/>
            </div>
            <div class="ml-3 text-sm font-bold text-gray-800">{{ toast.message }}</div>
            <button @click="toast.show = false" class="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 items-center justify-center">
                <X class="w-4 h-4"/>
            </button>
        </div>
    </transition>

  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
// 1. Importamos el Store
import { useDataStore } from '../stores/dataStore'
import { 
    Calendar as CalendarIcon, ChevronLeft, ChevronRight, 
    AlertTriangle, UserPlus, X, Check, Palmtree, MapPin, Briefcase 
} from 'lucide-vue-next'

// 2. Inicializamos
const store = useDataStore()
const currentUser = store.getCurrentUser() // Usamos el usuario real del store

// --- FECHA Y CALENDARIO ---
const currentDate = ref(new Date())
const year = computed(() => currentDate.value.getFullYear())
const month = computed(() => currentDate.value.getMonth())
const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

// --- CONEXIÓN DE DATOS (Store Wrappers) ---
// En lugar de filtrar un array local, pedimos los datos al store
const getAusenciasDia = (isoDate) => store.getAusenciasEquipoPorFecha(isoDate)
const getMiAusencia = (isoDate) => store.getAusenciaPorFecha(isoDate, currentUser.id)

// --- MODAL DE SOLICITUD ---
const mostrarModal = ref(false)
const form = ref({
    fechaInicio: '',
    fechaFin: '',
    tipo: 'vacaciones', 
})

// --- HELPERS VISUALES (Se mantienen igual) ---
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

// 1. Abrir Modal al hacer clic en un día
const abrirModal = (day) => {
    if (day.isWeekend) return

    // Si ya tengo algo, preguntar para BORRAR usando el STORE
    const existing = getMiAusencia(day.isoDate)
    if (existing) {
        if(confirm(`¿Eliminar tu ${existing.type} del día ${day.dayNum}?`)) {
            store.removeAusencia(day.isoDate, currentUser.id) // <--- Acción del Store
        }
        return
    }

    form.value = {
        fechaInicio: day.isoDate,
        fechaFin: day.isoDate, 
        tipo: 'vacaciones'
    }
    mostrarModal.value = true
}

// 2. Confirmar y Guardar en el STORE
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

    if (diasSolicitados.length === 0) return alert("Selecciona días laborables.")

    // Verificar Concurrencia
    let alertaJefe = false
    diasSolicitados.forEach(date => {
        const total = getAusenciasDia(date).length
        if (total >= 3) alertaJefe = true
    })

    if (alertaJefe) {
        const confirmar = confirm("⚠️ ALERTA DE ALTA DEMANDA\n\nAlgunos días ya tienen a 3 o más compañeros fuera.\nSe enviará una notificación al Jefe de Proyecto.\n\n¿Confirmar solicitud?")
        if (!confirmar) return
    }

    // GUARDAR EN EL STORE
    diasSolicitados.forEach(date => {
        // La función addAusencia del store ya controla duplicados
        store.addAusencia({
            date: date,
            userId: currentUser.id,
            nombre: currentUser.nombre,
            iniciales: currentUser.iniciales,
            type: form.value.tipo
        })
    })

    mostrarModal.value = false
}

// Navegación
const prevMonth = () => currentDate.value = new Date(year.value, month.value - 1, 1)
const nextMonth = () => currentDate.value = new Date(year.value, month.value + 1, 1)
</script>

<template>
  <div class="h-full flex flex-col font-sans p-6 bg-slate-50 overflow-y-auto">
    
    <div class="flex justify-between items-center mb-6">
        <div>
            <h1 class="h1-title flex items-center gap-2">
                <CalendarIcon class="w-8 h-8 text-slate-400" /> 
                Calendario Global
            </h1>
            <p class="subtitle">Coordina tus días libres con el resto del equipo.</p>
        </div>

        <div class="flex gap-4 text-xs items-center bg-white px-4 py-2 rounded-lg border border-slate-200 shadow-sm">
            <div class="flex items-center gap-1.5 font-medium text-emerald-700"><div class="w-2 h-2 rounded-full bg-emerald-500"></div> Vacaciones</div>
            <div class="flex items-center gap-1.5 font-medium text-orange-700"><div class="w-2 h-2 rounded-full bg-orange-500"></div> Festivo Local</div>
            <div class="flex items-center gap-1.5 font-medium text-blue-700"><div class="w-2 h-2 rounded-full bg-blue-500"></div> Asuntos P.</div>
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

  </div>
</template>
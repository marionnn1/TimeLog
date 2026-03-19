<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { 
    Calendar as CalendarIcon, ChevronLeft, ChevronRight, 
    AlertTriangle, UserPlus, X, Check, Palmtree, MapPin, Briefcase,
    AlertCircle, CheckCircle2, Trash2, Users
} from 'lucide-vue-next'

const store = useDataStore()
const currentUser = store.getCurrentUser() 

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

const confirmState = ref({ show: false, title: '', message: '', type: 'neutral', action: null })
const solicitarConfirmacion = (title, message, type, callback) => {
    confirmState.value = { show: true, title, message, type, action: callback }
}
const ejecutarConfirmacion = () => {
    if (confirmState.value.action) confirmState.value.action()
    confirmState.value.show = false
}

const currentDate = ref(new Date())
const year = computed(() => currentDate.value.getFullYear())
const month = computed(() => currentDate.value.getMonth())
const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

const ausenciasDelMes = ref([])
const resumenAnual = ref([])

const cargarAusencias = async () => {
    if (!currentUser) return
    try {
        const mesApi = month.value + 1
        const res = await fetch(`http://localhost:5000/api/absences?mes=${mesApi}&anio=${year.value}`)
        const json = await res.json()
        if (json.status === 'success') {
            ausenciasDelMes.value = json.data
        }
    } catch (e) {
        console.error("Error al cargar ausencias:", e)
    }
}

const cargarResumenAnual = async () => {
    if (!currentUser) return
    try {
        const promesas = []
        for(let m = 1; m <= 12; m++) {
            promesas.push(fetch(`http://localhost:5000/api/absences?mes=${m}&anio=${year.value}`).then(r => r.json()))
        }
        const resultados = await Promise.all(promesas)
        
        let todasLasAusencias = []
        resultados.forEach(res => {
            if(res.status === 'success') todasLasAusencias = todasLasAusencias.concat(res.data)
        })

        const grupos = {}
        todasLasAusencias.forEach(a => {
            if (!grupos[a.userId]) {
                grupos[a.userId] = { nombre: a.nombre, iniciales: a.iniciales, dias: [] }
            }
            if (!grupos[a.userId].dias.find(d => d.fecha === a.fecha)) {
                grupos[a.userId].dias.push(a)
            }
        })

        Object.values(grupos).forEach(g => {
            g.dias.sort((a,b) => new Date(a.fecha) - new Date(b.fecha))
        })

        resumenAnual.value = Object.values(grupos).sort((a,b) => a.nombre.localeCompare(b.nombre))
    } catch(e) {
        console.error("Error cargando resumen anual:", e)
    }
}

watch([month, year], cargarAusencias)
watch(year, cargarResumenAnual)

onMounted(() => {
    cargarAusencias()
    cargarResumenAnual()
})

const getAusenciasDia = (isoDate) => ausenciasDelMes.value.filter(a => a.fecha === isoDate)
const getMiAusencia = (isoDate) => getAusenciasDia(isoDate).find(a => a.userId === currentUser.id)

const mostrarModal = ref(false)
const form = ref({
    fechaInicio: '',
    fechaFin: '',
    tipo: 'vacaciones',
    comentario: ''
})

const getMiEstiloTipo = (tipo) => {
    const t = (tipo || '').toLowerCase()
    if (t.includes('vacaciones')) return 'bg-emerald-500 text-white border-emerald-600 shadow-md ring-1 ring-emerald-300'
    if (t.includes('festivo')) return 'bg-orange-500 text-white border-orange-600 shadow-md ring-1 ring-orange-300' 
    if (t.includes('asuntos')) return 'bg-blue-500 text-white border-blue-600 shadow-md ring-1 ring-blue-300'
    return 'bg-gray-700 text-white border-gray-800'
}

const getCompaneroEstiloTipo = (tipo) => {
    const t = (tipo || '').toLowerCase()
    if (t.includes('vacaciones')) return 'bg-emerald-50 text-emerald-700 border-emerald-200'
    if (t.includes('festivo')) return 'bg-orange-50 text-orange-700 border-orange-200' 
    if (t.includes('asuntos')) return 'bg-blue-50 text-blue-700 border-blue-200'
    return 'bg-gray-50 text-gray-700 border-gray-200'
}

const getAvatarColor = (tipo) => {
    const t = (tipo || '').toLowerCase()
    if (t.includes('vacaciones')) return 'bg-emerald-500 text-white'
    if (t.includes('festivo')) return 'bg-orange-500 text-white' 
    if (t.includes('asuntos')) return 'bg-blue-500 text-white'
    return 'bg-gray-500 text-white'
}

const getIconoTipo = (tipo) => {
    const t = (tipo || '').toLowerCase()
    if (t.includes('vacaciones')) return Palmtree
    if (t.includes('festivo')) return MapPin
    return Briefcase
}

const formatShortDate = (isoString) => {
    const d = new Date(isoString)
    return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' }).replace('.', '')
}

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

const abrirModal = (day) => {
    if (day.isWeekend) return

    const existing = getMiAusencia(day.isoDate)
    if (existing) {
        solicitarConfirmacion(
            'Eliminar Ausencia',
            `¿Estás seguro de eliminar tu ${existing.tipo} del día ${day.dayNum}?`,
            'danger',
            async () => {
                try {
                    await fetch('http://localhost:5000/api/absences', {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ usuario_id: currentUser.id, fecha: day.isoDate })
                    })
                    showToast('Ausencia eliminada correctamente', 'success')
                    cargarAusencias()
                    cargarResumenAnual()
                } catch(e) {
                    showToast('Error al eliminar', 'error')
                }
            }
        )
        return
    }

    form.value = { fechaInicio: day.isoDate, fechaFin: day.isoDate, tipo: 'vacaciones', comentario: '' }
    mostrarModal.value = true
}

const procesarSolicitud = async (diasSolicitados) => {
    try {
        const res = await fetch('http://localhost:5000/api/absences', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                usuario_id: currentUser.id,
                fechas: diasSolicitados,
                tipo: form.value.tipo,
                comentario: form.value.comentario
            })
        })
        if (res.ok) {
            mostrarModal.value = false
            showToast('Solicitud registrada con éxito', 'success')
            cargarAusencias()
            cargarResumenAnual()
        } else {
            showToast('Error al guardar la solicitud', 'error')
        }
    } catch(e) {
        showToast('Fallo en la conexión al servidor', 'error')
    }
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
  <div class="h-full flex flex-col font-sans p-6 bg-slate-50 overflow-y-auto relative pb-20">
    
    <div class="flex justify-between items-center mb-6 shrink-0">
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

    <div class="flex items-center justify-between bg-white p-4 rounded-t-xl border border-slate-200 border-b-0 shadow-sm shrink-0">
        <button @click="prevMonth" class="btn-ghost hover:bg-slate-100"><ChevronLeft/></button>
        <h2 class="text-xl font-bold text-slate-800 capitalize">{{ monthNames[month] }} {{ year }}</h2>
        <button @click="nextMonth" class="btn-ghost hover:bg-slate-100"><ChevronRight/></button>
    </div>

    <div class="bg-white rounded-b-xl border border-slate-200 shadow-sm overflow-hidden select-none mb-8 shrink-0">
        
        <div class="grid grid-cols-7 bg-slate-50 border-b border-slate-200 text-center py-3">
            <div v-for="d in ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']" :key="d" 
                 class="text-xs font-bold text-slate-400 uppercase tracking-wider">
                {{ d }}
            </div>
        </div>

        <div class="grid grid-cols-7 auto-rows-fr">
            <div v-for="p in startPadding" :key="'pad-'+p" class="bg-slate-50/50 border-b border-r border-slate-100 min-h-[100px] xl:min-h-[120px]"></div>

            <div v-for="day in daysInMonth" :key="day.isoDate" 
                 @click="abrirModal(day)"
                 class="relative border-b border-r border-slate-100 min-h-[100px] xl:min-h-[120px] p-2 transition-all group hover:bg-slate-50 cursor-pointer"
                 :class="{ 'bg-slate-50/50': day.isWeekend, 'bg-white': !day.isWeekend }">
                
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

                <div class="flex flex-col gap-1 overflow-y-auto no-scrollbar max-h-[85px] pr-1 mt-1">
                    <div v-for="aus in getAusenciasDia(day.isoDate)" :key="aus.userId"
                         class="px-1.5 py-1 rounded text-[10px] font-bold flex items-center gap-1.5 truncate transition-all border"
                         :class="aus.userId === currentUser.id ? getMiEstiloTipo(aus.tipo) : getCompaneroEstiloTipo(aus.tipo)"
                         :title="`${aus.nombre} - ${aus.tipo} ${aus.comentario ? '('+aus.comentario+')' : ''}`">
                        
                        <template v-if="aus.userId === currentUser.id">
                            <div class="w-3.5 h-3.5 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                                <component :is="getIconoTipo(aus.tipo)" class="w-2.5 h-2.5 text-white" />
                            </div>
                            <span class="truncate flex-1 uppercase tracking-wider">Tú - {{ aus.tipo }}</span>
                        </template>

                        <template v-else>
                            <div class="w-3.5 h-3.5 rounded-full flex items-center justify-center shrink-0 text-[7px]"
                                 :class="getAvatarColor(aus.tipo)">
                                {{ aus.iniciales }}
                            </div>
                            <span class="truncate flex-1">{{ aus.nombre }}</span>
                        </template>
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

    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm mt-4 shrink-0">
        <h2 class="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
            <Users class="w-5 h-5 text-primary" />
            Resumen Anual de Ausencias ({{ year }})
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <div v-for="user in resumenAnual" :key="user.nombre" class="p-5 rounded-xl border border-slate-100 bg-slate-50/50 hover:shadow-sm transition-all">
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-10 h-10 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center shadow-inner">
                        {{ user.iniciales }}
                    </div>
                    <div>
                        <h3 class="font-bold text-slate-800">{{ user.nombre }}</h3>
                        <p class="text-xs text-slate-500">{{ user.dias.length }} días registrados</p>
                    </div>
                </div>

                <div class="flex flex-wrap gap-1.5">
                    <span v-for="dia in user.dias" :key="dia.fecha"
                          class="px-2 py-1 rounded text-[10px] font-bold border flex items-center gap-1 cursor-default"
                          :class="getCompaneroEstiloTipo(dia.tipo)"
                          :title="dia.comentario || dia.tipo">
                        {{ formatShortDate(dia.fecha) }}
                    </span>
                </div>
            </div>
        </div>

        <div v-if="resumenAnual.length === 0" class="text-center py-10">
            <p class="text-slate-400 font-medium">No hay ausencias registradas en todo el año.</p>
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
                        <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Desde</label>
                        <input type="date" v-model="form.fechaInicio" class="w-full bg-slate-50 border border-slate-200 text-slate-800 rounded-lg px-3 py-2 font-bold focus:ring-2 focus:ring-primary outline-none">
                    </div>
                    <div>
                        <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Hasta</label>
                        <input type="date" v-model="form.fechaFin" class="w-full bg-slate-50 border border-slate-200 text-slate-800 rounded-lg px-3 py-2 font-bold focus:ring-2 focus:ring-primary outline-none">
                    </div>
                </div>

                <div>
                    <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Tipo de Ausencia</label>
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
                            <span class="text-[10px] font-bold uppercase">Festivo</span>
                        </div>
                        <div @click="form.tipo = 'asuntos'" 
                             class="cursor-pointer border rounded-xl p-3 flex flex-col items-center gap-2 transition-all"
                             :class="form.tipo === 'asuntos' ? 'border-blue-500 bg-blue-50 text-blue-700 ring-1 ring-blue-500' : 'border-slate-200 hover:border-slate-300 text-slate-500'">
                            <Briefcase class="w-6 h-6" />
                            <span class="text-[10px] font-bold uppercase">Asuntos P.</span>
                        </div>
                    </div>
                </div>

                <div>
                    <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Comentario (Opcional)</label>
                    <input type="text" v-model="form.comentario" placeholder="Ej: Viaje a Londres..." maxlength="255"
                           class="w-full bg-white border border-slate-200 text-slate-800 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none">
                </div>

                <button @click="confirmarSolicitud" class="w-full btn-primary py-3 justify-center text-base bg-primary text-white font-bold rounded-lg hover:bg-emerald-600 transition flex items-center">
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
                    <button @click="confirmState.show = false" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-lg font-bold flex-1 hover:bg-slate-200 transition">Cancelar</button>
                    <button @click="ejecutarConfirmacion" 
                            class="px-4 py-2 text-white rounded-lg font-bold flex-1 transition shadow-sm"
                            :class="confirmState.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : 'bg-amber-600 hover:bg-amber-700'">
                        Confirmar
                    </button>
                </div>
            </div>
        </div>
    </div>

    <transition enter-active-class="transform ease-out duration-300 transition" enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2" enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="toast.show" class="absolute bottom-6 right-6 z-50 flex items-center w-full max-w-xs p-4 space-x-3 text-gray-500 bg-white rounded-lg shadow-lg border border-gray-100">
            <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg" :class="toast.type === 'success' ? 'text-emerald-500 bg-emerald-100' : 'text-red-500 bg-red-100'">
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
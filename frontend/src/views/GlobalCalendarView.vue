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

// --- NOTIFICATION SYSTEM (TOAST) ---
const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

// --- CONFIRMATION SYSTEM ---
const confirmState = ref({ show: false, title: '', message: '', type: 'neutral', action: null })
const requestConfirmation = (title, message, type, callback) => {
    confirmState.value = { show: true, title, message, type, action: callback }
}
const executeConfirmation = () => {
    if (confirmState.value.action) confirmState.value.action()
    confirmState.value.show = false
}

// --- DATE AND CALENDAR ---
const currentDate = ref(new Date())
const year = computed(() => currentDate.value.getFullYear())
const month = computed(() => currentDate.value.getMonth())
const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

// --- API DATA CONNECTION ---
const monthAbsences = ref([])
const annualSummary = ref([])

const fetchAbsences = async () => {
    if (!currentUser) return
    try {
        const mesApi = month.value + 1
        const res = await fetch(`http://localhost:5000/api/absences?mes=${mesApi}&anio=${year.value}`)
        const json = await res.json()
        if (res.ok) {
            monthAbsences.value = json.data || json
        }
    } catch (e) {
        console.error("Error loading absences:", e)
    }
}

const fetchAnnualSummary = async () => {
    if (!currentUser) return
    try {
        const promesas = []
        for(let m = 1; m <= 12; m++) {
            promesas.push(fetch(`http://localhost:5000/api/absences?mes=${m}&anio=${year.value}`).then(r => r.json()))
        }
        const resultados = await Promise.all(promesas)
        
        if (res.ok) {
            const data = json.data || json
            // Agrupamos por usuario para el listado inferior
            const groups = {}
            data.forEach(a => {
                if (!groups[a.userId]) {
                    groups[a.userId] = { name: a.name, initials: a.initials, days: [] }
                }
                groups[a.userId].days.push(a)
            })

            annualSummary.value = Object.values(groups).sort((a, b) => a.name.localeCompare(b.name))
        }
    } catch (e) {
        console.error("Error loading annual summary:", e)
    }
}

watch([month, year], fetchAbsences)
watch(year, fetchAnnualSummary)

onMounted(() => {
    fetchAbsences()
    fetchAnnualSummary()
})

const getDayAbsences = (isoDate) => monthAbsences.value.filter(a => a.date === isoDate)
const getMyAbsence = (isoDate) => getDayAbsences(isoDate).find(a => a.userId === currentUser.id)

// --- MODAL AND STYLES ---
const showModal = ref(false)
const absenceForm = ref({
    startDate: '',
    endDate: '',
    type: 'vacaciones',
    comment: ''
})

const getMyAbsenceStyle = (type) => {
    const t = (type || '').toLowerCase()
    if (t.includes('vacaciones')) return 'bg-emerald-500 text-white border-emerald-600 shadow-md ring-1 ring-emerald-300'
    if (t.includes('festivo')) return 'bg-orange-500 text-white border-orange-600 shadow-md ring-1 ring-orange-300' 
    if (t.includes('asuntos')) return 'bg-blue-500 text-white border-blue-600 shadow-md ring-1 ring-blue-300'
    return 'bg-gray-700 text-white border-gray-800'
}

const getColleagueAbsenceStyle = (type) => {
    const t = (type || '').toLowerCase()
    if (t.includes('vacaciones')) return 'bg-emerald-50 text-emerald-700 border-emerald-200'
    if (t.includes('festivo')) return 'bg-orange-50 text-orange-700 border-orange-200' 
    if (t.includes('asuntos')) return 'bg-blue-50 text-blue-700 border-blue-200'
    return 'bg-gray-50 text-gray-700 border-gray-200'
}

const getAvatarColor = (type) => {
    const t = (type || '').toLowerCase()
    if (t.includes('vacaciones')) return 'bg-emerald-500 text-white'
    if (t.includes('festivo')) return 'bg-orange-500 text-white' 
    if (t.includes('asuntos')) return 'bg-blue-500 text-white'
    return 'bg-gray-500 text-white'
}

const getTypeIcon = (type) => {
    const t = (type || '').toLowerCase()
    if (t.includes('vacaciones')) return Palmtree
    if (t.includes('festivo')) return MapPin
    return Briefcase
}

const formatShortDate = (isoString) => {
    const d = new Date(isoString)
    return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' }).replace('.', '')
}

// --- CALENDAR CALCULATIONS ---
const daysInMonth = computed(() => {
    const totalDays = new Date(year.value, month.value + 1, 0).getDate()
    return Array.from({ length: totalDays }, (_, i) => {
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

// --- ACTIONS ---
const openAbsenceModal = (day) => {
    if (day.isWeekend) return

    const existing = getMyAbsence(day.isoDate)
    if (existing) {
        requestConfirmation(
            'Eliminar Ausencia',
            `¿Estás seguro de eliminar tu ${existing.type} del día ${day.dayNum}?`,
            'danger',
            async () => {
                try {
                    await fetch('http://localhost:5000/api/absences', {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ userId: currentUser.id, date: day.isoDate })
                    })
                    showToast('Ausencia eliminada correctamente', 'success')
                    await fetchAbsences()
                    await fetchAnnualSummary()
                } catch(e) {
                    showToast('Error al eliminar', 'error')
                }
            }
        )
        return
    }

    absenceForm.value = { startDate: day.isoDate, endDate: day.isoDate, type: 'vacaciones', comment: '' }
    showModal.value = true
}

const handleRequest = async (requestedDays) => {
    try {
        const res = await fetch('http://localhost:5000/api/absences', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                userId: currentUser.id,
                dates: requestedDays,
                type: absenceForm.value.type,
                comment: absenceForm.value.comment
            })
        })
        if (res.ok) {
            showModal.value = false
            showToast('Solicitud registrada con éxito', 'success')
            await fetchAbsences()
            await fetchAnnualSummary()
        } else {
            showToast('Error al guardar la solicitud', 'error')
        }
    } catch(e) {
        showToast('Fallo en la conexión al servidor', 'error')
    }
}

const confirmRequest = () => {
    const start = new Date(absenceForm.value.startDate)
    const end = new Date(absenceForm.value.endDate)
    const requestedDays = []

    for(let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        if (d.getDay() !== 0 && d.getDay() !== 6) {
            const offset = d.getTimezoneOffset() * 60000
            const iso = new Date(d.getTime() - offset).toISOString().split('T')[0]
            requestedDays.push(iso)
        }
    }

    if (requestedDays.length === 0) {
        showToast("Selecciona al menos un día laborable.", "error")
        return
    }

    let alertManager = false
    requestedDays.forEach(date => {
        const total = getDayAbsences(date).length
        if (total >= 3) alertManager = true
    })

    if (alertManager) {
        requestConfirmation(
            'Alta Demanda Detectada',
            'Algunos días seleccionados ya tienen a 3 o más compañeros fuera. Se notificará al responsable. ¿Continuar?',
            'warning',
            () => handleRequest(requestedDays)
        )
        return
    }

    handleRequest(requestedDays)
}
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
        <button @click="currentDate = new Date(year, month - 1, 1)" class="btn-ghost hover:bg-slate-100"><ChevronLeft/></button>
        <h2 class="text-xl font-bold text-slate-800 capitalize">{{ monthNames[month] }} {{ year }}</h2>
        <button @click="currentDate = new Date(year, month + 1, 1)" class="btn-ghost hover:bg-slate-100"><ChevronRight/></button>
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
                 @click="openAbsenceModal(day)"
                 class="relative border-b border-r border-slate-100 min-h-[100px] xl:min-h-[120px] p-2 transition-all group hover:bg-slate-50 cursor-pointer"
                 :class="{ 'bg-slate-50/50': day.isWeekend, 'bg-white': !day.isWeekend }">
                
                <div class="flex justify-between items-start mb-1">
                    <span class="text-sm font-bold" 
                          :class="day.isoDate === new Date().toISOString().split('T')[0] ? 'bg-slate-900 text-white w-6 h-6 rounded-full flex items-center justify-center' : 'text-slate-700'">
                        {{ day.dayNum }}
                    </span>
                    <div v-if="!day.isWeekend && getDayAbsences(day.isoDate).length >= 3" 
                         class="text-rose-500 animate-pulse" title="Alta concurrencia">
                        <AlertTriangle class="w-4 h-4" />
                    </div>
                </div>

                <div class="flex flex-col gap-1 overflow-y-auto no-scrollbar max-h-[85px] pr-1 mt-1">
                    <div v-for="aus in getDayAbsences(day.isoDate)" :key="aus.userId"
                         class="px-1.5 py-1 rounded text-[10px] font-bold flex items-center gap-1.5 truncate transition-all border"
                         :class="aus.userId === currentUser.id ? getMyAbsenceStyle(aus.type) : getColleagueAbsenceStyle(aus.type)">
                        
                        <template v-if="aus.userId === currentUser.id">
                            <div class="w-3.5 h-3.5 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                                <component :is="getTypeIcon(aus.type)" class="w-2.5 h-2.5 text-white" />
                            </div>
                            <span class="truncate flex-1 uppercase tracking-wider">Tú</span>
                        </template>
                        <template v-else>
                            <div class="w-3.5 h-3.5 rounded-full flex items-center justify-center shrink-0 text-[7px]"
                                 :class="getAvatarColor(aus.type)">
                                {{ aus.initials }}
                            </div>
                            <span class="truncate flex-1">{{ aus.name }}</span>
                        </template>
                    </div>
                </div>

                <div v-if="!day.isWeekend && !getMyAbsence(day.isoDate)" 
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
            Resumen Anual ({{ year }})
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <div v-for="user in annualSummary" :key="user.name" class="p-5 rounded-xl border border-slate-100 bg-slate-50/50">
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-10 h-10 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center shadow-inner">
                        {{ user.initials }}
                    </div>
                    <div>
                        <h3 class="font-bold text-slate-800">{{ user.name }}</h3>
                        <p class="text-xs text-slate-500">{{ user.days.length }} días registrados</p>
                    </div>
                </div>
                <div class="flex flex-wrap gap-1.5">
                    <span v-for="day in user.days" :key="day.date"
                          class="px-2 py-1 rounded text-[10px] font-bold border flex items-center gap-1"
                          :class="getColleagueAbsenceStyle(day.type)"
                          :title="day.comment || day.type">
                        {{ formatShortDate(day.date) }}
                    </span>
                </div>
            </div>
        </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl p-6 animate-in zoom-in-95">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-bold text-slate-800">Solicitar Días</h3>
                <button @click="showModal=false" class="text-slate-400 hover:text-slate-600"><X class="w-6 h-6"/></button>
            </div>
            <div class="space-y-6">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-[11px] font-bold text-slate-400 uppercase mb-2">Desde</label>
                        <input type="date" v-model="absenceForm.startDate" class="input-std w-full font-bold">
                    </div>
                    <div>
                        <label class="block text-[11px] font-bold text-slate-400 uppercase mb-2">Hasta</label>
                        <input type="date" v-model="absenceForm.endDate" class="input-std w-full font-bold">
                    </div>
                </div>
                <div>
                    <label class="block text-[11px] font-bold text-slate-400 uppercase mb-2">Tipo</label>
                    <div class="grid grid-cols-3 gap-2">
                        <div v-for="t in ['vacaciones', 'festivo', 'asuntos']" :key="t" 
                             @click="absenceForm.type = t"
                             class="cursor-pointer border rounded-xl p-3 flex flex-col items-center gap-2 transition-all capitalize"
                             :class="absenceForm.type === t ? 'border-primary bg-blue-50 text-primary ring-1 ring-primary' : 'border-slate-200 text-slate-500'">
                            <component :is="getTypeIcon(t)" class="w-6 h-6" />
                            <span class="text-[10px] font-bold">{{ t }}</span>
                        </div>
                    </div>
                </div>
                <div>
                    <label class="block text-[11px] font-bold text-slate-400 uppercase mb-2">Comentario (Opcional)</label>
                    <input type="text" v-model="absenceForm.comment" placeholder="..." class="input-std w-full">
                </div>
                <button @click="confirmRequest" class="w-full btn-primary py-3 justify-center text-base">
                    <Check class="w-5 h-5 mr-2"/> Confirmar Solicitud
                </button>
            </div>
        </div>
    </div>

    <transition enter-active-class="transform transition" enter-from-class="translate-y-2 opacity-0" enter-to-class="translate-y-0 opacity-100" leave-active-class="transition" leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="toast.show" class="fixed bottom-6 right-6 z-[200] flex items-center p-4 bg-white rounded-2xl shadow-2xl border border-slate-100 min-w-[300px]">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center mr-4" :class="toast.type === 'success' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'">
                <component :is="toast.type === 'success' ? CheckCircle2 : AlertCircle" class="w-6 h-6"/>
            </div>
            <div class="text-sm font-bold text-slate-800">{{ toast.message }}</div>
        </div>
    </transition>

    <div v-if="confirmState.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
        <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 text-center animate-in zoom-in-95">
            <component :is="confirmState.type === 'danger' ? Trash2 : AlertTriangle" class="w-12 h-12 mx-auto mb-4" :class="confirmState.type === 'danger' ? 'text-red-500' : 'text-amber-500'"/>
            <h3 class="text-lg font-bold text-slate-900">{{ confirmState.title }}</h3>
            <p class="text-sm text-slate-500 mt-2">{{ confirmState.message }}</p>
            <div class="flex gap-3 mt-6">
                <button @click="confirmState.show = false" class="btn-secondary flex-1">Cancelar</button>
                <button @click="executeConfirmation" class="btn-primary flex-1 justify-center" :class="confirmState.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : ''">Confirmar</button>
            </div>
        </div>
    </div>

  </div>
</template>
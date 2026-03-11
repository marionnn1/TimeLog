<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '../stores/dataStore'
import { 
  ChevronLeft, ChevronRight, Calendar as CalendarIcon, FileText,
  Hash, Briefcase, CheckCircle2, AlertCircle, X,
  MessageSquare, Send, Clock, ArrowRight
} from 'lucide-vue-next'

const router = useRouter()
const store = useDataStore()

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

const getDayAbsenceInfo = (date) => {
  const currentUser = store.getCurrentUser()
  if (!currentUser) return null

  const offset = date.getTimezoneOffset() * 60000
  const isoDate = new Date(date.getTime() - offset).toISOString().split('T')[0]

  const absence = store.state.ausencias?.find(a => a.date === isoDate && a.userId === currentUser.id)
  if (!absence) return null
  
  const mapLabels = {
      'vacaciones': 'Vacaciones',
      'festivo': 'Festivo',
      'asuntos': 'Asuntos P.'
  }
  return { type: absence.type, label: mapLabels[absence.type] || 'Ausencia' }
}

const currentDate = ref(new Date()) 
const today = new Date() 

const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const weekDays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonthIndex = computed(() => currentDate.value.getMonth())
const currentMonthName = computed(() => monthNames[currentMonthIndex.value])

const blankDays = computed(() => {
  const firstDay = new Date(currentYear.value, currentMonthIndex.value, 1).getDay()
  return firstDay === 0 ? 6 : firstDay - 1
})
const daysInMonthCount = computed(() => {
  return new Date(currentYear.value, currentMonthIndex.value + 1, 0).getDate()
})

const isWeekend = (day) => {
  const date = new Date(currentYear.value, currentMonthIndex.value, day)
  return date.getDay() === 0 || date.getDay() === 6 
}
const isToday = (day) => day === today.getDate() && currentMonthIndex.value === hoy.getMonth() && currentYear.value === hoy.getFullYear()

const monthlyEntries = ref([])

const projectColorPalette = [
    'bg-blue-50 text-blue-700 border-blue-100 hover:bg-blue-100',
    'bg-cyan-50 text-cyan-800 border-cyan-100 hover:bg-cyan-100',
    'bg-emerald-50 text-emerald-800 border-emerald-100 hover:bg-emerald-100',
    'bg-fuchsia-50 text-fuchsia-800 border-fuchsia-100 hover:bg-fuchsia-100',
    'bg-amber-50 text-amber-800 border-amber-100 hover:bg-amber-100',
    'bg-indigo-50 text-indigo-700 border-indigo-100 hover:bg-indigo-100'
]

const fetchCalendarData = async () => {
    const user = store.getCurrentUser()
    if (!user) return
    
    try {
        const monthParam = currentMonthIndex.value + 1
        const res = await fetch(`http://localhost:5000/api/myprojects/calendar?user_id=${user.id}&month=${monthParam}&year=${currentYear.value}`)
        const json = await res.json()
        
        if (res.ok) {
            const data = json.data || json
            monthlyEntries.value = data.map(imp => {
                const color = projectColorPalette[imp.projectId % projectColorPalette.length]
                return {
                    day: imp.day,
                    clientName: imp.client,
                    projectCode: `PRJ-${String(imp.projectId).padStart(3, '0')}`,
                    projectName: imp.project,
                    projectId: imp.projectId,
                    hours: imp.hours,
                    colorClass: color
                }
            })
        }
    } catch (e) {
        console.error("Error loading calendar:", e)
        showToast("Error al cargar los datos del calendario", "error")
    }
}

watch([currentMonthIndex, currentYear], fetchCalendarData)
onMounted(fetchCalendarData)

const getEntriesByDay = (day) => monthlyEntries.value.filter(imp => imp.day === day)
const getDayTotalHours = (day) => getEntriesByDay(day).reduce((acc, curr) => acc + curr.hours, 0)

const projectSummary = computed(() => {
  const groups = {}
  monthlyEntries.value.forEach(imp => {
    const key = imp.projectId
    if (!groups[key]) {
      groups[key] = {
        client: imp.clientName,
        code: imp.projectCode,
        project: imp.projectName,
        hours: 0
      }
    }
    groups[key].hours += imp.hours
  })
  return Object.values(groups).sort((a, b) => b.hours - a.hours)
})

const totalMonthHours = computed(() => {
  return monthlyEntries.value.reduce((acc, curr) => acc + curr.hours, 0)
})

const showRequestModal = ref(false)
const correctionForm = ref({
    displayDate: '',
    isoDate: '',
    projectName: '',
    projectId: null,
    message: '',
    currentHours: 0,
    newHours: 0
})

const openCorrectionRequest = (entry, day) => {
    const dateObj = new Date(currentYear.value, currentMonthIndex.value, day)
    const displayStr = dateObj.toLocaleDateString('es-ES', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    })
    
    const offset = dateObj.getTimezoneOffset() * 60000
    const isoDate = new Date(dateObj.getTime() - offset).toISOString().split('T')[0]
    
    correctionForm.value = {
        displayDate: displayStr,
        isoDate: isoDate,
        projectName: entry.projectName,
        projectId: entry.projectId,
        message: '',
        currentHours: entry.hours,
        newHours: entry.hours
    }
    showRequestModal.value = true
}

const sendCorrectionRequest = async () => {
    if (!correctionForm.value.message) {
        return showToast('Debes escribir un motivo para la solicitud', 'error')
    }

    const user = store.getCurrentUser()
    if (!user) return;

    try {
        const response = await fetch('http://localhost:5000/api/myprojects/request-correction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                userId: user.id,
                projectId: correctionForm.value.projectId,
                date: correctionForm.value.isoDate,
                newHours: correctionForm.value.newHours,
                reason: correctionForm.value.message
            })
        })

        if (response.ok) {
            showRequestModal.value = false
            showToast('Solicitud enviada al responsable', 'success')
            fetchCalendarData()
        } else {
            showToast('Error al enviar la solicitud', 'error')
        }
    } catch (error) {
        showToast('Error de conexión', 'error')
    }
}
</script>

<template>
  <div class="h-full flex flex-col font-sans bg-gray-50 p-6 overflow-y-auto relative">
    
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-4">
        <h1 class="text-3xl font-bold capitalize flex items-center gap-3 text-dark">
          <div class="p-2 rounded-lg bg-white shadow-sm border border-gray-100">
            <CalendarIcon class="w-6 h-6 text-primary"/>
          </div>
          {{ currentMonthName }} <span class="font-light opacity-50">{{ currentYear }}</span>
        </h1>
        
        <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200 ml-6">
          <button @click="currentDate = new Date(currentYear, currentMonthIndex - 1, 1)" class="p-2 hover:bg-gray-50 text-gray-600 rounded-l-lg border-r border-gray-200 transition">
              <ChevronLeft class="w-5 h-5" />
          </button>
          <button @click="currentDate = new Date()" class="px-4 py-2 text-xs font-bold tracking-widest hover:bg-gray-50 transition uppercase text-dark">
              Hoy
          </button>
          <button @click="currentDate = new Date(currentYear, currentMonthIndex + 1, 1)" class="p-2 hover:bg-gray-50 text-gray-600 rounded-r-lg border-l border-gray-200 transition">
              <ChevronRight class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <div class="card p-0 overflow-hidden mb-8 flex-none shadow-xl">
      <div class="grid grid-cols-7 border-b border-gray-200">
        <div v-for="dayName in weekDays" :key="dayName" class="py-4 text-center text-xs font-bold uppercase tracking-widest"
             :class="dayName === 'Sáb' || dayName === 'Dom' ? 'bg-dark text-white/90' : 'bg-white text-dark'">
          {{ dayName }}
        </div>
      </div>

      <div class="grid grid-cols-7 auto-rows-fr">
        <div v-for="blank in blankDays" :key="`blank-${blank}`" class="bg-gray-50/50 border-b border-r border-gray-100"></div>
        <div v-for="day in daysInMonthCount" :key="day" 
             class="min-h-[120px] p-2 border-b border-r border-gray-100 transition relative flex flex-col gap-1"
             :class="[isWeekend(day) ? 'bg-slate-100' : 'bg-white']">
          
          <div class="flex justify-between items-start mb-2">
            <span class="text-sm font-bold w-7 h-7 flex items-center justify-center rounded-full"
                  :class="day === today.getDate() && currentMonthIndex === today.getMonth() ? 'bg-primary text-white' : (isWeekend(day) ? 'text-slate-400' : 'text-dark')">
              {{ day }}
            </span>
            <span v-if="getDayTotalHours(day) > 0" class="text-[10px] font-bold px-2 py-0.5 rounded border bg-blue-50 text-dark border-blue-100">
              {{ getDayTotalHours(day) }}h
            </span>
          </div>

          <div v-if="!isWeekend(day)">
             <div v-for="(entry, idx) in getEntriesByDay(day)" :key="idx" 
                  @click.stop="openCorrectionRequest(entry, day)"
                  class="text-[10px] p-1.5 rounded border-l-2 mb-1 truncate shadow-sm cursor-pointer transition transform hover:scale-105 flex justify-between items-center"
                  :class="entry.colorClass">
               <span class="truncate font-semibold">{{ entry.projectName }}</span>
               <span class="font-bold opacity-80 ml-1">{{ entry.hours }}h</span>
             </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card p-0 overflow-hidden shadow-lg">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50/50 flex justify-between items-center">
            <h2 class="font-bold text-lg text-dark flex items-center gap-2">
                <FileText class="w-5 h-5 text-primary" />
                Resumen Mensual
            </h2>
            <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-gray-500 uppercase tracking-wide">Total:</span>
                <span class="text-lg font-bold text-dark bg-blue-50 px-3 py-1 rounded-lg border border-blue-100">
                    {{ totalMonthHours }}h
                </span>
            </div>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-white text-xs uppercase tracking-wider border-b-2 border-gray-100 text-dark">
                        <th class="px-6 py-3 font-bold">Cliente</th>
                        <th class="px-6 py-3 font-bold">Proyecto</th>
                        <th class="px-6 py-3 font-bold text-center">Horas</th>
                    </tr>
                </thead>
                <tbody class="text-sm text-gray-700 divide-y divide-gray-50">
                    <tr v-for="(item, index) in projectSummary" :key="index" class="hover:bg-blue-50/10 transition">
                        <td class="px-6 py-3 font-medium">{{ item.client }}</td>
                        <td class="px-6 py-3">
                           <div class="flex flex-col">
                             <span class="font-bold">{{ item.project }}</span>
                             <span class="text-[10px] text-gray-400 font-mono">{{ item.code }}</span>
                           </div>
                        </td>
                        <td class="px-6 py-3 text-center">
                            <span class="font-bold text-dark bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
                                {{ item.hours }}h
                            </span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div v-if="showRequestModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-white w-full max-w-md rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
            <div class="flex justify-between items-center mb-6 border-b border-gray-100 pb-3">
                <h3 class="text-lg font-bold text-dark flex items-center gap-2">
                    <MessageSquare class="w-5 h-5 text-primary"/> Solicitar Corrección
                </h3>
                <button @click="showRequestModal = false" class="text-gray-400 hover:text-red-500 transition">
                    <X class="w-5 h-5"/>
                </button>
            </div>

            <div class="space-y-5">
                <div class="p-3 bg-gray-50 rounded-lg border border-gray-200 text-sm">
                    <p class="text-gray-500 font-bold mb-1 flex items-center gap-2"><CalendarIcon class="w-4 h-4"/> {{ correctionForm.displayDate }}</p>
                    <p class="text-primary font-bold flex items-center gap-2"><Briefcase class="w-4 h-4"/> {{ correctionForm.projectName }}</p>
                </div>

                <div class="flex items-center justify-between gap-4">
                    <div class="flex-1 text-center">
                        <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Horas Actuales</label>
                        <div class="h-12 flex items-center justify-center bg-gray-100 rounded-xl border border-gray-200 text-gray-500 font-bold">
                            {{ correctionForm.currentHours }}h
                        </div>
                    </div>
                    <ArrowRight class="w-5 h-5 mt-4 text-gray-300"/>
                    <div class="flex-1 text-center">
                        <label class="block text-[10px] font-black uppercase mb-1 text-primary">Nuevas Horas</label>
                        <input v-model.number="correctionForm.newHours" type="number" step="0.5"
                            class="w-full h-12 text-center rounded-xl border-2 border-primary bg-blue-50 text-primary font-bold outline-none" />
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-gray-600 uppercase mb-1">Motivo del cambio</label>
                    <textarea v-model="correctionForm.message" rows="3" 
                        class="w-full border border-gray-200 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none"
                        placeholder="Explica por qué necesitas corregir estas horas..."></textarea>
                </div>

                <div class="flex gap-3 pt-2">
                    <button @click="showRequestModal = false" class="btn-secondary flex-1">Cancelar</button>
                    <button @click="sendCorrectionRequest" class="btn-primary flex-1">
                        <Send class="w-4 h-4 mr-2"/> Enviar Solicitud
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
        </div>
    </transition>

  </div>
</template>

<style scoped>
input[type=number]::-webkit-outer-spin-button,
input[type=number]::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
</style>
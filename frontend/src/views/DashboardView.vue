<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '../stores/dataStore' 
import {
    ChevronLeft, ChevronRight, Plus, Trash2, Save, Building2, Info, X, RotateCcw, 
    Clock, ChevronDown, Check, AlertCircle, CheckCircle2, Loader2
} from 'lucide-vue-next'

const route = useRoute()
const store = useDataStore() 

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null
const isLoading = ref(false)

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

const dailyHours = ref(8.5) 
const showWorkdaySelector = ref(false)

const workdayOptions = computed(() => {
    const opts = []
    for (let h = 8.5; h >= 4; h -= 0.5) {
        opts.push({ 
            value: h, 
            label: `${h}h / día`,
            desc: h === 8.5 ? 'Estándar (Viernes 6.5h)' : 'Jornada lineal L-V' 
        })
    }
    return opts
})

const selectHours = (value) => {
    dailyHours.value = value
    showWorkdaySelector.value = false
}

const selectorRef = ref(null)
const handleClickOutside = (event) => {
    if (selectorRef.value && !selectorRef.value.contains(event.target)) {
        showWorkdaySelector.value = false
    }
}

const getDayInfo = (date) => {
    const offset = date.getTimezoneOffset() * 60000
    const isoDate = new Date(date.getTime() - offset).toISOString().split('T')[0]
    const user = store.getCurrentUser()
    if (!user) return null
    
    // Accedemos a las ausencias del store (que se cargan en el calendario global)
    const absence = store.state.ausencias?.find(a => a.date === isoDate && a.userId === user.id)
    if (!absence) return null
    
    const normalizedType = (absence.type === 'asuntos' || absence.type === 'asuntos_propios') ? 'asuntos' : absence.type

    return {
        type: normalizedType,
        label: normalizedType === 'asuntos' ? 'Asuntos P.' : (absence.type.charAt(0).toUpperCase() + absence.type.slice(1))
    }
}

const getDayType = (date) => getDayInfo(date)?.type
const getDayLabel = (date) => getDayInfo(date)?.label

const showModal = ref(false)
const newEntry = ref({ projectId: undefined })
const currentDate = ref(new Date())
const selectedDay = ref(new Date().getDate())
const masterProjects = ref([])
const rows = ref([])

// --- LOGICA DE VALIDACION DE DECIMALES ---
const isInvalidStep = (value) => {
    if (!value || value === 0) return false
    return !Number.isInteger(value * 2)
}

// --- CARGA DE PROYECTOS MAESTROS ---
const fetchMasterProjects = async () => {
    try {
        // Usamos la ruta estandarizada de administración de proyectos
        const res = await fetch('http://localhost:5000/api/admin/projects')
        const json = await res.json()
        if (res.ok) {
            const data = json.data || json
            masterProjects.value = data.filter(p => p.status === 'Activo' || p.estado === 'Activo')
        }
    } catch (e) {
        console.error("Error fetching master projects", e)
    }
}

// --- LÓGICA DE API (SINCRONIZACIÓN) ---
const fetchWeeklyEntries = async () => {
    const user = store.getCurrentUser()
    if (!user) return
    const mondayStr = currentMonday.value.toISOString().split('T')[0]
    try {
        isLoading.value = true
        // Parámetros estandarizados: user_id y monday_date
        const res = await fetch(`http://localhost:5000/api/myprojects/week?user_id=${user.id}&monday_date=${mondayStr}`)
        const json = await res.json()
        
        if (res.ok) {
            const backendData = json.data || json || []
            const newRows = []
            const uniqueIds = [...new Set(backendData.map(d => d.projectId))]
            
            uniqueIds.forEach(pId => {
                const projectGroup = backendData.filter(d => d.projectId === pId)
                newRows.push({
                    id: pId,
                    client: projectGroup[0].clientName,
                    project: projectGroup[0].projectName,
                    hours: Array(7).fill(0).map((_, i) => {
                        const targetDate = new Date(currentMonday.value)
                        targetDate.setDate(currentMonday.value.getDate() + i)
                        const isoStr = targetDate.toISOString().split('T')[0]
                        const entry = projectGroup.find(r => r.date === isoStr)
                        return entry ? entry.hours : 0
                    }),
                    selected: false
                })
            })
            rows.value = newRows
        }
    } catch (error) {
        showToast("Error al conectar con el servidor", "error")
    } finally {
        isLoading.value = false
    }
}

const saveChanges = async () => {
    if (hasErrors.value) return showToast('Por favor corrige los errores antes de guardar.', 'error')
    const user = store.getCurrentUser()
    const weekDates = weekDays.value.map(d => d.toISOString().split('T')[0])
    
    const payload = {
        userId: user.id,
        weekDates: weekDates,
        rows: rows.value.map(r => ({ projectId: r.id, hours: r.hours }))
    }
    
    try {
        const res = await fetch('http://localhost:5000/api/myprojects/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        if (res.ok) {
            showToast('Imputaciones guardadas correctamente', 'success')
            await fetchWeeklyEntries()
        } else {
            showToast('Error al guardar: Revisa el servidor', 'error')
        }
    } catch (error) {
        showToast('Error de red', 'error')
    }
}

// --- NAVEGACIÓN ---
const getMonday = (date) => {
    const d = new Date(date)
    const day = d.getDay()
    const diff = d.getDate() - day + (day === 0 ? -6 : 1)
    return new Date(d.setDate(diff))
}
const currentMonday = computed(() => getMonday(currentDate.value))
const weekDays = computed(() => {
    const days = []
    for (let i = 0; i < 7; i++) {
        const d = new Date(currentMonday.value)
        d.setDate(currentMonday.value.getDate() + i)
        days.push(new Date(d))
    }
    return days
})

watch(currentMonday, fetchWeeklyEntries)

const isSummerSchedule = (date) => { const month = date.getMonth(); return month === 6 || month === 7 }
const getMaxDayHours = (date) => {
    if (getDayType(date)) return 0 
    if (date.getDay() === 0 || date.getDay() === 6) return 0 
    if (dailyHours.value === 8.5) {
        if (isSummerSchedule(date)) return 7.0
        if (date.getDay() === 5) return 6.5
        return 8.5
    }
    return dailyHours.value
}
const getMaxWeekHours = () => {
    return weekDays.value.reduce((total, date) => total + getMaxDayHours(date), 0)
}

const dayNames = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']
const formatHeaderDate = (date) => date.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
const isWeekendDay = (date) => { const d = date.getDay(); return d === 0 || d === 6 }
const isTodayDate = (date) => {
    const t = new Date()
    return date.getDate() === t.getDate() && date.getMonth() === t.getMonth() && date.getFullYear() === t.getFullYear()
}
const isEditableDate = (date) => {
    const t = new Date(); t.setHours(0,0,0,0)
    const d = new Date(date); d.setHours(0,0,0,0)
    return !isWeekendDay(date) && d >= t && !getDayType(date)
}

const selectDay = (date) => { selectedDay.value = date.getDate() }
const goToToday = () => { currentDate.value = new Date(); selectedDay.value = new Date().getDate() }

const rowTotal = (row) => row.hours.reduce((acc, h) => acc + (parseFloat(h) || 0), 0)
const dayTotal = (index) => rows.value.reduce((acc, r) => acc + (parseFloat(r.hours[index]) || 0), 0)
const weekTotal = computed(() => rows.value.reduce((acc, r) => acc + rowTotal(r), 0))

const dailyLimitExceeded = (index) => {
    const max = getMaxDayHours(weekDays.value[index])
    return max > 0 && dayTotal(index) > max
}
const weeklyLimitExceeded = computed(() => weekTotal.value > getMaxWeekHours())

const hasErrors = computed(() => {
    const overTime = weeklyLimitExceeded.value || Array.from({length:7}).some((_,i) => dailyLimitExceeded(i));
    const badDecimals = rows.value.some(r => r.hours.some(h => isInvalidStep(h)));
    return overTime || badDecimals;
})

const openAddModal = () => { newEntry.value = { projectId: undefined }; showModal.value = true }
const closeAddModal = () => { showModal.value = false }

const confirmAddLine = () => {
    const p = masterProjects.value.find(x => (x.id || x.Id) === newEntry.value.projectId)
    if (!p) return showToast('Selecciona un proyecto válido', 'error')
    if (rows.value.find(r => r.id === (p.id || p.Id))) return showToast('El proyecto ya está en la lista', 'error')
    
    rows.value.push({ 
        id: p.id || p.Id, 
        client: p.client || p.ClienteNombre || 'Cliente', 
        project: p.name || p.Nombre, 
        hours: [0, 0, 0, 0, 0, 0, 0], 
        selected: false 
    })
    closeAddModal()
}

const deleteLines = () => {
    rows.value = rows.value.filter(r => !r.selected)
    showToast('Líneas eliminadas de la vista', 'success')
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
    fetchWeeklyEntries()
    fetchMasterProjects()
})
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-4 gap-6 relative">
        <div class="flex flex-col gap-3">
            <div class="flex justify-between items-end">
                <div class="flex items-center gap-3">
                    <h1 class="h1-title capitalize">{{ formatHeaderDate(currentMonday) }}</h1>
                    <span class="text-sm font-medium text-gray-400 px-2 border-l border-gray-300">
                        Semana {{ currentMonday.getDate() }} - {{ weekDays[6].getDate() }}
                    </span>
                </div>
                <div class="flex gap-4 items-center">
                    <div class="relative" ref="selectorRef">
                        <button @click="showWorkdaySelector = !showWorkdaySelector" 
                                class="flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-4 py-2.5 shadow-sm hover:shadow-md transition-all group min-w-[180px] justify-between">
                            <div class="flex items-center gap-3">
                                <Clock class="w-4 h-4 text-blue-600" />
                                <div class="flex flex-col items-start text-left leading-none">
                                    <span class="text-[10px] text-gray-400 font-bold uppercase mb-0.5">Jornada</span>
                                    <span class="text-sm font-bold text-gray-700">{{ dailyHours }}h / día</span>
                                </div>
                            </div>
                            <ChevronDown class="w-4 h-4 text-gray-400" :class="showWorkdaySelector ? 'rotate-180' : ''"/>
                        </button>
                        <div v-if="showWorkdaySelector" class="absolute top-full right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border z-50 overflow-hidden">
                            <div v-for="option in workdayOptions" :key="option.value" @click="selectHours(option.value)"
                                 class="px-4 py-3 hover:bg-slate-50 cursor-pointer flex items-center gap-3 border-b last:border-0 transition-colors">
                                <div class="w-4 h-4 rounded-full border flex items-center justify-center" :class="dailyHours === option.value ? 'bg-blue-600 border-blue-600' : 'border-gray-300'">
                                    <Check v-if="dailyHours === option.value" class="w-2.5 h-2.5 text-white" stroke-width="3" />
                                </div>
                                <div class="flex flex-col">
                                    <span class="text-sm font-bold text-gray-700">{{ option.label }}</span>
                                    <span class="text-xs text-gray-400">{{ option.desc }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="h-8 w-px bg-gray-200 mx-2"></div>
                    <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                        <button @click="currentDate.setDate(currentDate.getDate() - 7)" class="p-2 hover:bg-gray-50 text-gray-600 border-r"><ChevronLeft class="w-5 h-5" /></button>
                        <button @click="goToToday" class="px-4 py-2 text-sm font-bold uppercase tracking-wide hover:bg-gray-50 flex items-center gap-2 min-w-[100px] justify-center text-dark">
                             {{ selectedDay === new Date().getDate() ? 'HOY' : 'Día ' + selectedDay }}
                        </button>
                        <button @click="currentDate.setDate(currentDate.getDate() + 7)" class="p-2 hover:bg-gray-50 text-gray-600 border-l"><ChevronRight class="w-5 h-5" /></button>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-7 gap-3 h-32 relative">
                <div v-if="isLoading" class="absolute inset-0 z-20 flex items-center justify-center bg-gray-50/50 backdrop-blur-[1px] rounded-xl">
                    <Loader2 class="w-8 h-8 text-primary animate-spin" />
                </div>
                <div v-for="(date, index) in weekDays" :key="index" @click="selectDay(date)"
                    class="relative rounded-xl border shadow-sm flex flex-col items-center justify-between p-3 transition-all cursor-pointer group"
                    :class="[
                        date.getDate() === selectedDay ? 'ring-2 ring-offset-2 ring-primary border-primary' : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-md',
                        isTodayDate(date) ? 'bg-blue-50/50' : '',
                        isWeekendDay(date) ? 'bg-slate-100 border-slate-200 cursor-default opacity-60' : '',
                        dailyLimitExceeded(index) ? 'border-red-500 bg-red-50' : ''
                    ]">
                    <span class="text-xs font-bold uppercase tracking-widest" :class="isTodayDate(date) ? 'text-primary' : 'text-gray-400'">{{ dayNames[index] }}</span>
                    <span class="text-2xl font-bold" :class="isTodayDate(date) ? 'text-dark' : (isWeekendDay(date) ? 'text-gray-400' : 'text-gray-700')">{{ date.getDate() }}</span>
                    <div v-if="getDayType(date)" class="mt-1">
                        <span class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded shadow-sm bg-blue-100 text-blue-700">{{ getDayLabel(date) }}</span>
                    </div>
                    <div v-else-if="dayTotal(index) > 0" class="px-2 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-dark">{{ dayTotal(index) }}h</div>
                    <div v-else class="h-5"></div>
                    <div v-if="isTodayDate(date)" class="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary"></div>
                </div>
            </div>
        </div>

        <div class="card flex-1 flex flex-col overflow-hidden p-0 bg-white rounded-2xl shadow-sm border border-gray-200">
            <div class="flex justify-between items-center px-6 py-4 border-b bg-gray-50/50">
                <h2 class="font-bold text-sm uppercase tracking-wider text-dark flex items-center gap-2"><Info class="w-4 h-4 text-primary" /> Detalle de Imputaciones</h2>
                <div class="flex gap-3">
                    <button @click="deleteLines" class="flex items-center gap-2 px-3 py-1.5 text-xs font-bold text-red-600 hover:bg-red-50 rounded uppercase">
                        <Trash2 class="w-3 h-3" /> Borrar
                    </button>
                    <button @click="openAddModal" class="btn-primary flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold bg-primary text-white transition">
                        <Plus class="w-4 h-4" /> Añadir Línea
                    </button>
                </div>
            </div>

            <div class="overflow-x-auto flex-1 relative">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-white text-xs uppercase tracking-wider border-b-2 border-gray-100 text-dark">
                            <th class="p-3 w-8 text-center"></th>
                            <th class="p-3 font-bold w-1/4">Cliente</th>
                            <th class="p-3 font-bold w-1/3">Proyecto</th>
                            <th v-for="(date, i) in weekDays" :key="i" class="p-2 text-center w-14">
                                <div class="flex flex-col items-center"><span>{{ dayNames[i] }}</span><span class="text-[10px] opacity-60 font-medium">{{ date.getDate() }}</span></div>
                            </th>
                            <th class="p-3 font-bold text-center w-16">Total</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-gray-700 divide-y divide-gray-50">
                        <tr v-if="rows.length === 0 && !isLoading"><td colspan="11" class="px-6 py-12 text-center text-gray-400 italic">No hay imputaciones esta semana. Pulsa "Añadir Línea" para comenzar.</td></tr>
                        <tr v-for="row in rows" :key="row.id" class="hover:bg-blue-50/20 transition group">
                            <td class="p-3 text-center"><input type="checkbox" v-model="row.selected" class="rounded border-gray-300"></td>
                            <td class="p-2"><div class="flex items-center gap-2 border border-transparent rounded px-2 py-1"><Building2 class="w-3 h-3 text-gray-400" /><span class="text-xs font-medium">{{ row.client }}</span></div></td>
                            <td class="p-2"><span class="text-xs font-bold text-slate-700 px-2">{{ row.project }}</span></td>
                            <td v-for="(hour, index) in row.hours" :key="index" class="p-1 text-center">
                                <input type="number" step="0.5" v-model="row.hours[index]" :disabled="!isEditableDate(weekDays[index])"
                                    class="w-full text-center py-1 rounded transition font-medium text-sm disabled:cursor-not-allowed appearance-none border"
                                    :class="{
                                        'bg-transparent border-transparent text-primary font-bold': isEditableDate(weekDays[index]) && row.hours[index] > 0,
                                        'bg-gray-100 text-gray-400': !isEditableDate(weekDays[index]),
                                        'border-red-500 bg-red-50 text-red-600 ring-2 ring-red-500': dailyLimitExceeded(index) || isInvalidStep(row.hours[index])
                                    }">
                            </td>
                            <td class="p-3 text-center font-bold text-dark bg-gray-50 text-sm">{{ rowTotal(row) }}</td>
                        </tr>
                    </tbody>
                    <tfoot class="bg-gray-50 border-t border-gray-200 text-xs font-bold text-dark uppercase">
                        <tr>
                            <td colspan="3" class="p-3 text-right">Total Diario:</td>
                            <td v-for="(date, index) in weekDays" :key="index" class="p-2 text-center" :class="dailyLimitExceeded(index) ? 'bg-red-100' : ''">
                                <span :class="dailyLimitExceeded(index) ? 'text-red-600 font-extrabold' : 'text-primary'">{{ dayTotal(index) }}</span>
                            </td>
                            <td class="p-3 text-center border-l border-blue-100 text-sm" :class="weeklyLimitExceeded ? 'bg-red-600 text-white' : 'bg-blue-50 text-blue-900'">{{ weekTotal }} / {{ getMaxWeekHours() }}</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <div class="p-4 bg-gray-50 border-t flex justify-end gap-4 items-center">
                <p v-if="hasErrors" class="text-xs font-bold text-red-600 animate-pulse flex items-center gap-1">
                    <AlertCircle class="w-4 h-4"/> {{ rows.some(r => r.hours.some(h => isInvalidStep(h))) ? 'Solo se permiten incrementos de 0.5h' : 'Corrige el exceso de horas' }}
                </p>
                <button @click="saveChanges" :disabled="hasErrors || isLoading" class="btn-primary px-8 py-2.5 rounded-xl font-bold uppercase tracking-widest text-xs shadow-md transition-all bg-slate-900 text-white disabled:bg-gray-300">
                    <Save class="w-4 h-4 mr-2" /> Guardar Imputaciones
                </button>
            </div>
        </div>

        <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
                <div class="bg-slate-50 border-b px-6 py-4 flex justify-between items-center">
                    <h3 class="text-lg font-bold text-slate-800">Añadir Proyecto</h3>
                    <button @click="closeAddModal"><X class="w-5 h-5 text-gray-400" /></button>
                </div>
                <div class="p-6">
                    <label class="text-[10px] font-black uppercase text-slate-400 tracking-widest">Proyecto Asignado</label>
                    <select v-model="newEntry.projectId" class="w-full border-2 border-slate-100 rounded-xl p-3 mt-2 outline-none focus:border-primary transition bg-slate-50">
                        <option :value="undefined" disabled>Selecciona un proyecto...</option>
                        <option v-for="p in masterProjects" :key="p.id || p.Id" :value="p.id || p.Id">
                            {{ p.name || p.Nombre }} - ({{ p.client || p.ClienteNombre }})
                        </option>
                    </select>
                </div>
                <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3">
                    <button @click="confirmAddLine" class="bg-primary text-white px-6 py-2 rounded-xl font-bold uppercase tracking-widest text-xs">Añadir a la Tabla</button>
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
    </div>
</template>
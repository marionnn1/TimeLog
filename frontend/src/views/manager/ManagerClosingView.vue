<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import ManagerAPI from '../../services/ManagerAPI'
import {
    Lock, Unlock, Search, Calendar, AlertCircle, CheckCircle2,
    FileDown, XCircle, Ban, Trash2, AlertTriangle, X
} from 'lucide-vue-next'

// Calculamos el mes actual dinámicamente en formato YYYY-MM
const today = new Date()
const currentMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`

const closingMonth = ref(currentMonth)
const searchQuery = ref('')
const isMonthClosed = ref(false)
const auditUsers = ref([])
const isLoading = ref(false)

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

const requestConfirmation = (title, message, type, callback) => {
    confirmState.value = { show: true, title, message, type, action: callback }
}

const executeConfirmation = () => {
    if (confirmState.value.action) confirmState.value.action()
    confirmState.value.show = false
}

// --- LLAMADAS AL BACKEND ---
const fetchClosingData = async () => {
    isLoading.value = true
    try {
        const response = await ManagerAPI.getClosingData(closingMonth.value)
        const data = response.data || response
        isMonthClosed.value = data.isMonthClosed
        auditUsers.value = data.users || []
    } catch (error) {
        console.error("Error obteniendo datos de cierre:", error)
        showToast("Error al conectar con el servidor", "error")
        auditUsers.value = []
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    fetchClosingData()
})

watch(closingMonth, () => {
    fetchClosingData()
})

const filteredUsers = computed(() => {
    return auditUsers.value.filter(u =>
        u.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
})

const canCloseMonth = computed(() => {
    // Verificamos el estado en inglés devuelto por el backend
    return !auditUsers.value.some(u => u.status === 'incomplete')
})

const statusSummary = computed(() => {
    const total = auditUsers.value.length
    const incompleteCount = auditUsers.value.filter(u => u.status === 'incomplete').length
    const emptyCount = auditUsers.value.filter(u => u.status === 'empty').length

    return { total, incomplete: incompleteCount, empty: emptyCount, complete: total - incompleteCount - emptyCount }
})

const processClosingToggle = async (actionStr) => {
    try {
        // actionStr será 'close' u 'open'
        await ManagerAPI.toggleClosingMonth(closingMonth.value, actionStr)
        isMonthClosed.value = (actionStr === 'close')
        showToast(`Mes de ${closingMonth.value} ${actionStr === 'close' ? 'cerrado' : 'reabierto'} correctamente`, 'success')
    } catch (error) {
        showToast(`Error al cambiar el estado del mes`, 'error')
    }
}

const executeClosing = () => {
    if (!canCloseMonth.value) {
        requestConfirmation(
            'Cierre Forzoso',
            'Hay usuarios con días pendientes de imputar. ¿Estás seguro de que quieres forzar el cierre del mes? Esto bloqueará futuras imputaciones.',
            'warning',
            () => processClosingToggle('close')
        )
        return
    }
    
    if (statusSummary.value.empty === statusSummary.value.total) {
        requestConfirmation(
            'Mes Vacío',
            'El mes parece no tener actividad registrada. ¿Cerrar igualmente?',
            'neutral',
            () => processClosingToggle('close')
        )
        return
    }
    
    processClosingToggle('close')
}

const reopenMonth = () => {
    requestConfirmation(
        'Reabrir Mes',
        '¿Estás seguro de que quieres reabrir este periodo? Los usuarios podrán volver a editar sus imputaciones.',
        'neutral',
        () => processClosingToggle('open')
    )
}

const exportExcel = () => {   
    const headers = ['ID', 'Nombre', 'Rol', 'Horas Reales', 'Estado', 'Dias Faltantes']
    const rows = auditUsers.value.map(u => [
        u.id,
        u.name,
        u.role,
        u.actualHours,
        u.status,
        u.missingDays.join(', ') 
    ])

    const csvContent = [
        headers.join(';'),
        ...rows.map(row => row.join(';'))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `auditoria_cierre_${closingMonth.value}.csv`)
    document.body.appendChild(link)

    link.click() 
    document.body.removeChild(link) 
    showToast('Archivo CSV descargado', 'success')
}

const notifyUser = (user) => {
    // Vuelve a ser solo un mock visual
    showToast(`Recordatorio enviado a ${user.name}`, 'success')
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-hidden relative">

        <div class="flex justify-between items-end shrink-0">
            <div>
                <h1 class="h1-title flex items-center gap-2">
                    <Lock v-if="isMonthClosed" class="w-8 h-8 text-emerald-600" />
                    <Unlock v-else class="w-8 h-8 text-amber-500" />
                    Auditoría y Cierre Mensual
                </h1>
                <p class="subtitle">Revisa los días faltantes antes de bloquear el periodo.</p>
            </div>

            <div class="flex items-center gap-4">
                <div class="flex items-center bg-white border border-gray-200 rounded-lg px-3 py-2 shadow-sm">
                    <Calendar class="w-4 h-4 text-gray-400 mr-2" />
                    <input type="month" v-model="closingMonth"
                        class="text-sm font-bold text-dark outline-none bg-transparent">
                </div>

                <button @click="exportExcel" class="btn-secondary flex items-center gap-2">
                    <FileDown class="w-4 h-4" /> Exportar Auditoría (.CSV)
                </button>
            </div>
        </div>

        <div class="card bg-slate-900 text-white p-4 flex justify-between items-center shadow-lg shrink-0 transition-colors duration-300"
            :class="isMonthClosed ? 'bg-emerald-900' : 'bg-slate-900'">

            <div class="flex items-center gap-4">
                <div class="p-3 rounded-full bg-white/10">
                    <component :is="isMonthClosed ? CheckCircle2 : AlertCircle" class="w-6 h-6 text-white" />
                </div>
                <div>
                    <h3 class="font-bold text-lg">
                        {{ isMonthClosed ? 'Periodo Cerrado' : 'Periodo Abierto' }}
                    </h3>
                    <p class="text-sm text-slate-300" v-if="!isMonthClosed">
                        <span v-if="statusSummary.incomplete > 0">
                            Hay <b>{{ statusSummary.incomplete }} usuarios</b> pendientes de completar jornada.
                        </span>
                        <span v-else-if="statusSummary.empty === statusSummary.total">
                            No hay actividad registrada en este mes.
                        </span>
                        <span v-else>
                            Todo el equipo está al día. Listo para cerrar.
                        </span>
                    </p>
                    <p class="text-sm text-emerald-200" v-else>
                        El mes está bloqueado. Solo se admiten correcciones mediante solicitud.
                    </p>
                </div>
            </div>

            <div v-if="!isMonthClosed">
                <button @click="executeClosing"
                    class="px-6 py-2.5 rounded-lg font-bold text-sm transition flex items-center gap-2 shadow-lg"
                    :class="canCloseMonth ? 'bg-emerald-500 hover:bg-emerald-400 text-white' : 'bg-amber-500 hover:bg-amber-400 text-white'">
                    <Lock class="w-4 h-4" />
                    {{ canCloseMonth ? 'Cerrar Mes Ahora' : 'Forzar Cierre' }}
                </button>
            </div>
            <div v-else>
                <button @click="reopenMonth"
                    class="px-6 py-2.5 rounded-lg font-bold text-sm bg-white/10 hover:bg-white/20 text-white flex items-center gap-2 transition">
                    <Unlock class="w-4 h-4" /> Reabrir Mes
                </button>
            </div>
        </div>

        <div class="card p-0 flex flex-col flex-1 overflow-hidden border border-gray-200 shadow-md">

            <div class="p-4 border-b border-gray-200 bg-gray-50 flex items-center gap-3">
                <Search class="w-5 h-5 text-gray-400" />
                <input v-model="searchQuery" type="text" placeholder="Buscar empleado..."
                    class="w-full bg-transparent border-none outline-none text-sm font-medium text-dark placeholder-gray-400">
            </div>

            <div class="overflow-auto flex-1">
                <table class="w-full text-left border-collapse">
                    <thead class="bg-white sticky top-0 z-10 shadow-sm">
                        <tr class="text-xs uppercase tracking-wider text-gray-400 border-b border-gray-100">
                            <th class="px-6 py-4 font-bold">Empleado</th>
                            <th class="px-6 py-4 font-bold text-center">Horas Reales</th>
                            <th class="px-6 py-4 font-bold w-1/3">Días Pendientes</th>
                            <th class="px-6 py-4 font-bold text-center">Estado</th>
                            <th class="px-6 py-4 font-bold text-right" v-if="!isMonthClosed">Acción</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm divide-y divide-gray-50">
                        <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-slate-50 transition group">

                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3">
                                    <div class="w-9 h-9 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">
                                        {{ user.name.charAt(0) }}
                                    </div>
                                    <div>
                                        <p class="font-bold text-dark">{{ user.name }}</p>
                                        <p class="text-xs text-gray-500 uppercase">{{ user.role }}</p>
                                    </div>
                                </div>
                            </td>

                            <td class="px-6 py-4 text-center">
                                <span class="font-mono font-bold text-lg"
                                    :class="user.actualHours === 0 ? 'text-gray-300' : 'text-dark'">
                                    {{ user.actualHours }}h
                                </span>
                            </td>

                            <td class="px-6 py-4">
                                <div v-if="user.status === 'complete'">
                                    <span class="flex items-center gap-1 text-emerald-600 text-xs font-bold w-fit">
                                        <CheckCircle2 class="w-3.5 h-3.5" /> Todo al día
                                    </span>
                                </div>
                                <div v-else-if="user.status === 'incomplete'" class="flex flex-col gap-1">
                                    <span class="text-[10px] font-bold text-gray-400 uppercase flex items-center gap-1">
                                        <XCircle class="w-3 h-3 text-red-400" /> Días sin registrar:
                                    </span>
                                    <div class="flex flex-wrap gap-1 max-w-[200px]">
                                        <span v-for="dia in user.missingDays" :key="dia"
                                            class="bg-red-50 text-red-600 border border-red-100 px-1.5 py-0.5 rounded text-[10px] font-mono font-bold">
                                            {{ dia }}
                                        </span>
                                    </div>
                                </div>
                                <div v-else>
                                    <span class="text-xs text-gray-300 italic flex items-center gap-1">
                                        <Ban class="w-3 h-3" /> Sin imputaciones
                                    </span>
                                </div>
                            </td>

                            <td class="px-6 py-4 text-center">
                                <span v-if="user.status === 'complete'"
                                    class="badge bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm">
                                    Completo
                                </span>
                                <span v-else-if="user.status === 'incomplete'"
                                    class="badge bg-amber-50 text-amber-700 border-amber-200 shadow-sm">
                                    Incompleto
                                </span>
                                <span v-else class="badge bg-gray-50 text-gray-400 border-gray-200">
                                    Sin actividad
                                </span>
                            </td>

                            <td class="px-6 py-4 text-right" v-if="!isMonthClosed">
                                <button v-if="user.status === 'incomplete'" @click="notifyUser(user)"
                                    class="text-xs font-bold text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-3 py-1.5 rounded transition border border-transparent hover:border-blue-100 ml-auto">
                                    Notificar
                                </button>
                                <span v-else class="text-gray-300 text-xs">-</span>
                            </td>

                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div v-if="confirmState.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
            <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
                <div class="flex flex-col items-center text-center gap-3">
                    <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2"
                         :class="confirmState.type === 'warning' ? 'bg-amber-100 text-amber-600' : 'bg-slate-100 text-slate-600'">
                        <component :is="confirmState.type === 'warning' ? AlertTriangle : CheckCircle2" class="w-6 h-6" />
                    </div>
                    <h3 class="text-lg font-bold text-slate-900">{{ confirmState.title }}</h3>
                    <p class="text-sm text-slate-500 leading-relaxed">{{ confirmState.message }}</p>
                    
                    <div class="flex gap-3 w-full mt-4">
                        <button @click="confirmState.show = false" class="btn-secondary flex-1 justify-center">Cancelar</button>
                        <button @click="executeConfirmation" 
                                class="flex-1 justify-center btn-primary"
                                :class="confirmState.type === 'warning' ? 'bg-amber-600 hover:bg-amber-700' : 'bg-slate-700 hover:bg-slate-800'">
                            Confirmar
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <transition enter-active-class="transform ease-out duration-300 transition" enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2" enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="toast.show" class="absolute bottom-6 right-6 z-50 flex items-center w-full max-w-xs p-4 space-x-3 text-gray-500 bg-white rounded-lg shadow-lg border border-gray-100" role="alert">
                <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg" :class="toast.type === 'success' ? 'text-green-500 bg-green-100' : 'text-red-500 bg-red-100'">
                    <component :is="toast.type === 'success' ? CheckCircle2 : AlertCircle" class="w-5 h-5"/>
                </div>
                <div class="ml-3 text-sm font-bold text-gray-800">{{ toast.message }}</div>
                <button @click="toast.show = false" type="button" class="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 items-center justify-center">
                    <X class="w-4 h-4"/>
                </button>
            </div>
        </transition>

    </div>
</template>
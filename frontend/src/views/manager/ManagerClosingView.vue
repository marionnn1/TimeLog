<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import ManagerAPI from '../../services/ManagerAPI'
import { useDataStore } from '../../stores/dataStore'
import {
    Lock, Unlock, Search, Calendar, AlertCircle, CheckCircle2,
    FileDown, XCircle, Ban
} from 'lucide-vue-next'
import ConfirmModal from '../../components/common/ConfirmModal.vue'
import ToastNotification from '../../components/common/ToastNotification.vue'

const store = useDataStore()
const user = store.getCurrentUser()

const hoy = new Date()
const mesActual = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}`

const fechaCierre = ref(mesActual)
const busqueda = ref('')
const mesCerrado = ref(false)
const auditoriaUsuarios = ref([])
const isLoading = ref(false)

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => { toast.value.show = false }, 3000)
}

const confirmState = ref({ show: false, title: '', message: '', type: 'neutral', action: null })

const solicitarConfirmacion = (title, message, type, callback) => {
    confirmState.value = { show: true, title, message, type, action: callback }
}

const ejecutarConfirmacion = () => {
    if (confirmState.value.action) confirmState.value.action()
    confirmState.value.show = false
}

const fetchClosingData = async () => {
    isLoading.value = true
    try {
        const response = await ManagerAPI.getClosingData(fechaCierre.value)
        mesCerrado.value = response.data.mesCerrado
        auditoriaUsuarios.value = response.data.usuarios || []
    } catch (error) {
        showToast("Error al conectar con el servidor", "error")
        auditoriaUsuarios.value = []
    } finally {
        isLoading.value = false
    }
}

onMounted(() => { fetchClosingData() })
watch(fechaCierre, () => { fetchClosingData() })

const usuariosFiltrados = computed(() => {
    return auditoriaUsuarios.value.filter(u =>
        u.nombre.toLowerCase().includes(busqueda.value.toLowerCase())
    )
})

const puedeCerrarMes = computed(() => {
    return !auditoriaUsuarios.value.some(u => u.estado === 'incompleto')
})

const resumenEstado = computed(() => {
    const total = auditoriaUsuarios.value.length
    const incompletos = auditoriaUsuarios.value.filter(u => u.estado === 'incompleto').length
    const vacios = auditoriaUsuarios.value.filter(u => u.estado === 'vacio').length
    return { total, incompletos, vacios, completos: total - incompletos - vacios }
})

const procesarCierreToggle = async (accion) => {
    try {
        await ManagerAPI.toggleCierreMes(fechaCierre.value, accion, user.id)
        mesCerrado.value = (accion === 'cerrar')
        showToast(`Mes de ${fechaCierre.value} ${accion === 'cerrar' ? 'cerrado' : 'reabierto'} correctamente`, 'success')
    } catch (error) {
        showToast(`Error al ${accion} el mes`, 'error')
    }
}

const ejecutarCierre = () => {
    if (!puedeCerrarMes.value) {
        solicitarConfirmacion(
            'Cierre Forzoso',
            'Hay usuarios con días pendientes de imputar. ¿Forzar el cierre del mes? Esto bloqueará futuras imputaciones.',
            'warning',
            () => procesarCierreToggle('cerrar')
        )
        return
    }
    
    if (resumenEstado.value.vacios === resumenEstado.value.total) {
        solicitarConfirmacion(
            'Mes Vacío',
            'El mes no tiene actividad registrada. ¿Cerrar igualmente?',
            'neutral',
            () => procesarCierreToggle('cerrar')
        )
        return
    }
    
    procesarCierreToggle('cerrar')
}

const reabrirMes = () => {
    solicitarConfirmacion(
        'Reabrir Mes',
        '¿Quieres reabrir este mes?',
        'neutral',
        () => procesarCierreToggle('reabrir')
    )
}

const exportarExcel = () => {   
    const headers = ['ID Empleado', 'Nombre Empleado', 'Rol', 'Estado Periodo', 'Días Faltantes', 'Horas Totales Mes', 'Cliente', 'Proyecto', 'Horas Proyecto']
    const rows = []

    auditoriaUsuarios.value.forEach(u => {
        const baseData = [ u.id, `"${u.nombre}"`, `"${u.rol}"`, `"${u.estado}"`, `"${u.diasFaltantes.join(', ')}"`, u.horasReales ]
        if (u.desgloseProyectos && u.desgloseProyectos.length > 0) {
            u.desgloseProyectos.forEach(p => { rows.push([ ...baseData, `"${p.cliente}"`, `"${p.proyecto}"`, p.horas ]) })
        } else {
            rows.push([ ...baseData, '""', '""', 0 ])
        }
    })

    const csvContent = [headers.join(';'), ...rows.map(row => row.join(';'))].join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `Cierre_Mensual_${fechaCierre.value}.csv`)
    document.body.appendChild(link)
    link.click() 
    document.body.removeChild(link) 
    showToast('Reporte descargado correctamente', 'success')
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-hidden relative">

        <div class="flex justify-between items-end shrink-0">
            <div>
                <h1 class="h1-title flex items-center gap-2">
                    <Lock v-if="mesCerrado" class="w-8 h-8 text-emerald-600" />
                    <Unlock v-else class="w-8 h-8 text-amber-500" />
                    Auditoría y Cierre Mensual
                </h1>
                <p class="subtitle">Revisa los días faltantes antes de bloquear el periodo.</p>
            </div>

            <div class="flex items-center gap-4">
                <div class="flex items-center bg-white border border-gray-200 rounded-lg px-3 py-2 shadow-sm">
                    <Calendar class="w-4 h-4 text-gray-400 mr-2" />
                    <input type="month" v-model="fechaCierre"
                        class="text-sm font-bold text-dark outline-none bg-transparent">
                </div>

                <button @click="exportarExcel" class="btn-secondary flex items-center gap-2">
                    <FileDown class="w-4 h-4" /> Exportar Auditoría (.CSV)
                </button>
            </div>
        </div>

        <div class="card bg-slate-900 text-white p-4 flex justify-between items-center shadow-lg shrink-0 transition-colors duration-300"
            :class="mesCerrado ? 'bg-emerald-900' : 'bg-slate-900'">

            <div class="flex items-center gap-4">
                <div class="p-3 rounded-full bg-white/10">
                    <component :is="mesCerrado ? CheckCircle2 : AlertCircle" class="w-6 h-6 text-white" />
                </div>
                <div>
                    <h3 class="font-bold text-lg">
                        {{ mesCerrado ? 'Periodo Cerrado' : 'Periodo Abierto' }}
                    </h3>
                    <p class="text-sm text-slate-300" v-if="!mesCerrado">
                        <span v-if="resumenEstado.incompletos > 0">
                            Hay <b>{{ resumenEstado.incompletos }} usuarios</b> pendientes de completar jornada.
                        </span>
                        <span v-else-if="resumenEstado.vacios === resumenEstado.total">
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

            <div v-if="!mesCerrado">
                <button @click="ejecutarCierre"
                    class="px-6 py-2.5 rounded-lg font-bold text-sm transition flex items-center gap-2 shadow-lg"
                    :class="puedeCerrarMes ? 'bg-emerald-500 hover:bg-emerald-400 text-white' : 'bg-amber-500 hover:bg-amber-400 text-white'">
                    <Lock class="w-4 h-4" />
                    {{ puedeCerrarMes ? 'Cerrar Mes Ahora' : 'Forzar Cierre' }}
                </button>
            </div>
            <div v-else>
                <button @click="reabrirMes"
                    class="px-6 py-2.5 rounded-lg font-bold text-sm bg-white/10 hover:bg-white/20 text-white flex items-center gap-2 transition">
                    <Unlock class="w-4 h-4" /> Reabrir Mes
                </button>
            </div>
        </div>

        <div class="card p-0 flex flex-col flex-1 overflow-hidden border border-gray-200 shadow-md">

            <div class="p-4 border-b border-gray-200 bg-gray-50 flex items-center gap-3">
                <Search class="w-5 h-5 text-gray-400" />
                <input v-model="busqueda" type="text" placeholder="Buscar empleado..."
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
                        </tr>
                    </thead>
                    <tbody class="text-sm divide-y divide-gray-50">
                        <tr v-for="user in usuariosFiltrados" :key="user.id" class="hover:bg-slate-50 transition group">

                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3">
                                    <img v-if="user.foto" :src="'data:image/jpeg;base64,' + user.foto" alt="Avatar" class="w-9 h-9 rounded-full object-cover shadow-sm shrink-0" />
                                    <div v-else class="w-9 h-9 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600 shrink-0">
                                        {{ user.nombre.charAt(0) }}
                                    </div>
                                    <div>
                                        <p class="font-bold text-dark">{{ user.nombre }}</p>
                                        <p class="text-xs text-gray-500 uppercase">{{ user.rol }}</p>
                                    </div>
                                </div>
                            </td>

                            <td class="px-6 py-4 text-center">
                                <span class="font-mono font-bold text-lg"
                                    :class="user.horasReales === 0 ? 'text-gray-300' : 'text-dark'">
                                    {{ user.horasReales }}h
                                </span>
                            </td>

                            <td class="px-6 py-4">
                                <div v-if="user.estado === 'completo'">
                                    <span class="flex items-center gap-1 text-emerald-600 text-xs font-bold w-fit">
                                        <CheckCircle2 class="w-3.5 h-3.5" /> Todo al día
                                    </span>
                                </div>
                                <div v-else-if="user.estado === 'incompleto'" class="flex flex-col gap-1">
                                    <span class="text-[10px] font-bold text-gray-400 uppercase flex items-center gap-1">
                                        <XCircle class="w-3 h-3 text-red-400" /> Días sin registrar:
                                    </span>
                                    <div class="flex flex-wrap gap-1 max-w-[200px]">
                                        <span v-for="dia in user.diasFaltantes" :key="dia"
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
                                <span v-if="user.estado === 'completo'"
                                    class="badge bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm">
                                    Completo
                                </span>
                                <span v-else-if="user.estado === 'incompleto'"
                                    class="badge bg-amber-50 text-amber-700 border-amber-200 shadow-sm">
                                    Incompleto
                                </span>
                                <span v-else class="badge bg-gray-50 text-gray-400 border-gray-200">
                                    Sin actividad
                                </span>
                            </td>

                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <ConfirmModal 
            :show="confirmState.show"
            :title="confirmState.title"
            :message="confirmState.message"
            :type="confirmState.type"
            @confirm="ejecutarConfirmacion"
            @cancel="confirmState.show = false"
        />

        <ToastNotification
            :show="toast.show"
            :message="toast.message"
            :type="toast.type"
            @close="toast.show = false"
        />

    </div>
</template>
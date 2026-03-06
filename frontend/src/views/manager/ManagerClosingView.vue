<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import ManagerAPI from '../../services/ManagerAPI'
import {
    Lock, Unlock, Search, Calendar, AlertCircle, CheckCircle2,
    FileDown, XCircle, Ban, Trash2, AlertTriangle, X
} from 'lucide-vue-next'

const fechaCierre = ref('2026-01')
const busqueda = ref('')
const mesCerrado = ref(false)
const auditoriaUsuarios = ref([])
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

const solicitarConfirmacion = (title, message, type, callback) => {
    confirmState.value = { show: true, title, message, type, action: callback }
}

const ejecutarConfirmacion = () => {
    if (confirmState.value.action) confirmState.value.action()
    confirmState.value.show = false
}

// --- LLAMADAS AL BACKEND ---
const fetchClosingData = async () => {
    isLoading.value = true
    try {
        const response = await ManagerAPI.getClosingData(fechaCierre.value)
        mesCerrado.value = response.data.mesCerrado
        auditoriaUsuarios.value = response.data.usuarios || []
    } catch (error) {
        console.error("Error obteniendo datos de cierre:", error)
        showToast("Error al conectar con el servidor", "error")
        auditoriaUsuarios.value = []
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    fetchClosingData()
})

watch(fechaCierre, () => {
    fetchClosingData()
})

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
        await ManagerAPI.toggleCierreMes(fechaCierre.value, accion)
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
            'Hay usuarios con días incompletos. ¿Estás seguro de que quieres forzar el cierre del mes? Esto bloqueará futuras imputaciones.',
            'warning',
            () => procesarCierreToggle('cerrar')
        )
        return
    }
    
    if (resumenEstado.value.vacios === resumenEstado.value.total) {
        solicitarConfirmacion(
            'Mes Vacío',
            'El mes parece no tener actividad registrada. ¿Cerrar igualmente?',
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
        '¿Estás seguro de que quieres reabrir este periodo? Los usuarios podrán volver a editar sus imputaciones.',
        'neutral',
        () => procesarCierreToggle('reabrir')
    )
}

const exportarExcel = () => {   
    const headers = ['ID', 'Nombre', 'Rol', 'Horas Reales', 'Horas Teoricas', 'Estado', 'Dias Faltantes']
    const rows = auditoriaUsuarios.value.map(u => [
        u.id,
        u.nombre,
        u.rol,
        u.horasReales,
        u.horasTeoricas,
        u.estado,
        u.diasFaltantes.join(' | ') 
    ])

    const csvContent = [
        headers.join(';'),
        ...rows.map(row => row.join(';'))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `auditoria_cierre_${fechaCierre.value}.csv`)
    document.body.appendChild(link)

    link.click() 
    document.body.removeChild(link) 
    showToast('Archivo CSV descargado', 'success')
}

const notificarUsuario = (nombre) => {
    showToast(`Recordatorio enviado a ${nombre}`, 'success')
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
                            <th class="px-6 py-4 font-bold text-center">Progreso (Horas)</th>
                            <th class="px-6 py-4 font-bold w-1/3">Auditoría Días</th>
                            <th class="px-6 py-4 font-bold text-center">Estado</th>
                            <th class="px-6 py-4 font-bold text-right" v-if="!mesCerrado">Acción</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm divide-y divide-gray-50">
                        <tr v-for="user in usuariosFiltrados" :key="user.id" class="hover:bg-slate-50 transition group">

                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3">
                                    <div
                                        class="w-9 h-9 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">
                                        {{ user.nombre.charAt(0) }}
                                    </div>
                                    <div>
                                        <p class="font-bold text-dark">{{ user.nombre }}</p>
                                        <p class="text-xs text-gray-500 uppercase">{{ user.rol }}</p>
                                    </div>
                                </div>
                            </td>

                            <td class="px-6 py-4">
                                <div class="flex flex-col items-center gap-1">
                                    <span class="font-mono font-bold"
                                        :class="user.horasReales === 0 ? 'text-gray-300' : 'text-dark'">
                                        {{ user.horasReales }} <span class="text-gray-300">/ {{ user.horasTeoricas
                                            }}</span>
                                    </span>
                                    <div class="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                        <div class="h-full rounded-full transition-all" :class="{
                                                'bg-emerald-500': user.estado === 'completo',
                                                'bg-amber-500': user.estado === 'incompleto',
                                                'bg-transparent': user.estado === 'vacio'
                                            }"
                                            :style="`width: ${Math.min((user.horasReales / user.horasTeoricas) * 100, 100)}%`">
                                        </div>
                                    </div>
                                </div>
                            </td>

                            <td class="px-6 py-4">
                                <div v-if="user.estado === 'completo'">
                                    <span class="flex items-center gap-1 text-emerald-600 text-xs font-bold w-fit">
                                        <CheckCircle2 class="w-3.5 h-3.5" /> Completo
                                    </span>
                                </div>
                                <div v-else-if="user.estado === 'incompleto'" class="flex flex-col gap-1">
                                    <span class="text-[10px] font-bold text-gray-400 uppercase flex items-center gap-1">
                                        <XCircle class="w-3 h-3 text-red-400" /> Faltan registros:
                                    </span>
                                    <div class="flex flex-wrap gap-1">
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

                            <td class="px-6 py-4 text-right" v-if="!mesCerrado">
                                <button v-if="user.estado === 'incompleto'" @click="notificarUsuario(user.nombre)"
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
                        <button @click="ejecutarConfirmacion" 
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
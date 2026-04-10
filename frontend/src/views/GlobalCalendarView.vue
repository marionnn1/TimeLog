<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useDataStore } from '../stores/dataStore'
import AbsencesAPI from '../services/AbsencesAPI'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

import {
    Calendar as CalendarIcon, ChevronLeft, ChevronRight,
    AlertTriangle, Plus, X, Check, Palmtree, MapPin, Briefcase,
    AlertCircle, CheckCircle2, Trash2, Users, Stethoscope
} from 'lucide-vue-next'
import ConfirmModal from '../components/common/ConfirmModal.vue'
import ToastNotification from '../components/common/ToastNotification.vue'

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
        const res = await AbsencesAPI.getAusenciasMes(mesApi, year.value)
        if (res.status === 'success') {
            ausenciasDelMes.value = res.data
        }
    } catch (e) {
        console.error("Error al cargar ausencias:", e)
    }
}

const cargarResumenAnual = async () => {
    if (!currentUser) return
    try {
        const res = await AbsencesAPI.getResumenAnual(year.value)
        if (res.status === 'success') {
            resumenAnual.value = res.data
        }
    } catch (e) {
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

const marcadoresAusencias = computed(() => {
    if (!ausenciasDelMes.value || !currentUser) return [];

    const misAusencias = ausenciasDelMes.value.filter(a => a.userId === currentUser.id);

    return misAusencias.map(aus => {
        let color = '#6b7280'; // Gris por defecto
        const tipo = (aus.tipo || '').toLowerCase();
        
        if (tipo.includes('vacaciones')) color = '#10b981'; // emerald-500
        if (tipo.includes('festivo')) color = '#f97316'; // orange-500
        if (tipo.includes('asuntos')) color = '#3b82f6'; // blue-500
        if (tipo.includes('baja')) color = '#a855f7'; // purple-500

        const [y, m, d] = aus.fecha.split('-');

        return {
            date: new Date(y, m - 1, d),
            type: 'dot',
            color: color,
            tooltip: [{ text: aus.tipo.toUpperCase(), color: color }]
        };
    });
});

const mostrarModal = ref(false)
const tabActiva = ref('solicitar')

const form = ref({
    fechaInicio: '',
    fechaFin: '',
    tipo: 'vacaciones',
    motivoBaja: '',
    comentario: ''
})

const motivosBaja = [
    "Baja médica",
    "Baja laboral",
    "Maternidad/Paternidad",
    "Riesgo durante el embarazo/lactancia",
    "Permiso por fallecimiento de familiar",
    "Permiso por enfermedad u hospitalización de familiar",
    "Cuidado familiar",
    "Otros"
]

const minDateISO = computed(() => {
    const d = new Date()
    const offset = d.getTimezoneOffset() * 60000
    return new Date(d.getTime() - offset).toISOString().split('T')[0]
})

const getMiEstiloTipo = (tipo) => {
    const t = (tipo || '').toLowerCase()
    if (t.includes('vacaciones')) return 'bg-emerald-500 text-white border-emerald-600 shadow-md ring-1 ring-emerald-300'
    if (t.includes('festivo')) return 'bg-orange-500 text-white border-orange-600 shadow-md ring-1 ring-orange-300'
    if (t.includes('asuntos')) return 'bg-blue-500 text-white border-blue-600 shadow-md ring-1 ring-blue-300'
    if (t.includes('baja')) return 'bg-purple-600 text-white border-purple-700 shadow-md ring-1 ring-purple-400'
    return 'bg-gray-700 text-white border-gray-800'
}

const getCompaneroEstiloTipo = (tipo) => {
    const t = (tipo || '').toLowerCase()
    if (t.includes('vacaciones')) return 'bg-emerald-50 text-emerald-700 border-emerald-200'
    if (t.includes('festivo')) return 'bg-orange-50 text-orange-700 border-orange-200'
    if (t.includes('asuntos')) return 'bg-blue-50 text-blue-700 border-blue-200'
    if (t.includes('baja')) return 'bg-purple-50 text-purple-700 border-purple-200'
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
    if (t.includes('baja')) return Stethoscope
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
        tabActiva.value = 'eliminar'
        form.value = { fechaInicio: day.isoDate, fechaFin: day.isoDate, tipo: existing.tipo, comentario: '' }
    } else {
        tabActiva.value = 'solicitar'
        form.value = { fechaInicio: day.isoDate, fechaFin: day.isoDate, tipo: 'vacaciones', comentario: '' }
    }

    mostrarModal.value = true
}

const procesarSolicitud = async (diasSolicitados) => {
    try {
        if (diasSolicitados.length > 15) {
            showToast('No se pueden solicitar más de 15 dias seguidos', 'error')
            return
        }

        let comentarioFinal = ''
        
        if (form.value.tipo === 'baja') {
            if (!form.value.motivoBaja) {
                return showToast('El motivo de la baja es obligatorio', 'error')
            }
            comentarioFinal = form.value.motivoBaja
        } else {
            comentarioFinal = form.value.comentario
        }

        const payload = {
            usuario_id: currentUser.id,
            fechas: diasSolicitados,
            tipo: form.value.tipo,
            comentario: comentarioFinal
        }

        const res = await AbsencesAPI.crearAusencia(payload)

        if (res.status === 'success') {
            mostrarModal.value = false
            showToast('Solicitud registrada con éxito', 'success')
            await Promise.all([cargarAusencias(), cargarResumenAnual()])
            form.value.motivoBaja = ''
            form.value.comentario = ''
        } else {
            showToast('Error al guardar la solicitud', 'error')
        }
    } catch (e) {
        showToast('Fallo en la conexión al servidor', 'error')
        console.log(e)
    }
}

const confirmarSolicitud = () => {
    const start = new Date(form.value.fechaInicio)
    const end = new Date(form.value.fechaFin)

    const hoyObj = new Date()
    hoyObj.setHours(0, 0, 0, 0)
    if (start < hoyObj) {
        return showToast("No puedes pedir ausencias para días pasados.", "error")
    }

    const diasSolicitados = []

    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
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

const confirmarEliminacion = async () => {
    const inicioStr = form.value.fechaInicio
    const finStr = form.value.fechaFin

    if (!inicioStr || !finStr) return showToast("Selecciona un rango válido", "error")

    try {
        const resCount = await AbsencesAPI.obtenerConteoRango(currentUser.id, inicioStr, finStr)
        const count = resCount.count

        if (count === 0) {
            return showToast("No hay nada que eliminar en esas fechas", "info")
        }

        solicitarConfirmacion(
            'Eliminar Ausencias',
            `Vas a cancelar ${count} día(s) de tus ausencias registradas. ¿Estás seguro?`,
            'danger',
            async () => {
                try {
                    await AbsencesAPI.eliminarAusencia(currentUser.id, inicioStr, finStr)
                    mostrarModal.value = false
                    showToast('Ausencias eliminadas correctamente', 'success')
                    await Promise.all([cargarAusencias(), cargarResumenAnual()])
                } catch (e) {
                    showToast('Error al eliminar', 'error')
                }
            }
        )
    } catch (e) {
        showToast('Error al verificar días', 'error')
    }
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
                <div class="flex items-center gap-1.5 font-medium text-purple-700">
                    <div class="w-2 h-2 rounded-full bg-purple-500"></div> Baja
                </div>
            </div>
        </div>

        <div class="flex items-center justify-between bg-white p-4 rounded-t-xl border border-slate-200 border-b-0 shadow-sm shrink-0">
            <button @click="prevMonth" class="btn-ghost hover:bg-slate-100">
                <ChevronLeft />
            </button>
            <h2 class="text-xl font-bold text-slate-800 capitalize">{{ monthNames[month] }} {{ year }}</h2>
            <button @click="nextMonth" class="btn-ghost hover:bg-slate-100">
                <ChevronRight />
            </button>
        </div>

        <div class="bg-white rounded-b-xl border border-slate-200 shadow-sm overflow-hidden select-none mb-8 shrink-0">
            <div class="grid grid-cols-7 bg-slate-50 border-b border-slate-200 text-center py-3">
                <div v-for="d in ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']" :key="d"
                    class="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    {{ d }}
                </div>
            </div>

            <div class="grid grid-cols-7 auto-rows-fr">
                <div v-for="p in startPadding" :key="'pad-' + p"
                    class="bg-slate-50/50 border-b border-r border-slate-100 min-h-[100px] xl:min-h-[120px]"></div>

                <div v-for="day in daysInMonth" :key="day.isoDate" @click="abrirModal(day)"
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
                            :title="`${aus.nombre} - ${aus.tipo} ${aus.comentario ? '(' + aus.comentario + ')' : ''}`">

                            <template v-if="aus.userId === currentUser.id">
                                <div class="w-3.5 h-3.5 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                                    <component :is="getIconoTipo(aus.tipo)" class="w-2.5 h-2.5 text-white" />
                                </div>
                                <span class="truncate flex-1 uppercase tracking-wider">Tú - {{ aus.tipo }}</span>
                            </template>

                            <template v-else>
                                <img v-if="aus.foto" :src="'data:image/jpeg;base64,' + aus.foto" alt="Avatar"
                                    class="w-3.5 h-3.5 rounded-full object-cover shrink-0" />
                                <div v-else
                                    class="w-3.5 h-3.5 rounded-full flex items-center justify-center shrink-0 text-[7px]"
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
                            <Plus class="w-5 h-5 text-primary" />
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
                <div v-for="user in resumenAnual" :key="user.nombre"
                    class="p-5 rounded-xl border border-slate-100 bg-slate-50/50 hover:shadow-sm transition-all">
                    <div class="flex items-center gap-3 mb-4">
                        <img v-if="user.foto" :src="'data:image/jpeg;base64,' + user.foto" alt="Avatar"
                            class="w-10 h-10 rounded-full object-cover shadow-inner shrink-0" />
                        <div v-else
                            class="w-10 h-10 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center shadow-inner shrink-0">
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
                            :class="getCompaneroEstiloTipo(dia.tipo)" :title="dia.comentario || dia.tipo">
                            {{ formatShortDate(dia.fecha) }}
                        </span>
                    </div>
                </div>
            </div>

            <div v-if="resumenAnual.length === 0" class="text-center py-10">
                <p class="text-slate-400 font-medium">No hay ausencias registradas en todo el año.</p>
            </div>
        </div>

        <div v-if="mostrarModal"
            class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl p-6 animate-in zoom-in-95">

                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold text-slate-800">Gestión de Ausencias</h3>
                    <button @click="mostrarModal = false" class="text-slate-400 hover:text-slate-600">
                        <X class="w-6 h-6" />
                    </button>
                </div>

                <div class="flex bg-slate-100 p-1 rounded-xl mb-6">
                    <button @click="tabActiva = 'solicitar'"
                        class="flex-1 py-2 rounded-lg text-sm font-bold transition-all"
                        :class="tabActiva === 'solicitar' ? 'bg-white shadow-sm text-primary' : 'text-slate-500 hover:text-slate-700'">
                        Solicitar Días
                    </button>
                    <button @click="tabActiva = 'eliminar'"
                        class="flex-1 py-2 rounded-lg text-sm font-bold transition-all"
                        :class="tabActiva === 'eliminar' ? 'bg-white shadow-sm text-rose-600' : 'text-slate-500 hover:text-slate-700'">
                        Cancelar Días
                    </button>
                </div>

                <div v-if="tabActiva === 'solicitar'" class="space-y-6">
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Desde</label>
                            <VueDatePicker 
                                v-model="form.fechaInicio" 
                                :min-date="minDateISO"
                                :markers="marcadoresAusencias"
                                :clearable="false" 
                                :enable-time-picker="false" 
                                auto-apply 
                                model-type="yyyy-MM-dd" 
                                format="dd/MM/yyyy"
                                placeholder="Selecciona inicio"
                                input-class-name="w-full bg-slate-50 border border-slate-200 text-slate-800 rounded-lg px-3 py-2 font-bold focus:ring-2 focus:ring-primary outline-none"
                            />
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Hasta</label>
                            <VueDatePicker 
                                v-model="form.fechaFin" 
                                :min-date="form.fechaInicio || minDateISO"
                                :markers="marcadoresAusencias"
                                :clearable="false" 
                                :enable-time-picker="false" 
                                auto-apply 
                                model-type="yyyy-MM-dd" 
                                format="dd/MM/yyyy"
                                placeholder="Selecciona fin"
                                input-class-name="w-full bg-slate-50 border border-slate-200 text-slate-800 rounded-lg px-3 py-2 font-bold focus:ring-2 focus:ring-primary outline-none"
                            />
                        </div>
                    </div>

                    <div>
                        <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Tipo de Ausencia</label>
                        <div class="grid grid-cols-2 gap-2"> 
                            <div @click="form.tipo = 'vacaciones'" 
                                class="cursor-pointer border rounded-xl p-3 flex flex-col items-center gap-2 transition-all"
                                :class="form.tipo === 'vacaciones' ? 'border-emerald-500 bg-emerald-50 text-emerald-700 ring-1 ring-emerald-500' : 'border-slate-200 text-slate-500 hover:border-slate-300'">
                                <Palmtree class="w-5 h-5" />
                                <span class="text-[10px] font-bold uppercase">Vacaciones</span>
                            </div>
                            
                            <div @click="form.tipo = 'festivo'" 
                                class="cursor-pointer border rounded-xl p-3 flex flex-col items-center gap-2 transition-all"
                                :class="form.tipo === 'festivo' ? 'border-orange-500 bg-orange-50 text-orange-700 ring-1 ring-orange-500' : 'border-slate-200 text-slate-500 hover:border-slate-300'">
                                <MapPin class="w-5 h-5" />
                                <span class="text-[10px] font-bold uppercase">Festivo</span>
                            </div>

                            <div @click="form.tipo = 'asuntos'" 
                                class="cursor-pointer border rounded-xl p-3 flex flex-col items-center gap-2 transition-all"
                                :class="form.tipo === 'asuntos' ? 'border-blue-500 bg-blue-50 text-blue-700 ring-1 ring-blue-500' : 'border-slate-200 text-slate-500 hover:border-slate-300'">
                                <Briefcase class="w-5 h-5" />
                                <span class="text-[10px] font-bold uppercase">Asuntos P.</span>
                            </div>

                            <div @click="form.tipo = 'baja'" 
                                class="cursor-pointer border rounded-xl p-3 flex flex-col items-center gap-2 transition-all"
                                :class="form.tipo === 'baja' ? 'border-purple-500 bg-purple-50 text-purple-700 ring-1 ring-purple-500' : 'border-slate-200 text-slate-500 hover:border-slate-300'">
                                <Stethoscope class="w-5 h-5" />
                                <span class="text-[10px] font-bold uppercase">Baja / Médica</span>
                            </div>
                        </div>
                    </div>

                    <div v-if="form.tipo === 'baja'" class="space-y-2 animate-in fade-in slide-in-from-top-2">
                        <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-widest">Motivo de la baja</label>
                        <select v-model="form.motivoBaja" 
                                class="w-full bg-slate-50 border border-slate-200 text-slate-800 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-violet-500 outline-none font-bold">
                            <option value="" disabled>Selecciona un motivo...</option>
                            <option v-for="motivo in motivosBaja" :key="motivo" :value="motivo">
                                {{ motivo }}
                            </option>
                        </select>
                    </div>

                    <div v-else>
                        <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2">Comentario (Opcional)</label>
                        <input type="text" v-model="form.comentario" placeholder="Ej: Viaje a Londres..."
                            maxlength="255"
                            class="w-full bg-white border border-slate-200 text-slate-800 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none">
                    </div>

                    <button @click="confirmarSolicitud"
                        class="w-full btn-primary py-3 justify-center text-base bg-primary text-white font-bold rounded-lg hover:bg-blue-700 shadow-md transition flex items-center">
                        <Check class="w-5 h-5 mr-2" /> Confirmar Solicitud
                    </button>
                </div>

                <div v-if="tabActiva === 'eliminar'" class="space-y-6">
                    <div class="bg-rose-50 p-4 rounded-xl border border-rose-200">
                        <p class="text-sm text-rose-700 font-medium mb-3">Selecciona el rango de fechas de las ausencias que deseas cancelar.</p>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-[10px] font-bold text-rose-500 uppercase tracking-widest mb-1">Desde</label>
                                <VueDatePicker 
                                    v-model="form.fechaInicio" 
                                    :markers="marcadoresAusencias"
                                    :clearable="false" 
                                    :enable-time-picker="false" 
                                    auto-apply 
                                    model-type="yyyy-MM-dd" 
                                    format="dd/MM/yyyy"
                                    placeholder="Selecciona inicio"
                                    input-class-name="w-full bg-white border border-rose-200 text-rose-900 rounded-lg px-3 py-2 font-bold focus:ring-2 focus:ring-rose-500 outline-none"
                                />
                            </div>
                            <div>
                                <label class="block text-[10px] font-bold text-rose-500 uppercase tracking-widest mb-1">Hasta</label>
                                <VueDatePicker 
                                    v-model="form.fechaFin" 
                                    :markers="marcadoresAusencias"
                                    :clearable="false" 
                                    :enable-time-picker="false" 
                                    auto-apply 
                                    model-type="yyyy-MM-dd" 
                                    format="dd/MM/yyyy"
                                    placeholder="Selecciona fin"
                                    input-class-name="w-full bg-white border border-rose-200 text-rose-900 rounded-lg px-3 py-2 font-bold focus:ring-2 focus:ring-rose-500 outline-none"
                                />
                            </div>
                        </div>
                    </div>
                    <button @click="confirmarEliminacion" class="w-full py-3 justify-center text-base bg-rose-600 text-white font-bold rounded-lg hover:bg-rose-700 shadow-md transition flex items-center">
                        <Trash2 class="w-5 h-5 mr-2" /> Cancelar Ausencias
                    </button>
                </div>

            </div>
        </div>

        <ConfirmModal :show="confirmState.show" :title="confirmState.title" :message="confirmState.message"
            :type="confirmState.type" @confirm="ejecutarConfirmacion" @cancel="confirmState.show = false" />

        <ToastNotification :show="toast.show" :message="toast.message" :type="toast.type" @close="toast.show = false" />

    </div>
</template>
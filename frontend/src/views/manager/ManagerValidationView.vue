<script setup>
import { ref, onMounted } from 'vue'
import ManagerAPI from '../../services/ManagerAPI'
import { useDataStore } from '../../stores/dataStore'
import { 
    AlertOctagon, Check, X, FileEdit, MessageSquare, Calendar, Clock, Save,
    ArrowRight, AlertTriangle
} from 'lucide-vue-next'
import ConfirmModal from '../../components/common/ConfirmModal.vue'
import ToastNotification from '../../components/common/ToastNotification.vue'

const store = useDataStore()
const currentUser = store.getCurrentUser()

const solicitudes = ref([])
const alertasVacaciones = ref([]) 
const isLoading = ref(false)

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => { toast.value.show = false }, 3000)
}

const confirmState = ref({ show: false, title: '', message: '', type: 'neutral', action: null, inputMode: false })

const solicitarConfirmacion = (title, message, type, callback, inputMode = false) => {
    confirmState.value = { show: true, title, message, type, action: callback, inputMode }
}

const ejecutarConfirmacion = (valorInput) => {
    if (confirmState.value.action) confirmState.value.action(valorInput)
    confirmState.value.show = false
}

const fetchValidations = async () => {
    isLoading.value = true
    try {
        const response = await ManagerAPI.getValidations()
        
        if (response.data && response.data.solicitudes) {
            solicitudes.value = response.data.solicitudes
            alertasVacaciones.value = response.data.alertas_vacaciones || []
        } else {
            solicitudes.value = Array.isArray(response.data) ? response.data : []
            alertasVacaciones.value = []
        }
    } catch (error) {
        showToast("Error al cargar los datos", "error")
    } finally {
        isLoading.value = false
    }
}

onMounted(() => { fetchValidations() })

const solicitudSeleccionada = ref(null)
const horasEditadas = ref(0)
const mostrarModal = ref(false)

const abrirEditor = (solicitud) => {
    solicitudSeleccionada.value = solicitud
    horasEditadas.value = solicitud.horasSolicitadas
    mostrarModal.value = true
}

const cerrarModal = () => {
    mostrarModal.value = false
    solicitudSeleccionada.value = null
}

const guardarCorreccion = async () => {
    try {
        await ManagerAPI.approveValidation(solicitudSeleccionada.value.id, horasEditadas.value, currentUser.id)
        showToast(`Corrección aplicada correctamente`, 'success')
        cerrarModal()
        fetchValidations() 
    } catch (error) {
        showToast(error.response?.data?.error || `Error al guardar la corrección`, 'error')
    }
}

const rechazarSolicitud = (id) => {
    solicitarConfirmacion(
        'Rechazar Solicitud',
        'Por favor, indica el motivo del rechazo para notificar al usuario:',
        'danger',
        async (motivo) => {
            if (motivo && motivo.trim() !== '') {
                try {
                    await ManagerAPI.rejectValidation(id, motivo, currentUser.id)
                    showToast("Solicitud rechazada y notificada.", "success")
                    fetchValidations() 
                } catch (error) {
                    showToast("Error al rechazar la solicitud.", "error")
                }
            } else {
                showToast("Debes indicar un motivo", "error")
            }
        },
        true 
    )
}
</script>

<template>
  <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto relative">
    
    <div>
        <h1 class="h1-title flex items-center gap-2">
            <AlertOctagon class="w-8 h-8 text-amber-500" /> Solicitudes de Corrección
        </h1>
        <p class="subtitle">Peticiones de usuarios para modificar horas en días cerrados o erróneos.</p>
    </div>

    <div v-if="alertasVacaciones.length > 0" class="bg-rose-50 border border-rose-200 p-4 rounded-xl shadow-sm shrink-0">
        <h3 class="font-bold text-rose-700 flex items-center gap-2 mb-3">
            <AlertTriangle class="w-5 h-5"/> ¡Atención! Exceso de vacaciones detectado
        </h3>
        <p class="text-sm text-rose-600 mb-4">Se ha detectado que 3 o más usuarios han solicitado vacaciones para los mismos días. Este es el orden en el que lo solicitaron:</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div v-for="alerta in alertasVacaciones" :key="alerta.fecha" class="bg-white border border-rose-200 p-3 rounded-lg shadow-sm">
                <div class="flex items-center gap-2 font-bold text-rose-700 mb-3 border-b border-rose-100 pb-2">
                    <Calendar class="w-4 h-4"/> {{ alerta.fecha }}
                    <span class="text-[10px] bg-rose-100 px-2 py-0.5 rounded-full ml-auto">{{ alerta.total }} personas</span>
                </div>
                <div class="flex flex-col gap-1.5">
                    <div v-for="(user, idx) in alerta.usuarios" :key="idx" class="text-xs flex items-center gap-2" :class="idx === alerta.usuarios.length - 1 ? 'text-rose-700 font-bold' : 'text-slate-600'">
                        <span class="w-4 h-4 rounded-full flex items-center justify-center text-[9px] font-black border shrink-0" 
                              :class="idx === alerta.usuarios.length - 1 ? 'bg-rose-500 text-white border-rose-600' : 'bg-slate-100 text-slate-500 border-slate-200'">
                            {{ idx + 1 }}
                        </span>
                        <span class="truncate" :title="user">{{ user }}</span>
                        <span v-if="idx === alerta.usuarios.length - 1" class="text-[8px] uppercase bg-rose-100 text-rose-600 px-1.5 py-0.5 rounded ml-auto shrink-0 border border-rose-200">
                            Último
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mb-4"></div>
        <p class="text-gray-500">Cargando solicitudes...</p>
    </div>

    <div v-else-if="solicitudes.length > 0" class="grid gap-4">
        <div v-for="solicitud in solicitudes" :key="solicitud.id" 
             class="card p-0 overflow-hidden flex flex-col md:flex-row shadow-md border-l-4 border-l-amber-400 group hover:shadow-lg transition">
            
            <div class="p-5 bg-slate-50 border-r border-gray-100 w-full md:w-64 flex flex-col gap-3 shrink-0">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-slate-200 text-slate-600 flex items-center justify-center font-bold">
                        {{ solicitud.avatar }}
                    </div>
                    <div>
                        <p class="font-bold text-dark">{{ solicitud.usuario }}</p>
                        <p class="text-xs text-gray-500 font-mono">ID Solicitud: #{{ solicitud.id }}</p>
                    </div>
                </div>
                <div class="space-y-1 mt-2">
                    <div class="flex items-center gap-2 text-xs text-gray-500 mb-1">
                        <Calendar class="w-3.5 h-3.5" />
                        <span class="font-bold text-dark">{{ solicitud.fecha }}</span>
                    </div>
                    
                    <div class="flex items-center gap-2 text-xs">
                        <Clock class="w-3.5 h-3.5 text-gray-400" />
                        <span class="text-gray-500 line-through">{{ solicitud.horasActuales }}h</span>
                        <ArrowRight class="w-3 h-3 text-primary" />
                        <span class="font-bold text-primary">{{ solicitud.horasSolicitadas }}h</span>
                    </div>
                </div>
            </div>

            <div class="p-5 flex-1 flex flex-col justify-center gap-3">
                <div class="flex items-center gap-2">
                    <span class="text-[10px] font-bold uppercase bg-blue-50 text-blue-700 px-2 py-0.5 rounded border border-blue-100">
                        {{ solicitud.cliente }}
                    </span>
                    <span class="text-sm font-bold text-dark">{{ solicitud.proyecto }}</span>
                </div>
                
                <div class="bg-amber-50 p-3 rounded-lg border border-amber-100 text-sm text-amber-900 flex gap-3 items-start">
                    <MessageSquare class="w-5 h-5 mt-0.5 text-amber-600 shrink-0" />
                    <p class="italic">"{{ solicitud.motivo }}"</p>
                </div>
            </div>

            <div class="p-5 flex flex-col justify-center gap-3 w-full md:w-56 shrink-0 bg-white border-l border-gray-100">
                <button @click="abrirEditor(solicitud)" 
                        class="btn-primary w-full flex items-center justify-center gap-2 text-xs shadow-sm">
                    <FileEdit class="w-4 h-4" /> Aceptar y Corregir
                </button>
                <button @click="rechazarSolicitud(solicitud.id)" 
                        class="w-full py-2 px-4 rounded-lg border border-gray-200 text-gray-500 hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition text-xs font-bold uppercase tracking-wide flex items-center justify-center gap-2">
                    <X class="w-4 h-4" /> Rechazar
                </button>
            </div>
        </div>
    </div>

    <div v-else class="flex-1 flex flex-col items-center justify-center text-center opacity-50">
        <Check class="w-16 h-16 text-emerald-500 mb-4 bg-emerald-50 rounded-full p-3" />
        <h3 class="text-xl font-bold text-dark">Bandeja limpia</h3>
        <p class="text-gray-500">No hay solicitudes de corrección pendientes.</p>
    </div>

    <div v-if="mostrarModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
            <div class="bg-primary px-6 py-4 flex justify-between items-center">
                <h3 class="text-lg font-bold text-white flex items-center gap-2">
                    <FileEdit class="w-5 h-5"/> Corregir Imputación
                </h3>
                <button @click="cerrarModal" class="text-white/80 hover:text-white"><X class="w-5 h-5"/></button>
            </div>

            <div v-if="solicitudSeleccionada" class="p-6 space-y-4">
                <div class="bg-gray-50 p-3 rounded border border-gray-200 text-sm space-y-1">
                    <p><span class="font-bold text-gray-500 w-20 inline-block">Usuario:</span> {{ solicitudSeleccionada.usuario }}</p>
                    <p><span class="font-bold text-gray-500 w-20 inline-block">Proyecto:</span> {{ solicitudSeleccionada.proyecto }}</p>
                    <p><span class="font-bold text-gray-500 w-20 inline-block">Fecha:</span> {{ solicitudSeleccionada.fecha }}</p>
                </div>

                <div>
                    <label class="label-std">Horas Solicitadas (Aprobar o Editar)</label>
                    <div class="flex items-center gap-3 mt-2">
                        <input type="number" step="0.5" min="0" max="24" v-model.number="horasEditadas" 
                               class="input-std text-center text-lg font-bold w-32" />
                        <span class="text-sm text-gray-500">Horas</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-2">
                        Al guardar, se actualizará el registro con estas horas y se marcará como resuelta.
                    </p>
                </div>
            </div>

            <div class="p-4 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
                <button @click="cerrarModal" class="btn-secondary">Cancelar</button>
                <button @click="guardarCorreccion" class="btn-primary">
                    <Save class="w-4 h-4 mr-2"/> Guardar Cambios
                </button>
            </div>
        </div>
    </div>

    <ConfirmModal 
        :show="confirmState.show"
        :title="confirmState.title"
        :message="confirmState.message"
        :type="confirmState.type"
        :inputMode="confirmState.inputMode"
        inputPlaceholder="Motivo del rechazo..."
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
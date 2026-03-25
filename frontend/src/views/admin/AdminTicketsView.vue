<script setup>
import { ref, onMounted } from 'vue'
import AdminAPI from '@/services/AdminAPI'
import { 
    AlertOctagon, Check, X, FileEdit, MessageSquare, Calendar, Clock, Save,
    ArrowRight, Loader2
} from 'lucide-vue-next'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import ToastNotification from '@/components/common/ToastNotification.vue'

const solicitudes = ref([])
const isLoading = ref(true)

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => { toast.value.show = false }, 3000)
}

const fetchTickets = async () => {
    isLoading.value = true
    try {
        const json = await AdminAPI.getTickets()
        // Nos aseguramos de leer la propiedad .data de nuestro success_response
        if (json.status === 'success') {
            solicitudes.value = json.data
        } else {
            solicitudes.value = json || [] // Fallback viejo
        }
    } catch (error) {
        showToast("Error al cargar las solicitudes", "error")
    } finally {
        isLoading.value = false
    }
}

onMounted(fetchTickets)

const confirmState = ref({ show: false, title: '', message: '', type: 'neutral', action: null, inputMode: false })

const solicitarConfirmacion = (title, message, type, callback, inputMode = false) => {
    confirmState.value = { show: true, title, message, type, action: callback, inputMode }
}

const ejecutarConfirmacion = (valorInput) => {
    if (confirmState.value.action) confirmState.value.action(valorInput)
    confirmState.value.show = false
}

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
        await AdminAPI.approveTicket(solicitudSeleccionada.value.id, horasEditadas.value)
        showToast(`Corrección aplicada correctamente`, 'success')
        cerrarModal()
        await fetchTickets() 
    } catch (error) {
        showToast(error.message || "Error al guardar la corrección", "error")
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
                    await AdminAPI.rejectTicket(id, motivo)
                    showToast("Solicitud rechazada y notificada.", "success")
                    await fetchTickets() 
                } catch (error) {
                    showToast(error.message || "Error al rechazar la solicitud.", "error")
                }
            } else {
                showToast("Debes indicar un motivo para el rechazo", "error")
            }
        },
        true 
    )
}
</script>

<template>
  <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto relative">
    
    <div>
        <h1 class="h1-title flex items-center gap-2 font-bold text-2xl text-[#232D4B]">
            <AlertOctagon class="w-8 h-8 text-amber-500" /> Administración de Solicitudes
        </h1>
        <p class="subtitle text-gray-500 mt-1 text-sm">Supervisión global de peticiones de modificación de horas.</p>
    </div>

    <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center">
        <Loader2 class="w-10 h-10 animate-spin text-gray-400 mb-2"/>
        <p class="text-gray-500 text-sm font-medium">Buscando solicitudes pendientes...</p>
    </div>

    <div v-else-if="solicitudes.length > 0" class="grid gap-4">
        <div v-for="solicitud in solicitudes" :key="solicitud.id" 
             class="card p-0 overflow-hidden flex flex-col md:flex-row shadow-md border-l-4 border-l-amber-400 group hover:shadow-lg transition bg-white">
            
            <div class="p-5 bg-slate-50 border-r border-gray-100 w-full md:w-64 flex flex-col gap-3 shrink-0">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-slate-200 text-slate-600 flex items-center justify-center font-bold">
                        {{ solicitud.avatar }}
                    </div>
                    <div>
                        <p class="font-bold text-[#232D4B]">{{ solicitud.usuario }}</p>
                        <p class="text-xs text-gray-500 font-mono">ID Solicitud: #{{ solicitud.id }}</p>
                    </div>
                </div>
                <div class="space-y-1 mt-2">
                    <div class="flex items-center gap-2 text-xs text-gray-500 mb-1">
                        <Calendar class="w-3.5 h-3.5" />
                        <span class="font-bold text-[#232D4B]">{{ solicitud.fecha }}</span>
                    </div>
                    
                    <div class="flex items-center gap-2 text-xs">
                        <Clock class="w-3.5 h-3.5 text-gray-400" />
                        <span class="text-gray-500 line-through">{{ solicitud.horasActuales }}h</span>
                        <ArrowRight class="w-3 h-3 text-[#26AA9B]" />
                        <span class="font-bold text-[#26AA9B]">{{ solicitud.horasSolicitadas }}h</span>
                    </div>
                </div>
            </div>

            <div class="p-5 flex-1 flex flex-col justify-center gap-3">
                <div class="flex items-center gap-2">
                    <span class="text-[10px] font-bold uppercase bg-blue-50 text-blue-700 px-2 py-0.5 rounded border border-blue-100">
                        {{ solicitud.cliente }}
                    </span>
                    <span class="text-sm font-bold text-[#232D4B]">{{ solicitud.proyecto }}</span>
                </div>
                
                <div class="bg-amber-50 p-3 rounded-lg border border-amber-100 text-sm text-amber-900 flex gap-3 items-start">
                    <MessageSquare class="w-5 h-5 mt-0.5 text-amber-600 shrink-0" />
                    <p class="italic">"{{ solicitud.motivo }}"</p>
                </div>
            </div>

            <div class="p-5 flex flex-col justify-center gap-3 w-full md:w-56 shrink-0 bg-white border-l border-gray-100">
                <button @click="abrirEditor(solicitud)" 
                        class="bg-[#26AA9B] hover:bg-[#209083] text-white py-2 px-4 rounded-lg transition flex items-center justify-center gap-2 text-xs font-bold shadow-sm">
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
        <h3 class="text-xl font-bold text-[#232D4B]">Bandeja limpia</h3>
        <p class="text-gray-500">No hay solicitudes de corrección pendientes.</p>
    </div>

    <div v-if="mostrarModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
            <div class="bg-[#26AA9B] px-6 py-4 flex justify-between items-center">
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
                    <div class="flex items-center gap-3">
                        <input type="number" step="0.5" min="0" max="24" v-model="horasEditadas" 
                               class="input-std text-center text-lg font-bold w-32" />
                        <span class="text-sm text-gray-500">Horas</span>
                    </div>
                </div>
            </div>
            <div class="p-4 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
                <button @click="cerrarModal" class="btn-secondary">Cancelar</button>
                <button @click="guardarCorreccion" class="bg-[#26AA9B] hover:bg-[#209083] text-white px-4 py-2 rounded-lg font-bold text-sm transition flex items-center gap-2">
                    <Save class="w-4 h-4"/> Guardar Cambios
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

<style scoped>
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type=number] {
  -moz-appearance: textfield;
}
</style>
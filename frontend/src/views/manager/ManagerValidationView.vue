<script setup>
import { ref } from 'vue'
import { 
    AlertOctagon, Check, X, FileEdit, MessageSquare, Calendar, Clock, Save,
    CheckCircle2, AlertCircle, Trash2, AlertTriangle
} from 'lucide-vue-next'

const solicitudes = ref([
    { 
        id: 1, 
        usuario: 'Mario León', 
        avatar: 'ML', 
        fecha: '2026-02-02', 
        proyecto: 'Migración Cloud', 
        cliente: 'Banco Santander',
        horasActuales: 8, 
        motivo: 'Me equivoqué al imputar. Puse 8 horas pero estuve 4 en el médico. Deberían ser 4h.',
        estado: 'pendiente'
    },
    { 
        id: 2, 
        usuario: 'Ana Ruiz', 
        avatar: 'AR', 
        fecha: '2026-01-28', 
        proyecto: 'Inditex TPV', 
        cliente: 'Inditex',
        horasActuales: 0, 
        motivo: 'Se me olvidó imputar este día y el mes ya está cerrado. ¿Podéis ponerme 8h?',
        estado: 'pendiente'
    }
])

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

const confirmState = ref({ show: false, title: '', message: '', type: 'neutral', action: null, inputMode: false, inputValue: '' })

const solicitarConfirmacion = (title, message, type, callback, inputMode = false) => {
    confirmState.value = { show: true, title, message, type, action: callback, inputMode, inputValue: '' }
}

const ejecutarConfirmacion = () => {
    if (confirmState.value.action) confirmState.value.action(confirmState.value.inputValue)
    confirmState.value.show = false
}

const solicitudSeleccionada = ref(null)
const horasEditadas = ref(0)
const mostrarModal = ref(false)

const abrirEditor = (solicitud) => {
    solicitudSeleccionada.value = solicitud
    horasEditadas.value = solicitud.horasActuales
    mostrarModal.value = true
}

const cerrarModal = () => {
    mostrarModal.value = false
    solicitudSeleccionada.value = null
}

const guardarCorreccion = () => {
    solicitudes.value = solicitudes.value.filter(s => s.id !== solicitudSeleccionada.value.id)
    cerrarModal()
    showToast(`Corrección aplicada correctamente`, 'success')
}

const rechazarSolicitud = (id) => {
    solicitarConfirmacion(
        'Rechazar Solicitud',
        'Por favor, indica el motivo del rechazo para notificar al usuario:',
        'danger',
        (motivo) => {
            if (motivo) {
                solicitudes.value = solicitudes.value.filter(s => s.id !== id)
                showToast("Solicitud rechazada y notificada.", "success")
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

    <div v-if="solicitudes.length > 0" class="grid gap-4">
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
                <div class="space-y-1">
                    <div class="flex items-center gap-2 text-xs text-gray-500">
                        <Calendar class="w-3.5 h-3.5" />
                        <span class="font-bold text-dark">{{ solicitud.fecha }}</span>
                    </div>
                    <div class="flex items-center gap-2 text-xs text-gray-500">
                        <Clock class="w-3.5 h-3.5" />
                        <span>Imputado actual: <b class="text-dark">{{ solicitud.horasActuales }}h</b></span>
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
                    <p><span class="font-bold text-gray-500 w--20 inline-block">Usuario:</span> {{ solicitudSeleccionada.usuario }}</p>
                    <p><span class="font-bold text-gray-500 w-20 inline-block">Proyecto:</span> {{ solicitudSeleccionada.proyecto }}</p>
                    <p><span class="font-bold text-gray-500 w-20 inline-block">Fecha:</span> {{ solicitudSeleccionada.fecha }}</p>
                </div>

                <div>
                    <label class="label-std">Horas Correctas (Sobrescribir)</label>
                    <div class="flex items-center gap-3">
                        <input type="number" step="0.5" min="0" max="24" v-model="horasEditadas" 
                               class="input-std text-center text-lg font-bold w-32" />
                        <span class="text-sm text-gray-500">Horas</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-2">
                        Al guardar, se actualizará el registro del usuario y se marcará la solicitud como resuelta.
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

    <div v-if="confirmState.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
        <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
            <div class="flex flex-col items-center text-center gap-3">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2"
                     :class="confirmState.type === 'danger' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'">
                    <component :is="confirmState.type === 'danger' ? Trash2 : AlertTriangle" class="w-6 h-6" />
                </div>
                <h3 class="text-lg font-bold text-slate-900">{{ confirmState.title }}</h3>
                <p class="text-sm text-slate-500 leading-relaxed">{{ confirmState.message }}</p>
                
                <div v-if="confirmState.inputMode" class="w-full mt-2">
                    <input v-model="confirmState.inputValue" type="text" placeholder="Motivo..." class="input-std w-full" autofocus>
                </div>

                <div class="flex gap-3 w-full mt-4">
                    <button @click="confirmState.show = false" class="btn-secondary flex-1 justify-center">Cancelar</button>
                    <button @click="ejecutarConfirmacion" 
                            class="flex-1 justify-center btn-primary"
                            :class="confirmState.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : 'bg-amber-600 hover:bg-amber-700'">
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
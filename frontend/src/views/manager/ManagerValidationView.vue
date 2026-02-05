<script setup>
import { ref } from 'vue'
import { 
    AlertOctagon, Check, X, FileEdit, MessageSquare, Calendar, Clock, Save 
} from 'lucide-vue-next'

// --- Solicitudes pendientes ---
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

// --- LÓGICA DE EDICIÓN ---
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
    // AQUÍ IRÍA LA LLAMADA AL BACKEND PARA ACTUALIZAR EL REGISTRO
    alert(`✅ Corrección Guardada:\nUsuario: ${solicitudSeleccionada.value.usuario}\nFecha: ${solicitudSeleccionada.value.fecha}\nNuevas Horas: ${horasEditadas.value}`)
    
    // Eliminamos la solicitud de la lista porque ya está resuelta
    solicitudes.value = solicitudes.value.filter(s => s.id !== solicitudSeleccionada.value.id)
    cerrarModal()
}

const rechazarSolicitud = (id) => {
    const motivoRechazo = prompt("Escribe el motivo del rechazo para el usuario:")
    if (motivoRechazo) {
        solicitudes.value = solicitudes.value.filter(s => s.id !== id)
        alert("❌ Solicitud rechazada. Se ha notificado al usuario.")
    }
}
</script>

<template>
  <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto">
    
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
                    <p><span class="font-bold text-gray-500 w-20 inline-block">Usuario:</span> {{ solicitudSeleccionada.usuario }}</p>
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

  </div>
</template>
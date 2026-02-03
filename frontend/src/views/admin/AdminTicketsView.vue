<script setup>
import { ref, computed } from 'vue'
import { Ticket, CheckCircle, Trash2, AlertCircle } from 'lucide-vue-next'
// Asegúrate de que esta ruta al store sea correcta según tu estructura
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()
const tickets = computed(() => store.getTickets())

const filtroEstado = ref('todos') // todos, pendiente, resuelto

const ticketsFiltrados = computed(() => {
    if (filtroEstado.value === 'todos') return tickets.value
    return tickets.value.filter(t => t.estado === filtroEstado.value)
})

const resolver = (id) => {
    if (confirm('¿Marcar incidencia como resuelta?')) store.resolveTicket(id)
}

const eliminar = (id) => {
    if (confirm('¿Eliminar este ticket del historial?')) store.deleteTicket(id)
}

const getTipoColor = (tipo) => {
    switch (tipo) {
        case 'Bug': return 'text-red-600 bg-red-50 border-red-100'
        case 'Acceso': return 'text-amber-600 bg-amber-50 border-amber-100'
        default: return 'text-blue-600 bg-blue-50 border-blue-100'
    }
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto">

        <div class="flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-[#232D4B] flex items-center gap-2">
                    <Ticket class="w-6 h-6 text-[#26AA9B]" /> Gestión de Incidencias
                </h1>
                <p class="text-sm text-gray-500 mt-1">Atiende los reportes y problemas enviados por los usuarios.</p>
            </div>

            <div class="flex bg-white p-1 rounded-lg border border-gray-200 shadow-sm">
                <button @click="filtroEstado = 'todos'"
                    :class="filtroEstado === 'todos' ? 'bg-gray-100 text-slate-800 font-bold' : 'text-gray-500'"
                    class="px-4 py-1.5 rounded-md text-sm transition">Todos</button>
                <button @click="filtroEstado = 'pendiente'"
                    :class="filtroEstado === 'pendiente' ? 'bg-amber-50 text-amber-700 font-bold' : 'text-gray-500'"
                    class="px-4 py-1.5 rounded-md text-sm transition flex items-center gap-1">
                    <AlertCircle class="w-3 h-3" /> Pendientes
                </button>
                <button @click="filtroEstado = 'resuelto'"
                    :class="filtroEstado === 'resuelto' ? 'bg-emerald-50 text-emerald-700 font-bold' : 'text-gray-500'"
                    class="px-4 py-1.5 rounded-md text-sm transition flex items-center gap-1">
                    <CheckCircle class="w-3 h-3" /> Resueltos
                </button>
            </div>
        </div>

        <div class="grid grid-cols-1 gap-4">
            <div v-for="ticket in ticketsFiltrados" :key="ticket.id"
                class="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col md:flex-row gap-4 justify-between items-start md:items-center transition hover:shadow-md"
                :class="{ 'opacity-60': ticket.estado === 'resuelto' }">

                <div class="flex gap-4 items-start">
                    <div class="mt-1">
                        <AlertCircle v-if="ticket.estado === 'pendiente'"
                            class="w-6 h-6 text-amber-500 animate-pulse" />
                        <CheckCircle v-else class="w-6 h-6 text-emerald-500" />
                    </div>

                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <span class="px-2 py-0.5 text-[10px] uppercase font-black tracking-wider rounded border"
                                :class="getTipoColor(ticket.tipo)">{{ ticket.tipo }}</span>
                            <span class="text-xs text-gray-400 font-mono">{{ ticket.fecha }}</span>
                            <span class="text-xs font-bold text-slate-700">• {{ ticket.usuario }}</span>
                        </div>
                        <h3 class="font-bold text-lg text-[#232D4B]">{{ ticket.asunto }}</h3>
                        <p class="text-sm text-gray-600 mt-1 max-w-2xl">{{ ticket.descripcion }}</p>
                    </div>
                </div>

                <div class="flex items-center gap-2 pl-10 md:pl-0">
                    <button v-if="ticket.estado === 'pendiente'" @click="resolver(ticket.id)"
                        class="px-4 py-2 bg-[#26AA9B] hover:bg-[#1f8c7f] text-white text-sm font-bold rounded-lg shadow-sm flex items-center gap-2 transition">
                        <CheckCircle class="w-4 h-4" /> Resolver
                    </button>
                    <div v-else
                        class="px-4 py-2 bg-gray-100 text-gray-500 text-sm font-bold rounded-lg flex items-center gap-2 cursor-default">
                        <CheckCircle class="w-4 h-4" /> Cerrado
                    </div>

                    <button @click="eliminar(ticket.id)"
                        class="p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition"
                        title="Eliminar ticket">
                        <Trash2 class="w-4 h-4" />
                    </button>
                </div>
            </div>

            <div v-if="ticketsFiltrados.length === 0" class="text-center py-12">
                <Ticket class="w-12 h-12 text-gray-200 mx-auto mb-2" />
                <p class="text-gray-400">No hay tickets en esta categoría.</p>
            </div>
        </div>
    </div>
</template>
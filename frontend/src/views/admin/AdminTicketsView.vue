<script setup>
import { ref, computed } from 'vue'
import { Ticket, CheckCircle, Trash2, AlertCircle } from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()
const tickets = computed(() => store.getTickets())

const filtroEstado = ref('todos') // todos, pendiente, resuelto

const ticketsFiltrados = computed(() => {
    if (filtroEstado.value === 'todos') return tickets.value
    return tickets.value.filter(t => t.estado === filtroEstado.value)
})

const resolver = (id) => {
    if(confirm('¿Marcar incidencia como resuelta?')) store.resolveTicket(id)
}

const eliminar = (id) => {
    if(confirm('¿Eliminar este ticket del historial?')) store.deleteTicket(id)
}

const getTipoColor = (tipo) => {
    switch(tipo) {
        case 'Bug': return 'text-red-600 bg-red-50 border-red-100'
        case 'Acceso': return 'text-amber-600 bg-amber-50 border-amber-100'
        default: return 'text-blue-600 bg-blue-50 border-blue-100'
    }
}
</script>

<template>
  <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto">
    
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <h1 class="h1-title flex items-center gap-2">
                <Ticket class="w-6 h-6 text-primary" /> Gestión de Incidencias
            </h1>
            <p class="subtitle">Atiende los reportes y problemas de los usuarios.</p>
        </div>
        
        <div class="flex bg-white p-1 rounded-lg border border-gray-200 shadow-sm">
            <button @click="filtroEstado = 'todos'" 
                    class="px-4 py-1.5 rounded-md text-sm transition font-medium"
                    :class="filtroEstado === 'todos' ? 'bg-gray-100 text-dark font-bold' : 'text-gray-500 hover:text-dark'">
                Todos
            </button>
            <button @click="filtroEstado = 'pendiente'" 
                    class="px-4 py-1.5 rounded-md text-sm transition font-medium flex items-center gap-1"
                    :class="filtroEstado === 'pendiente' ? 'bg-amber-50 text-amber-700 font-bold' : 'text-gray-500 hover:text-amber-600'">
                <AlertCircle class="w-3 h-3"/> Pendientes
            </button>
            <button @click="filtroEstado = 'resuelto'" 
                    class="px-4 py-1.5 rounded-md text-sm transition font-medium flex items-center gap-1"
                    :class="filtroEstado === 'resuelto' ? 'bg-emerald-50 text-emerald-700 font-bold' : 'text-gray-500 hover:text-emerald-600'">
                <CheckCircle class="w-3 h-3"/> Resueltos
            </button>
        </div>
    </div>

    <div class="grid grid-cols-1 gap-4">
        <div v-for="ticket in ticketsFiltrados" :key="ticket.id" 
             class="card flex flex-col md:flex-row gap-4 justify-between items-start md:items-center transition hover:shadow-md"
             :class="{'opacity-60': ticket.estado === 'resuelto'}">
            
            <div class="flex gap-4 items-start">
                <div class="mt-1">
                    <AlertCircle v-if="ticket.estado === 'pendiente'" class="w-6 h-6 text-amber-500 animate-pulse" />
                    <CheckCircle v-else class="w-6 h-6 text-emerald-500" />
                </div>
                
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="badge" :class="getTipoColor(ticket.tipo)">{{ ticket.tipo }}</span>
                        <span class="text-xs text-gray-400 font-mono">{{ ticket.fecha }}</span>
                        <span class="text-xs font-bold text-dark">• {{ ticket.usuario }}</span>
                    </div>
                    <h3 class="font-bold text-lg text-dark">{{ ticket.asunto }}</h3>
                    <p class="text-sm text-gray-600 mt-1 max-w-2xl">{{ ticket.descripcion }}</p>
                </div>
            </div>

            <div class="flex items-center gap-2 pl-10 md:pl-0 w-full md:w-auto justify-end">
                <button v-if="ticket.estado === 'pendiente'" @click="resolver(ticket.id)" class="btn-primary">
                    <CheckCircle class="w-4 h-4" /> Resolver
                </button>
                <div v-else class="px-4 py-2 bg-gray-100 text-gray-500 text-sm font-bold rounded-lg flex items-center gap-2 cursor-default">
                    <CheckCircle class="w-4 h-4" /> Cerrado
                </div>
                
                <button @click="eliminar(ticket.id)" class="btn-ghost text-gray-300 hover:text-red-500 hover:bg-red-50" title="Eliminar ticket">
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
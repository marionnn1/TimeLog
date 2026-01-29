<script setup>
import { ref, computed } from 'vue'
import {
    Briefcase,
    Search,
    Plus,
    Filter,
    MoreHorizontal,
    FolderOpen,
    Clock,
    CheckCircle2,
    XCircle
} from 'lucide-vue-next'

// --- DATOS MOCK (Simulando lo que vendrá de BD) ---
const proyectos = ref([
    { id: 1, nombre: 'Migración Cloud Azure', cliente: 'Banco Santander', codigo: 'PRJ-SAN-001', tipo: 'Proyecto', estado: true, jp: 'Ana García' },
    { id: 2, nombre: 'Mantenimiento Legacy', cliente: 'Mapfre', codigo: 'SRV-MAP-023', tipo: 'Servicio', estado: true, jp: 'Carlos Ruiz' },
    { id: 3, nombre: 'Despliegue TPVs', cliente: 'Inditex', codigo: 'PRJ-IND-104', tipo: 'Proyecto', estado: true, jp: 'Ana García' },
    { id: 4, nombre: 'Auditoría Seguridad', cliente: 'BBVA', codigo: 'PRJ-BBV-009', tipo: 'Proyecto', estado: false, jp: 'Elena Nito' },
    { id: 5, nombre: 'Soporte L3', cliente: 'Interno', codigo: 'SRV-INT-001', tipo: 'Servicio', estado: true, jp: 'Admin' },
    { id: 6, nombre: 'API Gateway', cliente: 'CaixaBank', codigo: 'PRJ-CAI-55', tipo: 'Proyecto', estado: true, jp: 'Carlos Ruiz' },
])

// --- FILTROS Y BÚSQUEDA ---
const busqueda = ref('')
const filtroEstado = ref('todos') // 'todos', 'activos', 'inactivos'

const proyectosFiltrados = computed(() => {
    return proyectos.value.filter(p => {
        // Filtro por texto (Nombre, Cliente o Código)
        const textoMatch =
            p.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) ||
            p.cliente.toLowerCase().includes(busqueda.value.toLowerCase()) ||
            p.codigo.toLowerCase().includes(busqueda.value.toLowerCase())

        // Filtro por estado
        const estadoMatch =
            filtroEstado.value === 'todos' ? true :
            filtroEstado.value === 'activos' ? p.estado :
            !p.estado

        return textoMatch && estadoMatch
    })
})

// Métodos auxiliares de estilo
const getTipoBadgeColor = (tipo) => {
    return tipo === 'Proyecto'
        ? 'bg-blue-50 text-blue-700 border-blue-100'
        : 'bg-purple-50 text-purple-700 border-purple-100'
}
</script>

<template>
    <div class="h-full flex flex-col font-sans">

        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center gap-4">
                <h1 class="text-3xl font-bold flex items-center gap-2" style="color: #232D4B;">
                    <Briefcase class="w-8 h-8 opacity-80" />
                    Proyectos
                    <span class="text-sm font-normal px-3 py-1 rounded-full bg-gray-100 text-gray-500 ml-2">
                        {{ proyectos.length }} Total
                    </span>
                </h1>
            </div>

            <button
                class="text-white px-5 py-2.5 rounded-lg shadow-md hover:shadow-lg transition transform hover:-translate-y-0.5 flex items-center gap-2 text-sm font-bold tracking-wide"
                style="background-color: #26AA9B;">
                <Plus class="w-5 h-5" />
                NUEVO PROYECTO
            </button>
        </div>

        <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6 flex gap-4 items-center">
            <div class="relative flex-1">
                <Search class="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input v-model="busqueda" type="text" placeholder="Buscar por cliente, nombre o código..."
                    class="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-300 transition text-gray-700 placeholder-gray-400" />
            </div>

            <div class="flex items-center bg-gray-50 rounded-lg p-1 border border-gray-200">
                <button @click="filtroEstado = 'todos'"
                    class="px-3 py-1.5 rounded-md text-sm font-medium transition"
                    :class="filtroEstado === 'todos' ? 'bg-white shadow-sm text-gray-800' : 'text-gray-500 hover:text-gray-700'">
                    Todos
                </button>
                <button @click="filtroEstado = 'activos'"
                    class="px-3 py-1.5 rounded-md text-sm font-medium transition"
                    :class="filtroEstado === 'activos' ? 'bg-white shadow-sm text-emerald-700' : 'text-gray-500 hover:text-gray-700'">
                    Activos
                </button>
                <button @click="filtroEstado = 'inactivos'"
                    class="px-3 py-1.5 rounded-md text-sm font-medium transition"
                    :class="filtroEstado === 'inactivos' ? 'bg-white shadow-sm text-red-600' : 'text-gray-500 hover:text-gray-700'">
                    Cerrados
                </button>
            </div>
        </div>

        <div v-if="proyectosFiltrados.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 overflow-y-auto pb-4">
            
            <div v-for="proyecto in proyectosFiltrados" :key="proyecto.id"
                class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition group relative overflow-hidden">
                
                <div class="absolute left-0 top-0 bottom-0 w-1" 
                     :class="proyecto.estado ? 'bg-[#26AA9B]' : 'bg-gray-300'"></div>

                <div class="flex justify-between items-start mb-3 pl-2">
                    <div>
                        <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">
                            {{ proyecto.cliente }}
                        </p>
                        <h3 class="text-lg font-bold text-[#232D4B] leading-tight">
                            {{ proyecto.nombre }}
                        </h3>
                    </div>
                    <button class="text-gray-400 hover:text-[#232D4B] p-1 rounded-md hover:bg-gray-50 transition">
                        <MoreHorizontal class="w-5 h-5" />
                    </button>
                </div>

                <div class="flex items-center gap-2 mb-4 pl-2">
                    <span class="text-xs px-2 py-1 rounded border font-medium flex items-center gap-1"
                        :class="getTipoBadgeColor(proyecto.tipo)">
                        <component :is="proyecto.tipo === 'Proyecto' ? FolderOpen : Clock" class="w-3 h-3" />
                        {{ proyecto.tipo }}
                    </span>
                    <span class="text-xs px-2 py-1 rounded border font-medium flex items-center gap-1"
                        :class="proyecto.estado ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-gray-100 text-gray-500 border-gray-200'">
                        <component :is="proyecto.estado ? CheckCircle2 : XCircle" class="w-3 h-3" />
                        {{ proyecto.estado ? 'Activo' : 'Cerrado' }}
                    </span>
                </div>

                <div class="border-t border-gray-100 pt-3 mt-2 flex justify-between items-center pl-2">
                    <div class="text-xs text-gray-500">
                        <span class="block text-gray-400 text-[10px] uppercase">Código</span>
                        <span class="font-mono">{{ proyecto.codigo }}</span>
                    </div>
                    <div class="text-xs text-right">
                        <span class="block text-gray-400 text-[10px] uppercase">Responsable</span>
                        <span class="font-medium text-gray-700">{{ proyecto.jp }}</span>
                    </div>
                </div>
            </div>

        </div>

        <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-400 opacity-60">
            <Filter class="w-16 h-16 mb-4 text-gray-300" />
            <p class="text-lg font-medium">No se encontraron proyectos</p>
            <p class="text-sm">Prueba con otros términos de búsqueda</p>
        </div>

    </div>
</template>
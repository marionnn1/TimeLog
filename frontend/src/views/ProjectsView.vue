<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
    Briefcase, Search, Plus, Filter, MoreHorizontal, FolderOpen, Clock,
    CheckCircle2, XCircle, UserPlus, Users, X, Check, Trash2
} from 'lucide-vue-next'

// --- DATOS MOCK PROYECTOS ---
const proyectos = ref([
    { 
        id: 1, nombre: 'Migración Cloud Azure', cliente: 'Banco Santander', codigo: 'PRJ-SAN-001', tipo: 'Proyecto', estado: true, jp: 'Ana García',
        equipo: [
            { nombre: 'Mario León', rol: 'Dev' },
            { nombre: 'Laura G.', rol: 'QA' }
        ]
    },
    { 
        id: 2, nombre: 'Mantenimiento Legacy', cliente: 'Mapfre', codigo: 'SRV-MAP-023', tipo: 'Servicio', estado: true, jp: 'Carlos Ruiz',
        equipo: [
            { nombre: 'Pedro Sola', rol: 'Junior' }
        ]
    },
    { 
        id: 3, nombre: 'Despliegue TPVs', cliente: 'Inditex', codigo: 'PRJ-IND-104', tipo: 'Proyecto', estado: true, jp: 'Ana García',
        equipo: [] // Sin equipo
    },
    { 
        id: 4, nombre: 'Auditoría Seguridad', cliente: 'BBVA', codigo: 'PRJ-BBV-009', tipo: 'Proyecto', estado: false, jp: 'Elena Nito',
        equipo: [
            { nombre: 'Mario León', rol: 'Dev' },
            { nombre: 'Ana Ruiz', rol: 'Security' },
            { nombre: 'Carlos M.', rol: 'Manager' }
        ]
    },
    { 
        id: 5, nombre: 'Soporte L3', cliente: 'Interno', codigo: 'SRV-INT-001', tipo: 'Servicio', estado: true, jp: 'Admin',
        equipo: [
            { nombre: 'Pedro Sola', rol: 'Junior' }
        ]
    },
    { 
        id: 6, nombre: 'API Gateway', cliente: 'CaixaBank', codigo: 'PRJ-CAI-55', tipo: 'Proyecto', estado: true, jp: 'Carlos Ruiz',
        equipo: []
    },
])

// --- DATOS MOCK USUARIOS ---
const usuariosDisponibles = [
    { id: 1, nombre: 'Mario León', rol: 'Dev' },
    { id: 2, nombre: 'Ana Ruiz', rol: 'QA' },
    { id: 3, nombre: 'Pedro Sola', rol: 'Junior' },
    { id: 4, nombre: 'Laura Gómez', rol: 'Manager' },
]

// --- ESTADOS ---
const menuAbiertoId = ref(null)
const mostrarModalAsignar = ref(false)
const asignacionData = ref({ proyectoId: null, nombreProyecto: '', usuarioId: '' })
const busqueda = ref('')
const filtroEstado = ref('todos')

// --- LÓGICA FILTROS ---
const proyectosFiltrados = computed(() => {
    return proyectos.value.filter(p => {
        const textoMatch =
            p.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) ||
            p.cliente.toLowerCase().includes(busqueda.value.toLowerCase()) ||
            p.codigo.toLowerCase().includes(busqueda.value.toLowerCase())

        const estadoMatch =
            filtroEstado.value === 'todos' ? true :
            filtroEstado.value === 'activos' ? p.estado :
            !p.estado

        return textoMatch && estadoMatch
    })
})

const getTipoBadgeColor = (tipo) => {
    return tipo === 'Proyecto'
        ? 'bg-blue-50 text-blue-700 border-blue-100'
        : 'bg-purple-50 text-purple-700 border-purple-100'
}

// --- MENÚS ---
const toggleMenu = (id) => {
    menuAbiertoId.value = menuAbiertoId.value === id ? null : id
}

const clickOutside = (e) => {
    if (!e.target.closest('.menu-trigger')) {
        menuAbiertoId.value = null
    }
}
onMounted(() => document.addEventListener('click', clickOutside))
onUnmounted(() => document.removeEventListener('click', clickOutside))

// --- ASIGNACIÓN ---
const abrirModalAsignacion = (proyecto) => {
    asignacionData.value = {
        proyectoId: proyecto.id,
        nombreProyecto: proyecto.nombre,
        usuarioId: ''
    }
    menuAbiertoId.value = null
    mostrarModalAsignar.value = true
}

const confirmarAsignacion = () => {
    if (!asignacionData.value.usuarioId) return alert('Por favor, selecciona un usuario.')
    
    const usuarioObj = usuariosDisponibles.find(u => u.id === asignacionData.value.usuarioId)
    const proyectoTarget = proyectos.value.find(p => p.id === asignacionData.value.proyectoId)
    
    if(proyectoTarget && usuarioObj) {
        if(!proyectoTarget.equipo.find(u => u.nombre === usuarioObj.nombre)){
             proyectoTarget.equipo.push({ nombre: usuarioObj.nombre, rol: usuarioObj.rol })
        }
    }

    alert(`✅ Usuario "${usuarioObj.nombre}" asignado correctamente.`)
    mostrarModalAsignar.value = false
}
</script>

<template>
    <div class="h-full flex flex-col font-sans">

        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center gap-4">
                <h1 class="text-3xl font-bold flex items-center gap-2 text-dark">
                    <Briefcase class="w-8 h-8 opacity-80" />
                    Proyectos
                    <span class="text-sm font-normal px-3 py-1 rounded-full bg-gray-100 text-gray-500 ml-2">
                        {{ proyectos.length }} Total
                    </span>
                </h1>
            </div>

            <button class="btn-primary uppercase tracking-wide">
                <Plus class="w-5 h-5" />
                Nuevo Proyecto
            </button>
        </div>

        <div class="card mb-6 flex gap-4 items-center">
            <div class="relative flex-1">
                <Search class="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input v-model="busqueda" type="text" placeholder="Buscar por cliente, nombre o código..."
                    class="input-std pl-10" />
            </div>

            <div class="flex items-center bg-gray-50 rounded-lg p-1 border border-gray-200">
                <button @click="filtroEstado = 'todos'"
                    class="px-3 py-1.5 rounded-md text-sm font-medium transition"
                    :class="filtroEstado === 'todos' ? 'bg-white shadow-sm text-dark' : 'text-gray-500 hover:text-gray-700'">
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
                class="card p-0 hover:shadow-lg transition group relative overflow-visible flex flex-col">
                
                <div class="absolute left-0 top-0 bottom-0 w-1 rounded-l-lg z-10" 
                     :class="proyecto.estado ? 'bg-primary' : 'bg-gray-300'"></div>

                <div class="p-5 pb-2 pl-6 relative">
                    <div class="flex justify-between items-start mb-2">
                        <div>
                            <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
                                {{ proyecto.cliente }}
                            </p>
                            <h3 class="text-lg font-bold text-dark leading-tight line-clamp-1" :title="proyecto.nombre">
                                {{ proyecto.nombre }}
                            </h3>
                        </div>
                        
                        <div class="relative menu-trigger ml-2">
                            <button @click.stop="toggleMenu(proyecto.id)" 
                                    class="btn-ghost p-1 rounded-md hover:bg-gray-100 transition">
                                <MoreHorizontal class="w-5 h-5 text-gray-500" />
                            </button>

                            <div v-if="menuAbiertoId === proyecto.id" 
                                 class="absolute right-0 top-8 w-48 bg-white rounded-lg shadow-xl border border-gray-100 z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
                                <div class="py-1">
                                    <button @click="abrirModalAsignacion(proyecto)" 
                                            class="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 hover:text-primary flex items-center gap-2 transition font-medium">
                                        <UserPlus class="w-4 h-4" /> Asignar Usuario
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="flex flex-wrap items-center gap-2 mb-2">
                        <span class="badge flex items-center gap-1" :class="getTipoBadgeColor(proyecto.tipo)">
                            <component :is="proyecto.tipo === 'Proyecto' ? FolderOpen : Clock" class="w-3 h-3" />
                            {{ proyecto.tipo }}
                        </span>
                        <span class="badge flex items-center gap-1"
                            :class="proyecto.estado ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-gray-100 text-gray-500 border-gray-200'">
                            <component :is="proyecto.estado ? CheckCircle2 : XCircle" class="w-3 h-3" />
                            {{ proyecto.estado ? 'Activo' : 'Cerrado' }}
                        </span>
                    </div>
                    
                    <div class="text-xs text-gray-400 font-mono mb-2">
                        {{ proyecto.codigo }}
                    </div>
                </div>

                <div class="h-px bg-gray-100 mx-5"></div>

                <div class="p-5 pl-6 pt-3 bg-slate-50/50 flex-1 rounded-b-xl flex flex-col">
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3 flex justify-between items-center">
                        Equipo Asignado
                        <span class="bg-gray-200 text-gray-600 px-1.5 rounded text-[9px]">{{ proyecto.equipo.length }}</span>
                    </p>
                    
                    <div v-if="proyecto.equipo.length > 0" class="flex flex-col gap-1.5">
                        <div v-for="(user, idx) in proyecto.equipo" :key="idx" 
                             class="flex items-center justify-between p-2 rounded-lg bg-white border border-gray-100 hover:border-blue-200 hover:shadow-sm transition group/user cursor-default">
                            
                            <div class="flex items-center gap-3">
                                <div class="w-6 h-6 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-[9px] font-bold border border-slate-200 group-hover/user:bg-primary group-hover/user:text-white transition-colors group-hover/user:border-primary">
                                    {{ user.nombre.charAt(0) }}
                                </div>
                                <span class="text-xs font-bold text-dark group-hover/user:text-primary transition-colors">
                                    {{ user.nombre.split(' ')[0] }} {{ user.nombre.split(' ')[1]?.charAt(0) }}.
                                </span>
                            </div>
                            
                            <span class="text-[9px] uppercase font-bold text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded border border-gray-100 group-hover/user:bg-blue-50 group-hover/user:text-blue-600 group-hover/user:border-blue-100 transition-colors">
                                {{ user.rol }}
                            </span>
                        </div>
                    </div>

                    <div v-else class="text-xs text-gray-400 italic flex items-center gap-2 py-2 justify-center border border-dashed border-gray-200 rounded-lg">
                        <Users class="w-3 h-3 opacity-50"/> Sin equipo asignado
                    </div>
                </div>

            </div>

        </div>

        <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-400 opacity-60">
            <Filter class="w-16 h-16 mb-4 text-gray-300" />
            <p class="text-lg font-medium">No se encontraron proyectos</p>
            <p class="text-sm">Prueba con otros términos de búsqueda</p>
        </div>

        <div v-if="mostrarModalAsignar" class="fixed inset-0 bg-slate-900/40 flex items-center justify-center z-[100] p-4 backdrop-blur-sm">
            <div class="card w-full max-w-sm space-y-4 shadow-2xl animate-in zoom-in-95 duration-200">
                
                <div class="flex justify-between items-center border-b border-gray-100 pb-4 bg-slate-50 -m-6 mb-4 p-6 rounded-t-xl">
                    <div>
                        <h3 class="font-bold text-lg text-dark flex items-center gap-2">
                            <UserPlus class="w-5 h-5 text-primary"/> Asignar Recurso
                        </h3>
                        <p class="text-xs text-gray-500 mt-1">Proyecto: <b>{{ asignacionData.nombreProyecto }}</b></p>
                    </div>
                    <button @click="mostrarModalAsignar=false"><X class="w-5 h-5 text-gray-400 hover:text-red-500 transition"/></button>
                </div>
                
                <div class="mt-2">
                    <label class="label-std">Seleccionar Usuario</label>
                    <div class="relative">
                        <select v-model="asignacionData.usuarioId" class="input-std appearance-none bg-white">
                            <option value="" disabled selected>Elige un empleado...</option>
                            <option v-for="user in usuariosDisponibles" :key="user.id" :value="user.id">
                                {{ user.nombre }} ({{ user.rol }})
                            </option>
                        </select>
                        <div class="absolute right-3 top-3 pointer-events-none text-gray-400">
                            <Users class="w-4 h-4"/>
                        </div>
                    </div>
                    <p class="text-xs text-gray-400 mt-2">
                        El usuario podrá ver este proyecto en su desplegable de imputaciones.
                    </p>
                </div>

                <div class="flex gap-2 pt-4 border-t border-gray-100 mt-4">
                    <button @click="mostrarModalAsignar=false" class="btn-secondary flex-1">Cancelar</button>
                    <button @click="confirmarAsignacion" class="btn-primary flex-1">
                        <Check class="w-4 h-4 mr-1"/> Confirmar
                    </button>
                </div>
            </div>
        </div>

    </div>
</template>
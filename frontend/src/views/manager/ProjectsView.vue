<script setup>
import { ref, computed } from 'vue'
import {
    LayoutGrid, Search, Plus, Pencil, Trash2, X, Check,
    Briefcase, UserPlus, Tag, Hash, Save
} from 'lucide-vue-next'


const proyectos = ref([
    { 
        id: 1, nombre: 'Auditoría Backend', cliente: 'Banco Santander', idCliente: 'SAN-001', codigo: 'PRJ-SAN-001', tipo: 'Proyecto', estado: true, jp: 'Ana García',
        equipo: [] 
    },
    { 
        id: 2, nombre: 'Migración Cloud', cliente: 'Mapfre', idCliente: 'MAP-99', codigo: 'SRV-MAP-023', tipo: 'Servicio', estado: true, jp: 'Carlos Ruiz',
        equipo: [
            { nombre: 'Ana García', rol: 'Dev', iniciales: 'AG', color: 'bg-pink-100 text-pink-600' },
            { nombre: 'Carlos Ruiz', rol: 'QA', iniciales: 'CR', color: 'bg-blue-100 text-blue-600' },
        ]
    },
    { 
        id: 4, nombre: 'Auditoría Seguridad', cliente: 'BBVA', idCliente: 'BBVA-ES', codigo: 'PRJ-BBV-009', tipo: 'Proyecto', estado: false, jp: 'Elena Nito',
        equipo: [
            { nombre: 'Mario León', rol: 'Dev', iniciales: 'ML', color: 'bg-indigo-100 text-indigo-600' }
        ]
    },
])


const usuariosDisponibles = [
    { id: 1, nombre: 'Mario León', rol: 'Dev', iniciales: 'ML', color: 'bg-indigo-100 text-indigo-600' },
    { id: 2, nombre: 'Ana Ruiz', rol: 'QA', iniciales: 'AR', color: 'bg-rose-100 text-rose-600' },
    { id: 3, nombre: 'Pedro Sola', rol: 'Junior', iniciales: 'PS', color: 'bg-cyan-100 text-cyan-600' },
]

// --- ESTADOS ---
const mostrarModalAsignar = ref(false)
const mostrarModalProyecto = ref(false) 
const esEdicion = ref(false)

const asignacionData = ref({ proyectoId: null, nombreProyecto: '', usuarioId: '' })
const proyectoForm = ref({ id: null, nombre: '', cliente: '', idCliente: '', codigo: '', estado: true }) 

const busqueda = ref('')
const filtroEstado = ref('todos')

// --- LÓGICA FILTROS ---
const proyectosFiltrados = computed(() => {
    return proyectos.value.filter(p => {
        const textoMatch =
            p.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) ||
            p.cliente.toLowerCase().includes(busqueda.value.toLowerCase())
        
        const estadoMatch =
            filtroEstado.value === 'todos' ? true :
            filtroEstado.value === 'activos' ? p.estado :
            !p.estado

        return textoMatch && estadoMatch
    })
})

// --- GESTIÓN PROYECTOS ---

const abrirCrearProyecto = () => {
    esEdicion.value = false
    proyectoForm.value = { id: null, nombre: '', cliente: '', idCliente: '', codigo: '', estado: true }
    mostrarModalProyecto.value = true
}

const abrirEditarProyecto = (proy) => {
    esEdicion.value = true
    proyectoForm.value = { ...proy }
    mostrarModalProyecto.value = true
}

const guardarProyecto = () => {
    if (!proyectoForm.value.nombre || !proyectoForm.value.cliente) return alert("Nombre y Cliente son obligatorios")

    if (esEdicion.value) {
        const index = proyectos.value.findIndex(p => p.id === proyectoForm.value.id)
        if (index !== -1) {
            proyectos.value[index] = { 
                ...proyectos.value[index], 
                ...proyectoForm.value      
            }
        }
    } else {
        // CREAR
        const nuevoId = Date.now()
        proyectos.value.push({
            ...proyectoForm.value,
            id: nuevoId,
            codigo: `PRJ-${Math.floor(Math.random()*1000)}`, 
            equipo: [] 
        })
    }
    mostrarModalProyecto.value = false
}

const eliminarProyecto = (id) => {
    if(confirm('¿Seguro que quieres eliminar este proyecto?')) {
        proyectos.value = proyectos.value.filter(p => p.id !== id)
    }
}

// --- ASIGNACIÓN USUARIOS ---
const abrirModalAsignacion = (proyecto) => {
    asignacionData.value = { proyectoId: proyecto.id, nombreProyecto: proyecto.nombre, usuarioId: '' }
    mostrarModalAsignar.value = true
}

const confirmarAsignacion = () => {
    if (!asignacionData.value.usuarioId) return
    const usuarioObj = usuariosDisponibles.find(u => u.id === asignacionData.value.usuarioId)
    const proyectoTarget = proyectos.value.find(p => p.id === asignacionData.value.proyectoId)
    
    if(proyectoTarget && usuarioObj) {
        if(!proyectoTarget.equipo.find(u => u.nombre === usuarioObj.nombre)){
             proyectoTarget.equipo.push({ ...usuarioObj })
        }
    }
    mostrarModalAsignar.value = false
}
</script>

<template>
    <div class="h-full flex flex-col font-sans p-8 bg-slate-50 overflow-y-auto">

        <div class="flex justify-between items-center mb-8">
            <div class="flex items-center gap-4">
                <h1 class="text-3xl font-bold flex items-center gap-3 text-slate-800">
                    <LayoutGrid class="w-8 h-8 text-slate-400" />
                    Gestión Proyectos
                    <span class="text-sm font-bold px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-500 shadow-sm ml-2">
                        {{ proyectos.length }}
                    </span>
                </h1>
            </div>

            <button @click="abrirCrearProyecto" class="btn-primary flex items-center gap-2 shadow-lg shadow-emerald-500/20">
                <Plus class="w-5 h-5" />
                Nuevo Proyecto
            </button>
        </div>

        <div class="bg-white p-1 rounded-xl shadow-sm border border-slate-200 mb-8 flex gap-4 items-center">
            <div class="relative flex-1">
                <Search class="w-5 h-5 absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input v-model="busqueda" type="text" placeholder="Buscar por cliente, nombre..."
                    class="w-full pl-12 pr-4 py-3 bg-transparent text-sm focus:outline-none text-slate-600 placeholder:text-slate-400" />
            </div>
            
            <div class="h-6 w-px bg-slate-200 mx-2"></div>

            <div class="flex items-center pr-2 gap-1">
                <button @click="filtroEstado = 'todos'" class="px-4 py-2 rounded-lg text-sm font-medium transition"
                    :class="filtroEstado === 'todos' ? 'bg-slate-100 text-slate-900' : 'text-slate-500 hover:text-slate-700'">Todos</button>
                <button @click="filtroEstado = 'activos'" class="px-4 py-2 rounded-lg text-sm font-medium transition"
                    :class="filtroEstado === 'activos' ? 'bg-emerald-50 text-emerald-700' : 'text-slate-500 hover:text-slate-700'">Activos</button>
                <button @click="filtroEstado = 'inactivos'" class="px-4 py-2 rounded-lg text-sm font-medium transition"
                    :class="filtroEstado === 'inactivos' ? 'bg-red-50 text-red-700' : 'text-slate-500 hover:text-slate-700'">Cerrados</button>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-10">
            
            <div v-for="proy in proyectosFiltrados" :key="proy.id"
                class="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 group relative flex flex-col p-5 min-h-[320px]">
                
                <div class="flex justify-between items-start mb-4">
                    <div class="w-10 h-10 rounded-xl bg-[#E8F5F3] flex items-center justify-center text-[#26AA9B]">
                        <Briefcase class="w-5 h-5" stroke-width="2.5"/>
                    </div>

                    <div class="flex items-center gap-2">
                        <span class="px-3 py-1 rounded-md text-[11px] font-bold tracking-wide uppercase border transition-colors"
                            :class="proy.estado 
                                ? 'bg-emerald-50 text-emerald-600 border-emerald-200' 
                                : 'bg-slate-50 text-slate-500 border-slate-200'">
                            {{ proy.estado ? 'Activo' : 'Cerrado' }}
                        </span>

                        <button @click.stop="abrirEditarProyecto(proy)"
                            class="w-7 h-7 flex items-center justify-center rounded bg-white border border-slate-200 text-slate-400 hover:text-blue-600 hover:border-blue-200 transition-all shadow-sm"
                            title="Editar Proyecto">
                            <Pencil class="w-3.5 h-3.5" />
                        </button>

                        <button @click.stop="eliminarProyecto(proy.id)"
                            class="w-7 h-7 flex items-center justify-center rounded bg-white border border-slate-200 text-slate-400 hover:text-red-600 hover:border-red-200 transition-all shadow-sm"
                            title="Eliminar">
                            <Trash2 class="w-3.5 h-3.5" />
                        </button>
                    </div>
                </div>

                <div class="mb-5">
                    <h3 class="text-lg font-bold text-slate-800 leading-tight mb-1 truncate" :title="proy.nombre">
                        {{ proy.nombre }}
                    </h3>
                    <div class="flex flex-col gap-1">
                        <p class="text-sm text-slate-500 flex items-center gap-1.5 font-medium truncate">
                            <Tag class="w-3.5 h-3.5" /> {{ proy.cliente }}
                        </p>
                        <p v-if="proy.idCliente" class="text-xs text-slate-400 flex items-center gap-1.5 font-mono">
                            <Hash class="w-3 h-3" /> {{ proy.idCliente }}
                        </p>
                    </div>
                </div>

                <div class="h-px bg-slate-100 w-full mb-4"></div>

                <div class="flex flex-col flex-1 overflow-hidden">
                    <div class="flex justify-between items-center mb-3">
                        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                            Equipo Asignado
                        </span>
                        <button @click.stop="abrirModalAsignacion(proy)" class="text-slate-300 hover:text-emerald-600 transition" title="Añadir miembro">
                            <UserPlus class="w-4 h-4"/>
                        </button>
                    </div>

                    <div class="flex-1 overflow-y-auto pr-1 space-y-3 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
                        
                        <template v-if="proy.equipo.length > 0">
                            <div v-for="(user, index) in proy.equipo" :key="index" class="flex items-center gap-3 group/user">
                                <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
                                     :class="user.color || 'bg-slate-100 text-slate-500'">
                                    {{ user.iniciales }}
                                </div>
                                <span class="text-sm text-slate-600 font-medium group-hover/user:text-slate-900 transition-colors">
                                    {{ user.nombre }}
                                </span>
                            </div>
                        </template>

                        <div v-else class="h-full flex flex-col items-center justify-center text-slate-300 gap-2 min-h-[100px]">
                            <Users class="w-8 h-8 opacity-20" />
                            <span class="text-xs italic">Sin equipo asignado</span>
                        </div>

                    </div>
                </div>

            </div>
        </div>

        <div v-if="mostrarModalAsignar" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div class="bg-white w-full max-w-sm rounded-2xl shadow-2xl p-6 animate-in zoom-in-95">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-lg font-bold text-slate-800">Asignar a Proyecto</h3>
                        <p class="text-sm text-slate-500 truncate w-64">{{ asignacionData.nombreProyecto }}</p>
                    </div>
                    <button @click="mostrarModalAsignar=false" class="text-slate-400 hover:text-slate-600">
                        <X class="w-5 h-5"/>
                    </button>
                </div>

                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Empleado</label>
                        <select v-model="asignacionData.usuarioId" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                            <option value="" disabled>Seleccionar...</option>
                            <option v-for="u in usuariosDisponibles" :key="u.id" :value="u.id">{{ u.nombre }}</option>
                        </select>
                    </div>
                    <button @click="confirmarAsignacion" class="w-full btn-primary py-3 justify-center">
                        Confirmar Asignación
                    </button>
                </div>
            </div>
        </div>

        <div v-if="mostrarModalProyecto" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl p-6 animate-in zoom-in-95">
                <div class="flex justify-between items-start mb-6">
                    <div>
                        <h3 class="text-xl font-bold text-slate-800">
                            {{ esEdicion ? 'Editar Proyecto' : 'Nuevo Proyecto' }}
                        </h3>
                        <p class="text-sm text-slate-500">Completa la información del proyecto.</p>
                    </div>
                    <button @click="mostrarModalProyecto=false" class="text-slate-400 hover:text-slate-600">
                        <X class="w-6 h-6"/>
                    </button>
                </div>

                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Nombre Proyecto</label>
                        <input v-model="proyectoForm.nombre" type="text" placeholder="Ej: Migración Cloud" 
                               class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Cliente</label>
                            <input v-model="proyectoForm.cliente" type="text" placeholder="Ej: Santander" 
                                class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase mb-2">ID Cliente</label>
                            <input v-model="proyectoForm.idCliente" type="text" placeholder="Ej: CLI-001" 
                                class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                        </div>
                    </div>

                    <div>
                         <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Estado</label>
                         <div class="flex gap-2">
                            <button @click="proyectoForm.estado = true" 
                                    class="flex-1 py-2 rounded-lg text-sm font-bold border transition-colors"
                                    :class="proyectoForm.estado ? 'bg-emerald-50 border-emerald-500 text-emerald-700' : 'bg-white border-slate-200 text-slate-500'">
                                Activo
                            </button>
                            <button @click="proyectoForm.estado = false" 
                                    class="flex-1 py-2 rounded-lg text-sm font-bold border transition-colors"
                                    :class="!proyectoForm.estado ? 'bg-slate-100 border-slate-400 text-slate-700' : 'bg-white border-slate-200 text-slate-500'">
                                Cerrado
                            </button>
                         </div>
                    </div>

                    <div class="pt-2">
                        <button @click="guardarProyecto" class="w-full btn-primary py-3 justify-center flex items-center gap-2">
                            <Save class="w-4 h-4"/>
                            {{ esEdicion ? 'Guardar Cambios' : 'Crear Proyecto' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<style scoped>
.btn-primary {
    @apply bg-[#26AA9B] hover:bg-[#208f82] text-white px-5 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center gap-2;
}
</style>
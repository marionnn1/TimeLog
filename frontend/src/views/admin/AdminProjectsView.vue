<script setup>
import { ref, computed } from 'vue'
import { FolderPlus, Trash2, Tag, X, Briefcase, Users } from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()
const proyectos = computed(() => store.getProjects())

// --- DATOS FAKE (HARDCODEADOS) PARA VISUALIZACIÓN ---
const usuariosFake = [
    { id: 1, nombre: 'Ana García', iniciales: 'AG', color: 'bg-pink-100 text-pink-700' },
    { id: 2, nombre: 'Carlos Ruiz', iniciales: 'CR', color: 'bg-blue-100 text-blue-700' },
    { id: 3, nombre: 'Elena Nito', iniciales: 'EN', color: 'bg-purple-100 text-purple-700' },
    { id: 4, nombre: 'Javi M.', iniciales: 'JM', color: 'bg-emerald-100 text-emerald-700' },
    { id: 5, nombre: 'Laura P.', iniciales: 'LP', color: 'bg-orange-100 text-orange-700' },
    { id: 6, nombre: 'Mario L.', iniciales: 'ML', color: 'bg-indigo-100 text-indigo-700' },
]

// Función que "inventa" asignaciones según el ID del proyecto para que veas variedad
const getUsuariosProyecto = (proyectoId) => {
    if (proyectoId % 2 === 0) return usuariosFake // Devuelve los 6 (para probar el scroll)
    else if (proyectoId % 3 === 0) return [usuariosFake[0], usuariosFake[3]] // Solo 2
    return [] // Vacío
}

// --- LÓGICA DE PROYECTOS ---
const mostrarModal = ref(false)
const nuevoProyecto = ref({ nombre: '', cliente: '', estado: 'Activo' })

const guardarProyecto = () => {
    store.addProject(nuevoProyecto.value)
    mostrarModal.value = false
    nuevoProyecto.value = { nombre: '', cliente: '', estado: 'Activo' }
}

const eliminarProyecto = (id) => {
    if(confirm('¿Eliminar este proyecto?')) {
        store.deleteProject(id)
    }
}
</script>

<template>
  <div class="h-full p-6 bg-gray-50 flex flex-col gap-6 font-sans">
    
    <div class="flex justify-between items-center">
        <div>
            <h1 class="h1-title">Administrar Proyectos</h1>
            <p class="subtitle">Visión general de proyectos y equipos asignados.</p>
        </div>
        <button @click="mostrarModal = true" class="btn-primary">
            <FolderPlus class="w-4 h-4" /> Nuevo Proyecto
        </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="proy in proyectos" :key="proy.id" class="card group hover:border-primary hover:shadow-md transition relative flex flex-col min-h-[200px]">
            
            <div class="flex-shrink-0">
                <div class="flex justify-between items-start mb-3">
                    
                    <div class="bg-gray-100 p-2 rounded-lg text-slate-500 group-hover:bg-primary/10 group-hover:text-primary transition">
                        <Briefcase class="w-5 h-5"/>
                    </div>
                    
                    <div class="flex items-center gap-2">
                        <span class="badge" 
                              :class="proy.estado === 'Activo' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-gray-100 text-gray-500 border-gray-200'">
                            {{ proy.estado }}
                        </span>
                        
                        <button @click.stop="eliminarProyecto(proy.id)" 
                                class="text-gray-300 hover:text-red-500 transition opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-50" 
                                title="Eliminar proyecto">
                            <Trash2 class="w-4 h-4" />
                        </button>
                    </div>
                </div>
                
                <h3 class="font-bold text-lg text-dark mb-1 leading-tight">{{ proy.nombre }}</h3>
                <p class="text-sm text-gray-500 mb-4 flex items-center gap-1">
                    <Tag class="w-3 h-3"/> {{ proy.cliente }}
                </p>
            </div>

            <div class="mt-auto pt-3 border-t border-gray-100 flex flex-col flex-1 overflow-hidden">
                <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 flex-shrink-0">
                    <Users class="w-3 h-3"/> Equipo Asignado
                </div>
                
                <div class="flex-1 overflow-y-auto pr-1 space-y-1 scrollbar-thin scrollbar-thumb-gray-200 scrollbar-track-transparent max-h-[140px]">
                    <template v-if="getUsuariosProyecto(proy.id).length > 0">
                        <div v-for="user in getUsuariosProyecto(proy.id)" :key="user.id" 
                             class="flex items-center gap-2 p-1.5 rounded-md hover:bg-gray-50 transition-colors">
                            
                            <div class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold shadow-sm shrink-0"
                                 :class="user.color">
                                {{ user.iniciales }}
                            </div>
                            
                            <span class="text-xs font-medium text-slate-600 truncate">
                                {{ user.nombre }}
                            </span>
                        </div>
                    </template>
                    
                    <div v-else class="h-full flex flex-col items-center justify-center text-gray-300 italic text-xs py-4">
                        <Users class="w-8 h-8 opacity-20 mb-1" />
                        Sin equipo asignado
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div v-if="mostrarModal" class="fixed inset-0 bg-dark/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
        <div class="card w-full max-w-sm space-y-4 shadow-2xl">
            <div class="flex justify-between items-center border-b border-gray-100 pb-2">
                <h3 class="font-bold text-lg text-dark">Nuevo Proyecto</h3>
                <button @click="mostrarModal=false"><X class="w-5 h-5 text-gray-400 hover:text-red-500"/></button>
            </div>
            <div>
                <label class="label-std">Nombre Proyecto</label>
                <input v-model="nuevoProyecto.nombre" class="input-std" placeholder="Ej: Migración Cloud">
            </div>
            <div>
                <label class="label-std">Cliente</label>
                <input v-model="nuevoProyecto.cliente" class="input-std" placeholder="Ej: Banco Santander">
            </div>
            <div class="flex gap-2 pt-2">
                <button @click="mostrarModal=false" class="btn-secondary flex-1">Cancelar</button>
                <button @click="guardarProyecto" class="btn-primary flex-1">Crear</button>
            </div>
        </div>
    </div>
  </div>
</template>
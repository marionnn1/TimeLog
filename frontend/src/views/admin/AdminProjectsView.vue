<script setup>
import { ref, computed } from 'vue'
import { FolderPlus, Trash2, Tag, X, Briefcase } from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()
const proyectos = computed(() => store.getProjects())

const mostrarModal = ref(false)
const nuevoProyecto = ref({ nombre: '', cliente: '', estado: 'Activo' })

const guardarProyecto = () => {
    store.addProject(nuevoProyecto.value)
    mostrarModal.value = false
    nuevoProyecto.value = { nombre: '', cliente: '', estado: 'Activo' }
}

const eliminarProyecto = (id) => {
    if(confirm('¿Eliminar este proyecto y sus imputaciones asociadas?')) {
        store.deleteProject(id)
    }
}
</script>

<template>
  <div class="h-full p-6 bg-gray-50 flex flex-col gap-6 font-sans">
    
    <div class="flex justify-between items-center">
        <div>
            <h1 class="h1-title">Administrar Proyectos</h1>
            <p class="subtitle">Crea o cierra proyectos para imputación.</p>
        </div>
        <button @click="mostrarModal = true" class="btn-primary">
            <FolderPlus class="w-4 h-4" /> Nuevo Proyecto
        </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="proy in proyectos" :key="proy.id" class="card group hover:border-primary hover:shadow-md transition relative">
            
            <div class="flex justify-between items-start mb-3">
                <div class="bg-gray-100 p-2 rounded-lg text-slate-500 group-hover:bg-primary/10 group-hover:text-primary transition">
                    <Briefcase class="w-5 h-5"/>
                </div>
                <span class="badge" 
                      :class="proy.estado === 'Activo' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-gray-100 text-gray-500 border-gray-200'">
                    {{ proy.estado }}
                </span>
            </div>
            
            <h3 class="font-bold text-lg text-dark">{{ proy.nombre }}</h3>
            <p class="text-sm text-gray-500 mb-4 flex items-center gap-1">
                <Tag class="w-3 h-3"/> {{ proy.cliente }}
            </p>

            <button @click="eliminarProyecto(proy.id)" class="absolute bottom-4 right-4 text-gray-300 hover:text-red-500 transition opacity-0 group-hover:opacity-100">
                <Trash2 class="w-4 h-4" />
            </button>
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
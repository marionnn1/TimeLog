<script setup>
import { ref, computed } from 'vue'
import { FolderPlus, Pencil, Tag, X, Briefcase, Users, Check } from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()
const proyectos = computed(() => store.getProjects())

// --- DATOS DE USUARIOS DISPONIBLES (MOCK) ---
const usuariosFake = [
    { id: 1, nombre: 'Ana García', iniciales: 'AG', color: 'bg-pink-100 text-pink-700' },
    { id: 2, nombre: 'Carlos Ruiz', iniciales: 'CR', color: 'bg-blue-100 text-blue-700' },
    { id: 3, nombre: 'Elena Nito', iniciales: 'EN', color: 'bg-purple-100 text-purple-700' },
    { id: 4, nombre: 'Javi M.', iniciales: 'JM', color: 'bg-emerald-100 text-emerald-700' },
    { id: 5, nombre: 'Laura P.', iniciales: 'LP', color: 'bg-orange-100 text-orange-700' },
    { id: 6, nombre: 'Mario L.', iniciales: 'ML', color: 'bg-indigo-100 text-indigo-700' },
]

// Helper para visualización: Si el proyecto tiene equipo real (editado) lo usa, si no, usa el fake por ID
const getDisplayUsuarios = (proy) => {
    if (proy.equipo && proy.equipo.length > 0) return proy.equipo
    // Fallback a lógica fake antigua para demos
    if (proy.id % 2 === 0) return usuariosFake
    else if (proy.id % 3 === 0) return [usuariosFake[0], usuariosFake[3]]
    return []
}

// --- LÓGICA DE MODAL Y FORMULARIO ---
const mostrarModal = ref(false)
const esEdicion = ref(false) // Para saber si estamos creando o editando

// Modelo del formulario
const proyectoForm = ref({
    id: null,
    nombre: '',
    cliente: '',
    estado: 'Activo',
    equipo: []
})

// Abrir modal para NUEVO proyecto
const abrirModalCrear = () => {
    esEdicion.value = false
    proyectoForm.value = { id: Date.now(), nombre: '', cliente: '', estado: 'Activo', equipo: [] }
    mostrarModal.value = true
}

// Abrir modal para EDITAR proyecto
const abrirModalEditar = (proy) => {
    esEdicion.value = true
    // Copiamos los datos para no modificar directamente hasta guardar
    // Importante: Si no tiene equipo asignado, cargamos el fake inicial o vacío
    const equipoActual = proy.equipo || getDisplayUsuarios(proy)

    proyectoForm.value = {
        ...proy,
        equipo: [...equipoActual] // Clonamos el array para no mutar por referencia
    }
    mostrarModal.value = true
}

// Gestionar selección de usuarios en el modal
const toggleUsuarioEnForm = (usuario) => {
    const index = proyectoForm.value.equipo.findIndex(u => u.id === usuario.id)
    if (index >= 0) {
        proyectoForm.value.equipo.splice(index, 1) 
    } else {
        proyectoForm.value.equipo.push(usuario) 
    }
}

const estaSeleccionado = (userId) => {
    return proyectoForm.value.equipo.some(u => u.id === userId)
}

// Guardar (Crear o Actualizar)
const guardarProyecto = () => {
    if (esEdicion.value) {
        // Lógica de actualización (Simulada si no tienes updateProject en el store)
        // store.updateProject(proyectoForm.value) <--- Lo ideal
        // Como parche, borramos y creamos (o actualizamos localmente si el store lo permite)
        store.deleteProject(proyectoForm.value.id)
        store.addProject(proyectoForm.value)
    } else {
        store.addProject(proyectoForm.value)
    }
    mostrarModal.value = false
}
</script>

<template>
    <div class="h-full p-6 bg-gray-50 flex flex-col gap-6 font-sans">

        <div class="flex justify-between items-center">
            <div>
                <h1 class="h1-title">Administrar Proyectos</h1>
                <p class="subtitle">Visión general y gestión de equipos.</p>
            </div>
            <button @click="abrirModalCrear" class="btn-primary">
                <FolderPlus class="w-4 h-4" /> Nuevo Proyecto
            </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="proy in proyectos" :key="proy.id"
                class="card group hover:border-primary hover:shadow-md transition relative flex flex-col min-h-[200px]">

                <div class="flex-shrink-0">
                    <div class="flex justify-between items-start mb-3">

                        <div
                            class="bg-gray-100 p-2 rounded-lg text-slate-500 group-hover:bg-primary/10 group-hover:text-primary transition">
                            <Briefcase class="w-5 h-5" />
                        </div>

                        <div class="flex items-center gap-2">
                            <span class="badge"
                                :class="proy.estado === 'Activo' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-gray-100 text-gray-500 border-gray-200'">
                                {{ proy.estado }}
                            </span>

                            <button @click.stop="abrirModalEditar(proy)"
                                class="text-gray-300 hover:text-blue-500 transition opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-blue-50"
                                title="Editar proyecto y equipo">
                                <Pencil class="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <h3 class="font-bold text-lg text-dark mb-1 leading-tight">{{ proy.nombre }}</h3>
                    <p class="text-sm text-gray-500 mb-4 flex items-center gap-1">
                        <Tag class="w-3 h-3" /> {{ proy.cliente }}
                    </p>
                </div>

                <div class="mt-auto pt-3 border-t border-gray-100 flex flex-col flex-1 overflow-hidden">
                    <div
                        class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 flex-shrink-0">
                        <Users class="w-3 h-3" /> Equipo Asignado
                    </div>

                    <div
                        class="flex-1 overflow-y-auto pr-1 space-y-1 scrollbar-thin scrollbar-thumb-gray-200 scrollbar-track-transparent max-h-[140px]">
                        <template v-if="getDisplayUsuarios(proy).length > 0">
                            <div v-for="user in getDisplayUsuarios(proy)" :key="user.id"
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

                        <div v-else
                            class="h-full flex flex-col items-center justify-center text-gray-300 italic text-xs py-4">
                            <Users class="w-8 h-8 opacity-20 mb-1" />
                            Sin equipo asignado
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="mostrarModal"
            class="fixed inset-0 bg-dark/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div class="card w-full max-w-md space-y-4 shadow-2xl animate-in zoom-in-95 max-h-[90vh] flex flex-col">

                <div class="flex justify-between items-center border-b border-gray-100 pb-2 flex-shrink-0">
                    <h3 class="font-bold text-lg text-dark">
                        {{ esEdicion ? 'Editar Proyecto' : 'Nuevo Proyecto' }}
                    </h3>
                    <button @click="mostrarModal = false">
                        <X class="w-5 h-5 text-gray-400 hover:text-red-500" />
                    </button>
                </div>

                <div class="overflow-y-auto flex-1 pr-1 space-y-4">
                    <div>
                        <label class="label-std">Nombre Proyecto</label>
                        <input v-model="proyectoForm.nombre" class="input-std" placeholder="Ej: Migración Cloud">
                    </div>

                    <div>
                        <label class="label-std">Cliente</label>
                        <input v-model="proyectoForm.cliente" class="input-std" placeholder="Ej: Banco Santander">
                    </div>

                    <div>
                        <label class="label-std mb-2">Asignar Equipo</label>
                        <div class="grid grid-cols-2 gap-2">
                            <div v-for="user in usuariosFake" :key="user.id" @click="toggleUsuarioEnForm(user)"
                                class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition select-none"
                                :class="estaSeleccionado(user.id) ? 'bg-primary/5 border-primary shadow-sm' : 'bg-white border-gray-200 hover:border-gray-300'">

                                <div class="w-4 h-4 rounded border flex items-center justify-center transition"
                                    :class="estaSeleccionado(user.id) ? 'bg-primary border-primary' : 'bg-white border-gray-300'">
                                    <Check v-if="estaSeleccionado(user.id)" class="w-3 h-3 text-white" />
                                </div>

                                <div class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold"
                                    :class="user.color">
                                    {{ user.iniciales }}
                                </div>
                                <span class="text-xs font-medium truncate"
                                    :class="estaSeleccionado(user.id) ? 'text-primary' : 'text-gray-600'">
                                    {{ user.nombre }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex gap-2 pt-2 flex-shrink-0">
                    <button @click="mostrarModal = false" class="btn-secondary flex-1">Cancelar</button>
                    <button @click="guardarProyecto" class="btn-primary flex-1">
                        {{ esEdicion ? 'Guardar Cambios' : 'Crear Proyecto' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
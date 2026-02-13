<script setup>
import { ref, computed } from 'vue'
import { FolderPlus, Pencil, Tag, X, Briefcase, Users, Check, CheckCircle2, AlertCircle } from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()

// --- CONFIGURACIÓN & DATOS MOCK ---
const USUARIOS_MOCK = [
    { id: 1, nombre: 'Ana García', iniciales: 'AG', color: 'bg-pink-100 text-pink-700' },
    { id: 2, nombre: 'Carlos Ruiz', iniciales: 'CR', color: 'bg-blue-100 text-blue-700' },
    { id: 3, nombre: 'Elena Nito', iniciales: 'EN', color: 'bg-purple-100 text-purple-700' },
    { id: 4, nombre: 'Javi M.', iniciales: 'JM', color: 'bg-emerald-100 text-emerald-700' },
    { id: 5, nombre: 'Laura P.', iniciales: 'LP', color: 'bg-orange-100 text-orange-700' },
    { id: 6, nombre: 'Mario L.', iniciales: 'ML', color: 'bg-indigo-100 text-indigo-700' },
]

const FORM_DEFAULT = {
    id: null,
    nombre: '',
    cliente: '',
    estado: 'Activo',
    equipo: []
}

// --- ESTADO ---
const proyectos = computed(() => store.getProjects())
const mostrarModal = ref(false)
const esEdicion = ref(false)
const formulario = ref({ ...FORM_DEFAULT })
const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

// --- ACCIONES DE UI ---
const mostrarNotificacion = (mensaje, tipo = 'success') => {
    toast.value = { show: true, message: mensaje, type }
    clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => toast.value.show = false, 3000)
}

const obtenerEquipoVisual = (proyecto) => {
    if (proyecto.equipo?.length > 0) return proyecto.equipo
    if (proyecto.id % 2 === 0) return USUARIOS_MOCK
    if (proyecto.id % 3 === 0) return [USUARIOS_MOCK[0], USUARIOS_MOCK[3]]
    return []
}

// --- GESTIÓN DEL MODAL ---
const abrirCrear = () => {
    esEdicion.value = false
    formulario.value = { ...FORM_DEFAULT }
    mostrarModal.value = true
}

const abrirEditar = (proyecto) => {
    esEdicion.value = true
    formulario.value = { 
        ...proyecto, 
        equipo: proyecto.equipo?.length ? [...proyecto.equipo] : [...obtenerEquipoVisual(proyecto)]
    }
    mostrarModal.value = true
}

// --- LÓGICA DE NEGOCIO ---
const toggleMiembroEquipo = (usuario) => {
    const index = formulario.value.equipo.findIndex(u => u.id === usuario.id)
    if (index >= 0) {
        formulario.value.equipo.splice(index, 1)
    } else {
        formulario.value.equipo.push(usuario)
    }
}

const esMiembroSeleccionado = (userId) => {
    return formulario.value.equipo.some(u => u.id === userId)
}

const guardar = () => {
    store.saveProject(formulario.value)
    mostrarNotificacion(
        esEdicion.value ? 'Proyecto actualizado correctamente' : 'Proyecto creado correctamente'
    )
    mostrarModal.value = false
}
</script>

<template>
    <div class="h-full p-6 bg-gray-50 flex flex-col gap-6 font-sans relative">

        <div class="flex justify-between items-center">
            <div>
                <h1 class="h1-title">Administrar Proyectos</h1>
                <p class="subtitle">Visión general y gestión de equipos.</p>
            </div>
            <button @click="abrirCrear" class="btn-primary">
                <FolderPlus class="w-4 h-4" /> Nuevo Proyecto
            </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="proyecto in proyectos" :key="proyecto.id"
                class="card group hover:border-primary hover:shadow-md transition relative flex flex-col min-h-[200px]">

                <div class="flex-shrink-0">
                    <div class="flex justify-between items-start mb-3">
                        <div class="bg-gray-100 p-2 rounded-lg text-slate-500 group-hover:bg-primary/10 group-hover:text-primary transition">
                            <Briefcase class="w-5 h-5" />
                        </div>

                        <div class="flex items-center gap-2">
                            <span class="badge"
                                :class="proyecto.estado === 'Activo' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-gray-100 text-gray-500 border-gray-200'">
                                {{ proyecto.estado }}
                            </span>

                            <button @click.stop="abrirEditar(proyecto)"
                                class="text-gray-300 hover:text-blue-500 transition opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-blue-50"
                                title="Editar proyecto">
                                <Pencil class="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <h3 class="font-bold text-lg text-dark mb-1 leading-tight">{{ proyecto.nombre }}</h3>
                    <p class="text-sm text-gray-500 mb-4 flex items-center gap-1">
                        <Tag class="w-3 h-3" /> {{ proyecto.cliente }}
                    </p>
                </div>

                <div class="mt-auto pt-3 border-t border-gray-100 flex flex-col flex-1 overflow-hidden">
                    <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 flex-shrink-0">
                        <Users class="w-3 h-3" /> Equipo Asignado
                    </div>

                    <div class="flex-1 overflow-y-auto pr-1 space-y-1 scrollbar-thin scrollbar-thumb-gray-200 scrollbar-track-transparent max-h-[140px]">
                        <template v-if="obtenerEquipoVisual(proyecto).length > 0">
                            <div v-for="miembro in obtenerEquipoVisual(proyecto)" :key="miembro.id"
                                class="flex items-center gap-2 p-1.5 rounded-md hover:bg-gray-50 transition-colors">
                                
                                <div class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold shadow-sm shrink-0"
                                    :class="miembro.color">
                                    {{ miembro.iniciales }}
                                </div>
                                <span class="text-xs font-medium text-slate-600 truncate">
                                    {{ miembro.nombre }}
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
                        <input v-model="formulario.nombre" class="input-std" placeholder="Ej: Migración Cloud">
                    </div>

                    <div>
                        <label class="label-std">Cliente</label>
                        <input v-model="formulario.cliente" class="input-std" placeholder="Ej: Banco Santander">
                    </div>

                    <div>
                        <label class="label-std mb-2">Asignar Equipo</label>
                        <div class="grid grid-cols-2 gap-2">
                            <div v-for="user in USUARIOS_MOCK" :key="user.id" 
                                @click="toggleMiembroEquipo(user)"
                                class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition select-none"
                                :class="esMiembroSeleccionado(user.id) ? 'bg-primary/5 border-primary shadow-sm' : 'bg-white border-gray-200 hover:border-gray-300'">

                                <div class="w-4 h-4 rounded border flex items-center justify-center transition"
                                    :class="esMiembroSeleccionado(user.id) ? 'bg-primary border-primary' : 'bg-white border-gray-300'">
                                    <Check v-if="esMiembroSeleccionado(user.id)" class="w-3 h-3 text-white" />
                                </div>

                                <div class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold"
                                    :class="user.color">
                                    {{ user.iniciales }}
                                </div>
                                <span class="text-xs font-medium truncate"
                                    :class="esMiembroSeleccionado(user.id) ? 'text-primary' : 'text-gray-600'">
                                    {{ user.nombre }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex gap-2 pt-2 flex-shrink-0">
                    <button @click="mostrarModal = false" class="btn-secondary flex-1">Cancelar</button>
                    <button @click="guardar" class="btn-primary flex-1">
                        {{ esEdicion ? 'Guardar Cambios' : 'Crear Proyecto' }}
                    </button>
                </div>
            </div>
        </div>

        <transition enter-active-class="transform ease-out duration-300 transition" enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2" enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="toast.show" class="absolute bottom-6 right-6 z-50 flex items-center w-full max-w-xs p-4 space-x-3 text-gray-500 bg-white rounded-lg shadow-lg border border-gray-100" role="alert">
                <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg" :class="toast.type === 'success' ? 'text-green-500 bg-green-100' : 'text-red-500 bg-red-100'">
                    <component :is="toast.type === 'success' ? CheckCircle2 : AlertCircle" class="w-5 h-5"/>
                </div>
                <div class="ml-3 text-sm font-bold text-gray-800">{{ toast.message }}</div>
                <button @click="toast.show = false" type="button" class="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 items-center justify-center">
                    <X class="w-4 h-4"/>
                </button>
            </div>
        </transition>

    </div>
</template>
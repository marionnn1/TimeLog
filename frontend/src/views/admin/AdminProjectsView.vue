<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { 
    FolderPlus, Pencil, Tag, X, Briefcase, Users, Check, 
    CheckCircle2, AlertCircle, Trash2, AlertTriangle 
} from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()

// --- CONFIGURACIÓN ---
const FORM_DEFAULT = {
    id: null,
    nombre: '',
    cliente: '',
    estado: 'Activo',
    equipo: []
}

// --- ESTADO ---
const proyectos = ref([])
const usuarios_db = ref([])
const cargando = ref(true)

const mostrarModal = ref(false)
const esEdicion = ref(false)
const formulario = ref({ ...FORM_DEFAULT })

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const confirmacion = reactive({
    show: false,
    title: '',
    message: '',
    type: 'neutral',
    proyectoId: null,
    modo: '' 
})

// --- LÓGICA DE API: CARGAR DATOS ---
const cargarDatos = async () => {
    try {
        cargando.value = true
        // 1. Cargamos Proyectos y sus equipos asignados desde SQL Server
        const resProj = await fetch('http://localhost:5000/api/proyectos')
        const jsonProj = await resProj.json()
        
        if (jsonProj.status === 'success') {
            proyectos.value = jsonProj.data.map(p => ({
                id: p.Id,
                nombre: p.Nombre,
                cliente: p.Cliente,
                estado: p.Estado,
                // MAPEO CORREGIDO: El servicio devuelve 'id' y 'nombre' en minúsculas dentro de Equipo
                equipo: p.Equipo ? p.Equipo.map(u => ({
                    id: u.id,
                    nombre: u.nombre,
                    iniciales: u.nombre.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2),
                    color: 'bg-indigo-100 text-indigo-700'
                })) : []
            }))
        }

        // 2. Cargamos Usuarios para el selector del modal
        const resUser = await fetch('http://localhost:5000/api/usuarios')
        const jsonUser = await resUser.json()
        if (jsonUser.status === 'success') {
            usuarios_db.value = jsonUser.data.map(u => ({
                id: u.Id,
                nombre: u.Nombre,
                iniciales: u.Nombre.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2),
                color: 'bg-indigo-100 text-indigo-700'
            }))
        }
    } catch (error) {
        mostrarNotificacion('Error al conectar con el servidor', 'error')
    } finally {
        cargando.value = false
    }
}

onMounted(cargarDatos)

// --- ACCIONES DE UI ---
const mostrarNotificacion = (mensaje, tipo = 'success') => {
    toast.value = { show: true, message: mensaje, type: tipo }
    clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => toast.value.show = false, 3000)
}

const abrirCrear = () => {
    esEdicion.value = false
    formulario.value = { ...FORM_DEFAULT }
    mostrarModal.value = true
}

const abrirEditar = (proyecto) => {
    esEdicion.value = true
    formulario.value = { 
        ...proyecto, 
        equipo: proyecto.equipo ? [...proyecto.equipo] : [] 
    }
    mostrarModal.value = true
}

// --- LÓGICA DE API: GUARDAR ---
const guardar = async () => {
    try {
        const metodo = esEdicion.value ? 'PUT' : 'POST'
        const url = esEdicion.value 
            ? `http://localhost:5000/api/proyectos/${formulario.value.id}`
            : 'http://localhost:5000/api/proyectos'
        
        const payload = {
            nombre: formulario.value.nombre,
            cliente: formulario.value.cliente,
            estado: formulario.value.estado,
            // ENVIAMOS LA LISTA DE IDs AL BACKEND
            usuarios_ids: formulario.value.equipo.map(u => u.id) 
        }

        const res = await fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        
        if (res.ok) {
            mostrarModal.value = false
            await cargarDatos()
            mostrarNotificacion(esEdicion.value ? 'Proyecto actualizado' : 'Proyecto creado')
        } else {
            mostrarNotificacion('Error en la respuesta del servidor', 'error')
        }
    } catch (error) {
        mostrarNotificacion('Error al guardar', 'error')
    }
}

const solicitarAccion = (id, modo) => {
    confirmacion.proyectoId = id
    confirmacion.modo = modo
    if (modo === 'cerrar') {
        confirmacion.title = 'Cerrar Proyecto'
        confirmacion.message = '¿Deseas marcar este proyecto como Cerrado?'
        confirmacion.type = 'neutral'
    } else {
        confirmacion.title = 'Eliminar de la BD'
        confirmacion.message = '¿Estás seguro? Esta acción borrará el registro de SQL Server.'
        confirmacion.type = 'danger'
    }
    confirmacion.show = true
}

const ejecutarAccionConfirmada = async () => {
    try {
        const url = confirmacion.modo === 'eliminar' 
            ? `http://localhost:5000/api/proyectos/${confirmacion.proyectoId}/force`
            : `http://localhost:5000/api/proyectos/${confirmacion.proyectoId}`;

        const res = await fetch(url, { method: 'DELETE' });
        const data = await res.json();
        
        if (res.ok) {
            await cargarDatos();
            mostrarNotificacion(data.message || 'Operación realizada');
        } else {
            mostrarNotificacion(data.message || 'Error en la operación', 'error');
        }
    } catch (error) {
        mostrarNotificacion('Error de red', 'error');
    }
    confirmacion.show = false;
}

const toggleMiembroEquipo = (usuario) => {
    const index = formulario.value.equipo.findIndex(u => u.id === usuario.id)
    if (index >= 0) formulario.value.equipo.splice(index, 1)
    else formulario.value.equipo.push(usuario)
}

const esMiembroSeleccionado = (userId) => formulario.value.equipo.some(u => u.id === userId)
const obtenerEquipoVisual = (proyecto) => proyecto.equipo || []
</script>

<template>
    <div class="h-full p-6 bg-gray-50 flex flex-col gap-6 font-sans relative">

        <div class="flex justify-between items-center">
            <div>
                <h1 class="h1-title font-bold text-2xl text-slate-800">Administrar Proyectos</h1>
                <p class="subtitle text-slate-500 text-sm">Visión general y gestión de equipos.</p>
            </div>
            <button @click="abrirCrear" class="btn-primary flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition font-medium shadow-md">
                <FolderPlus class="w-4 h-4" /> Nuevo Proyecto
            </button>
        </div>

        <div class="relative min-h-[300px]">
            <div v-if="cargando" class="absolute inset-0 flex flex-col items-center justify-center bg-white/50 backdrop-blur-sm z-10 rounded-xl">
                <div class="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p class="mt-2 text-sm text-gray-500 font-bold">Consultando SQL Server...</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="proyecto in proyectos" :key="proyecto.id"
                    class="bg-white border border-gray-100 rounded-xl p-5 group hover:border-blue-400 hover:shadow-lg transition relative flex flex-col min-h-[220px] shadow-sm">

                    <div class="flex-shrink-0">
                        <div class="flex justify-between items-start mb-3">
                            <div class="bg-gray-100 p-2 rounded-lg text-slate-500 group-hover:bg-blue-50 group-hover:text-blue-600 transition">
                                <Briefcase class="w-5 h-5" />
                            </div>

                            <div class="flex items-center gap-1">
                                <span class="badge px-2 py-0.5 rounded-full font-bold text-[10px] border" 
                                    :class="proyecto.estado === 'Activo' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-gray-100 text-gray-500 border-gray-200'">
                                    {{ proyecto.estado }}
                                </span>

                                <div class="flex items-center opacity-0 group-hover:opacity-100 transition">
                                    <button @click.stop="abrirEditar(proyecto)" class="p-1 text-gray-400 hover:text-blue-500" title="Editar"><Pencil class="w-4 h-4" /></button>
                                    <button v-if="proyecto.estado === 'Activo'" @click.stop="solicitarAccion(proyecto.id, 'cerrar')" class="p-1 text-gray-400 hover:text-emerald-500" title="Cerrar"><Check class="w-4 h-4" /></button>
                                    <button @click.stop="solicitarAccion(proyecto.id, 'eliminar')" class="p-1 text-gray-400 hover:text-red-500" title="Eliminar"><Trash2 class="w-4 h-4" /></button>
                                </div>
                            </div>
                        </div>

                        <h3 class="font-bold text-lg text-slate-800 mb-1 leading-tight">{{ proyecto.nombre }}</h3>
                        <p class="text-sm text-gray-500 mb-4 flex items-center gap-1">
                            <Tag class="w-3 h-3" /> {{ proyecto.cliente }}
                        </p>
                    </div>

                    <div class="mt-auto pt-3 border-t border-gray-100 flex flex-col flex-1 overflow-hidden">
                        <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 flex-shrink-0">
                            <Users class="w-3 h-3" /> Equipo Asignado
                        </div>

                        <div class="flex-1 overflow-y-auto pr-1 space-y-1 scrollbar-thin max-h-[140px]">
                            <template v-if="obtenerEquipoVisual(proyecto).length > 0">
                                <div v-for="miembro in obtenerEquipoVisual(proyecto)" :key="miembro.id"
                                    class="flex items-center gap-2 p-1.5 rounded-md hover:bg-gray-50 transition-colors">
                                    <div class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold shadow-sm shrink-0" :class="miembro.color">
                                        {{ miembro.iniciales }}
                                    </div>
                                    <span class="text-xs font-medium text-slate-600 truncate">{{ miembro.nombre }}</span>
                                </div>
                            </template>
                            <div v-else class="h-full flex flex-col items-center justify-center text-gray-300 italic text-xs py-4">
                                Sin equipo asignado
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="mostrarModal" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div class="bg-white rounded-2xl w-full max-w-md space-y-4 shadow-2xl animate-in zoom-in-95 max-h-[90vh] flex flex-col p-6 border border-gray-100">
                <div class="flex justify-between items-center border-b border-gray-100 pb-2 flex-shrink-0">
                    <h3 class="font-bold text-lg text-slate-800">{{ esEdicion ? 'Editar Proyecto' : 'Nuevo Proyecto' }}</h3>
                    <button @click="mostrarModal = false"><X class="w-5 h-5 text-gray-400 hover:text-red-500 transition" /></button>
                </div>

                <div class="overflow-y-auto flex-1 pr-1 space-y-4">
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Nombre Proyecto</label>
                        <input v-model="formulario.nombre" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ej: Migración Cloud">
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Cliente</label>
                        <input v-model="formulario.cliente" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ej: Banco Santander">
                    </div>

                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-2">Asignar Equipo</label>
                        <div class="grid grid-cols-2 gap-2">
                            <div v-for="user in usuarios_db" :key="user.id" 
                                @click="toggleMiembroEquipo(user)"
                                class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition select-none"
                                :class="esMiembroSeleccionado(user.id) ? 'bg-blue-50 border-blue-400 shadow-sm' : 'bg-white border-gray-200 hover:border-gray-300'">
                                
                                <div class="w-4 h-4 rounded border flex items-center justify-center transition"
                                    :class="esMiembroSeleccionado(user.id) ? 'bg-blue-600 border-blue-600' : 'bg-white border-gray-300'">
                                    <Check v-if="esMiembroSeleccionado(user.id)" class="w-3 h-3 text-white" />
                                </div>
                                <div class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold bg-blue-100 text-blue-700">
                                    {{ user.iniciales }}
                                </div>
                                <span class="text-[11px] font-bold truncate" :class="esMiembroSeleccionado(user.id) ? 'text-blue-700' : 'text-gray-600'">{{ user.nombre }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex gap-2 pt-4 border-t border-gray-100 flex-shrink-0">
                    <button @click="mostrarModal = false" class="flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition">Cancelar</button>
                    <button @click="guardar" class="flex-1 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 shadow-lg shadow-blue-200">Guardar</button>
                </div>
            </div>
        </div>

        <div v-if="confirmacion.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
            <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 text-center animate-in zoom-in-95">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4"
                     :class="confirmacion.type === 'danger' ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'">
                    <component :is="confirmacion.type === 'danger' ? Trash2 : Check" class="w-6 h-6" />
                </div>
                <h3 class="text-lg font-bold text-slate-900">{{ confirmacion.title }}</h3>
                <p class="text-sm text-slate-500 mt-2">{{ confirmacion.message }}</p>
                <div class="flex gap-3 mt-6">
                    <button @click="confirmacion.show = false" class="flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition">Cancelar</button>
                    <button @click="ejecutarAccionConfirmada" class="flex-1 py-2 text-white rounded-lg font-bold transition shadow-md"
                            :class="confirmacion.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : 'bg-emerald-600 hover:bg-emerald-700'">
                        Confirmar
                    </button>
                </div>
            </div>
        </div>

        <div v-if="toast.show" class="fixed bottom-6 right-6 z-50 flex items-center p-4 space-x-3 text-slate-600 bg-white rounded-xl shadow-2xl border border-gray-100 animate-in slide-in-from-right">
            <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg" :class="toast.type === 'success' ? 'text-green-500 bg-green-100' : 'text-red-500 bg-red-100'">
                <component :is="toast.type === 'success' ? CheckCircle2 : AlertCircle" class="w-5 h-5"/>
            </div>
            <div class="ml-3 text-sm font-bold text-slate-800">{{ toast.message }}</div>
        </div>

    </div>
</template>
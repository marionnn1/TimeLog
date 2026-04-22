<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { 
    FolderPlus, Pencil, Tag, X, Briefcase, Users, Check, 
    Trash2, Plus, Building2, UserPlus, Lock, Ban, Play, Hash 
} from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'
import AdminAPI from '../../services/AdminAPI'
import ConfirmModal from '../../components/common/ConfirmModal.vue'
import ToastNotification from '../../components/common/ToastNotification.vue'

const store = useDataStore()

const FORM_DEFAULT = { id: null, nombre: '', cliente: '', estado: 'Activo', equipo: [] }
const CLIENTE_DEFAULT = { id: null, nombre: '' }

const proyectos = ref([])
const clientes_db = ref([])
const usuarios_db = ref([])
const cargando = ref(true)

const isSubmittingCliente = ref(false)
const isSubmittingProyecto = ref(false)
const isConfirming = ref(false)

const mostrarModal = ref(false)
const mostrarModalCliente = ref(false)

const esEdicion = ref(false)
const esEdicionCliente = ref(false)

const formulario = ref({ ...FORM_DEFAULT })
const clienteForm = ref({ ...CLIENTE_DEFAULT })

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const confirmacion = reactive({ show: false, title: '', message: '', type: 'neutral', id: null, modo: '' })

// AÑADIDO: Guardar el código del cliente en la agrupación
const proyectosAgrupados = computed(() => {
    const grupos = {}
    
    clientes_db.value.forEach(c => { 
        grupos[c.nombre] = { id: c.id, codigo: c.codigo, proyectos: [] } 
    })

    proyectos.value.forEach(p => {
        const nombreCliente = p.cliente || 'Sin Cliente asignado'
        if (!grupos[nombreCliente]) {
            grupos[nombreCliente] = { id: null, codigo: null, proyectos: [] }
        }
        grupos[nombreCliente].proyectos.push(p)
    })
    
    return Object.keys(grupos).sort().reduce((obj, key) => {
        obj[key] = grupos[key]
        return obj
    }, {})
})

const cargarDatos = async () => {
    try {
        cargando.value = true
        
        const jsonCli = await AdminAPI.getClientes()
        if (jsonCli.status === 'success') clientes_db.value = jsonCli.data

        const jsonProj = await AdminAPI.getProyectos()
        if (jsonProj.status === 'success') {
            proyectos.value = jsonProj.data.map(p => ({
                id: p.Id, nombre: p.Nombre, cliente: p.Cliente, estado: p.Estado, codigo: p.codigo,
                equipo: p.Equipo ? p.Equipo.map(u => ({
                    id: u.id, nombre: u.nombre, foto: u.foto,
                    iniciales: u.nombre.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2),
                    color: 'bg-indigo-100 text-indigo-700'
                })) : []
            }))
        }

        const jsonUser = await AdminAPI.getUsuarios()
        if (jsonUser.status === 'success') {
            usuarios_db.value = jsonUser.data.map(u => ({
                id: u.Id, nombre: u.Nombre, foto: u.Foto,
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

const mostrarNotificacion = (mensaje, tipo = 'success') => {
    toast.value = { show: true, message: mensaje, type: tipo }
    clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => toast.value.show = false, 3000)
}

const abrirCrearCliente = () => {
    esEdicionCliente.value = false
    clienteForm.value = { ...CLIENTE_DEFAULT }
    mostrarModalCliente.value = true
}

const abrirEditarCliente = (clienteData, nombreActual) => {
    if (!clienteData.id) return 
    esEdicionCliente.value = true
    clienteForm.value = { 
        id: clienteData.id, 
        nombre: nombreActual
    }
    mostrarModalCliente.value = true
}

const guardarCliente = async () => {
    if(!clienteForm.value.nombre) return mostrarNotificacion("El nombre es obligatorio", "error")
    
    if (isSubmittingCliente.value) return;
    isSubmittingCliente.value = true;

    try {
        let res;
        if (esEdicionCliente.value) res = await AdminAPI.editarCliente(clienteForm.value.id, clienteForm.value)
        else res = await AdminAPI.crearCliente(clienteForm.value)

        if (res.status === 'success') {
            mostrarModalCliente.value = false
            await cargarDatos()
            mostrarNotificacion(esEdicionCliente.value ? 'Cliente actualizado' : 'Cliente creado')
        } else {
            mostrarNotificacion(res.message || 'Error al guardar cliente', 'error')
        }
    } catch (e) { 
        mostrarNotificacion('Error de red', 'error') 
    } finally {
        isSubmittingCliente.value = false;
    }
}

const solicitarEliminarCliente = (clienteId) => {
    confirmacion.id = clienteId
    confirmacion.modo = 'eliminar_cliente'
    confirmacion.title = 'Eliminar Cliente'
    confirmacion.message = '¿Deseas eliminar este cliente? Solo es posible si no tiene proyectos asignados.'
    confirmacion.type = 'danger'
    confirmacion.show = true
}

const abrirCrearProyectoGlobal = () => { 
    esEdicion.value = false
    formulario.value = { ...FORM_DEFAULT }
    mostrarModal.value = true 
}

const abrirCrearDesdeCliente = (nombreCliente) => {
    esEdicion.value = false
    formulario.value = { ...FORM_DEFAULT, cliente: nombreCliente }
    mostrarModal.value = true 
}

const abrirEditar = (proyecto) => { 
    esEdicion.value = true
    formulario.value = { ...proyecto, equipo: proyecto.equipo ? [...proyecto.equipo] : [] }
    mostrarModal.value = true 
}

const guardar = async () => {
    if (isSubmittingProyecto.value) return;
    isSubmittingProyecto.value = true;

    try {
        const payload = {
            nombre: formulario.value.nombre,
            cliente: formulario.value.cliente,
            estado: formulario.value.estado,
            usuarios_ids: formulario.value.equipo.map(u => u.id) 
        }

        let res
        if (esEdicion.value) res = await AdminAPI.editarProyecto(formulario.value.id, payload)
        else res = await AdminAPI.crearProyecto(payload)
        
        if (res.status === 'success') {
            mostrarModal.value = false
            await cargarDatos()
            mostrarNotificacion(esEdicion.value ? 'Proyecto actualizado' : 'Proyecto creado')
        } else {
            mostrarNotificacion('Error en la respuesta del servidor', 'error')
        }
    } catch (error) { 
        mostrarNotificacion('Error al guardar proyecto', 'error') 
    } finally {
        isSubmittingProyecto.value = false;
    }
}

const solicitarAccion = (id, modo) => {
    confirmacion.id = id
    confirmacion.modo = modo
    
    if (modo === 'cerrar') {
        confirmacion.title = 'Cerrar Proyecto'
        confirmacion.message = '¿Deseas Cerrar este proyecto? Significa que ha finalizado (histórico).'
        confirmacion.type = 'neutral'
    } else if (modo === 'desactivar') {
        confirmacion.title = 'Desactivar Proyecto'
        confirmacion.message = '¿Deseas Desactivar este proyecto? Quedará en pausa y no se le podrán imputar horas.'
        confirmacion.type = 'warning'
    } else if (modo === 'activar') {
        confirmacion.title = 'Activar Proyecto'
        confirmacion.message = '¿Deseas volver a Activar este proyecto para que el equipo impute horas?'
        confirmacion.type = 'success'
    } else if (modo === 'eliminar') {
        confirmacion.title = 'Eliminar Proyecto (Físico)'
        confirmacion.message = '¿Estás seguro? Esta acción borrará el registro de la BD. Solo el sistema te dejará hacerlo si NO tiene horas imputadas.'
        confirmacion.type = 'danger'
    }
    confirmacion.show = true
}

const ejecutarAccionConfirmada = async () => {
    if (isConfirming.value) return;
    isConfirming.value = true;

    try {
        let res;
        if (confirmacion.modo === 'eliminar_cliente') res = await AdminAPI.eliminarCliente(confirmacion.id)
        else if (confirmacion.modo === 'eliminar') res = await AdminAPI.eliminarProyecto(confirmacion.id)
        else if (['cerrar', 'desactivar', 'activar'].includes(confirmacion.modo)) {
            const mapEstado = { 'cerrar': 'Cerrado', 'desactivar': 'Inactivo', 'activar': 'Activo' }
            res = await AdminAPI.cambiarEstadoProyecto(confirmacion.id, mapEstado[confirmacion.modo])
        }
        
        if (res.status === 'success') {
            await cargarDatos();
            mostrarModal.value = false;
            mostrarNotificacion(res.message || 'Operación realizada');
        } else {
            mostrarNotificacion(res.message || 'Error en la operación', 'error');
        }
    } catch (error) {
        mostrarNotificacion(error.response?.data?.message || 'Error de red', 'error');
    } finally {
        isConfirming.value = false;
        confirmacion.show = false;
    }
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
    <div class="absolute inset-0 overflow-y-auto bg-gray-50 p-6 flex flex-col font-sans">
        
        <div class="max-w-[1600px] mx-auto w-full space-y-6">

            <div class="flex justify-between items-center bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                <div>
                    <h1 class="font-bold text-2xl text-slate-800">Administrar Proyectos</h1>
                    <p class="text-slate-500 text-sm">Gestión de base de datos de Clientes y Proyectos.</p>
                </div>
                <div class="flex gap-3">
                    <button @click="abrirCrearCliente" class="btn-secondary flex items-center gap-2 bg-white border border-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition font-medium shadow-sm">
                        <Building2 class="w-4 h-4" /> Nuevo Cliente
                    </button>
                    <button @click="abrirCrearProyectoGlobal" class="btn-primary flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition font-medium shadow-md shadow-blue-500/20">
                        <FolderPlus class="w-4 h-4" /> Nuevo Proyecto
                    </button>
                </div>
            </div>

            <div class="relative min-h-[300px]">
                <div v-if="cargando" class="absolute inset-0 flex flex-col items-center justify-center bg-white/50 backdrop-blur-sm z-10 rounded-xl">
                    <div class="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    <p class="mt-2 text-sm text-gray-500 font-bold">Consultando SQL Server...</p>
                </div>

                <div class="space-y-6 pb-10">
                    <div v-for="(datosCliente, clienteNombre) in proyectosAgrupados" :key="clienteNombre" class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        
                        <div class="flex items-start gap-4 border-b border-gray-100 pb-4 mb-4 group/header">
                            <div class="bg-blue-50 p-2.5 rounded-xl text-blue-600 mt-1">
                                <Briefcase class="w-6 h-6" stroke-width="2.5" />
                            </div>
                            
                            <div class="flex flex-col gap-1">
                                <div class="flex items-center gap-2">
                                    <h2 class="text-xl font-bold text-slate-800">{{ clienteNombre }}</h2>
                                    <span class="text-xs font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
                                        {{ datosCliente.proyectos.length }} proyectos
                                    </span>
                                </div>
                                <div v-if="datosCliente.codigo" class="text-xs text-slate-400 font-mono font-bold flex items-center gap-1">
                                    <Hash class="w-3.5 h-3.5" /> {{ datosCliente.codigo }}
                                </div>
                            </div>

                            <div class="ml-auto flex items-center gap-3 mt-1">
                                <div v-if="datosCliente.id" class="flex items-center opacity-0 group-hover/header:opacity-100 transition-opacity gap-1">
                                    <button @click="abrirEditarCliente(datosCliente, clienteNombre)" class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="Editar Cliente">
                                        <Pencil class="w-4 h-4" />
                                    </button>
                                    <button @click="solicitarEliminarCliente(datosCliente.id)" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Eliminar Cliente">
                                        <Trash2 class="w-4 h-4" />
                                    </button>
                                </div>

                                <button @click="abrirCrearDesdeCliente(clienteNombre)" class="text-sm font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 px-3 py-2 rounded-lg transition-colors flex items-center gap-1.5">
                                    <Plus class="w-4 h-4" /> Añadir Proyecto
                                </button>
                            </div>
                        </div>

                        <div v-if="datosCliente.proyectos.length === 0" class="py-8 border-2 border-dashed border-gray-100 rounded-xl flex flex-col items-center justify-center text-gray-400 bg-gray-50/50">
                            <Building2 class="w-8 h-8 opacity-40 mb-2" />
                            <p class="text-sm font-medium">Cliente registrado, pero sin proyectos aún.</p>
                        </div>

                        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            <div v-for="proyecto in datosCliente.proyectos" :key="proyecto.id"
                                class="bg-white border border-gray-100 rounded-xl p-5 group hover:border-blue-400 hover:shadow-lg transition relative flex flex-col min-h-[220px] shadow-sm"
                                :class="{'opacity-75 bg-gray-50': proyecto.estado !== 'Activo'}"> 

                                <div class="flex-shrink-0">
                                    <div class="flex justify-between items-start mb-3">
                                        <div class="bg-gray-100 p-2 rounded-lg text-slate-500 group-hover:bg-blue-50 group-hover:text-blue-600 transition">
                                            <Briefcase class="w-5 h-5" />
                                        </div>

                                        <div class="flex items-center gap-1">
                                            <span class="badge px-2 py-0.5 rounded-full font-bold text-[10px] border" 
                                                :class="{
                                                    'bg-emerald-50 text-emerald-700 border-emerald-200': proyecto.estado === 'Activo',
                                                    'bg-amber-50 text-amber-700 border-amber-200': proyecto.estado === 'Cerrado',
                                                    'bg-orange-50 text-orange-700 border-orange-200': proyecto.estado === 'Inactivo'
                                                }">
                                                {{ proyecto.estado }}
                                            </span>

                                            <div class="flex items-center opacity-0 group-hover:opacity-100 transition gap-1">
                                                <button @click.stop="abrirEditar(proyecto)" class="p-1 text-gray-400 hover:text-blue-500" title="Editar"><Pencil class="w-4 h-4" /></button>
                                                
                                                <button v-if="proyecto.estado === 'Activo'" @click.stop="solicitarAccion(proyecto.id, 'cerrar')" class="p-1 text-gray-400 hover:text-amber-500" title="Cerrar Proyecto"><Lock class="w-4 h-4" /></button>
                                                
                                                <button v-if="proyecto.estado === 'Activo'" @click.stop="solicitarAccion(proyecto.id, 'desactivar')" class="p-1 text-gray-400 hover:text-orange-500" title="Desactivar Proyecto"><Ban class="w-4 h-4" /></button>
                                                
                                                <button v-if="proyecto.estado !== 'Activo'" @click.stop="solicitarAccion(proyecto.id, 'activar')" class="p-1 text-gray-400 hover:text-emerald-500" title="Activar Proyecto"><Play class="w-4 h-4" /></button>
                                                
                                                <button @click.stop="solicitarAccion(proyecto.id, 'eliminar')" class="p-1 text-gray-400 hover:text-red-500" title="Eliminar"><Trash2 class="w-4 h-4" /></button>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="mb-5">
                                        <h3 class="text-lg font-bold text-slate-800 leading-tight mb-2 truncate" :title="proyecto.nombre" :class="{'text-slate-500': proyecto.estado !== 'Activo'}">
                                            {{ proyecto.nombre }}
                                        </h3>
                                        
                                        <div class="flex flex-col gap-2">
                                            <p class="text-sm text-slate-500 flex items-center gap-1.5 font-medium truncate" title="Cliente asignado">
                                                <Tag class="w-3.5 h-3.5" /> {{ proyecto.cliente }}
                                            </p>
                                            <div v-if="proyecto.codigo" class="flex items-center mt-0.5">
                                                <span class="bg-indigo-50 text-indigo-600 border border-indigo-200 px-2 py-0.5 rounded text-[10px] font-bold font-mono tracking-wider flex items-center gap-1 w-fit" title="Código Interno de Proyecto">
                                                    <Hash class="w-3 h-3 opacity-60" /> {{ proyecto.codigo }}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="mt-auto pt-3 border-t border-gray-100 flex flex-col flex-1 overflow-hidden">
                                    
                                    <div class="flex justify-between items-center mb-3">
                                        <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5 flex-shrink-0">
                                            <Users class="w-3 h-3" /> Usuarios Asignados
                                        </div>
                                        <button @click.stop="abrirEditar(proyecto)" class="text-gray-300 hover:text-blue-600 transition" title="Modificar equipo">
                                            <UserPlus class="w-4 h-4"/>
                                        </button>
                                    </div>

                                    <div class="flex-1 overflow-y-auto pr-1 space-y-1 scrollbar-thin max-h-[140px]">
                                        <template v-if="obtenerEquipoVisual(proyecto).length > 0">
                                            <div v-for="miembro in obtenerEquipoVisual(proyecto)" :key="miembro.id"
                                                class="flex items-center gap-2 p-1.5 rounded-md hover:bg-gray-50 transition-colors">
                                                
                                                <img v-if="miembro.foto" :src="'data:image/jpeg;base64,' + miembro.foto" class="h-6 w-6 rounded-full object-cover shadow-sm shrink-0" />
                                                <div v-else class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold shadow-sm shrink-0" :class="miembro.color">
                                                    {{ miembro.iniciales }}
                                                </div>

                                                <span class="text-xs font-medium text-slate-600 truncate">{{ miembro.nombre }}</span>
                                            </div>
                                        </template>
                                        
                                        <div v-else class="h-full flex flex-col items-center justify-center text-gray-300 gap-2 min-h-[100px]">
                                            <UserPlus class="w-8 h-8 opacity-20" />
                                            <span class="text-xs italic">Sin usuarios asignados</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>

        <div v-if="mostrarModalCliente" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div class="bg-white rounded-2xl w-full max-w-sm p-6 shadow-2xl animate-in zoom-in-95">
                <div class="flex justify-between items-center mb-5">
                    <h3 class="font-bold text-lg text-slate-800">{{ esEdicionCliente ? 'Editar Cliente' : 'Nuevo Cliente' }}</h3>
                    <button @click="mostrarModalCliente=false"><X class="w-5 h-5 text-gray-400 hover:text-red-500 transition" /></button>
                </div>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Nombre *</label>
                        <input v-model="clienteForm.nombre" type="text" placeholder="Ej: Banco Santander" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                    </div>

                    <button @click="guardarCliente" 
                            :disabled="isSubmittingCliente"
                            class="w-full py-2.5 rounded-lg font-bold shadow mt-2 transition flex justify-center items-center gap-2"
                            :class="isSubmittingCliente ? 'bg-slate-400 text-white cursor-not-allowed' : 'bg-slate-800 text-white hover:bg-slate-700'">
                        
                        <svg v-if="isSubmittingCliente" class="animate-spin w-5 h-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>

                        {{ isSubmittingCliente ? 'Guardando...' : 'Guardar' }}
                    </button>
                </div>
            </div>
        </div>

        <div v-if="mostrarModal" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl animate-in zoom-in-95 max-h-[90vh] flex flex-col p-6 border border-gray-100 overflow-y-auto">
                <div class="flex justify-between items-center border-b border-gray-100 pb-2 flex-shrink-0">
                    <div>
                        <h3 class="font-bold text-lg text-slate-800">{{ esEdicion ? 'Editar Proyecto' : 'Nuevo Proyecto' }}</h3>
                    </div>
                    <button @click="mostrarModal = false"><X class="w-5 h-5 text-gray-400 hover:text-red-500 transition" /></button>
                </div>

                <div class="overflow-y-auto flex-1 pr-1 py-4 space-y-4">
                    
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Cliente Base</label>
                        <select v-model="formulario.cliente" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none bg-white">
                            <option value="" disabled>Seleccionar cliente...</option>
                            <option v-for="c in clientes_db" :key="c.id" :value="c.nombre">{{ c.nombre }}</option>
                        </select>
                        <p class="text-xs text-gray-400 mt-1">Si no aparece el cliente, ciérralo y pulsa "Nuevo Cliente".</p>
                    </div>

                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Nombre del Proyecto</label>
                        <input v-model="formulario.nombre" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ej: Migración Cloud">
                    </div>

                    <div v-if="esEdicion" class="p-4 bg-gray-50 rounded-lg border border-gray-200 mt-4 flex items-center justify-between">
                        <div>
                            <p class="text-sm font-bold text-slate-700">Estado del Proyecto</p>
                            <p class="text-xs text-gray-500">Actualmente: <span class="font-bold" :class="formulario.estado === 'Activo' ? 'text-emerald-600' : (formulario.estado === 'Cerrado' ? 'text-amber-600' : 'text-orange-600')">{{ formulario.estado }}</span></p>
                        </div>
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

                                <img v-if="user.foto" :src="'data:image/jpeg;base64,' + user.foto" class="h-6 w-6 rounded-full object-cover shrink-0" />
                                <div v-else class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold bg-blue-100 text-blue-700 shrink-0">
                                    {{ user.iniciales }}
                                </div>
                                
                                <span class="text-[11px] font-bold truncate" :class="esMiembroSeleccionado(user.id) ? 'text-blue-700' : 'text-gray-600'">{{ user.nombre }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex gap-2 pt-4 border-t border-gray-100 flex-shrink-0">
                    <button @click="mostrarModal = false" :disabled="isSubmittingProyecto" class="flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition disabled:opacity-50">Cancelar</button>
                    
                    <button @click="guardar" 
                            :disabled="isSubmittingProyecto"
                            class="flex-1 py-2 text-white rounded-lg font-bold shadow-lg transition flex justify-center items-center gap-2"
                            :class="isSubmittingProyecto ? 'bg-blue-400 cursor-not-allowed opacity-80' : 'bg-blue-600 hover:bg-blue-700 shadow-blue-200'">
                        
                        <svg v-if="isSubmittingProyecto" class="animate-spin w-4 h-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>

                        {{ isSubmittingProyecto ? 'Guardando...' : 'Guardar Proyecto' }}
                    </button>
                </div>
            </div>
        </div>

        <ConfirmModal 
            :show="confirmacion.show"
            :title="confirmacion.title"
            :message="confirmacion.message"
            :type="confirmacion.type"
            :isLoading="isConfirming"
            @confirm="ejecutarAccionConfirmada"
            @cancel="confirmacion.show = false"
        />

        <ToastNotification
            :show="toast.show"
            :message="toast.message"
            :type="toast.type"
            @close="toast.show = false"
        />

    </div>
</template>
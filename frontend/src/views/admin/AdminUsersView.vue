<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { 
    Plus, Pencil, Trash2, Search, MapPin, X, Save,
    AlertTriangle, CheckCircle2, AlertCircle
} from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()

// --- CONFIGURACIÓN ---
const DEFAULT_FORM = {
    id: null,
    nombre: '',
    email: '',
    rol: 'Técnico',
    sede: 'Tarragona',
    activo: 1
}

// --- ESTADO ---
const usuarios = ref([])
const cargando = ref(true)

const sedesDisponibles = store.getSedes()
const busqueda = ref('')

const mostrarModal = ref(false)
const esEdicion = ref(false)
const formulario = ref({ ...DEFAULT_FORM })

const confirmacion = reactive({
    show: false,
    title: '',
    message: '',
    type: 'neutral',
    action: null,
    usuarioId: null 
})

// --- LÓGICA DE API: LEER (GET) ---
const cargarUsuariosDesdeAPI = async () => {
    try {
        cargando.value = true
        const respuesta = await fetch('http://127.0.0.1:5000/api/usuarios')
        const json = await respuesta.json()
        
        if (json.status === 'success') {
            usuarios.value = json.data.map(u => ({
                id: u.Id,
                nombre: u.Nombre,
                email: u.OidAzure,
                rol: u.Rol,
                sede: u.Sede,
                activo: u.Activo 
            }))
        } else {
            console.error("Error del servidor:", json.message)
        }
    } catch (error) {
        console.error("Error de red al conectar con la API:", error)
    } finally {
        cargando.value = false
    }
}

onMounted(() => {
    cargarUsuariosDesdeAPI()
})

// --- LÓGICA DE FILTRADO ---
const usuariosFiltrados = computed(() => {
    const texto = busqueda.value.toLowerCase().trim()
    if (!texto) return usuarios.value

    return usuarios.value.filter(u => 
        u.nombre.toLowerCase().includes(texto) ||
        u.email.toLowerCase().includes(texto)
    )
})

// --- GESTIÓN DE MODAL ---
const resetForm = () => {
    formulario.value = { ...DEFAULT_FORM, sede: sedesDisponibles[0] }
}

const abrirCrear = () => {
    esEdicion.value = false
    resetForm()
    mostrarModal.value = true
}

const abrirEditar = (usuario) => {
    esEdicion.value = true
    formulario.value = { ...usuario }
    mostrarModal.value = true
}

// --- LÓGICA DE API: CREAR Y EDITAR (POST/PUT) ---
const guardar = async () => {
    try {
        const metodo = esEdicion.value ? 'PUT' : 'POST'
        const url = esEdicion.value 
            ? `http://localhost:5000/api/usuarios/${formulario.value.id}`
            : 'http://localhost:5000/api/usuarios'
        
        const payload = {
            nombre: formulario.value.nombre,
            email: formulario.value.email,
            rol: formulario.value.rol,
            sede: formulario.value.sede
        }

        const respuesta = await fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        
        const resultado = await respuesta.json()
        
        if (respuesta.ok && resultado.status === 'success') {
            mostrarModal.value = false
            await cargarUsuariosDesdeAPI() 
        } else {
            console.error("Error del servidor:", resultado.message)
        }
    } catch (error) {
        console.error("Error de red al intentar guardar:", error)
    }
}

// --- LÓGICA DE CONFIRMACIÓN (ELIMINAR Y TOGGLE) ---
const solicitarAccion = (id, modo) => {
    confirmacion.usuarioId = id
    confirmacion.action = modo
    
    if (modo === 'toggle') {
        const user = usuarios.value.find(u => u.id === id) || formulario.value
        if (user.activo === 1 || user.activo === true) {
            confirmacion.title = 'Desactivar Acceso'
            confirmacion.message = 'Desactivar acceso a este usuario? Perderá acceso pero sus datos se conservarán.'
            confirmacion.type = 'neutral'
        } else {
            confirmacion.title = 'Reactivar Acceso'
            confirmacion.message = '¿Deseas restaurar el acceso de este usuario al sistema?'
            confirmacion.type = 'success'
        }
    } else {
        confirmacion.title = 'Eliminar de la BD'
        confirmacion.message = '¿Estás seguro? Esta acción borrará el registro físicamente de SQL Server.'
        confirmacion.type = 'danger'
    }
    confirmacion.show = true
}

const confirmarAccion = async () => {
    try {
        let respuesta;
        
        if (confirmacion.action === 'eliminar') {
            respuesta = await fetch(`http://127.0.0.1:5000/api/usuarios/${confirmacion.usuarioId}`, {
                method: 'DELETE'
            });
        } else if (confirmacion.action === 'toggle') {
            respuesta = await fetch(`http://127.0.0.1:5000/api/usuarios/${confirmacion.usuarioId}/toggle`, {
                method: 'PUT'
            });
        }
        
        if (respuesta && respuesta.ok) {
            await cargarUsuariosDesdeAPI(); 
            mostrarModal.value = false; // Cierra el modal de edición si estaba abierto
        } else {
            console.error("Error del servidor en la operación")
        }
    } catch (error) {
        console.error("Error de red en confirmarAccion:", error)
    }
    confirmacion.show = false;
}

// --- ESTILOS ---
const obtenerEstiloRol = (rol) => {
    if (rol === 'Admin' || rol === 'Administrador') return 'bg-red-50 text-red-700 border-red-200'
    if (rol === 'JP' || rol === 'Jefe de Proyecto') return 'bg-amber-50 text-amber-700 border-amber-200'
    return 'bg-blue-50 text-blue-700 border-blue-200'
}
</script>

<template>
  <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto relative">
    
    <div class="flex justify-between items-center">
      <div>
        <h1 class="h1-title font-bold text-2xl text-slate-800">Gestión de Usuarios</h1>
        <p class="subtitle text-slate-500 text-sm">Administra altas, bajas y sedes de trabajo.</p>
      </div>
      <button @click="abrirCrear" class="btn-primary flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition font-medium shadow-md">
        <Plus class="w-4 h-4" /> Nuevo Usuario
      </button>
    </div>

    <div class="card py-3">
        <div class="relative w-full max-w-sm">
            <Search class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input 
                v-model="busqueda" 
                type="text" 
                placeholder="Buscar por nombre o Azure ID..." 
                class="input-std pl-10 border border-gray-300 rounded-lg w-full py-2 focus:ring-2 focus:ring-blue-500 outline-none"
            >
        </div>
    </div>

    <div class="card p-0 overflow-hidden relative min-h-[200px] bg-white border border-gray-200 rounded-xl shadow-sm">
        <div v-if="cargando" class="absolute inset-0 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center z-10">
            <div class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-2"></div>
            <p class="text-sm text-gray-500 font-medium">Conectando con SQL Server...</p>
        </div>

        <table class="w-full text-left">
            <thead class="bg-gray-50 text-xs uppercase text-gray-500 border-b border-gray-200">
                <tr>
                    <th class="px-6 py-4">Usuario</th>
                    <th class="px-6 py-4">Rol</th>
                    <th class="px-6 py-4">Sede / Ubicación</th>
                    <th class="px-6 py-4 text-right">Acciones</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 text-sm">
                <tr v-if="!cargando && usuariosFiltrados.length === 0">
                    <td colspan="4" class="px-6 py-8 text-center text-gray-400">
                        No se han encontrado usuarios.
                    </td>
                </tr>

                <tr v-for="user in usuariosFiltrados" :key="user.id" class="hover:bg-slate-50 transition" :class="{'opacity-50': user.activo === 0 || user.activo === false}">
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-2">
                            <p class="font-bold text-slate-800" :class="{'line-through text-slate-400': user.activo === 0 || user.activo === false}">{{ user.nombre }}</p>
                            <span v-if="user.activo === 0 || user.activo === false" class="bg-red-100 text-red-600 border border-red-200 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase">Inactivo</span>
                        </div>
                        <p class="text-xs text-gray-400">{{ user.email }}</p>
                    </td>
                    <td class="px-6 py-4">
                        <span :class="obtenerEstiloRol(user.rol)" class="px-2 py-1 rounded-md text-[10px] font-bold uppercase border">
                            {{ user.rol }}
                        </span>
                    </td>
                    <td class="px-6 py-4 flex items-center gap-2 text-gray-600">
                        <MapPin class="w-4 h-4 text-gray-400"/> {{ user.sede }}
                    </td>
                    <td class="px-6 py-4 text-right">
                        <div class="flex items-center justify-end gap-2">
                            <button @click="abrirEditar(user)" class="p-2 text-gray-400 hover:text-blue-500 transition rounded-lg hover:bg-blue-50" title="Editar">
                                <Pencil class="w-4 h-4"/>
                            </button>
                            <button @click="solicitarAccion(user.id, 'eliminar')" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 transition rounded-lg" title="Eliminar de BD">
                                <Trash2 class="w-4 h-4"/>
                            </button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div v-if="mostrarModal" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
        <div class="bg-white rounded-2xl w-full max-w-md space-y-5 shadow-2xl p-6 border border-gray-100 animate-in zoom-in-95">
            
            <div class="flex justify-between items-center border-b border-gray-100 pb-3">
                <h3 class="font-bold text-lg text-slate-800">
                    {{ esEdicion ? 'Editar' : 'Nuevo' }} Usuario
                </h3>
                <button @click="mostrarModal = false" class="text-gray-400 hover:text-red-500 transition">
                    <X class="w-5 h-5"/>
                </button>
            </div>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Nombre Completo</label>
                    <input v-model="formulario.nombre" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Email Corporativo / Azure ID</label>
                    <input v-model="formulario.email" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Rol</label>
                        <select v-model="formulario.rol" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                            <option>Tecnico</option>
                            <option>JP</option>
                            <option>Admin</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Sede</label>
                        <select v-model="formulario.sede" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                            <option v-for="s in sedesDisponibles" :key="s" :value="s">{{ s }}</option>
                        </select>
                    </div>
                </div>

                <div v-if="esEdicion" class="p-4 bg-gray-50 rounded-lg border border-gray-200 mt-2 flex items-center justify-between">
                    <div>
                        <p class="text-sm font-bold text-slate-700">Acceso al Sistema</p>
                        <p class="text-xs text-gray-500">Estado: <span class="font-bold" :class="(formulario.activo === 1 || formulario.activo === true) ? 'text-emerald-600' : 'text-red-600'">{{ (formulario.activo === 1 || formulario.activo === true) ? 'Activo' : 'Inactivo' }}</span></p>
                    </div>
                    <button @click.prevent="solicitarAccion(formulario.id, 'toggle')"
                            class="px-3 py-1.5 rounded text-xs font-bold transition border"
                            :class="(formulario.activo === 1 || formulario.activo === true) ? 'bg-white border-red-200 text-red-600 hover:bg-red-50' : 'bg-white border-emerald-200 text-emerald-600 hover:bg-emerald-50'">
                        {{ (formulario.activo === 1 || formulario.activo === true) ? 'Desactivar Acceso' : 'Reactivar Acceso' }}
                    </button>
                </div>
            </div>

            <div class="flex gap-3 pt-2">
                <button @click="mostrarModal = false" class="flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition">Cancelar</button>
                <button @click="guardar" class="flex-1 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 shadow-lg shadow-blue-200 transition">Guardar</button>
            </div>
        </div>
    </div>

    <div v-if="confirmacion.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
        <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
            <div class="flex flex-col items-center text-center gap-3">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2"
                     :class="confirmacion.type === 'danger' ? 'bg-red-100 text-red-600' : (confirmacion.type === 'success' ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-600')">
                    <component :is="confirmacion.type === 'danger' ? Trash2 : (confirmacion.type === 'success' ? CheckCircle2 : AlertTriangle)" class="w-6 h-6" />
                </div>
                <h3 class="text-lg font-bold text-slate-900">{{ confirmacion.title }}</h3>
                <p class="text-sm text-slate-500 leading-relaxed">{{ confirmacion.message }}</p>
                
                <div class="flex gap-3 w-full mt-4">
                    <button @click="confirmacion.show = false" class="btn-secondary flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition justify-center">
                        Cancelar
                    </button>
                    <button @click="confirmarAccion" 
                            class="flex-1 py-2 text-white rounded-lg font-bold transition shadow-md justify-center"
                            :class="confirmacion.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : (confirmacion.type === 'success' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-slate-700 hover:bg-slate-800')">
                        Confirmar
                    </button>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>
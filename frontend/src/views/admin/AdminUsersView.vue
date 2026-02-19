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
    sede: 'Tarragona' 
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
    usuarioId: null // Nuevo: Para guardar el ID del usuario a borrar
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
                activo: u.Activo // Mapeamos el campo activo
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
        
        // Preparamos el paquete de datos exactamente como lo espera el servicio de Python
        const payload = {
            nombre: formulario.value.nombre,
            email: formulario.value.email,
            rol: formulario.value.rol,
            sede: formulario.value.sede
        }

        console.log("Enviando datos al backend:", payload) // Esto es para que lo veas en la consola

        const respuesta = await fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        
        const resultado = await respuesta.json()
        
        if (respuesta.ok && resultado.status === 'success') {
            mostrarModal.value = false
            await cargarUsuariosDesdeAPI() // Forzamos recarga de la tabla
            console.log("Guardado con éxito")
        } else {
            console.error("Error del servidor:", resultado.message)
        }
    } catch (error) {
        console.error("Error de red al intentar guardar:", error)
    }
}

// --- LÓGICA DE API: ELIMINAR (DELETE) ---
const solicitarEliminacion = (id) => {
    confirmacion.title = 'Eliminar Usuario'
    confirmacion.message = '¿Estás seguro de que deseas dar de baja a este usuario?'
    confirmacion.type = 'danger'
    confirmacion.usuarioId = id // Guardamos el ID real de la BD
    confirmacion.action = 'eliminar'
    confirmacion.show = true
}

const confirmarAccion = async () => {
    if (confirmacion.action === 'eliminar') {
        try {
            const respuesta = await fetch(`http://127.0.0.1:5000/api/usuarios/${confirmacion.usuarioId}`, {
                method: 'DELETE'
            })
            
            if (respuesta.ok) {
                cargarUsuariosDesdeAPI() // Recargamos la tabla
            } else {
                console.error("Error del servidor al intentar dar de baja")
            }
        } catch (error) {
            console.error("Error de red al intentar eliminar:", error)
        }
    }
    confirmacion.show = false
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
        <h1 class="h1-title">Gestión de Usuarios</h1>
        <p class="subtitle">Administra altas, bajas y sedes de trabajo.</p>
      </div>
      <button @click="abrirCrear" class="btn-primary">
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
                class="input-std pl-10"
            >
        </div>
    </div>

    <div class="card p-0 overflow-hidden relative min-h-[200px]">
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
                            <p class="font-bold text-dark">{{ user.nombre }}</p>
                            <span v-if="user.activo === 0 || user.activo === false" class="bg-red-100 text-red-600 text-[10px] px-2 py-0.5 rounded-full font-bold">Inactivo</span>
                        </div>
                        <p class="text-xs text-gray-400">{{ user.email }}</p>
                    </td>
                    <td class="px-6 py-4">
                        <span :class="obtenerEstiloRol(user.rol)" class="badge">
                            {{ user.rol }}
                        </span>
                    </td>
                    <td class="px-6 py-4 flex items-center gap-2 text-gray-600">
                        <MapPin class="w-4 h-4 text-gray-400"/> {{ user.sede }}
                    </td>
                    <td class="px-6 py-4 text-right">
                        <div class="flex items-center justify-end gap-2">
                            <button @click="abrirEditar(user)" class="btn-ghost text-blue-500 hover:text-blue-600">
                                <Pencil class="w-4 h-4"/>
                            </button>
                            <button v-if="user.activo !== 0 && user.activo !== false" @click="solicitarEliminacion(user.id)" class="btn-ghost text-red-400 hover:text-red-600">
                                <Trash2 class="w-4 h-4"/>
                            </button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div v-if="mostrarModal" class="fixed inset-0 bg-dark/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
        <div class="card w-full max-w-md space-y-5 shadow-2xl">
            
            <div class="flex justify-between items-center border-b border-gray-100 pb-3">
                <h3 class="font-bold text-lg text-dark">
                    {{ esEdicion ? 'Editar' : 'Nuevo' }} Usuario
                </h3>
                <button @click="mostrarModal = false" class="text-gray-400 hover:text-red-500 transition">
                    <X class="w-5 h-5"/>
                </button>
            </div>
            
            <div class="space-y-4">
                <div>
                    <label class="label-std">Nombre Completo</label>
                    <input v-model="formulario.nombre" class="input-std">
                </div>
                <div>
                    <label class="label-std">Email Corporativo / Azure ID</label>
                    <input v-model="formulario.email" class="input-std">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="label-std">Rol</label>
                        <select v-model="formulario.rol" class="input-std">
                            <option>Tecnico</option>
                            <option>JP</option>
                            <option>Admin</option>
                        </select>
                    </div>
                    <div>
                        <label class="label-std">Sede</label>
                        <select v-model="formulario.sede" class="input-std">
                            <option v-for="s in sedesDisponibles" :key="s" :value="s">{{ s }}</option>
                        </select>
                    </div>
                </div>
            </div>

            <div class="flex gap-3 pt-2">
                <button @click="mostrarModal = false" class="btn-secondary flex-1">Cancelar</button>
                <button @click="guardar" class="btn-primary flex-1">Guardar</button>
            </div>
        </div>
    </div>

    <div v-if="confirmacion.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
        <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
            <div class="flex flex-col items-center text-center gap-3">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2"
                     :class="confirmacion.type === 'danger' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'">
                    <component :is="confirmacion.type === 'danger' ? Trash2 : AlertTriangle" class="w-6 h-6" />
                </div>
                <h3 class="text-lg font-bold text-slate-900">{{ confirmacion.title }}</h3>
                <p class="text-sm text-slate-500 leading-relaxed">{{ confirmacion.message }}</p>
                
                <div class="flex gap-3 w-full mt-4">
                    <button @click="confirmacion.show = false" class="btn-secondary flex-1 justify-center">
                        Cancelar
                    </button>
                    <button @click="confirmarAccion" 
                            class="flex-1 justify-center btn-primary"
                            :class="confirmacion.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : 'bg-slate-700 hover:bg-slate-800'">
                        Confirmar
                    </button>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>
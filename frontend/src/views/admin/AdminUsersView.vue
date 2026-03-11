<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { 
    Plus, Pencil, Trash2, Search, MapPin, X, Save,
    AlertTriangle, CheckCircle2, AlertCircle
} from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()

const DEFAULT_FORM = {
    id: null,
    name: '',
    email: '',
    role: 'Técnico', 
    location: 'Tarragona',
    active: 1
}

const users = ref([])
const isLoading = ref(true)

const availableLocations = store.getSedes()
const searchQuery = ref('')

const showModal = ref(false)
const isEditing = ref(false)
const form = ref({ ...DEFAULT_FORM })

const confirmation = reactive({
    show: false,
    title: '',
    message: '',
    type: 'neutral',
    action: null,
    userId: null 
})

const fetchUsers = async () => {
    try {
        isLoading.value = true
        const res = await fetch('http://127.0.0.1:5000/api/admin/users')
        const json = await res.json()
        
        if (json.status === 'success' || res.ok) {
            const data = json.data || json
            users.value = data.map(u => ({
                id: u.id,
                name: u.name,
                email: u.email,
                role: u.role,
                location: u.location,
                active: u.active 
            }))
        } else {
            console.error("Error del servidor:", json.message)
        }
    } catch (error) {
        console.error("Error de red al conectar con la API:", error)
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    fetchUsers()
})

const filteredUsers = computed(() => {
    const text = searchQuery.value.toLowerCase().trim()
    if (!text) return users.value

    return users.value.filter(u => 
        u.name.toLowerCase().includes(text) ||
        u.email.toLowerCase().includes(text)
    )
})

const resetForm = () => {
    form.value = { ...DEFAULT_FORM, location: availableLocations[0] }
}

const openCreate = () => {
    isEditing.value = false
    resetForm()
    showModal.value = true
}

const openEdit = (user) => {
    isEditing.value = true
    form.value = { ...user }
    showModal.value = true
}

const saveUser = async () => {
    try {
        const method = isEditing.value ? 'PUT' : 'POST'
        const url = isEditing.value 
            ? `http://127.0.0.1:5000/api/admin/users/${form.value.id}`
            : 'http://127.0.0.1:5000/api/admin/users'
        
        const payload = {
            name: form.value.name,
            email: form.value.email,
            role: form.value.role,
            location: form.value.location
        }

        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        
        const result = await res.json()
        
        if (res.ok) {
            showModal.value = false
            await fetchUsers() 
        } else {
            console.error("Error del servidor:", result.message || result.error)
        }
    } catch (error) {
        console.error("Error de red al intentar guardar:", error)
    }
}

const requestAction = (id, mode) => {
    confirmation.userId = id
    confirmation.action = mode
    
    if (mode === 'toggle') {
        const user = users.value.find(u => u.id === id) || form.value
        if (user.active === 1 || user.active === true) {
            confirmation.title = 'Desactivar Acceso'
            confirmation.message = '¿Desactivar acceso a este usuario? Perderá acceso pero sus datos se conservarán.'
            confirmation.type = 'neutral'
        } else {
            confirmation.title = 'Reactivar Acceso'
            confirmation.message = '¿Deseas restaurar el acceso de este usuario al sistema?'
            confirmation.type = 'success'
        }
    } else {
        confirmation.title = 'Eliminar de la BD'
        confirmation.message = '¿Estás seguro? Esta acción borrará el registro físicamente de SQL Server.'
        confirmation.type = 'danger'
    }
    confirmation.show = true
}

const confirmAction = async () => {
    try {
        let res;
        
        if (confirmation.action === 'eliminar') {
            res = await fetch(`http://127.0.0.1:5000/api/admin/users/${confirmation.userId}/force`, {
                method: 'DELETE'
            });
        } else if (confirmation.action === 'toggle') {
            res = await fetch(`http://127.0.0.1:5000/api/admin/users/${confirmation.userId}/toggle`, {
                method: 'PUT'
            });
        }
        
        if (res && res.ok) {
            await fetchUsers(); 
            showModal.value = false; 
        } else {
            console.error("Error del servidor en la operación")
        }
    } catch (error) {
        console.error("Error de red en confirmAction:", error)
    }
    confirmation.show = false;
}

const getRoleStyle = (role) => {
    if (role === 'Admin' || role === 'Administrador') return 'bg-red-50 text-red-700 border-red-200'
    if (role === 'JP' || role === 'Jefe de Proyecto') return 'bg-amber-50 text-amber-700 border-amber-200'
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
      <button @click="openCreate" class="btn-primary flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition font-medium shadow-md">
        <Plus class="w-4 h-4" /> Nuevo Usuario
      </button>
    </div>

    <div class="card py-3">
        <div class="relative w-full max-w-sm">
            <Search class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="Buscar por nombre o Azure ID..." 
                class="input-std pl-10 border border-gray-300 rounded-lg w-full py-2 focus:ring-2 focus:ring-blue-500 outline-none"
            >
        </div>
    </div>

    <div class="card p-0 overflow-hidden relative min-h-[200px] bg-white border border-gray-200 rounded-xl shadow-sm">
        <div v-if="isLoading" class="absolute inset-0 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center z-10">
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
                <tr v-if="!isLoading && filteredUsers.length === 0">
                    <td colspan="4" class="px-6 py-8 text-center text-gray-400">
                        No se han encontrado usuarios.
                    </td>
                </tr>

                <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-slate-50 transition" :class="{'opacity-50': user.active === 0 || user.active === false}">
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-2">
                            <p class="font-bold text-slate-800" :class="{'line-through text-slate-400': user.active === 0 || user.active === false}">{{ user.name }}</p>
                            <span v-if="user.active === 0 || user.active === false" class="bg-red-100 text-red-600 border border-red-200 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase">Inactivo</span>
                        </div>
                        <p class="text-xs text-gray-400">{{ user.email }}</p>
                    </td>
                    <td class="px-6 py-4">
                        <span :class="getRoleStyle(user.role)" class="px-2 py-1 rounded-md text-[10px] font-bold uppercase border">
                            {{ user.role }}
                        </span>
                    </td>
                    <td class="px-6 py-4 flex items-center gap-2 text-gray-600">
                        <MapPin class="w-4 h-4 text-gray-400"/> {{ user.location }}
                    </td>
                    <td class="px-6 py-4 text-right">
                        <div class="flex items-center justify-end gap-2">
                            <button @click="openEdit(user)" class="p-2 text-gray-400 hover:text-blue-500 transition rounded-lg hover:bg-blue-50" title="Editar">
                                <Pencil class="w-4 h-4"/>
                            </button>
                            <button @click="requestAction(user.id, 'eliminar')" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 transition rounded-lg" title="Eliminar de BD">
                                <Trash2 class="w-4 h-4"/>
                            </button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
        <div class="bg-white rounded-2xl w-full max-w-md space-y-5 shadow-2xl p-6 border border-gray-100 animate-in zoom-in-95">
            
            <div class="flex justify-between items-center border-b border-gray-100 pb-3">
                <h3 class="font-bold text-lg text-slate-800">
                    {{ isEditing ? 'Editar' : 'Nuevo' }} Usuario
                </h3>
                <button @click="showModal = false" class="text-gray-400 hover:text-red-500 transition">
                    <X class="w-5 h-5"/>
                </button>
            </div>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Nombre Completo</label>
                    <input v-model="form.name" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Email Corporativo / Azure ID</label>
                    <input v-model="form.email" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Rol</label>
                        <select v-model="form.role" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                            <option>Técnico</option>
                            <option>JP</option>
                            <option>Admin</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Sede</label>
                        <select v-model="form.location" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                            <option v-for="s in availableLocations" :key="s" :value="s">{{ s }}</option>
                        </select>
                    </div>
                </div>

                <div v-if="isEditing" class="p-4 bg-gray-50 rounded-lg border border-gray-200 mt-2 flex items-center justify-between">
                    <div>
                        <p class="text-sm font-bold text-slate-700">Acceso al Sistema</p>
                        <p class="text-xs text-gray-500">Estado: <span class="font-bold" :class="(form.active === 1 || form.active === true) ? 'text-emerald-600' : 'text-red-600'">{{ (form.active === 1 || form.active === true) ? 'Activo' : 'Inactivo' }}</span></p>
                    </div>
                    <button @click.prevent="requestAction(form.id, 'toggle')"
                            class="px-3 py-1.5 rounded text-xs font-bold transition border"
                            :class="(form.active === 1 || form.active === true) ? 'bg-white border-red-200 text-red-600 hover:bg-red-50' : 'bg-white border-emerald-200 text-emerald-600 hover:bg-emerald-50'">
                        {{ (form.active === 1 || form.active === true) ? 'Desactivar Acceso' : 'Reactivar Acceso' }}
                    </button>
                </div>
            </div>

            <div class="flex gap-3 pt-2">
                <button @click="showModal = false" class="flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition">Cancelar</button>
                <button @click="saveUser" class="flex-1 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 shadow-lg shadow-blue-200 transition">Guardar</button>
            </div>
        </div>
    </div>

    <div v-if="confirmation.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
        <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
            <div class="flex flex-col items-center text-center gap-3">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2"
                     :class="confirmation.type === 'danger' ? 'bg-red-100 text-red-600' : (confirmation.type === 'success' ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-600')">
                    <component :is="confirmation.type === 'danger' ? Trash2 : (confirmation.type === 'success' ? CheckCircle2 : AlertTriangle)" class="w-6 h-6" />
                </div>
                <h3 class="text-lg font-bold text-slate-900">{{ confirmation.title }}</h3>
                <p class="text-sm text-slate-500 leading-relaxed">{{ confirmation.message }}</p>
                
                <div class="flex gap-3 w-full mt-4">
                    <button @click="confirmation.show = false" class="btn-secondary flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition justify-center">
                        Cancelar
                    </button>
                    <button @click="confirmAction" 
                            class="flex-1 py-2 text-white rounded-lg font-bold transition shadow-md justify-center"
                            :class="confirmation.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : (confirmation.type === 'success' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-slate-700 hover:bg-slate-800')">
                        Confirmar
                    </button>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>
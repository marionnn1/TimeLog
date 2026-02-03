<script setup>
import { ref, computed } from 'vue'
import { Plus, Pencil, Trash2, Search, MapPin, X, Save, Shield, Briefcase, User } from 'lucide-vue-next'

// 1. IMPORTAMOS EL STORE
import { useDataStore } from '../../stores/dataStore'

// 2. INICIALIZAMOS EL STORE
const store = useDataStore()

// 3. SUSTITUIMOS LOS DATOS HARDCODEADOS POR LOS DEL STORE
// const usuarios = ref([...])  <-- ESTO SE BORRA
const usuarios = computed(() => store.getUsers()) // Usamos computed para que sea reactivo
const sedesDisponibles = store.getSedes()

// --- LÓGICA DEL MODAL ---
const mostrarModal = ref(false)
const modoEdicion = ref(false)
const formulario = ref({ id: null, nombre: '', email: '', rol: 'Técnico', sede: 'Madrid' })

const abrirCrear = () => {
    modoEdicion.value = false
    // Cogemos la primera sede por defecto
    formulario.value = { id: null, nombre: '', email: '', rol: 'Técnico', sede: sedesDisponibles[0] }
    mostrarModal.value = true
}

const abrirEditar = (user) => {
    modoEdicion.value = true
    formulario.value = { ...user } // Copia para no editar en caliente
    mostrarModal.value = true
}

// 4. USAMOS LAS FUNCIONES DEL STORE PARA GUARDAR/BORRAR
const guardarUsuario = () => {
    if (modoEdicion.value) {
        store.updateUser(formulario.value)
    } else {
        store.addUser(formulario.value)
    }
    mostrarModal.value = false
}

const eliminarUsuario = (id) => {
    if (confirm('¿Seguro que deseas dar de baja a este usuario?')) {
        store.deleteUser(id)
    }
}

// --- FILTROS (Igual que antes) ---
const busqueda = ref('')
// Nota: como 'usuarios' ahora es un computed, accedemos con .value igualmente
const usuariosFiltrados = computed(() => {
    return usuarios.value.filter(u =>
        u.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) ||
        u.email.toLowerCase().includes(busqueda.value.toLowerCase())
    )
})

const getRolColor = (rol) => {
    if (rol === 'Administrador') return 'text-red-600 bg-red-50 border-red-200'
    if (rol === 'Jefe de Proyecto') return 'text-amber-600 bg-amber-50 border-amber-200'
    return 'text-blue-600 bg-blue-50 border-blue-200'
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto">
        <div class="flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-[#232D4B]">Gestión de Usuarios</h1>
                <p class="text-sm text-gray-500">Administra altas, bajas y sedes de trabajo.</p>
            </div>
            <button @click="abrirCrear"
                class="bg-[#26AA9B] text-white px-4 py-2 rounded-lg font-bold text-sm shadow hover:bg-[#1f8c7f] flex items-center gap-2">
                <Plus class="w-4 h-4" /> Nuevo Usuario
            </button>
        </div>

        <div class="bg-white p-3 rounded-xl border border-gray-200 shadow-sm">
            <div class="relative w-full max-w-sm">
                <Search class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                <input v-model="busqueda" type="text" placeholder="Buscar por nombre..."
                    class="pl-10 w-full border border-gray-300 rounded-lg p-2 text-sm outline-none focus:border-[#26AA9B]">
            </div>
        </div>

        <div class="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-gray-50 text-xs uppercase text-gray-500 border-b">
                    <tr>
                        <th class="px-6 py-4">Usuario</th>
                        <th class="px-6 py-4">Rol</th>
                        <th class="px-6 py-4">Sede / Ubicación</th>
                        <th class="px-6 py-4 text-right">Acciones</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-sm">
                    <tr v-for="user in usuariosFiltrados" :key="user.id" class="hover:bg-slate-50">
                        <td class="px-6 py-4 font-bold text-[#232D4B]">{{ user.nombre }} <br><span
                                class="text-xs font-normal text-gray-400">{{ user.email }}</span></td>
                        <td class="px-6 py-4"><span :class="getRolColor(user.rol)"
                                class="px-2 py-1 rounded-md text-xs font-bold border">{{ user.rol }}</span></td>
                        <td class="px-6 py-4 flex items-center gap-2 text-gray-600">
                            <MapPin class="w-4 h-4 text-gray-400" /> {{ user.sede }}
                        </td>
                        <td class="px-6 py-4 text-right">
                            <button @click="abrirEditar(user)" class="text-blue-500 hover:bg-blue-50 p-2 rounded mr-2">
                                <Pencil class="w-4 h-4" />
                            </button>
                            <button @click="eliminarUsuario(user.id)" class="text-red-500 hover:bg-red-50 p-2 rounded">
                                <Trash2 class="w-4 h-4" />
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="mostrarModal"
            class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 space-y-4">
                <div class="flex justify-between items-center border-b pb-3">
                    <h3 class="font-bold text-lg">{{ modoEdicion ? 'Editar' : 'Nuevo' }} Usuario</h3>
                    <button @click="mostrarModal = false">
                        <X class="w-5 h-5 text-gray-400" />
                    </button>
                </div>
                <input v-model="formulario.nombre" placeholder="Nombre Completo"
                    class="w-full border p-2 rounded outline-none focus:border-[#26AA9B]">
                <input v-model="formulario.email" placeholder="Email"
                    class="w-full border p-2 rounded outline-none focus:border-[#26AA9B]">
                <div class="grid grid-cols-2 gap-4">
                    <select v-model="formulario.rol" class="border p-2 rounded outline-none bg-white">
                        <option>Técnico</option>
                        <option>Jefe de Proyecto</option>
                        <option>Administrador</option>
                    </select>
                    <select v-model="formulario.sede" class="border p-2 rounded outline-none bg-white">
                        <option v-for="s in sedesDisponibles" :key="s" :value="s">{{ s }}</option>
                    </select>
                </div>
                <button @click="guardarUsuario"
                    class="w-full bg-[#26AA9B] text-white py-2 rounded font-bold hover:opacity-90">Guardar</button>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ShieldCheck, LogIn, Users, Loader2, UserPlus } from 'lucide-vue-next'
import { useDataStore } from '../stores/dataStore'

const router = useRouter()
const store = useDataStore()

const usuariosValidos = ref([])
const cargando = ref(true)

// Cargamos los usuarios reales de la base de datos
const cargarUsuarios = async () => {
    try {
        cargando.value = true
        const res = await fetch('http://localhost:5000/api/usuarios')
        const json = await res.json()
        if (json.status === 'success') {
            usuariosValidos.value = json.data
        }
    } catch (error) {
        console.error("Error al conectar con el backend:", error)
    } finally {
        cargando.value = false
    }
}

onMounted(cargarUsuarios)

const entrarComo = (user) => {
    // Mapeamos los campos de la BD al objeto que espera la app
    const usuarioParaStore = {
        id: user.Id,
        nombre: user.Nombre,
        email: user.OidAzure || 'test@inetum.com',
        rol: user.Rol.toLowerCase(), // 'admin', 'jp' o 'tecnico'
        iniciales: user.Nombre.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2),
        sede: user.Sede
    }

    store.setCurrentUser(usuarioParaStore)
    localStorage.setItem('isAuthenticated', 'true')
    router.push('/')
}
</script>

<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-slate-50 font-sans">
    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-slate-100">
      
      <div class="text-center mb-8">
        <div class="inline-flex p-3 bg-[#002B49] rounded-xl mb-4 shadow-lg">
            <ShieldCheck class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-[#002B49]">TimeLog Login</h1>
        <p class="text-slate-500 text-sm mt-1">Selecciona un usuario para entrar</p>
      </div>

      <div v-if="cargando" class="flex flex-col items-center py-10">
        <Loader2 class="w-8 h-8 text-blue-600 animate-spin mb-2" />
        <p class="text-xs text-slate-400 font-bold uppercase">Consultando base de datos...</p>
      </div>

      <div v-else-if="usuariosValidos.length > 0" class="space-y-3 max-h-80 overflow-y-auto pr-1">
        <button v-for="user in usuariosValidos" :key="user.Id"
                @click="entrarComo(user)"
                class="w-full flex items-center gap-4 p-4 rounded-xl border border-slate-100 bg-slate-50 hover:bg-white hover:border-blue-400 hover:shadow-md transition-all group text-left">
          
          <div class="w-10 h-10 rounded-full bg-[#002B49] text-white flex items-center justify-center font-bold text-sm">
            {{ user.Nombre.substring(0,2).toUpperCase() }}
          </div>
          
          <div class="flex-1">
            <p class="font-bold text-slate-800">{{ user.Nombre }}</p>
            <span class="text-[10px] font-black uppercase px-1.5 py-0.5 rounded border"
                  :class="user.Rol === 'Admin' ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-600'">
                {{ user.Rol }}
            </span>
          </div>
          <LogIn class="w-4 h-4 text-slate-300 group-hover:text-blue-500" />
        </button>
      </div>

      <div v-else class="text-center py-6">
        <p class="text-sm text-slate-500">No hay usuarios. Créalos en la vista de Admin.</p>
      </div>

    </div>
  </div>
</template>
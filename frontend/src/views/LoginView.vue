<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ShieldCheck, LogIn, Users, Loader2, UserPlus } from 'lucide-vue-next'
import { useDataStore } from '../stores/dataStore'

const router = useRouter()
const store = useDataStore()

const validUsers = ref([])
const isLoading = ref(true)

const fetchUsers = async () => {
    try {
        isLoading.value = true
        const res = await fetch('http://127.0.0.1:5000/api/admin/users')
        if (!res.ok) throw new Error("Error en la respuesta del servidor")
        
        const json = await res.json()
        const data = json.data || json
        
        // Filtramos para asegurar que mapeamos bien (aceptando tanto SQL directo como el estandarizado)
        if (data && data.length > 0) {
            validUsers.value = data
        }
    } catch (error) {
        console.error("Error al conectar con el backend:", error)
    } finally {
        isLoading.value = false
    }
}

onMounted(fetchUsers)

const loginAs = (user) => {
    // Mapeamos los campos tolerando tanto el formato antiguo (Español/PascalCase) como el nuevo (Inglés)
    const userDataForStore = {
        id: user.id || user.Id,
        name: user.name || user.Nombre,
        email: user.email || user.OidAzure || 'user@inetum.com',
        role: (user.role || user.Rol || '').toLowerCase(), 
        initials: (user.name || user.Nombre || '').split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2),
        location: user.location || user.Sede
    }

    store.setCurrentUser(userDataForStore)
    localStorage.setItem('isAuthenticated', 'true') // Necesario si tienes guardia en el router
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
        <p class="text-slate-500 text-sm mt-1">Selecciona un perfil para acceder</p>
      </div>

      <div v-if="isLoading" class="flex flex-col items-center py-10">
        <Loader2 class="w-8 h-8 text-blue-600 animate-spin mb-2" />
        <p class="text-xs text-slate-400 font-bold uppercase">Conectando...</p>
      </div>

      <div v-else-if="validUsers.length > 0" class="space-y-3 max-h-80 overflow-y-auto pr-1 custom-scrollbar">
        <button v-for="user in validUsers" :key="user.id || user.Id"
                @click="loginAs(user)"
                class="w-full flex items-center gap-4 p-4 rounded-xl border border-slate-100 bg-slate-50 hover:bg-white hover:border-blue-400 hover:shadow-md transition-all group text-left">
          
          <div class="w-10 h-10 rounded-full bg-[#002B49] text-white flex items-center justify-center font-bold text-sm">
            {{ (user.name || user.Nombre).substring(0,2).toUpperCase() }}
          </div>
          
          <div class="flex-1">
            <p class="font-bold text-slate-800">{{ user.name || user.Nombre }}</p>
            <span class="text-[10px] font-black uppercase px-1.5 py-0.5 rounded border"
                  :class="((user.role || user.Rol) || '').toLowerCase() === 'admin' ? 'bg-red-50 text-red-600 border-red-100' : 'bg-blue-50 text-blue-600 border-blue-100'">
                {{ user.role || user.Rol }}
            </span>
          </div>
          <LogIn class="w-4 h-4 text-slate-300 group-hover:text-blue-500 transition-colors" />
        </button>
      </div>

      <div v-else class="text-center py-6">
        <p class="text-sm text-slate-500 italic">No hay usuarios registrados.</p>
        <p class="text-xs text-slate-400 mt-2">Contacta con soporte o revisa la base de datos.</p>
      </div>

    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
</style>
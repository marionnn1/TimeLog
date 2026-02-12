<script setup>
import { useRouter } from 'vue-router'
import { ShieldCheck, LogIn } from 'lucide-vue-next'
import { useDataStore } from '../stores/dataStore'

const router = useRouter()
const store = useDataStore()

// --- BYPASS DE LOGIN (SIN AZURE) ---
const iniciarSesion = () => {
  // 1. Creamos un usuario ficticio
  const usuarioSimulado = {
    id: 1,
    nombre: 'Mario León',
    email: 'mario.leon@inetum.com',
    rol: 'admin',
    iniciales: 'ML',
    oid_azure: 'local-dev-id'
  }

  // 2. Guardamos en el Store
  store.setCurrentUser(usuarioSimulado)
  
  // 3. Guardamos la "cookie" falsa
  localStorage.setItem('isAuthenticated', 'true')

  // 4. Redirigimos
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-slate-50 relative overflow-hidden">
    
    <div class="absolute -top-24 -right-24 w-96 h-96 bg-[#002B49]/10 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-blue-900/10 rounded-full blur-3xl pointer-events-none"></div>

    <div class="bg-white p-10 rounded-2xl shadow-xl shadow-slate-200/50 w-full max-w-sm border border-slate-100 relative z-10 text-center">
      
      <div class="flex flex-col items-center justify-center mb-8">
        <div class="p-3 bg-[#002B49] rounded-xl mb-3 shadow-lg shadow-slate-300">
            <ShieldCheck class="w-10 h-10 text-white" />
        </div>
        
        <h1 class="text-3xl font-bold text-[#002B49] tracking-tight">TimeLog</h1>
        
        <div class="mt-2 px-3 py-1 bg-slate-100 rounded-full border border-slate-200">
            <p class="text-slate-500 text-[10px] font-bold uppercase tracking-widest">
                Modo Desarrollo
            </p>
        </div>
      </div>

      <div class="my-8">
        <button @click="iniciarSesion" 
                class="w-full flex items-center justify-center gap-3 bg-[#002B49] hover:bg-[#001a2c] text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-300 shadow-md hover:shadow-lg hover:shadow-blue-900/20 transform hover:-translate-y-0.5 group">
          
          <LogIn class="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
          
          <span>Entrar al Sistema</span>
        </button>
      </div>

      <div class="border-t border-slate-100 my-6"></div>

      <div class="flex justify-center hover:opacity-80 transition duration-300">
         <img src="/INETUM_LOGO.png" alt="Inetum" class="h-8 w-auto object-contain" />
      </div>

      <p class="mt-6 text-center text-[10px] text-slate-400">
        &copy; {{ new Date().getFullYear() }} Inetum. Entorno Local.
      </p>

    </div>
  </div>
</template>
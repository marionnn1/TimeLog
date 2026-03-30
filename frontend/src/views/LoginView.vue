<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ShieldCheck, LogIn, Loader2 } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login, handleRedirect } = useAuth()
const cargando = ref(true)

onMounted(async () => {
    // Al cargar la vista, comprobamos si venimos rebotados de Microsoft tras hacer login
    const loggedIn = await handleRedirect()
    
    if (loggedIn) {
        // Si el login fue exitoso, redirigimos al dashboard
        router.push('/')
    } else {
        // Si no venimos de un login, mostramos el botón para iniciar sesión
        cargando.value = false
    }
})

const iniciarSesionMicrosoft = () => {
    cargando.value = true
    login() // Llama a MSAL para redirigir a la pasarela de Microsoft
}
</script>

<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-slate-50 font-sans">
    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-slate-100">
      
      <div class="text-center mb-8">
        <div class="inline-flex p-3 bg-[#002B49] rounded-xl mb-4 shadow-lg">
            <ShieldCheck class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-[#002B49]">TimeLog</h1>
        <p class="text-slate-500 text-sm mt-1">Inicia sesión con tu cuenta corporativa</p>
      </div>

      <div v-if="cargando" class="flex flex-col items-center py-10">
        <Loader2 class="w-8 h-8 text-blue-600 animate-spin mb-2" />
        <p class="text-xs text-slate-400 font-bold uppercase">Autenticando...</p>
      </div>

      <div v-else class="text-center py-6">
        <button @click="iniciarSesionMicrosoft"
                class="w-full flex items-center justify-center gap-3 p-4 rounded-xl bg-[#002B49] text-white hover:bg-blue-900 transition-all font-bold shadow-md">
          <LogIn class="w-5 h-5" />
          Iniciar sesión con Microsoft
        </button>
      </div>

    </div>
  </div>
</template>
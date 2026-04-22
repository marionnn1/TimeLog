<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ShieldCheck, LogIn, Loader2 } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login, handleRedirect, state } = useAuth()

const cargando = ref(true)
const isSubmitting = ref(false) // NUEVA VARIABLE PARA EL BOTÓN

onMounted(async () => {
  try {
    const handled = await handleRedirect()

    if (handled || state.isAuthenticated) {
      router.push('/')
    }
  } catch (error) {
    console.error("Error al procesar el retorno de Microsoft:", error)
  } finally {
    cargando.value = false
  }
})

const iniciarSesion = async () => {
  // Evitar doble clic
  if (isSubmitting.value) return 
  
  isSubmitting.value = true
  
  try {
    await login()
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-slate-50 font-sans">
    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-slate-100 text-center">

      <div class="mb-8">
        <div class="inline-flex p-3 bg-[#002B49] rounded-xl mb-4 shadow-lg">
          <ShieldCheck class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-[#002B49]">TimeLog</h1>
        <p class="text-slate-500 text-sm mt-1">Inicia sesión con tu cuenta corporativa</p>
      </div>

      <div v-if="cargando" class="flex flex-col items-center py-10">
        <Loader2 class="w-8 h-8 text-blue-600 animate-spin mb-4" />
        <p class="text-xs text-slate-400 font-bold uppercase tracking-wider">Verificando credenciales...</p>
      </div>

      <div v-else class="space-y-4">
        <button @click="iniciarSesion"
          :disabled="isSubmitting"
          class="w-full flex items-center justify-center gap-3 p-4 rounded-xl text-white transition-all shadow-md font-bold"
          :class="isSubmitting ? 'bg-slate-400 cursor-not-allowed' : 'bg-[#002B49] hover:bg-[#00406d] hover:shadow-lg'">
          
          <svg v-if="isSubmitting" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <LogIn v-else class="w-5 h-5" />

          <span>{{ isSubmitting ? 'Conectando...' : 'Entrar con Microsoft' }}</span>
        </button>
      </div>

    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ShieldCheck, LogIn, Loader2 } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login, handleRedirect, state } = useAuth()
const cargando = ref(true)

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
  cargando.value = true
  await login()

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
          class="w-full flex items-center justify-center gap-3 p-4 rounded-xl bg-[#002B49] text-white hover:bg-[#00406d] transition-all shadow-md hover:shadow-lg font-bold">
          <LogIn class="w-5 h-5" />
          <span>Entrar con Microsoft</span>
        </button>
      </div>

    </div>
  </div>
</template>
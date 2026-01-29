<script setup>
import { ref, onMounted } from 'vue'

// Variable reactiva para el mensaje
const mensajeBackend = ref('Cargando respuesta...')

onMounted(async () => {
  try {
    // Intentamos conectar con tu Flask
    const res = await fetch('http://127.0.0.1:5000/api/test')
    const data = await res.json()
    mensajeBackend.value = data.mensaje
  } catch (error) {
    mensajeBackend.value = '❌ Error: No se puede conectar con Flask'
    console.error(error)
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
    
    <div class="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full text-center border border-gray-200">
      <h1 class="text-3xl font-bold text-blue-600 mb-2">
        TimeLog
      </h1>
      <p class="text-gray-500 mb-6">Panel de Control de Vulnerabilidades</p>

      <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
        <p class="text-sm font-bold text-gray-400 uppercase tracking-wide">Estado del Backend</p>
        <p class="text-xl mt-1 font-semibold text-green-600">
          {{ mensajeBackend }}
        </p>
      </div>

      <button class="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-200">
        ¡Botón Tailwind!
      </button>
    </div>

  </div>
</template>
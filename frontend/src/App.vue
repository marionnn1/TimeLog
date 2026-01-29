<script setup>
import { ref, onMounted } from 'vue'

// 1. Preparamos una variable reactiva para guardar el mensaje
const mensajeBackend = ref('Esperando respuesta del servidor...')
const estado = ref('cargando') // para cambiar el color

// 2. Esta función se ejecuta sola cuando la página se carga
onMounted(async () => {
  try {
    // Intentamos llamar a tu Backend (Flask)
    const respuesta = await fetch('http://127.0.0.1:5000/api/test')
    
    // Si responde, convertimos la respuesta a texto/json
    const datos = await respuesta.json()
    
    // Guardamos el mensaje que nos envió Python
    mensajeBackend.value = datos.mensaje
    estado.value = 'exito'
    
  } catch (error) {
    console.error("Error conectando:", error)
    mensajeBackend.value = '❌ Error: No se puede conectar con Flask. ¿Está encendido?'
    estado.value = 'error'
  }
})
</script>

<template>
  <div class="contenedor">
    <h1>Prueba de Conexión</h1>
    
    <div :class="['caja', estado]">
      <p>Estado del Backend:</p>
      <h2>{{ mensajeBackend }}</h2>
    </div>
  </div>
</template>

<style scoped>
/* Un poco de estilo para que no se vea feo */
.contenedor {
  font-family: sans-serif;
  text-align: center;
  margin-top: 50px;
}
.caja {
  padding: 20px;
  border-radius: 10px;
  border: 2px solid #ccc;
  display: inline-block;
  margin-top: 20px;
}
.caja.cargando { background-color: #f0f0f0; color: #555; }
.caja.exito { background-color: #d4edda; border-color: #c3e6cb; color: #155724; }
.caja.error { background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; }
</style>
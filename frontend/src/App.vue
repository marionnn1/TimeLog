<script setup>
import SideBar from './components/layout/SideBar.vue'
import { useRoute } from 'vue-router'

// Truco para ocultar el menú si estamos en el Login (lo veremos más adelante)
// De momento asumimos que siempre se ve.
</script>

<template>
  <div class="flex min-h-screen bg-gray-100 font-sans">
    
    <SideBar />

    <main class="flex-1 p-8">
      <router-view />
    </main>

  </div>
</template>
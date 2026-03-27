<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import SideBar from './components/layout/SideBar.vue'

const route = useRoute()

const showSidebar = computed(() => route.meta.layout !== 'empty')
</script>

<template>
  <div class="flex h-screen w-full bg-gray-100 overflow-hidden font-sans">
    
    <SideBar v-if="showSidebar" />

    <main class="flex-1 h-full overflow-hidden relative flex flex-col">
      <router-view />
    </main>

  </div>
</template>
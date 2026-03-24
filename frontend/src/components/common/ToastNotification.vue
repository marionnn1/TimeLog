<script setup>
import { CheckCircle2, AlertCircle, X } from 'lucide-vue-next'

defineProps({
    show: { type: Boolean, required: true },
    message: { type: String, required: true },
    type: { type: String, default: 'success' } // 'success' o 'error'
})

defineEmits(['close'])
</script>

<template>
    <transition 
        enter-active-class="transform ease-out duration-300 transition" 
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2" 
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" 
        leave-active-class="transition ease-in duration-100" 
        leave-from-class="opacity-100" 
        leave-to-class="opacity-0">
        
        <div v-if="show" class="fixed bottom-6 right-6 z-[200] flex items-center w-full max-w-xs p-4 space-x-3 text-slate-600 bg-white rounded-xl shadow-2xl border border-gray-100">
            <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg" 
                 :class="type === 'success' ? 'text-emerald-500 bg-emerald-100' : 'text-red-500 bg-red-100'">
                <component :is="type === 'success' ? CheckCircle2 : AlertCircle" class="w-5 h-5"/>
            </div>
            <div class="ml-3 text-sm font-bold text-slate-800">{{ message }}</div>
            <button @click="$emit('close')" class="ml-auto bg-white text-gray-400 hover:text-gray-900 rounded-lg p-1.5 hover:bg-gray-100 transition">
                <X class="w-4 h-4"/>
            </button>
        </div>
    </transition>
</template>
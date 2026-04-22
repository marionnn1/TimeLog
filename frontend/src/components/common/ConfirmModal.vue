<script setup>
import { ref, watch } from 'vue'
import { Trash2, AlertTriangle, CheckCircle2 } from 'lucide-vue-next'

const props = defineProps({
    show: { type: Boolean, required: true },
    title: { type: String, required: true },
    message: { type: String, required: true },
    type: { type: String, default: 'neutral' },
    inputMode: { type: Boolean, default: false }, 
    inputPlaceholder: { type: String, default: 'Escribe aquí...' },
    isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'cancel'])
const inputValue = ref('')

watch(() => props.show, (newVal) => {
    if (newVal) inputValue.value = ''
})
</script>

<template>
    <div v-if="show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[70] p-4">
        <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
            <div class="flex flex-col items-center text-center gap-3">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2"
                     :class="type === 'danger' ? 'bg-red-100 text-red-600' : (type === 'success' ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600')">
                    <component :is="type === 'danger' ? Trash2 : (type === 'success' ? CheckCircle2 : AlertTriangle)" class="w-6 h-6" />
                </div>
                <h3 class="text-lg font-bold text-slate-900">{{ title }}</h3>
                <p class="text-sm text-slate-500 leading-relaxed">{{ message }}</p>
                
                <div v-if="inputMode" class="w-full mt-2">
                    <input v-model="inputValue" type="text" :placeholder="inputPlaceholder" class="w-full border border-gray-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" autofocus>
                </div>

                <div class="flex gap-3 w-full mt-4">
                    <button @click="$emit('cancel')" :disabled="isLoading" class="btn-secondary flex-1 justify-center py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition disabled:opacity-50">
                        Cancelar
                    </button>
                    <button @click="$emit('confirm', inputValue)" 
                            :disabled="isLoading"
                            class="flex-1 py-2 text-white rounded-lg font-bold transition shadow-md flex items-center justify-center gap-2"
                            :class="[
                                type === 'danger' ? 'bg-red-600 hover:bg-red-700' : (type === 'success' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-amber-600 hover:bg-amber-700'),
                                isLoading ? 'opacity-70 cursor-not-allowed' : ''
                            ]">
                        
                        <svg v-if="isLoading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>

                        {{ isLoading ? 'Procesando...' : 'Confirmar' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
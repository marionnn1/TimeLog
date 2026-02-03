<script setup>
import { ref } from 'vue'
import { Megaphone, AlertTriangle, Info, Save, CheckCircle } from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()
const anuncio = ref({ ...store.getAnuncio() })
const guardado = ref(false)

const guardarAnuncio = () => {
    store.updateAnuncio(anuncio.value)
    guardado.value = true
    setTimeout(() => guardado.value = false, 3000)
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto">

        <div>
            <h1 class="h1-title flex items-center gap-2">
                <Megaphone class="w-6 h-6 text-primary" /> Gestión de Anuncios
            </h1>
            <p class="subtitle">Configura el banner global.</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">

            <div class="card space-y-6">
                <h3 class="font-bold text-lg text-dark border-b border-gray-100 pb-2">Configuración</h3>

                <div>
                    <label class="label-std">Mensaje</label>
                    <textarea v-model="anuncio.mensaje" rows="4" class="input-std resize-none"></textarea>
                </div>

                <div class="flex flex-col sm:flex-row gap-4">
                    <div class="flex-1">
                        <label class="label-std">Tipo</label>
                        <select v-model="anuncio.tipo" class="input-std">
                            <option value="info">ℹ️ Información (Azul)</option>
                            <option value="warning">⚠️ Alerta (Naranja)</option>
                        </select>
                    </div>

                    <div class="flex-1 flex items-end">
                        <label
                            class="flex items-center gap-3 cursor-pointer bg-gray-50 px-4 py-2.5 rounded-lg border border-gray-200 hover:bg-gray-100 transition w-full">
                            <input type="checkbox" v-model="anuncio.activo"
                                class="w-5 h-5 text-primary rounded focus:ring-primary">
                            <span class="text-sm font-bold text-dark">Activo</span>
                        </label>
                    </div>
                </div>

                <div class="pt-4 flex items-center justify-between">
                    <span v-if="guardado"
                        class="text-emerald-600 text-sm font-bold flex items-center gap-1 animate-pulse">
                        <CheckCircle class="w-4 h-4" /> Publicado
                    </span>
                    <span v-else></span>

                    <button @click="guardarAnuncio" class="btn-primary">
                        <Save class="w-4 h-4" /> Guardar y Publicar
                    </button>
                </div>
            </div>

            <div
                class="bg-gray-100 p-6 rounded-xl border border-dashed border-gray-300 flex flex-col items-center justify-center min-h-[300px] relative">
                <div class="absolute top-4 left-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Vista
                    Previa</div>

                <div class="w-full max-w-md bg-slate-900 rounded-t-lg p-3 flex items-center gap-3 opacity-90">
                    <div class="w-3 h-3 rounded-full bg-red-500"></div>
                    <div class="w-3 h-3 rounded-full bg-amber-500"></div>
                    <div class="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
                <div
                    class="w-full max-w-md bg-white shadow-xl rounded-b-lg overflow-hidden pb-10 border border-gray-200">
                    <div v-if="anuncio.activo" class="p-4 flex items-start gap-3 border-b"
                        :class="anuncio.tipo === 'warning' ? 'bg-amber-50 border-amber-100 text-amber-900' : 'bg-blue-50 border-blue-100 text-blue-900'">
                        <AlertTriangle v-if="anuncio.tipo === 'warning'" class="w-5 h-5 shrink-0 mt-0.5" />
                        <Info v-else class="w-5 h-5 shrink-0 mt-0.5" />
                        <span class="text-sm font-medium leading-snug">{{ anuncio.mensaje }}</span>
                    </div>
                    <div class="p-6 space-y-4 opacity-30 blur-[1px]">
                        <div class="h-4 bg-gray-200 rounded w-1/3"></div>
                        <div class="h-32 bg-gray-100 rounded border border-gray-200"></div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>
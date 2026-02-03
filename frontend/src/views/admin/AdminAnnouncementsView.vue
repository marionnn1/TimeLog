<script setup>
import { ref, onMounted } from 'vue'
import { Megaphone, AlertTriangle, Info, Save, CheckCircle } from 'lucide-vue-next'
// 1. IMPORTAR STORE
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()

// 2. CARGAR DATOS DEL STORE
// Creamos una copia local para editar el formulario sin cambiar el store en tiempo real (hasta que le den a guardar)
const anuncio = ref({ ...store.getAnuncio() })

const guardado = ref(false)

const guardarAnuncio = () => {
    // 3. ACTUALIZAR EL STORE AL GUARDAR
    store.updateAnuncio(anuncio.value)

    guardado.value = true
    setTimeout(() => guardado.value = false, 3000)
}
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-6 gap-6 overflow-y-auto">

        <div>
            <h1 class="text-2xl font-bold text-[#232D4B] flex items-center gap-2">
                <Megaphone class="w-6 h-6 text-[#26AA9B]" /> Gestión de Anuncios
            </h1>
            <p class="text-sm text-gray-500 mt-1">Configura el banner global.</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">

            <div class="bg-white p-6 rounded-xl shadow-lg border border-gray-200 space-y-6">
                <h3 class="font-bold text-lg text-slate-700 border-b pb-2">Configuración</h3>

                <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Mensaje</label>
                    <textarea v-model="anuncio.mensaje" rows="4"
                        class="w-full border border-gray-300 rounded-lg p-3 text-sm focus:border-[#26AA9B] outline-none shadow-sm resize-none"></textarea>
                </div>

                <div class="flex flex-col sm:flex-row gap-4">
                    <div class="flex-1">
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Tipo</label>
                        <select v-model="anuncio.tipo"
                            class="w-full border border-gray-300 rounded-lg p-2.5 text-sm outline-none bg-white">
                            <option value="info">ℹ️ Información (Azul)</option>
                            <option value="warning">⚠️ Alerta (Naranja)</option>
                        </select>
                    </div>

                    <div class="flex-1 flex items-end">
                        <label
                            class="flex items-center gap-3 cursor-pointer bg-gray-50 px-4 py-2.5 rounded-lg border border-gray-200 hover:bg-gray-100 transition w-full">
                            <input type="checkbox" v-model="anuncio.activo"
                                class="w-5 h-5 text-[#26AA9B] rounded focus:ring-[#26AA9B]">
                            <span class="text-sm font-bold text-slate-700">Activo</span>
                        </label>
                    </div>
                </div>

                <div class="pt-4 flex items-center justify-between">
                    <span v-if="guardado"
                        class="text-emerald-600 text-sm font-bold flex items-center gap-1 animate-pulse">
                        <CheckCircle class="w-4 h-4" /> Publicado
                    </span>
                    <span v-else></span>

                    <button @click="guardarAnuncio"
                        class="bg-[#26AA9B] text-white px-6 py-2 rounded-lg font-bold text-sm shadow-md hover:opacity-90 transition flex items-center gap-2">
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
<script setup>
import { ref, computed } from 'vue'
import { FolderPlus, Trash2, Tag, X } from 'lucide-vue-next'
// 1. IMPORTAR STORE
import { useDataStore } from '../../stores/dataStore'

// 2. USAR STORE
const store = useDataStore()

// 3. SUSTITUIR DATOS LOCALES POR LOS DEL STORE
// Usamos computed para que si otra persona (o el sistema) añade un proyecto, se vea aquí.
const proyectos = computed(() => store.getProjects())

const mostrarModal = ref(false)
const nuevoProyecto = ref({ nombre: '', cliente: '', estado: 'Activo' })

const guardarProyecto = () => {
    // 4. GUARDAR EN EL STORE
    store.addProject(nuevoProyecto.value)

    mostrarModal.value = false
    nuevoProyecto.value = { nombre: '', cliente: '', estado: 'Activo' }
}

const eliminarProyecto = (id) => {
    if (confirm('¿Eliminar este proyecto y sus imputaciones asociadas?')) {
        // 5. BORRAR DEL STORE
        store.deleteProject(id)
    }
}
</script>

<template>
    <div class="h-full p-6 bg-gray-50 flex flex-col gap-6 font-sans">

        <div class="flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-[#232D4B]">Administrar Proyectos</h1>
                <p class="text-sm text-gray-500">Crea o cierra proyectos para imputación.</p>
            </div>
            <button @click="mostrarModal = true"
                class="bg-[#26AA9B] text-white px-4 py-2 rounded-lg font-bold text-sm shadow hover:bg-[#1f8c7f] flex items-center gap-2">
                <FolderPlus class="w-4 h-4" /> Nuevo Proyecto
            </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="proy in proyectos" :key="proy.id"
                class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 group hover:border-[#26AA9B] transition relative">

                <div class="flex justify-between items-start mb-2">
                    <div class="bg-gray-100 p-2 rounded-lg text-slate-500">
                        <Tag class="w-5 h-5" />
                    </div>
                    <span class="px-2 py-1 rounded text-xs font-bold uppercase"
                        :class="proy.estado === 'Activo' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'">
                        {{ proy.estado }}
                    </span>
                </div>

                <h3 class="font-bold text-lg text-slate-800">{{ proy.nombre }}</h3>
                <p class="text-sm text-gray-500 mb-4">{{ proy.cliente }}</p>

                <button @click="eliminarProyecto(proy.id)"
                    class="absolute bottom-4 right-4 text-gray-300 hover:text-red-500 transition">
                    <Trash2 class="w-4 h-4" />
                </button>
            </div>
        </div>

        <div v-if="mostrarModal"
            class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6 space-y-4">
                <div class="flex justify-between items-center border-b pb-2">
                    <h3 class="font-bold text-lg">Nuevo Proyecto</h3>
                    <button @click="mostrarModal = false">
                        <X class="w-5 h-5 text-gray-400" />
                    </button>
                </div>

                <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre Proyecto</label>
                    <input v-model="nuevoProyecto.nombre"
                        class="w-full border p-2 rounded outline-none focus:border-[#26AA9B]">
                </div>

                <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Cliente</label>
                    <input v-model="nuevoProyecto.cliente"
                        class="w-full border p-2 rounded outline-none focus:border-[#26AA9B]">
                </div>

                <div class="flex gap-2 pt-2">
                    <button @click="mostrarModal = false"
                        class="flex-1 bg-gray-100 py-2 rounded font-bold text-gray-600">Cancelar</button>
                    <button @click="guardarProyecto"
                        class="flex-1 bg-[#26AA9B] text-white py-2 rounded font-bold">Crear</button>
                </div>
            </div>
        </div>
    </div>
</template>
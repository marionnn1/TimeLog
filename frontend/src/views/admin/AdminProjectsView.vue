<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { 
    FolderPlus, Pencil, Tag, X, Briefcase, Users, Check, 
    CheckCircle2, AlertCircle, Trash2, AlertTriangle
} from 'lucide-vue-next'
import { useDataStore } from '../../stores/dataStore'

const store = useDataStore()

const FORM_DEFAULT = {
    id: null,
    name: '',
    client: '',
    status: 'Activo', 
    team: []
}

const projects = ref([])
const availableUsers = ref([])
const isLoading = ref(true)

const showModal = ref(false)
const isEditing = ref(false)
const form = ref({ ...FORM_DEFAULT })

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const confirmation = reactive({
    show: false,
    title: '',
    message: '',
    type: 'neutral',
    projectId: null,
    mode: '' 
})

const fetchData = async () => {
    try {
        isLoading.value = true

        const resProj = await fetch('http://localhost:5000/api/admin/projects')
        const jsonProj = await resProj.json()
        
        if (jsonProj.status === 'success' || resProj.ok) {
            const dataProj = jsonProj.data || jsonProj
            projects.value = dataProj.map(p => ({
                id: p.id,
                name: p.name,
                client: p.client,
                status: p.status,
                team: p.team ? p.team.map(u => ({
                    id: u.id,
                    name: u.name,
                    initials: u.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2),
                    color: 'bg-indigo-100 text-indigo-700'
                })) : []
            }))
        }

        const resUser = await fetch('http://localhost:5000/api/admin/users')
        const jsonUser = await resUser.json()
        
        if (jsonUser.status === 'success' || resUser.ok) {
            const dataUser = jsonUser.data || jsonUser
            availableUsers.value = dataUser.map(u => ({
                id: u.id,
                name: u.name,
                initials: u.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2),
                color: 'bg-indigo-100 text-indigo-700'
            }))
        }
    } catch (error) {
        showToast('Error al conectar con el servidor', 'error')
    } finally {
        isLoading.value = false
    }
}

onMounted(fetchData)

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => toast.value.show = false, 3000)
}

const openCreate = () => {
    isEditing.value = false
    form.value = { ...FORM_DEFAULT }
    showModal.value = true
}

const openEdit = (project) => {
    isEditing.value = true
    form.value = { 
        ...project, 
        team: project.team ? [...project.team] : [] 
    }
    showModal.value = true
}

const saveProject = async () => {
    try {
        const method = isEditing.value ? 'PUT' : 'POST'
        const url = isEditing.value 
            ? `http://localhost:5000/api/admin/projects/${form.value.id}`
            : 'http://localhost:5000/api/admin/projects'

        const payload = {
            name: form.value.name,
            client: form.value.client,
            status: form.value.status,
            user_ids: form.value.team.map(u => u.id) 
        }

        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        
        if (res.ok) {
            showModal.value = false
            await fetchData()
            showToast(isEditing.value ? 'Proyecto actualizado' : 'Proyecto creado')
        } else {
            showToast('Error en la respuesta del servidor', 'error')
        }
    } catch (error) {
        showToast('Error al guardar', 'error')
    }
}

const requestAction = (id, mode) => {
    confirmation.projectId = id
    confirmation.mode = mode
    
    if (mode === 'toggle') {
        const proj = projects.value.find(p => p.id === id) || form.value
        if (proj.status === 'Activo') {
            confirmation.title = 'Cerrar Proyecto'
            confirmation.message = '¿Deseas marcar este proyecto como Cerrado? Ya no admitirá imputaciones.'
            confirmation.type = 'neutral'
        } else {
            confirmation.title = 'Reabrir Proyecto'
            confirmation.message = '¿Deseas volver a activar este proyecto? Estará disponible de nuevo.'
            confirmation.type = 'success'
        }
    } else {
        confirmation.title = 'Eliminar de la BD'
        confirmation.message = '¿Estás seguro? Esta acción borrará el registro físicamente de SQL Server.'
        confirmation.type = 'danger'
    }
    confirmation.show = true
}

const executeConfirmedAction = async () => {
    try {
        let res;
        if (confirmation.mode === 'eliminar') {
            res = await fetch(`http://localhost:5000/api/admin/projects/${confirmation.projectId}/force`, { method: 'DELETE' });
        } else if (confirmation.mode === 'toggle') {
            res = await fetch(`http://localhost:5000/api/admin/projects/${confirmation.projectId}/toggle`, { method: 'PUT' });
        }

        const data = await res.json();
        
        if (res.ok) {
            await fetchData();
            showModal.value = false;
            showToast(data.message || 'Operación realizada');
        } else {
            showToast(data.error || data.message || 'Error en la operación', 'error');
        }
    } catch (error) {
        showToast('Error de red', 'error');
    }
    confirmation.show = false;
}

const toggleTeamMember = (user) => {
    const index = form.value.team.findIndex(u => u.id === user.id)
    if (index >= 0) form.value.team.splice(index, 1)
    else form.value.team.push(user)
}

const isMemberSelected = (userId) => form.value.team.some(u => u.id === userId)
const getVisualTeam = (project) => project.team || []
</script>

<template>
    <div class="h-full p-6 bg-gray-50 flex flex-col gap-6 font-sans relative">

        <div class="flex justify-between items-center">
            <div>
                <h1 class="h1-title font-bold text-2xl text-slate-800">Administrar Proyectos</h1>
                <p class="subtitle text-slate-500 text-sm">Visión general y gestión de equipos.</p>
            </div>
            <button @click="openCreate" class="btn-primary flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition font-medium shadow-md">
                <FolderPlus class="w-4 h-4" /> Nuevo Proyecto
            </button>
        </div>

        <div class="relative min-h-[300px]">
            <div v-if="isLoading" class="absolute inset-0 flex flex-col items-center justify-center bg-white/50 backdrop-blur-sm z-10 rounded-xl">
                <div class="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p class="mt-2 text-sm text-gray-500 font-bold">Consultando SQL Server...</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="project in projects" :key="project.id"
                    class="bg-white border border-gray-100 rounded-xl p-5 group hover:border-blue-400 hover:shadow-lg transition relative flex flex-col min-h-[220px] shadow-sm"
                    :class="{'opacity-75': project.status === 'Cerrado'}"> 

                    <div class="flex-shrink-0">
                        <div class="flex justify-between items-start mb-3">
                            <div class="bg-gray-100 p-2 rounded-lg text-slate-500 group-hover:bg-blue-50 group-hover:text-blue-600 transition">
                                <Briefcase class="w-5 h-5" />
                            </div>

                            <div class="flex items-center gap-1">
                                <span class="badge px-2 py-0.5 rounded-full font-bold text-[10px] border" 
                                    :class="project.status === 'Activo' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-gray-100 text-gray-500 border-gray-200'">
                                    {{ project.status }}
                                </span>

                                <div class="flex items-center opacity-0 group-hover:opacity-100 transition">
                                    <button @click.stop="openEdit(project)" class="p-1 text-gray-400 hover:text-blue-500" title="Editar"><Pencil class="w-4 h-4" /></button>
                                    <button @click.stop="requestAction(project.id, 'eliminar')" class="p-1 text-gray-400 hover:text-red-500" title="Eliminar"><Trash2 class="w-4 h-4" /></button>
                                </div>
                            </div>
                        </div>

                        <h3 class="font-bold text-lg text-slate-800 mb-1 leading-tight" :class="{'line-through text-gray-400': project.status === 'Cerrado'}">
                            {{ project.name }}
                        </h3>
                        <p class="text-sm text-gray-500 mb-4 flex items-center gap-1">
                            <Tag class="w-3 h-3" /> {{ project.client }}
                        </p>
                    </div>

                    <div class="mt-auto pt-3 border-t border-gray-100 flex flex-col flex-1 overflow-hidden">
                        <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 flex-shrink-0">
                            <Users class="w-3 h-3" /> Equipo Asignado
                        </div>

                        <div class="flex-1 overflow-y-auto pr-1 space-y-1 scrollbar-thin max-h-[140px]">
                            <template v-if="getVisualTeam(project).length > 0">
                                <div v-for="member in getVisualTeam(project)" :key="member.id"
                                    class="flex items-center gap-2 p-1.5 rounded-md hover:bg-gray-50 transition-colors">
                                    <div class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold shadow-sm shrink-0" :class="member.color">
                                        {{ member.initials }}
                                    </div>
                                    <span class="text-xs font-medium text-slate-600 truncate">{{ member.name }}</span>
                                </div>
                            </template>
                            <div v-else class="h-full flex flex-col items-center justify-center text-gray-300 italic text-xs py-4">
                                Sin equipo asignado
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="showModal" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div class="bg-white rounded-2xl w-full max-w-md space-y-4 shadow-2xl animate-in zoom-in-95 max-h-[90vh] flex flex-col p-6 border border-gray-100">
                <div class="flex justify-between items-center border-b border-gray-100 pb-2 flex-shrink-0">
                    <h3 class="font-bold text-lg text-slate-800">{{ isEditing ? 'Editar Proyecto' : 'Nuevo Proyecto' }}</h3>
                    <button @click="showModal = false"><X class="w-5 h-5 text-gray-400 hover:text-red-500 transition" /></button>
                </div>

                <div class="overflow-y-auto flex-1 pr-1 space-y-4">
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Nombre Proyecto</label>
                        <input v-model="form.name" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ej: Migración Cloud">
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-1">Cliente</label>
                        <input v-model="form.client" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ej: Banco Santander">
                    </div>

                    <div v-if="isEditing" class="p-4 bg-gray-50 rounded-lg border border-gray-200 mt-4 flex items-center justify-between">
                        <div>
                            <p class="text-sm font-bold text-slate-700">Estado del Proyecto</p>
                            <p class="text-xs text-gray-500">Actualmente: <span class="font-bold" :class="form.status === 'Activo' ? 'text-emerald-600' : 'text-gray-500'">{{ form.status }}</span></p>
                        </div>
                        <button @click.prevent="requestAction(form.id, 'toggle')"
                                class="px-3 py-1.5 rounded text-xs font-bold transition border"
                                :class="form.status === 'Activo' ? 'bg-white border-amber-200 text-amber-600 hover:bg-amber-50' : 'bg-white border-emerald-200 text-emerald-600 hover:bg-emerald-50'">
                            {{ form.status === 'Activo' ? 'Cerrar Proyecto' : 'Reabrir Proyecto' }}
                        </button>
                    </div>

                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-2">Asignar Equipo</label>
                        <div class="grid grid-cols-2 gap-2">
                            <div v-for="user in availableUsers" :key="user.id" 
                                @click="toggleTeamMember(user)"
                                class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition select-none"
                                :class="isMemberSelected(user.id) ? 'bg-blue-50 border-blue-400 shadow-sm' : 'bg-white border-gray-200 hover:border-gray-300'">
                                
                                <div class="w-4 h-4 rounded border flex items-center justify-center transition"
                                    :class="isMemberSelected(user.id) ? 'bg-blue-600 border-blue-600' : 'bg-white border-gray-300'">
                                    <Check v-if="isMemberSelected(user.id)" class="w-3 h-3 text-white" />
                                </div>
                                <div class="h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold bg-blue-100 text-blue-700">
                                    {{ user.initials }}
                                </div>
                                <span class="text-[11px] font-bold truncate" :class="isMemberSelected(user.id) ? 'text-blue-700' : 'text-gray-600'">{{ user.name }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex gap-2 pt-4 border-t border-gray-100 flex-shrink-0">
                    <button @click="showModal = false" class="flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition">Cancelar</button>
                    <button @click="saveProject" class="flex-1 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 shadow-lg shadow-blue-200">Guardar</button>
                </div>
            </div>
        </div>

        <div v-if="confirmation.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
            <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 text-center animate-in zoom-in-95">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4"
                     :class="confirmation.type === 'danger' ? 'bg-red-100 text-red-600' : (confirmation.type === 'success' ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600')">
                    <component :is="confirmation.type === 'danger' ? Trash2 : (confirmation.type === 'success' ? Check : AlertTriangle)" class="w-6 h-6" />
                </div>
                <h3 class="text-lg font-bold text-slate-900">{{ confirmation.title }}</h3>
                <p class="text-sm text-slate-500 mt-2">{{ confirmation.message }}</p>
                <div class="flex gap-3 mt-6">
                    <button @click="confirmation.show = false" class="flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition">Cancelar</button>
                    <button @click="executeConfirmedAction" class="flex-1 py-2 text-white rounded-lg font-bold transition shadow-md"
                            :class="confirmation.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : (confirmation.type === 'success' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-amber-600 hover:bg-amber-700')">
                        Confirmar
                    </button>
                </div>
            </div>
        </div>

        <div v-if="toast.show" class="fixed bottom-6 right-6 z-50 flex items-center p-4 space-x-3 text-slate-600 bg-white rounded-xl shadow-2xl border border-gray-100 animate-in slide-in-from-right">
            <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg" :class="toast.type === 'success' ? 'text-green-500 bg-green-100' : 'text-red-500 bg-red-100'">
                <component :is="toast.type === 'success' ? CheckCircle2 : AlertCircle" class="w-5 h-5"/>
            </div>
            <div class="ml-3 text-sm font-bold text-slate-800">{{ toast.message }}</div>
        </div>

    </div>
</template>
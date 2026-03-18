<script setup>
import { ref, computed, onMounted } from 'vue'
import ManagerAPI from '../../services/ManagerAPI'
import {
    LayoutGrid, Search, Plus, Pencil, Trash2, X, Check,
    Briefcase, UserPlus, Tag, Hash, Save,
    CheckCircle2, AlertCircle, AlertTriangle
} from 'lucide-vue-next'

const projects = ref([])
const availableUsers = ref([])
const isLoading = ref(false)

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

const confirmState = ref({ show: false, title: '', message: '', type: 'neutral', action: null })

const requestConfirmation = (title, message, type, callback) => {
    confirmState.value = { show: true, title, message, type, action: callback }
}

const executeConfirmation = () => {
    if (confirmState.value.action) confirmState.value.action()
    confirmState.value.show = false
}

const fetchProjects = async () => {
    isLoading.value = true
    try {
        const response = await ManagerAPI.getProjectsData()
        const data = response.data || response
        projects.value = data.projects || []
        availableUsers.value = data.availableUsers || []
    } catch (error) {
        console.error("Error cargando proyectos:", error)
        showToast("Error al cargar los datos", "error")
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    fetchProjects()
})

const showAssignModal = ref(false)
const showProjectModal = ref(false) 
const isEditing = ref(false)

const assignmentData = ref({ projectId: null, projectName: '', userId: '' })
const projectForm = ref({ id: null, name: '', client: '', clientId: '', code: '', status: true }) 

const searchQuery = ref('')
const statusFilter = ref('todos')

const filteredProjects = computed(() => {
    return projects.value.filter(p => {
        const textMatch =
            p.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            p.client.toLowerCase().includes(searchQuery.value.toLowerCase())
        
        const statusMatch =
            statusFilter.value === 'todos' ? true :
            statusFilter.value === 'activos' ? p.status :
            !p.status

        return textMatch && statusMatch
    })
})

const openCreateProject = () => {
    isEditing.value = false
    projectForm.value = { id: null, name: '', client: '', clientId: '', code: '', status: true }
    showProjectModal.value = true
}

const openEditProject = (proy) => {
    isEditing.value = true
    projectForm.value = { ...proy }
    showProjectModal.value = true
}

const saveProject = async () => {
    if (!projectForm.value.name || !projectForm.value.client) {
        showToast("Nombre y Cliente son obligatorios", "error")
        return
    }

    try {
        if (isEditing.value) {
            await ManagerAPI.updateProject(projectForm.value.id, projectForm.value)
            showToast("Proyecto actualizado", "success")
        } else {
            await ManagerAPI.createProject(projectForm.value)
            showToast("Proyecto creado", "success")
        }
        showProjectModal.value = false
        fetchProjects() 
    } catch (error) {
        showToast("Error al guardar el proyecto", "error")
    }
}

const deleteProject = (id) => {
    requestConfirmation(
        'Eliminar Proyecto',
        '¿Estás seguro de que deseas eliminar este proyecto de forma permanente?',
        'danger',
        async () => {
            try {
                await ManagerAPI.deleteProject(id)
                showToast("Proyecto eliminado correctamente", "success")
                fetchProjects() 
            } catch (error) {
                showToast("Error al eliminar", "error")
            }
        }
    )
}

const openAssignmentModal = (project) => {
    assignmentData.value = { projectId: project.id, projectName: project.name, userId: '' }
    showAssignModal.value = true
}

const confirmAssignment = async () => {
    if (!assignmentData.value.userId) {
        showToast("Selecciona un empleado", "error")
        return
    }
    
    try {
        await ManagerAPI.assignUserToProject(assignmentData.value.projectId, assignmentData.value.userId)
        showToast("Usuario asignado correctamente", "success")
        showAssignModal.value = false
        fetchProjects() 
    } catch (error) {
        showToast(error.response?.data?.error || "Error al asignar usuario", "error")
    }
}

const getColorClass = (name) => {
    const colors = [
        'bg-indigo-100 text-indigo-600', 'bg-rose-100 text-rose-600', 
        'bg-cyan-100 text-cyan-600', 'bg-emerald-100 text-emerald-600',
        'bg-amber-100 text-amber-600', 'bg-purple-100 text-purple-600'
    ];
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return colors[Math.abs(hash) % colors.length];
}
</script>

<template>
    <div class="h-full flex flex-col font-sans p-8 bg-slate-50 overflow-y-auto relative">

        <div class="flex justify-between items-center mb-8">
            <div class="flex items-center gap-4">
                <h1 class="text-3xl font-bold flex items-center gap-3 text-slate-800">
                    <LayoutGrid class="w-8 h-8 text-slate-400" />
                    Gestión Proyectos
                    <span class="text-sm font-bold px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-500 shadow-sm ml-2">
                        {{ projects.length }}
                    </span>
                </h1>
            </div>

            <button @click="openCreateProject" class="btn-primary flex items-center gap-2 shadow-lg shadow-emerald-500/20">
                <Plus class="w-5 h-5" />
                Nuevo Proyecto
            </button>
        </div>

        <div class="bg-white p-1 rounded-xl shadow-sm border border-slate-200 mb-8 flex gap-4 items-center">
            <div class="relative flex-1">
                <Search class="w-5 h-5 absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input v-model="searchQuery" type="text" placeholder="Buscar por cliente, nombre..."
                    class="w-full pl-12 pr-4 py-3 bg-transparent text-sm focus:outline-none text-slate-600 placeholder:text-slate-400" />
            </div>
            
            <div class="h-6 w-px bg-slate-200 mx-2"></div>

            <div class="flex items-center pr-2 gap-1">
                <button @click="statusFilter = 'todos'" class="px-4 py-2 rounded-lg text-sm font-medium transition"
                    :class="statusFilter === 'todos' ? 'bg-slate-100 text-slate-900' : 'text-slate-500 hover:text-slate-700'">Todos</button>
                <button @click="statusFilter = 'activos'" class="px-4 py-2 rounded-lg text-sm font-medium transition"
                    :class="statusFilter === 'activos' ? 'bg-emerald-50 text-emerald-700' : 'text-slate-500 hover:text-slate-700'">Activos</button>
                <button @click="statusFilter = 'inactivos'" class="px-4 py-2 rounded-lg text-sm font-medium transition"
                    :class="statusFilter === 'inactivos' ? 'bg-red-50 text-red-700' : 'text-slate-500 hover:text-slate-700'">Cerrados</button>
            </div>
        </div>

        <div v-if="isLoading" class="flex justify-center py-10">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-500"></div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-10">
            
            <div v-for="proy in filteredProjects" :key="proy.id"
                class="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 group relative flex flex-col p-5 min-h-[320px]">
                
                <div class="flex justify-between items-start mb-4">
                    <div class="w-10 h-10 rounded-xl bg-[#E8F5F3] flex items-center justify-center text-[#26AA9B]">
                        <Briefcase class="w-5 h-5" stroke-width="2.5"/>
                    </div>

                    <div class="flex items-center gap-2">
                        <span class="px-3 py-1 rounded-md text-[11px] font-bold tracking-wide uppercase border transition-colors"
                            :class="proy.status 
                                ? 'bg-emerald-50 text-emerald-600 border-emerald-200' 
                                : 'bg-slate-50 text-slate-500 border-slate-200'">
                            {{ proy.status ? 'Activo' : 'Cerrado' }}
                        </span>

                        <button @click.stop="openEditProject(proy)"
                            class="w-7 h-7 flex items-center justify-center rounded bg-white border border-slate-200 text-slate-400 hover:text-blue-600 hover:border-blue-200 transition-all shadow-sm"
                            title="Editar Proyecto">
                            <Pencil class="w-3.5 h-3.5" />
                        </button>

                        <button @click.stop="deleteProject(proy.id)"
                            class="w-7 h-7 flex items-center justify-center rounded bg-white border border-slate-200 text-slate-400 hover:text-red-600 hover:border-red-200 transition-all shadow-sm"
                            title="Eliminar">
                            <Trash2 class="w-3.5 h-3.5" />
                        </button>
                    </div>
                </div>

                <div class="mb-5">
                    <h3 class="text-lg font-bold text-slate-800 leading-tight mb-1 truncate" :title="proy.name">
                        {{ proy.name }}
                    </h3>
                    <div class="flex flex-col gap-1">
                        <p class="text-sm text-slate-500 flex items-center gap-1.5 font-medium truncate">
                            <Tag class="w-3.5 h-3.5" /> {{ proy.client }}
                        </p>
                        <p v-if="proy.clientId" class="text-xs text-slate-400 flex items-center gap-1.5 font-mono">
                            <Hash class="w-3 h-3" /> {{ proy.clientId }}
                        </p>
                    </div>
                </div>

                <div class="h-px bg-slate-100 w-full mb-4"></div>

                <div class="flex flex-col flex-1 overflow-hidden">
                    <div class="flex justify-between items-center mb-3">
                        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                            Equipo Asignado
                        </span>
                        <button @click.stop="openAssignmentModal(proy)" class="text-slate-300 hover:text-emerald-600 transition" title="Añadir miembro">
                            <UserPlus class="w-4 h-4"/>
                        </button>
                    </div>

                    <div class="flex-1 overflow-y-auto pr-1 space-y-3 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
                        
                        <template v-if="proy.team.length > 0">
                            <div v-for="(user, index) in proy.team" :key="index" class="flex items-center gap-3 group/user">
                                <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
                                     :class="getColorClass(user.name)">
                                    {{ user.initials }}
                                </div>
                                <span class="text-sm text-slate-600 font-medium group-hover/user:text-slate-900 transition-colors">
                                    {{ user.name }}
                                </span>
                            </div>
                        </template>

                        <div v-else class="h-full flex flex-col items-center justify-center text-slate-300 gap-2 min-h-[100px]">
                            <UserPlus class="w-8 h-8 opacity-20" />
                            <span class="text-xs italic">Sin equipo asignado</span>
                        </div>

                    </div>
                </div>

            </div>
        </div>

        <div v-if="showAssignModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div class="bg-white w-full max-w-sm rounded-2xl shadow-2xl p-6 animate-in zoom-in-95">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-lg font-bold text-slate-800">Asignar a Proyecto</h3>
                        <p class="text-sm text-slate-500 truncate w-64">{{ assignmentData.projectName }}</p>
                    </div>
                    <button @click="showAssignModal=false" class="text-slate-400 hover:text-slate-600">
                        <X class="w-5 h-5"/>
                    </button>
                </div>

                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Empleado</label>
                        <select v-model="assignmentData.userId" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                            <option value="" disabled>Seleccionar...</option>
                            <option v-for="u in availableUsers" :key="u.id" :value="u.id">{{ u.name }}</option>
                        </select>
                    </div>
                    <button @click="confirmAssignment" class="w-full btn-primary py-3 justify-center">
                        Confirmar Asignación
                    </button>
                </div>
            </div>
        </div>

        <div v-if="showProjectModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl p-6 animate-in zoom-in-95">
                <div class="flex justify-between items-start mb-6">
                    <div>
                        <h3 class="text-xl font-bold text-slate-800">
                            {{ isEditing ? 'Editar Proyecto' : 'Nuevo Proyecto' }}
                        </h3>
                        <p class="text-sm text-slate-500">Completa la información del proyecto.</p>
                    </div>
                    <button @click="showProjectModal=false" class="text-slate-400 hover:text-slate-600">
                        <X class="w-6 h-6"/>
                    </button>
                </div>

                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Nombre Proyecto</label>
                        <input v-model="projectForm.name" type="text" placeholder="Ej: Migración Cloud" 
                               class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Cliente</label>
                            <input v-model="projectForm.client" type="text" placeholder="Ej: Santander" 
                                class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase mb-2">ID Cliente</label>
                            <input v-model="projectForm.clientId" type="text" placeholder="Ej: CLI-001" 
                                class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                        </div>
                    </div>

                    <div>
                         <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Estado</label>
                         <div class="flex gap-2">
                            <button @click="projectForm.status = true" 
                                    class="flex-1 py-2 rounded-lg text-sm font-bold border transition-colors"
                                    :class="projectForm.status ? 'bg-emerald-50 border-emerald-500 text-emerald-700' : 'bg-white border-slate-200 text-slate-500'">
                                Activo
                            </button>
                            <button @click="projectForm.status = false" 
                                    class="flex-1 py-2 rounded-lg text-sm font-bold border transition-colors"
                                    :class="!projectForm.status ? 'bg-slate-100 border-slate-400 text-slate-700' : 'bg-white border-slate-200 text-slate-500'">
                                Cerrado
                            </button>
                         </div>
                    </div>

                    <div class="pt-2">
                        <button @click="saveProject" class="w-full btn-primary py-3 justify-center flex items-center gap-2">
                            <Save class="w-4 h-4"/>
                            {{ isEditing ? 'Guardar Cambios' : 'Crear Proyecto' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="confirmState.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
            <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
                <div class="flex flex-col items-center text-center gap-3">
                    <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2"
                         :class="confirmState.type === 'danger' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'">
                        <component :is="confirmState.type === 'danger' ? Trash2 : AlertTriangle" class="w-6 h-6" />
                    </div>
                    <h3 class="text-lg font-bold text-slate-900">{{ confirmState.title }}</h3>
                    <p class="text-sm text-slate-500 leading-relaxed">{{ confirmState.message }}</p>
                    
                    <div class="flex gap-3 w-full mt-4">
                        <button @click="confirmState.show = false" class="btn-secondary flex-1 justify-center">Cancelar</button>
                        <button @click="executeConfirmation" 
                                class="flex-1 justify-center btn-primary"
                                :class="confirmState.type === 'danger' ? 'bg-red-600 hover:bg-red-700' : 'bg-amber-600 hover:bg-amber-700'">
                            Confirmar
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <transition enter-active-class="transform ease-out duration-300 transition" enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2" enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="toast.show" class="absolute bottom-6 right-6 z-50 flex items-center w-full max-w-xs p-4 space-x-3 text-gray-500 bg-white rounded-lg shadow-lg border border-gray-100" role="alert">
                <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg" :class="toast.type === 'success' ? 'text-green-500 bg-green-100' : 'text-red-500 bg-red-100'">
                    <component :is="toast.type === 'success' ? CheckCircle2 : AlertCircle" class="w-5 h-5"/>
                </div>
                <div class="ml-3 text-sm font-bold text-gray-800">{{ toast.message }}</div>
                <button @click="toast.show = false" type="button" class="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 items-center justify-center">
                    <X class="w-4 h-4"/>
                </button>
            </div>
        </transition>

    </div>
</template>

<style scoped>
.btn-primary {
    @apply bg-[#26AA9B] hover:bg-[#208f82] text-white px-5 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center gap-2;
}
.btn-secondary {
    @apply bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 px-5 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center gap-2;
}
</style>
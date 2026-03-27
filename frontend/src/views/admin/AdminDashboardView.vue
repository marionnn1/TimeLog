<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Users, FolderOpen, Ticket, ShieldCheck, FileText, Activity, Download, ArrowRight } from 'lucide-vue-next'
import AdminAPI from '../../services/AdminAPI'
import ToastNotification from '@/components/common/ToastNotification.vue'

const router = useRouter()

const stats = ref({
    totalUsuarios: 0,
    proyectosActivos: 0,
    ticketsPendientes: 0,
    ticketsTotales: 0
})

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null
const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => { toast.value.show = false }, 3000)
}

const cargarEstadisticas = async () => {
    try {
        const json = await AdminAPI.getDashboardStats()
        if (json.status === 'success') {
            stats.value = json.data
        }
    } catch (error) {
        showToast("Error crítico al cargar el dashboard.", "error")
    }
}

onMounted(cargarEstadisticas)

const exportarCSV = async () => {
    try {
        const json = await AdminAPI.getAuditoria()
        if (json.status === 'success') {
            const logs = json.data
            if (logs.length === 0) return showToast("No hay registros en la auditoría para exportar.", "error")

            const cabeceras = ['ID', 'Fecha', 'Actor', 'Acción', 'Gravedad', 'Detalle']
            const filas = logs.map(log => [
                log.id, `"${log.fecha}"`, `"${log.actor}"`, `"${log.accion}"`, `"${log.gravedad}"`, `"${log.detalle}"`
            ])

            const contenidoCSV = [cabeceras.join(','), ...filas.map(f => f.join(','))].join('\n')
            const blob = new Blob([contenidoCSV], { type: 'text/csv;charset=utf-8;' })
            const url = URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.setAttribute('href', url)
            link.setAttribute('download', `Auditoria_Timelog_${new Date().toISOString().split('T')[0]}.csv`)
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            
            showToast("Logs exportados correctamente", "success")
        }
    } catch (error) {
        showToast("Ocurrió un error al intentar exportar los logs.", "error")
    }
}

const ejecutarAccion = (idAccion) => {
    if (idAccion === 'exportar') exportarCSV()
    else if (idAccion === 'tickets') router.push('/admin/tickets')
}

const panelesAdministracion = [
    { label: 'Auditoría de Sistema', icono: FileText, ruta: '/admin/audit' },
    { label: 'Gestión de Usuarios', icono: Users, ruta: '/admin/users' },
    { label: 'Gestión de Proyectos', icono: FolderOpen, ruta: '/admin/projects-manager' },
    { label: 'Soporte y Tickets', icono: Ticket, ruta: '/admin/tickets' }
]

const accionesRapidas = [
    { id: 'exportar', texto: 'Exportar Logs de Auditoría', colorPunto: 'text-blue-500', iconoAccion: Download },
    { id: 'tickets', texto: 'Revisar Tickets Críticos', colorPunto: 'text-amber-500', iconoAccion: ArrowRight }
]
</script>

<template>
  <div class="h-full p-8 bg-gray-50 flex flex-col gap-8 font-sans overflow-y-auto relative">
    
    <div>
        <h1 class="h1-title text-3xl font-extrabold text-[#232D4B]">Centro de Control</h1>
        <p class="subtitle text-gray-500 text-base mt-1">Visión general del estado del sistema y soporte.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div @click="router.push('/admin/users')" class="cursor-pointer bg-white rounded-2xl border border-gray-200 shadow-lg p-6 flex items-center justify-between group hover:border-[#26AA9B] hover:shadow-xl transition-all">
            <div>
                <p class="text-sm font-bold uppercase tracking-wider text-gray-400">Usuarios Totales</p>
                <p class="text-5xl font-extrabold text-[#232D4B] mt-2">{{ stats.totalUsuarios }}</p>
            </div>
            <div class="p-4 rounded-full bg-blue-50 text-blue-600 group-hover:bg-blue-100 transition">
                <Users class="w-8 h-8" />
            </div>
        </div>

        <div @click="router.push('/admin/projects-manager')" class="cursor-pointer bg-white rounded-2xl border border-gray-200 shadow-lg p-6 flex items-center justify-between group hover:border-[#26AA9B] hover:shadow-xl transition-all">
            <div>
                <p class="text-sm font-bold uppercase tracking-wider text-gray-400">Proyectos Activos</p>
                <p class="text-5xl font-extrabold text-[#232D4B] mt-2">{{ stats.proyectosActivos }}</p>
            </div>
            <div class="p-4 rounded-full bg-emerald-50 text-emerald-600 group-hover:bg-emerald-100 transition">
                <FolderOpen class="w-8 h-8" />
            </div>
        </div>

        <div @click="router.push('/admin/tickets')" class="cursor-pointer bg-white rounded-2xl border border-gray-200 shadow-lg p-6 flex items-center justify-between group hover:border-amber-400 hover:shadow-xl transition-all relative overflow-hidden">
            <div class="z-10">
                <p class="text-sm font-bold uppercase tracking-wider text-gray-400">Tickets Pendientes</p>
                <p class="text-5xl font-extrabold text-amber-500 mt-2">{{ stats.ticketsPendientes }}</p>
                <p class="text-xs font-medium text-gray-500 mt-1">de {{ stats.ticketsTotales }} totales</p>
            </div>
            <div class="p-4 rounded-full bg-amber-100 text-amber-600 z-10">
                <Ticket class="w-8 h-8" />
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1">
        
        <div class="lg:col-span-2 bg-white rounded-2xl p-8 border border-gray-100 shadow-lg">
            <div class="flex items-center gap-3 mb-8">
                <div class="p-3 rounded-lg bg-gray-100 text-gray-600">
                    <ShieldCheck class="w-6 h-6" />
                </div>
                <h3 class="font-bold text-2xl text-[#232D4B]">Panel de Administración Global</h3>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div v-for="(panel, index) in panelesAdministracion" :key="index" 
                     @click="router.push(panel.ruta)"
                     class="bg-gray-50 p-6 rounded-xl border border-gray-100 flex items-center gap-4 hover:bg-gray-100 hover:border-gray-300 hover:shadow-sm cursor-pointer transition-all">
                    <component :is="panel.icono" class="w-10 h-10 text-gray-500" />
                    <span class="font-semibold text-gray-800 text-lg">{{ panel.label }}</span>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 flex flex-col gap-5">
            <h3 class="text-xl font-bold text-[#232D4B] mb-2">Acciones Rápidas</h3>
            
            <button v-for="(accion, index) in accionesRapidas" :key="index"
                    @click="ejecutarAccion(accion.id)"
                    class="w-full text-left p-4 rounded-xl bg-gray-50 hover:bg-gray-100 border border-gray-100 flex items-center gap-3 transition text-sm font-bold text-gray-600 active:scale-[0.98]">
                <Activity class="w-2 h-2" :class="accion.colorPunto" />
                {{ accion.texto }}
                <component :is="accion.iconoAccion" class="w-5 h-5 ml-auto text-gray-400" />
            </button>
        </div>
    </div>

    <ToastNotification
        :show="toast.show"
        :message="toast.message"
        :type="toast.type"
        @close="toast.show = false"
    />
  </div>
</template>
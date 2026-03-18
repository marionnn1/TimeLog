<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router' // <--- IMPORTAMOS EL ROUTER
import { Users, FolderOpen, Ticket, Activity, X, Send, Download } from 'lucide-vue-next'

const router = useRouter() // <--- INICIALIZAMOS EL ROUTER

// --- ESTADO ---
const stats = ref({
    totalUsuarios: 0,
    proyectosActivos: 0,
    ticketsPendientes: 0,
    ticketsTotales: 0
})

// Estado para el modal del comunicado
const mostrarModalComunicado = ref(false)
const comunicado = ref({ titulo: '', mensaje: '' })

// --- LÓGICA DE API: ESTADÍSTICAS ---
const cargarEstadisticas = async () => {
    try {
        const res = await fetch('http://localhost:5000/api/dashboard/stats')
        if (!res.ok) throw new Error(`El servidor respondió con código ${res.status}`)
        
        const json = await res.json()
        
        if (json.status === 'success') {
            stats.value = json.data
        }
    } catch (error) {
        console.error("Error crítico al cargar el dashboard.", error)
    }
}

onMounted(cargarEstadisticas)

// --- ACCIONES DE LOS BOTONES ---

// Acción 1: Exportar CSV
const exportarCSV = async () => {
    try {
        const res = await fetch('http://localhost:5000/api/auditoria')
        const json = await res.json()
        
        if (json.status === 'success') {
            const logs = json.data
            if (logs.length === 0) return alert("No hay registros en la auditoría para exportar.")

            const cabeceras = ['ID', 'Fecha', 'Actor', 'Acción', 'Gravedad', 'Detalle']
            const filas = logs.map(log => [
                log.id, 
                `"${log.fecha}"`, 
                `"${log.actor}"`, 
                `"${log.accion}"`, 
                `"${log.gravedad}"`, 
                `"${log.detalle}"`
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
        }
    } catch (error) {
        console.error("Error al exportar:", error)
        alert("Ocurrió un error al intentar exportar los logs.")
    }
}

// Acción 2: Enviar Comunicado
const enviarComunicado = () => {
    console.log("Enviando comunicado:", comunicado.value)
    mostrarModalComunicado.value = false
    comunicado.value = { titulo: '', mensaje: '' }
    alert("Comunicado enviado al equipo.")
}

// Enrutador de acciones
const ejecutarAccion = (idAccion) => {
    if (idAccion === 'comunicado') {
        mostrarModalComunicado.value = true
    } else if (idAccion === 'exportar') {
        exportarCSV()
    } else if (idAccion === 'tickets') {
        router.push('/admin/tickets') // <--- REDIRIGE A TICKETS
    }
}

// --- CONFIGURACIÓN DE VISTA ---
const metricasSistema = [
    { label: 'Base de Datos', valor: 'Conectada', colorTexto: 'text-white' },
    { label: 'Latencia API', valor: '24ms', colorTexto: 'text-[#26AA9B]' },
    { label: 'Último Backup', valor: '04:00 AM', colorTexto: 'text-white' },
]

const accionesRapidas = [
    { id: 'comunicado', texto: 'Nuevo Comunicado Global', colorPunto: 'bg-[#26AA9B]' },
    { id: 'exportar', texto: 'Exportar Logs de Auditoría', colorPunto: 'bg-blue-500' },
    { id: 'tickets', texto: 'Revisar Tickets Críticos', colorPunto: 'bg-amber-500' },
]
</script>

<template>
  <div class="h-full p-6 bg-gray-50 flex flex-col gap-6 font-sans overflow-y-auto relative">
    
    <div>
        <h1 class="h1-title text-2xl font-bold text-[#232D4B]">Centro de Control</h1>
        <p class="subtitle text-gray-500 text-sm mt-1">Visión general del estado del sistema y soporte.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div @click="router.push('/admin/users')" class="cursor-pointer bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex items-center justify-between group hover:border-[#26AA9B] transition">
            <div>
                <p class="text-xs font-bold uppercase tracking-wider text-gray-400">Usuarios Totales</p>
                <p class="text-3xl font-black text-[#232D4B] mt-1">{{ stats.totalUsuarios }}</p>
            </div>
            <div class="p-3 rounded-xl bg-blue-50 text-blue-600 group-hover:bg-blue-100 transition">
                <Users class="w-6 h-6" />
            </div>
        </div>

        <div @click="router.push('/admin/projects-manager')" class="cursor-pointer bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex items-center justify-between group hover:border-[#26AA9B] transition">
            <div>
                <p class="text-xs font-bold uppercase tracking-wider text-gray-400">Proyectos Activos</p>
                <p class="text-3xl font-black text-[#232D4B] mt-1">{{ stats.proyectosActivos }}</p>
            </div>
            <div class="p-3 rounded-xl bg-emerald-50 text-emerald-600 group-hover:bg-emerald-100 transition">
                <FolderOpen class="w-6 h-6" />
            </div>
        </div>

        <div @click="router.push('/admin/tickets')" class="cursor-pointer bg-white rounded-xl border border-amber-200 shadow-sm p-5 flex items-center justify-between group hover:border-amber-400 transition relative overflow-hidden bg-amber-50/30">
            <div class="absolute right-0 top-0 w-16 h-16 bg-amber-400/10 rounded-bl-full"></div>
            <div class="z-10">
                <p class="text-xs font-bold uppercase tracking-wider text-amber-600/70">Tickets Pendientes</p>
                <p class="text-3xl font-black text-amber-600 mt-1">{{ stats.ticketsPendientes }}</p>
                <p class="text-[10px] font-bold text-gray-400 mt-1 uppercase">de {{ stats.ticketsTotales }} totales</p>
            </div>
            <div class="p-3 rounded-xl bg-amber-100 text-amber-600 z-10">
                <Ticket class="w-6 h-6" />
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        
        <div class="lg:col-span-2 bg-[#1E293B] rounded-xl p-6 text-white shadow-lg relative overflow-hidden flex flex-col justify-between">
            <div class="absolute top-0 right-0 p-40 bg-[#26AA9B] rounded-full blur-[100px] opacity-10 pointer-events-none"></div>
            
            <div class="flex justify-between items-start relative z-10">
                <div>
                    <h3 class="font-bold text-lg flex items-center gap-2">
                        <Activity class="w-5 h-5 text-[#26AA9B]" /> Monitor de Sistema
                    </h3>
                    <p class="text-slate-400 text-sm">Rendimiento en tiempo real</p>
                </div>
                <span class="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full text-xs font-bold border border-emerald-500/50 flex items-center gap-2 animate-pulse">
                    Operativo
                </span>
            </div>

            <div class="grid grid-cols-3 gap-4 mt-8 relative z-10">
                <div v-for="(metrica, index) in metricasSistema" :key="index" 
                     class="bg-white/5 p-4 rounded-lg border border-white/10 backdrop-blur-sm">
                    <p class="text-xs text-slate-400 mb-1 font-bold">{{ metrica.label }}</p>
                    <div class="text-xl font-mono font-bold" :class="metrica.colorTexto">
                        {{ metrica.valor }}
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 flex flex-col gap-3">
            <h3 class="text-sm font-bold text-slate-700 mb-2 uppercase tracking-wider">Acciones Rápidas</h3>
            
            <button v-for="(accion, index) in accionesRapidas" :key="index"
                    @click="ejecutarAccion(accion.id)"
                    class="w-full text-left p-3 rounded-lg bg-gray-50 hover:bg-gray-100 border border-gray-100 flex items-center gap-3 transition text-sm font-bold text-gray-600 active:scale-[0.98]">
                <div class="w-2 h-2 rounded-full" :class="accion.colorPunto"></div>
                {{ accion.texto }}
                <Download v-if="accion.id === 'exportar'" class="w-4 h-4 ml-auto text-gray-400" />
            </button>
        </div>
    </div>

    <div v-if="mostrarModalComunicado" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
        <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl animate-in zoom-in-95 flex flex-col p-6 border border-gray-100">
            <div class="flex justify-between items-center border-b border-gray-100 pb-4 mb-4">
                <h3 class="font-bold text-lg text-slate-800">Lanzar Comunicado Global</h3>
                <button @click="mostrarModalComunicado = false"><X class="w-5 h-5 text-gray-400 hover:text-red-500 transition" /></button>
            </div>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Título del aviso</label>
                    <input v-model="comunicado.titulo" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#26AA9B] outline-none" placeholder="Ej: Mantenimiento del servidor el Viernes">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Mensaje</label>
                    <textarea v-model="comunicado.mensaje" rows="4" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#26AA9B] outline-none resize-none" placeholder="Escribe aquí los detalles..."></textarea>
                </div>
            </div>

            <div class="flex gap-2 mt-6">
                <button @click="mostrarModalComunicado = false" class="flex-1 py-2 border border-gray-300 text-slate-600 rounded-lg font-bold hover:bg-gray-50 transition">Cancelar</button>
                <button @click="enviarComunicado" class="flex-1 py-2 bg-[#26AA9B] text-white rounded-lg font-bold hover:bg-[#209083] shadow-md flex justify-center items-center gap-2">
                    <Send class="w-4 h-4" /> Enviar Aviso
                </button>
            </div>
        </div>
    </div>

  </div>
</template>
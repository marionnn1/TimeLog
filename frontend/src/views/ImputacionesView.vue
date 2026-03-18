<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '../stores/dataStore'
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon, 
  FileText,
  Hash, 
  Briefcase,
  CheckCircle2,
  AlertCircle,
  X,
  MessageSquare, 
  Send, 
  Clock,
  ArrowRight
} from 'lucide-vue-next'

const router = useRouter()
const store = useDataStore()

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

// ==========================================
// LÓGICA DE AUSENCIAS (CON REACTIVIDAD VUE 3)
// ==========================================
const ausenciasPersonales = ref([])

const cargarAusenciasAPI = async () => {
    const user = store.getCurrentUser()
    if (!user) return
    try {
        const mesReal = mesActualIndex.value + 1
        const res = await fetch(`http://localhost:5000/api/absences?mes=${mesReal}&anio=${anioActual.value}`)
        const json = await res.json()
        if (json.status === 'success') {
            ausenciasPersonales.value = json.data.filter(a => String(a.userId) === String(user.id))
        }
    } catch (e) {
        console.error(e)
    }
}

// Diccionario Reactivo para búsquedas instantáneas en el template HTML
const ausenciasMesMap = computed(() => {
    const map = {}
    ausenciasPersonales.value.forEach(a => {
        map[a.fecha] = (a.tipo === 'asuntos' || a.tipo === 'asuntos_propios') ? 'asuntos' : a.tipo
    })
    return map
})

const getTipoDia = (dateObj) => {
    const offset = dateObj.getTimezoneOffset() * 60000
    const iso = new Date(dateObj.getTime() - offset).toISOString().split('T')[0]
    return ausenciasMesMap.value[iso] || null
}

const getLabelDia = (dateObj) => {
    const tipo = getTipoDia(dateObj)
    if (!tipo) return null
    if (tipo === 'asuntos') return 'Asuntos P.'
    return tipo.charAt(0).toUpperCase() + tipo.slice(1)
}
// ==========================================

const fechaActual = ref(new Date()) 
const hoy = new Date() 

const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

const anioActual = computed(() => fechaActual.value.getFullYear())
const mesActualIndex = computed(() => fechaActual.value.getMonth())
const nombreMes = computed(() => meses[mesActualIndex.value])

const diasEnBlanco = computed(() => {
  const primerDia = new Date(anioActual.value, mesActualIndex.value, 1).getDay()
  return primerDia === 0 ? 6 : primerDia - 1
})
const diasDelMes = computed(() => {
  return new Date(anioActual.value, mesActualIndex.value + 1, 0).getDate()
})

const esFinDeSemana = (dia) => {
  const fecha = new Date(anioActual.value, mesActualIndex.value, dia)
  return fecha.getDay() === 0 || fecha.getDay() === 6 
}
const esHoy = (dia) => dia === hoy.getDate() && mesActualIndex.value === hoy.getMonth() && anioActual.value === hoy.getFullYear()

const mesAnterior = () => fechaActual.value = new Date(anioActual.value, mesActualIndex.value - 1, 1)
const mesSiguiente = () => fechaActual.value = new Date(anioActual.value, mesActualIndex.value + 1, 1)
const irAHoy = () => fechaActual.value = new Date()

const imputaciones = ref([])

const coloresProyectos = [
    'bg-blue-50 text-blue-700 border-blue-100 hover:bg-blue-100',
    'bg-cyan-50 text-cyan-800 border-cyan-100 hover:bg-cyan-100',
    'bg-emerald-50 text-emerald-800 border-emerald-100 hover:bg-emerald-100',
    'bg-fuchsia-50 text-fuchsia-800 border-fuchsia-100 hover:bg-fuchsia-100',
    'bg-amber-50 text-amber-800 border-amber-100 hover:bg-amber-100',
    'bg-indigo-50 text-indigo-700 border-indigo-100 hover:bg-indigo-100'
]

const cargarCalendario = async () => {
    const user = store.getCurrentUser()
    if (!user) return
    
    try {
        const mesReal = mesActualIndex.value + 1
        const res = await fetch(`http://localhost:5000/api/myprojects/calendario?usuario_id=${user.id}&mes=${mesReal}&anio=${anioActual.value}`)
        const json = await res.json()
        
        if (json.status === 'success') {
            imputaciones.value = json.data.map(imp => {
                const colorAsignado = coloresProyectos[imp.proyecto_id % coloresProyectos.length]
                return {
                    dia: imp.dia,
                    cliente: imp.cliente,
                    codigo: `PRJ-${String(imp.proyecto_id).padStart(3, '0')}`,
                    proyecto: imp.proyecto,
                    proyecto_id: imp.proyecto_id,
                    horas: imp.horas,
                    color: colorAsignado
                }
            })
        }
    } catch (e) {}
}

watch([mesActualIndex, anioActual], () => {
    cargarCalendario()
    cargarAusenciasAPI() // Recargamos ausencias al cambiar de mes
})

onMounted(() => {
    cargarCalendario()
    cargarAusenciasAPI()
})

const getImputacionesPorDia = (dia) => imputaciones.value.filter(imp => imp.dia === dia)
const getTotalHoras = (dia) => getImputacionesPorDia(dia).reduce((acc, curr) => acc + curr.horas, 0)

const resumenProyectos = computed(() => {
  const grupos = {}
  imputaciones.value.forEach(imp => {
    const key = imp.codigo
    if (!grupos[key]) {
      grupos[key] = { cliente: imp.cliente, codigo: imp.codigo, proyecto: imp.proyecto, horas: 0 }
    }
    grupos[key].horas += imp.horas
  })
  return Object.values(grupos).sort((a, b) => b.horas - a.horas)
})

const totalHorasMes = computed(() => {
  return imputaciones.value.reduce((acc, curr) => acc + curr.horas, 0)
})

const exportarDatos = () => {
    const headers = ['Fecha', 'Cliente', 'Código Proyecto', 'Proyecto', 'Horas']
    const rows = imputaciones.value.map(imp => {
        const fechaStr = `${imp.dia}/${mesActualIndex.value + 1}/${anioActual.value}`
        return [fechaStr, `"${imp.cliente}"`, imp.codigo, `"${imp.proyecto}"`, imp.horas]
    })
    const csvContent = [headers.join(';'), ...rows.map(row => row.join(';'))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `imputaciones_${nombreMes.value}_${anioActual.value}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    showToast('Informe exportado correctamente', 'success')
}

const mostrarModalSolicitud = ref(false)
const formSolicitud = ref({
    fechaVisible: '', fechaISO: '', proyecto: '', proyecto_id: null, mensaje: '', horasActuales: 0, horasNuevas: 0
})

const abrirSolicitud = (imputacion, dia) => {
    const fechaObj = new Date(anioActual.value, mesActualIndex.value, dia)
    
    // BLOQUEAMOS EL CLIC DE EDICIÓN EN DÍAS DE VACACIONES
    if (getTipoDia(fechaObj)) {
        showToast(`No puedes modificar horas en un día de ${getLabelDia(fechaObj)}.`, 'error')
        return
    }

    const fechaStr = fechaObj.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
    const offset = fechaObj.getTimezoneOffset() * 60000
    const isoDate = new Date(fechaObj.getTime() - offset).toISOString().split('T')[0]
    
    formSolicitud.value = {
        fechaVisible: fechaStr, fechaISO: isoDate, proyecto: imputacion.proyecto, proyecto_id: imputacion.proyecto_id,
        mensaje: '', horasActuales: imputacion.horas, horasNuevas: imputacion.horas
    }
    mostrarModalSolicitud.value = true
}

const enviarSolicitudJefe = async () => {
    if (!formSolicitud.value.mensaje) return showToast('Debes escribir un motivo para la solicitud', 'error')
    const user = store.getCurrentUser()
    if (!user) return;

    try {
        const response = await fetch('http://localhost:5000/api/myprojects/solicitar-correccion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                usuario_id: user.id, proyecto_id: formSolicitud.value.proyecto_id, fecha: formSolicitud.value.fechaISO,
                nuevas_horas: formSolicitud.value.horasNuevas, motivo: formSolicitud.value.mensaje
            })
        })
        const json = await response.json()
        if (response.ok && json.status === 'success') {
            mostrarModalSolicitud.value = false
            showToast('Solicitud enviada al responsable', 'success')
            cargarCalendario() 
        } else {
            showToast(json.message || 'Error al enviar la solicitud', 'error')
        }
    } catch (error) {}
}
</script>

<template>
  <div class="h-full flex flex-col font-sans bg-gray-50 p-6 overflow-y-auto relative">
    
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-4">
        <h1 class="text-3xl font-bold capitalize flex items-center gap-3 text-dark">
          <div class="p-2 rounded-lg bg-white shadow-sm border border-gray-100">
            <CalendarIcon class="w-6 h-6 text-primary"/>
          </div>
          {{ nombreMes }} <span class="font-light opacity-50">{{ anioActual }}</span>
        </h1>
        
        <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200 ml-6">
          <button @click="mesAnterior" class="p-2 hover:bg-gray-50 text-gray-600 rounded-l-lg border-r border-gray-200 transition"><ChevronLeft class="w-5 h-5" /></button>
          <button @click="irAHoy" class="px-4 py-2 text-xs font-bold tracking-widest hover:bg-gray-50 transition uppercase text-dark">Hoy</button>
          <button @click="mesSiguiente" class="p-2 hover:bg-gray-50 text-gray-600 rounded-r-lg border-l border-gray-200 transition"><ChevronRight class="w-5 h-5" /></button>
        </div>
      </div>
      <button @click="exportarDatos" class="btn-secondary"><FileText class="w-4 h-4"/> Exportar</button>
    </div>

    <div class="bg-white p-3 rounded-lg border border-gray-200 shadow-sm mb-4 flex flex-wrap items-center gap-4 text-xs font-medium">
        <span class="uppercase text-gray-400 tracking-wider mr-2 font-bold">Leyenda:</span>
        <div class="flex items-center gap-2 px-2 py-1 rounded-md bg-gray-50 border border-gray-100">
            <div class="w-2.5 h-2.5 rounded-full bg-white border border-gray-300"></div><span class="text-gray-600">Laborable</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1 rounded-md bg-orange-50 border border-orange-100">
            <div class="w-2.5 h-2.5 rounded-full bg-orange-500"></div><span class="text-orange-700">Festivo</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1 rounded-md bg-emerald-50 border border-emerald-100">
            <div class="w-2.5 h-2.5 rounded-full bg-emerald-500"></div><span class="text-emerald-700">Vacaciones</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1 rounded-md bg-blue-50 border border-blue-100">
            <div class="w-2.5 h-2.5 rounded-full bg-blue-500"></div><span class="text-blue-700">Asuntos P.</span>
        </div>
    </div>

    <div class="card p-0 overflow-hidden mb-8 flex-none shadow-xl">
      <div class="grid grid-cols-7 border-b border-gray-200">
        <div v-for="dia in diasSemana.slice(0, 5)" :key="dia" class="py-4 text-center text-xs font-bold uppercase tracking-widest bg-white text-dark">{{ dia }}</div>
        <div v-for="dia in diasSemana.slice(5, 7)" :key="dia" class="py-4 text-center text-xs font-bold uppercase tracking-widest text-white/90 bg-dark">{{ dia }}</div>
      </div>

      <div class="grid grid-cols-7 auto-rows-fr">
        <div v-for="blank in diasEnBlanco" :key="`blank-${blank}`" class="bg-gray-50/50 border-b border-r border-gray-100"></div>
        <div v-for="dia in diasDelMes" :key="dia" 
             class="min-h-[100px] p-2 border-b border-r border-gray-100 transition relative flex flex-col gap-1"
             :class="[
               esFinDeSemana(dia) ? 'bg-slate-100 cursor-default' : 'bg-white',
               getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'festivo' ? 'bg-orange-50/40' : '',
               getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'vacaciones' ? 'bg-emerald-50/40' : '',
               getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'asuntos' ? 'bg-blue-50/40' : '',
             ]">
          <div class="flex justify-between items-start mb-2">
            <span class="text-sm font-bold w-7 h-7 flex items-center justify-center rounded-full"
                  :class="esHoy(dia) ? 'bg-primary text-white' : (esFinDeSemana(dia) ? 'text-slate-400' : 'text-dark')">{{ dia }}</span>
            <span v-if="getTotalHoras(dia) > 0" class="text-[10px] font-bold px-2 py-0.5 rounded border bg-blue-50 text-dark border-blue-100">{{ getTotalHoras(dia) }}h</span>
          </div>

          <div v-if="getTipoDia(new Date(anioActual, mesActualIndex, dia))" class="flex-1 flex items-center justify-center mt-2">
              <span class="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded w-full text-center border shadow-sm"
                    :class="{
                        'text-emerald-700 bg-emerald-100/80 border-emerald-200': getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'vacaciones',
                        'text-orange-700 bg-orange-100/80 border-orange-200': getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'festivo',
                        'text-blue-700 bg-blue-100/80 border-blue-200': getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'asuntos'
                    }">
                  {{ getLabelDia(new Date(anioActual, mesActualIndex, dia)) }}
              </span>
          </div>

          <div v-else-if="!esFinDeSemana(dia)">
             <div v-for="(item, idx) in getImputacionesPorDia(dia)" :key="idx" 
                  @click.stop="abrirSolicitud(item, dia)"
                  class="text-[10px] p-1.5 rounded border-l-2 mb-1 truncate shadow-sm cursor-pointer transition transform hover:scale-105 flex justify-between items-center group"
                  :class="item.color">
               <span class="truncate font-semibold">{{ item.proyecto }}</span>
               <span class="font-bold opacity-80 ml-1">{{ item.horas }}h</span>
             </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card p-0 overflow-hidden shadow-lg">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50/50 flex justify-between items-center">
            <h2 class="font-bold text-lg text-dark flex items-center gap-2"><FileText class="w-5 h-5 text-primary" /> Resumen de Proyectos</h2>
            <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-gray-500 uppercase tracking-wide">Total Mes:</span>
                <span class="text-lg font-bold text-dark bg-blue-50 px-3 py-1 rounded-lg border border-blue-100">{{ totalHorasMes }}h</span>
            </div>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-white text-xs uppercase tracking-wider border-b-2 border-gray-100 text-dark">
                        <th class="px-6 py-3 font-bold">Cliente</th>
                        <th class="px-6 py-3 font-bold">Cód. Proyecto</th>
                        <th class="px-6 py-3 font-bold">Proyecto / Tarea</th>
                        <th class="px-6 py-3 font-bold text-center">Horas Mensuales</th>
                    </tr>
                </thead>
                <tbody class="text-sm text-gray-700 divide-y divide-gray-50">
                    <tr v-for="(item, index) in resumenProyectos" :key="index" class="hover:bg-blue-50/10 transition">
                        <td class="px-6 py-3"><div class="flex items-center gap-2 font-medium text-dark"><Briefcase class="w-3.5 h-3.5 text-gray-400"/><span>{{ item.cliente }}</span></div></td>
                        <td class="px-6 py-3"><span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-gray-100 text-gray-600 text-xs font-mono border border-gray-200"><Hash class="w-3 h-3 opacity-50"/> {{ item.codigo }}</span></td>
                        <td class="px-6 py-3 font-medium">{{ item.proyecto }}</td>
                        <td class="px-6 py-3 text-center"><span class="inline-flex items-center gap-1 font-bold text-dark bg-blue-50 px-3 py-1 rounded-full border border-blue-100 min-w-[3rem] justify-center">{{ item.horas }}h</span></td>
                    </tr>
                    <tr v-if="resumenProyectos.length === 0"><td colspan="4" class="px-6 py-8 text-center text-gray-400 italic">No hay imputaciones registradas este mes.</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <div v-if="mostrarModalSolicitud" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-white w-full max-w-md rounded-xl shadow-2xl p-6 animate-in zoom-in-95">
            <div class="flex justify-between items-center mb-6 border-b border-gray-100 pb-3">
                <h3 class="text-lg font-bold text-dark flex items-center gap-2"><MessageSquare class="w-5 h-5 text-primary"/> Solicitar Corrección</h3>
                <button @click="mostrarModalSolicitud = false" class="text-gray-400 hover:text-red-500 transition"><X class="w-5 h-5"/></button>
            </div>
            <div class="space-y-5">
                <div class="p-3 bg-gray-50 rounded-lg border border-gray-200 text-sm">
                    <p class="text-gray-500 font-bold mb-1 flex items-center gap-2"><CalendarIcon class="w-4 h-4"/> {{ formSolicitud.fechaVisible }}</p>
                    <p class="text-primary font-bold flex items-center gap-2"><Briefcase class="w-4 h-4"/> {{ formSolicitud.proyecto }}</p>
                </div>
                <div class="flex items-center justify-between gap-4">
                    <div class="flex-1 text-center">
                        <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Horas Imputadas</label>
                        <div class="h-12 flex items-center justify-center bg-gray-100 rounded-xl border border-gray-200 text-gray-500 font-bold">{{ formSolicitud.horasActuales }}h</div>
                    </div>
                    <div class="pt-4 text-gray-300"><ArrowRight class="w-5 h-5"/></div>
                    <div class="flex-1 text-center">
                        <label class="block text-[10px] font-black uppercase mb-1" :class="formSolicitud.horasNuevas !== formSolicitud.horasActuales ? 'text-primary' : 'text-gray-400'">Horas a Solicitar</label>
                        <input v-model.number="formSolicitud.horasNuevas" type="number" step="0.5" class="w-full h-12 text-center rounded-xl border-2 font-bold transition-all outline-none" :class="formSolicitud.horasNuevas !== formSolicitud.horasActuales ? 'border-primary bg-blue-50 text-primary' : 'border-gray-200 bg-white text-dark'"/>
                    </div>
                </div>
                <div v-if="formSolicitud.horasNuevas === formSolicitud.horasActuales" class="flex items-center gap-2 text-[11px] font-bold text-gray-400 bg-gray-50 p-2 rounded-lg border border-dashed border-gray-200">
                    <Clock class="w-3.5 h-3.5"/> No has modificado las horas aún.
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-600 uppercase mb-1">Motivo del cambio</label>
                    <textarea v-model="formSolicitud.mensaje" rows="3" class="w-full border border-gray-200 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none" placeholder="Explica detalladamente por qué solicitas el cambio..."></textarea>
                </div>
                <div class="flex gap-3 pt-2">
                    <button @click="mostrarModalSolicitud = false" class="btn-secondary flex-1">Cancelar</button>
                    <button @click="enviarSolicitudJefe" class="btn-primary flex-1"><Send class="w-4 h-4 mr-2"/> Enviar Solicitud</button>
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
            <button @click="toast.show = false" type="button" class="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 items-center justify-center"><X class="w-4 h-4"/></button>
        </div>
    </transition>
  </div>
</template>

<style scoped>
input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
input[type=number] { -moz-appearance: textfield; }
</style>
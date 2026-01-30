<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon, 
  FileText,
  Hash, 
  Briefcase, 
  Clock
} from 'lucide-vue-next'

const router = useRouter()

// --- CONFIGURACIÓN DE DÍAS ESPECIALES ---
const diasEspeciales = [
  { dia: 12, mes: 1, tipo: 'festivo', label: 'Festivo' }, 
  { dia: 16, mes: 1, tipo: 'vacaciones', label: 'Vacaciones' }, 
  { dia: 20, mes: 1, tipo: 'asuntos_propios', label: 'Asuntos P.' }, 
  { dia: 27, mes: 1, tipo: 'libre_disposicion', label: 'Libre Disp.' }
]

const getTipoDia = (date) => {
  const especial = diasEspeciales.find(d => 
    d.dia === date.getDate() && d.mes === date.getMonth() && date.getFullYear() === 2026
  )
  return especial ? especial.tipo : null
}

const getLabelDia = (date) => {
  const especial = diasEspeciales.find(d => 
    d.dia === date.getDate() && d.mes === date.getMonth() && date.getFullYear() === 2026
  )
  return especial ? especial.label : null
}

// --- LÓGICA FECHAS ---
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

// --- DATOS SIMULADOS ---
const imputaciones = ref([
  { dia: 5, cliente: 'Banco Santander', codigo: 'SAN-001', proyecto: 'Auditoría Backend', horas: 8, color: 'bg-blue-50 text-blue-700 border-blue-100 hover:bg-blue-100' },
  { dia: 6, cliente: 'Mapfre', codigo: 'MAP-220', proyecto: 'Migración Cloud', horas: 4, color: 'bg-cyan-50 text-cyan-800 border-cyan-100 hover:bg-cyan-100' },
  { dia: 6, cliente: 'Interno', codigo: 'INT-999', proyecto: 'Formación Vue 3', horas: 4, color: 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100' },
  { dia: 12, cliente: 'Inditex', codigo: 'ITX-554', proyecto: 'API TPV', horas: 8.5, color: 'bg-fuchsia-50 text-fuchsia-800 border-fuchsia-100 hover:bg-fuchsia-100' },
  { dia: 20, cliente: 'Banco Santander', codigo: 'SAN-001', proyecto: 'Auditoría Backend', horas: 4, color: 'bg-blue-50 text-blue-700 border-blue-100 hover:bg-blue-100' },
])

const getImputacionesPorDia = (dia) => imputaciones.value.filter(imp => imp.dia === dia)
const getTotalHoras = (dia) => getImputacionesPorDia(dia).reduce((acc, curr) => acc + curr.horas, 0)

// --- AGRUPACIÓN POR PROYECTO (TOTAL MES) ---
const resumenProyectos = computed(() => {
  const grupos = {}
  imputaciones.value.forEach(imp => {
    const key = imp.codigo
    if (!grupos[key]) {
      grupos[key] = {
        cliente: imp.cliente,
        codigo: imp.codigo,
        proyecto: imp.proyecto,
        horas: 0
      }
    }
    grupos[key].horas += imp.horas
  })
  return Object.values(grupos).sort((a, b) => b.horas - a.horas)
})

const totalHorasMes = computed(() => {
  return imputaciones.value.reduce((acc, curr) => acc + curr.horas, 0)
})

const irAlDashboard = (dia) => {
  const fechaDestino = new Date(anioActual.value, mesActualIndex.value, dia)
  const offset = fechaDestino.getTimezoneOffset()
  const fechaLocal = new Date(fechaDestino.getTime() - (offset*60*1000))
  router.push({ name: 'dashboard', query: { fecha: fechaLocal.toISOString().split('T')[0] } })
}
</script>

<template>
  <div class="h-full flex flex-col font-sans bg-gray-50 p-6 overflow-y-auto">
    
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-4">
        <h1 class="text-3xl font-bold capitalize flex items-center gap-3" style="color: #232D4B;">
          <div class="p-2 rounded-lg bg-white shadow-sm border border-gray-100">
            <CalendarIcon class="w-6 h-6 text-[#26AA9B]"/>
          </div>
          {{ nombreMes }} <span class="font-light opacity-50">{{ anioActual }}</span>
        </h1>
        <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200 ml-6">
          <button @click="mesAnterior" class="p-2 hover:bg-gray-50 text-gray-600 rounded-l-lg border-r border-gray-200 transition"><ChevronLeft class="w-5 h-5" /></button>
          <button @click="irAHoy" class="px-4 py-2 text-xs font-bold tracking-widest hover:bg-gray-50 transition uppercase" style="color: #232D4B;">Hoy</button>
          <button @click="mesSiguiente" class="p-2 hover:bg-gray-50 text-gray-600 rounded-r-lg border-l border-gray-200 transition"><ChevronRight class="w-5 h-5" /></button>
        </div>
      </div>
      <button class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg shadow-sm hover:bg-gray-50 text-sm font-bold flex items-center gap-2">
        <FileText class="w-4 h-4"/> Exportar
      </button>
    </div>

    <div class="bg-white p-3 rounded-lg border border-gray-200 shadow-sm mb-4 flex flex-wrap items-center gap-4 text-xs font-medium">
        <span class="uppercase text-gray-400 tracking-wider mr-2 font-bold">Leyenda:</span>
        <div class="flex items-center gap-2 px-2 py-1 rounded-md bg-gray-50 border border-gray-100">
            <div class="w-2.5 h-2.5 rounded-full bg-white border border-gray-300"></div><span class="text-gray-600">Laborable</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1 rounded-md bg-rose-50 border border-rose-100">
            <div class="w-2.5 h-2.5 rounded-full bg-rose-300"></div><span class="text-rose-600">Festivo</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1 rounded-md bg-teal-50 border border-teal-100">
            <div class="w-2.5 h-2.5 rounded-full bg-teal-300"></div><span class="text-teal-600">Vacaciones</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1 rounded-md bg-amber-50 border border-amber-100">
            <div class="w-2.5 h-2.5 rounded-full bg-amber-300"></div><span class="text-amber-600">Libre Disp.</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1 rounded-md bg-violet-50 border border-violet-100">
            <div class="w-2.5 h-2.5 rounded-full bg-violet-300"></div><span class="text-violet-600">Asuntos P.</span>
        </div>
    </div>

    <div class="bg-white rounded-xl shadow-xl border border-gray-200 flex-none overflow-hidden mb-8">
      <div class="grid grid-cols-7 border-b border-gray-200">
        <div v-for="dia in diasSemana.slice(0, 5)" :key="dia" class="py-4 text-center text-xs font-bold uppercase tracking-widest bg-white" style="color: #232D4B;">{{ dia }}</div>
        <div v-for="dia in diasSemana.slice(5, 7)" :key="dia" class="py-4 text-center text-xs font-bold uppercase tracking-widest text-white/90" style="background-color: #232D4B;">{{ dia }}</div>
      </div>

      <div class="grid grid-cols-7 auto-rows-fr">
        <div v-for="blank in diasEnBlanco" :key="`blank-${blank}`" class="bg-gray-50/50 border-b border-r border-gray-100"></div>

        <div v-for="dia in diasDelMes" :key="dia" 
             class="min-h-[100px] p-2 border-b border-r border-gray-100 transition relative flex flex-col gap-1"
             :class="[
               esFinDeSemana(dia) ? 'bg-slate-100 cursor-default' : 'bg-white',
               getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'festivo' ? 'bg-rose-50/40' : '',
               getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'vacaciones' ? 'bg-teal-50/40' : '',
               getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'libre_disposicion' ? 'bg-amber-50/40' : '',
               getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'asuntos_propios' ? 'bg-violet-50/40' : '',
             ]"
             :style="esFinDeSemana(dia) ? 'background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.03) 10px, rgba(0,0,0,0.03) 20px);' : ''"
        >
          <div class="flex justify-between items-start mb-2">
            <span class="text-sm font-bold w-7 h-7 flex items-center justify-center rounded-full transition-all"
                  :style="esHoy(dia) ? 'background-color: #26AA9B; color: white;' : (esFinDeSemana(dia) ? 'color: #cbd5e1;' : 'color: #232D4B;')">
              {{ dia }}
            </span>
            <span v-if="getTotalHoras(dia) > 0" class="text-[10px] font-bold px-2 py-0.5 rounded border"
                  :class="esFinDeSemana(dia) ? 'bg-slate-200 text-slate-400 border-transparent' : 'bg-blue-50 text-[#232D4B] border-blue-100'">
              {{ getTotalHoras(dia) }}h
            </span>
          </div>

          <div v-if="getTipoDia(new Date(anioActual, mesActualIndex, dia))" class="mb-1 flex justify-center">
             <span class="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full border shadow-sm tracking-wide"
               :class="{
                 'text-rose-600 bg-rose-50 border-rose-100': getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'festivo',
                 'text-teal-600 bg-teal-50 border-teal-100': getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'vacaciones',
                 'text-amber-600 bg-amber-50 border-amber-100': getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'libre_disposicion',
                 'text-violet-600 bg-violet-50 border-violet-100': getTipoDia(new Date(anioActual, mesActualIndex, dia)) === 'asuntos_propios'
               }">
               {{ getLabelDia(new Date(anioActual, mesActualIndex, dia)) }}
             </span>
          </div>

          <div v-if="!esFinDeSemana(dia)">
             <div v-for="(item, idx) in getImputacionesPorDia(dia)" :key="idx" 
                  @click.stop="irAlDashboard(dia)"
                  class="text-[10px] p-1.5 rounded border-l-2 mb-1 truncate shadow-sm cursor-pointer transition transform hover:scale-105 flex justify-between items-center group"
                  :class="item.color" title="Ir al detalle semanal">
               <span class="truncate font-semibold">{{ item.proyecto }}</span>
               <span class="font-bold opacity-80 ml-1">{{ item.horas }}h</span>
             </div>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50/50 flex justify-between items-center">
            <h2 class="font-bold text-lg text-[#232D4B] flex items-center gap-2">
                <FileText class="w-5 h-5 text-[#26AA9B]" />
                Resumen de Proyectos
            </h2>
            <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-gray-500 uppercase tracking-wide">Total Mes:</span>
                <span class="text-lg font-bold text-[#232D4B] bg-blue-50 px-3 py-1 rounded-lg border border-blue-100">
                    {{ totalHorasMes }}h
                </span>
            </div>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-white text-xs uppercase tracking-wider border-b-2 border-gray-100" style="color: #232D4B;">
                        <th class="px-6 py-3 font-bold">Cliente</th>
                        <th class="px-6 py-3 font-bold">Cód. Proyecto</th>
                        <th class="px-6 py-3 font-bold">Proyecto / Tarea</th>
                        <th class="px-6 py-3 font-bold text-center">Horas Mensuales</th>
                    </tr>
                </thead>
                <tbody class="text-sm text-gray-700 divide-y divide-gray-50">
                    <tr v-for="(item, index) in resumenProyectos" :key="index" class="hover:bg-blue-50/10 transition">
                        
                        <td class="px-6 py-3">
                            <div class="flex items-center gap-2 font-medium text-[#232D4B]">
                                <Briefcase class="w-3.5 h-3.5 text-gray-400"/>
                                <span>{{ item.cliente }}</span>
                            </div>
                        </td>

                        <td class="px-6 py-3">
                            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-gray-100 text-gray-600 text-xs font-mono border border-gray-200">
                                <Hash class="w-3 h-3 opacity-50"/> {{ item.codigo }}
                            </span>
                        </td>

                        <td class="px-6 py-3 font-medium">
                            {{ item.proyecto }}
                        </td>

                        <td class="px-6 py-3 text-center">
                            <span class="inline-flex items-center gap-1 font-bold text-[#232D4B] bg-blue-50 px-3 py-1 rounded-full border border-blue-100 min-w-[3rem] justify-center">
                                {{ item.horas }}h
                            </span>
                        </td>
                    </tr>
                    
                    <tr v-if="resumenProyectos.length === 0">
                        <td colspan="4" class="px-6 py-8 text-center text-gray-400 italic">
                            No hay imputaciones registradas este mes.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

  </div>
</template>
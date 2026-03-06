<script setup>
import { ref, onMounted, watch } from 'vue'
import { useDataStore } from '../stores/dataStore'
import { 
    Calendar, Clock, LayoutGrid, ChevronLeft, 
    ChevronRight, Info, AlertCircle, Loader2, Target
} from 'lucide-vue-next'

const store = useDataStore()
const datos = ref(null)
const cargando = ref(true)

// Estado del filtro
const mesActual = new Date().getMonth() + 1
const anioActual = new Date().getFullYear()
const mesSeleccionado = ref(mesActual)
const anioSeleccionado = ref(anioActual)

const meses = [
    { v: 1, n: 'Enero' }, { v: 2, n: 'Febrero' }, { v: 3, n: 'Marzo' },
    { v: 4, n: 'Abril' }, { v: 5, n: 'Mayo' }, { v: 6, n: 'Junio' },
    { v: 7, n: 'Julio' }, { v: 8, n: 'Agosto' }, { v: 9, n: 'Septiembre' },
    { v: 10, n: 'Octubre' }, { v: 11, n: 'Noviembre' }, { v: 12, n: 'Diciembre' }
]

const cargarData = async () => {
    cargando.value = true
    const user = store.getCurrentUser()
    if (!user) return
    
    try {
        const res = await fetch(`http://localhost:5000/api/myprojects/analitica-mensual?usuario_id=${user.id}&mes=${mesSeleccionado.value}&anio=${anioSeleccionado.value}`)
        const json = await res.json()
        datos.value = json.data
    } catch (e) {
        console.error(e)
    } finally {
        cargando.value = false
    }
}

// Recargar cuando cambie el selector
watch([mesSeleccionado, anioSeleccionado], cargarData)
onMounted(cargarData)

const getBarColor = (p) => {
    if (p < 50) return 'bg-slate-300'
    if (p >= 100) return 'bg-emerald-500'
    return 'bg-primary'
}
</script>

<template>
  <div class="p-6 bg-slate-50 min-h-screen h-full overflow-y-auto pb-24 font-sans">
    
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
            <h1 class="text-2xl font-black text-slate-800 uppercase tracking-tight flex items-center gap-3">
                <LayoutGrid class="w-6 h-6 text-primary" /> Mi Dedicación Mensual
            </h1>
            <p class="text-slate-500 text-sm">Control de horas asignadas vs realizadas.</p>
        </div>

        <div class="flex items-center gap-2 bg-white p-1.5 rounded-2xl shadow-sm border border-slate-200">
            <select v-model="mesSeleccionado" class="bg-transparent font-bold text-sm text-slate-700 outline-none px-4 py-2 border-r border-slate-100">
                <option v-for="m in meses" :key="m.v" :value="m.v">{{ m.n }}</option>
            </select>
            <select v-model="anioSeleccionado" class="bg-transparent font-bold text-sm text-slate-700 outline-none px-4 py-2">
                <option :value="2026">2026</option>
                <option :value="2025">2025</option>
            </select>
        </div>
    </div>

    <div v-if="cargando" class="flex justify-center py-20"><Loader2 class="animate-spin text-primary w-10 h-10" /></div>

    <div v-else-if="datos">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-[#002B49] p-6 rounded-3xl text-white shadow-xl flex justify-between items-center">
                <div>
                    <p class="text-[10px] font-bold text-blue-200 uppercase tracking-widest mb-1">Total Mes</p>
                    <p class="text-4xl font-black">{{ datos.totales.mes_real }}h</p>
                </div>
                <Clock class="w-12 h-12 opacity-20" />
            </div>
            
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex justify-between items-center">
                <div>
                    <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Acumulado Año</p>
                    <p class="text-3xl font-black text-slate-800">{{ datos.totales.ano_acumulado }}h</p>
                </div>
                <Calendar class="w-10 h-10 text-slate-100" />
            </div>

            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-center">
                <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Nota Informativa</p>
                <div class="flex items-center gap-2 text-amber-600 bg-amber-50 p-2 rounded-xl border border-amber-100">
                    <Info class="w-4 h-4 shrink-0" />
                    <p class="text-[10px] font-bold leading-tight">Las barras de progreso se basan en tu asignación semanal de cada proyecto.</p>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div v-for="p in datos.proyectos" :key="p.proyecto" class="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition group">
                <div class="p-6">
                    <div class="flex justify-between items-start mb-6">
                        <div>
                            <span class="text-[10px] font-black text-blue-600 uppercase bg-blue-50 px-3 py-1 rounded-full tracking-wider">{{ p.cliente }}</span>
                            <h3 class="text-xl font-bold text-slate-800 mt-2">{{ p.proyecto }}</h3>
                        </div>
                        <div class="text-right">
                            <p class="text-[10px] font-bold text-slate-400 uppercase">Asignación</p>
                            <p class="text-lg font-black text-slate-700">{{ p.asignado_semanal }}h<span class="text-xs text-slate-400 font-medium">/sem</span></p>
                        </div>
                    </div>

                    <div class="space-y-3">
                        <div class="flex justify-between items-end">
                            <div class="flex items-baseline gap-1">
                                <span class="text-3xl font-black text-slate-800">{{ p.real }}</span>
                                <span class="text-sm text-slate-400 font-bold">/ {{ p.objetivo_mensual }}h mes</span>
                            </div>
                            <span class="text-sm font-black text-primary">{{ p.porcentaje }}%</span>
                        </div>
                        <div class="w-full h-4 bg-slate-100 rounded-full overflow-hidden p-1">
                            <div class="h-full rounded-full transition-all duration-1000" 
                                 :class="getBarColor(p.porcentaje)"
                                 :style="{ width: Math.min(p.porcentaje, 100) + '%' }"></div>
                        </div>
                    </div>
                </div>
                
                <div class="bg-slate-50 px-6 py-3 border-t border-slate-100 flex justify-between items-center">
                    <div class="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase">
                        <Target class="w-3 h-3" /> Estado: 
                        <span :class="p.porcentaje >= 100 ? 'text-emerald-600' : 'text-amber-500'">
                            {{ p.porcentaje >= 100 ? 'Objetivo Cumplido' : 'En Progreso' }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="datos.proyectos.length === 0" class="bg-white p-20 rounded-3xl text-center border-2 border-dashed border-slate-200">
            <p class="text-slate-400 font-bold uppercase text-xs tracking-widest">Sin imputaciones en {{ meses[mesSeleccionado-1].n }}</p>
        </div>
    </div>
  </div>
</template>
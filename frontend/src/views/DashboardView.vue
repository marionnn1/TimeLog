<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '../stores/dataStore' 
import {
    ChevronLeft, ChevronRight, Plus, Trash2, Save, Building2, Info, X, RotateCcw, 
    Clock, ChevronDown, Check, AlertCircle, CheckCircle2, Loader2
} from 'lucide-vue-next'

const route = useRoute()
const store = useDataStore() 

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null
const cargando = ref(false)

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

const horasDiarias = ref(8.5) 
const mostrarSelectorJornada = ref(false)

const opcionesHoras = computed(() => {
    const opts = []
    for (let h = 8.5; h >= 4; h -= 0.5) {
        opts.push({ 
            value: h, 
            label: `${h}h / día`,
            desc: h === 8.5 ? 'Estándar (Viernes 6.5h)' : 'Jornada lineal L-V' 
        })
    }
    return opts
})

const seleccionarHoras = (valor) => {
    horasDiarias.value = valor
    mostrarSelectorJornada.value = false
}

const selectorRef = ref(null)
const handleClickOutside = (event) => {
    if (selectorRef.value && !selectorRef.value.contains(event.target)) {
        mostrarSelectorJornada.value = false
    }
}

const ausenciasPersonales = ref([])

const cargarAusenciasAPI = async () => {
    const user = store.getCurrentUser()
    if (!user) return
    try {
        const m1 = diasSemana.value[0].getMonth() + 1
        const y1 = diasSemana.value[0].getFullYear()
        const m2 = diasSemana.value[6].getMonth() + 1
        const y2 = diasSemana.value[6].getFullYear()
        
        const res1 = await fetch(`http://localhost:5000/api/absences?mes=${m1}&anio=${y1}`)
        const json1 = await res1.json()
        let todas = json1.status === 'success' ? json1.data : []

        if (m1 !== m2 || y1 !== y2) {
            const res2 = await fetch(`http://localhost:5000/api/absences?mes=${m2}&anio=${y2}`)
            const json2 = await res2.json()
            if (json2.status === 'success') todas = todas.concat(json2.data)
        }
        
        ausenciasPersonales.value = todas.filter(a => String(a.userId) === String(user.id))
    } catch (e) {
        console.error("Error cargando ausencias:", e)
    }
}

// Creamos arrays computados. Si hay cambios, Vue redibuja la tabla al instante.
const tiposDiasSemana = computed(() => {
    return diasSemana.value.map(date => {
        const offset = date.getTimezoneOffset() * 60000
        const iso = new Date(date.getTime() - offset).toISOString().split('T')[0]
        const ausencia = ausenciasPersonales.value.find(a => a.fecha === iso)
        if (!ausencia) return null
        return (ausencia.tipo === 'asuntos' || ausencia.tipo === 'asuntos_propios') ? 'asuntos' : ausencia.tipo
    })
})

const labelsDiasSemana = computed(() => {
    return tiposDiasSemana.value.map(tipo => {
        if (!tipo) return null
        if (tipo === 'asuntos') return 'Asuntos P.'
        return tipo.charAt(0).toUpperCase() + tipo.slice(1)
    })
})
// ==========================================

const mostrarModal = ref(false)
const nuevoRegistro = ref({ proyectoId: undefined })
const fechaActual = ref(new Date())
const diaSeleccionado = ref(new Date().getDate())
const proyectosRealDB = ref([])
const filas = ref([])

const esPasoInvalido = (valor) => {
    if (!valor || valor === 0) return false
    return !Number.isInteger(valor * 2)
}

const cargarProyectosParaModal = async () => {
    const user = store.getCurrentUser();
    if (!user) return;

    try {
        const res = await fetch('http://localhost:5000/api/proyectos')
        const json = await res.json()
        if (json.status === 'success') {
            // Filtramos proyectos: que estén activos Y que el usuario esté en su Equipo
            proyectosRealDB.value = json.data.filter(p => {
                const estaActivo = p.Estado === 'Activo';
                const estaAsignado = p.Equipo && p.Equipo.some(miembro => String(miembro.id) === String(user.id));
                
                return estaActivo && estaAsignado;
            })
        }
    } catch (e) {
        console.error("Error al obtener proyectos maestros", e)
    }
}

const cargarHorasDesdeAPI = async () => {
    const user = store.getCurrentUser()
    if (!user) return
    const lunesStr = lunesActual.value.toISOString().split('T')[0]
    try {
        cargando.value = true
        const res = await fetch(`http://localhost:5000/api/myprojects/semana?usuario_id=${user.id}&fecha_lunes=${lunesStr}`)
        const json = await res.json()
        if (json.status === 'success') {
            const datosBackend = json.data || []
            const nuevasFilas = []
            const proyectosUnicos = [...new Set(datosBackend.map(d => d.ProyectoId))]
            
            proyectosUnicos.forEach(pId => {
                const registrosP = datosBackend.filter(d => d.ProyectoId === pId)
                nuevasFilas.push({
                    id: pId,
                    cliente: registrosP[0].ClienteNombre,
                    proyecto: registrosP[0].ProyectoNombre,
                    horas: Array(7).fill(0).map((_, i) => {
                        const fechaBuscada = new Date(lunesActual.value)
                        fechaBuscada.setDate(lunesActual.value.getDate() + i)
                        const isoBuscada = fechaBuscada.toISOString().split('T')[0]
                        const reg = registrosP.find(r => new Date(r.Fecha).toISOString().split('T')[0] === isoBuscada)
                        return reg ? reg.Horas : 0
                    }),
                    seleccionado: false
                })
            })
            filas.value = nuevasFilas
        }
    } catch (error) {
        showToast("Error al conectar con el servidor", "error")
    } finally {
        cargando.value = false
    }
}

const guardarCambios = async () => {
    if (hayErrores.value) return showToast('Por favor corrige los errores antes de guardar.', 'error')
    
    // Forzamos 0 horas en días bloqueados por seguridad antes de enviar
    filas.value.forEach(f => {
        f.horas = f.horas.map((h, i) => tiposDiasSemana.value[i] ? 0 : h)
    })

    const user = store.getCurrentUser()
    const fechasSemana = diasSemana.value.map(d => d.toISOString().split('T')[0])
    const payload = {
        usuario_id: user.id,
        fechas: fechasSemana,
        filas: filas.value.map(f => ({ id_proyecto: f.id, horas: f.horas }))
    }
    try {
        const res = await fetch('http://localhost:5000/api/myprojects/guardar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        if (res.ok) {
            showToast('Imputaciones guardadas correctamente', 'success')
            await cargarHorasDesdeAPI()
        } else {
            showToast('Error al guardar: Revisa la consola del servidor', 'error')
        }
    } catch (error) {
        showToast('Error de red', 'error')
    }
}

const getLunesSemana = (fecha) => {
    const d = new Date(fecha)
    const dia = d.getDay()
    const diff = d.getDate() - dia + (dia === 0 ? -6 : 1)
    return new Date(d.setDate(diff))
}
const lunesActual = computed(() => getLunesSemana(fechaActual.value))
const diasSemana = computed(() => {
    const dias = []
    for (let i = 0; i < 7; i++) {
        const d = new Date(lunesActual.value)
        d.setDate(lunesActual.value.getDate() + i)
        dias.push(new Date(d))
    }
    return dias
})

watch(lunesActual, () => {
    cargarHorasDesdeAPI()
    cargarAusenciasAPI() // Recargar ausencias al cambiar de semana
})

const esJornadaVerano = (date) => { const mes = date.getMonth(); return mes === 6 || mes === 7 }

const getMaxHorasDia = (index) => {
    const date = diasSemana.value[index]
    if (tiposDiasSemana.value[index]) return 0 
    if (date.getDay() === 0 || date.getDay() === 6) return 0
    
    // Regla 1: Verano (Julio y Agosto) -> Máximo 7h TODOS los días laborables (incluyendo viernes)
    if (esJornadaVerano(date)) {
        return Math.min(horasDiarias.value, 7.0);
    }

    // Regla 2: Resto del año (Invierno) -> L-J lo que marque la jornada, Viernes máximo 6.5h (si la jornada es > 7h)
    let maxHoras = horasDiarias.value;
    if (date.getDay() === 5 && horasDiarias.value > 7) {
        maxHoras = Math.min(maxHoras, 6.5);
    }

    return maxHoras;
}
const getMaxHorasSemana = () => {
    return diasSemana.value.reduce((total, _, i) => total + getMaxHorasDia(i), 0)
}

const nombresDias = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']
const formatoFechaCabecera = (fecha) => fecha.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
const esFinDeSemana = (date) => { const d = date.getDay(); return d === 0 || d === 6 }
const esHoy = (date) => {
    const hoy = new Date()
    return date.getDate() === hoy.getDate() && date.getMonth() === hoy.getMonth() && date.getFullYear() === hoy.getFullYear()
}
const esEditable = (index) => {
    const date = diasSemana.value[index]
    const hoy = new Date(); hoy.setHours(0,0,0,0)
    const fComp = new Date(date); fComp.setHours(0,0,0,0)
    // No editable si es fin de semana, pasado, o si hay vacaciones
    return !esFinDeSemana(date) && fComp >= hoy && !tiposDiasSemana.value[index]
}

const esSeleccionado = (date) => date.getDate() === diaSeleccionado.value && date.getMonth() === fechaActual.value.getMonth()
const semanaAnterior = () => { const d = new Date(fechaActual.value); d.setDate(d.getDate() - 7); fechaActual.value = d }
const semanaSiguiente = () => { const d = new Date(fechaActual.value); d.setDate(d.getDate() + 7); fechaActual.value = d }
const seleccionarDia = (date) => { diaSeleccionado.value = date.getDate() }
const irAHoy = () => { fechaActual.value = new Date(); diaSeleccionado.value = new Date().getDate() }

const textoBotonCentral = computed(() => {
    const hoy = new Date()
    const seleccion = new Date(fechaActual.value); seleccion.setDate(diaSeleccionado.value)
    if (seleccion.getDate() === hoy.getDate() && seleccion.getMonth() === hoy.getMonth()) return 'HOY'
    return `${nombresDias[seleccion.getDay() === 0 ? 6 : seleccion.getDay() - 1]} ${diaSeleccionado.value}`
})

const handleFocus = (event) => { if (event.target.value == 0) event.target.value = '' }
const handleBlur = (event, fila, index) => { if (event.target.value === '') fila.horas[index] = 0 }
const totalFila = (fila) => fila.horas.reduce((acc, h) => acc + (parseFloat(h) || 0), 0)
const totalDia = (index) => filas.value.reduce((acc, f) => acc + (parseFloat(f.horas[index]) || 0), 0)
const totalSemanal = computed(() => filas.value.reduce((acc, f) => acc + totalFila(f), 0))

const excedeLimiteDiario = (index) => {
    const max = getMaxHorasDia(index)
    return max > 0 && totalDia(index) > max
}
const excedeLimiteSemanal = computed(() => totalSemanal.value > getMaxHorasSemana())

const hayErrores = computed(() => {
    const excedeHoras = excedeLimiteSemanal.value || Array.from({length:7}).some((_,i) => excedeLimiteDiario(i));
    const tieneDecimalesMal = filas.value.some(f => f.horas.some(h => esPasoInvalido(h)));
    return excedeHoras || tieneDecimalesMal;
})

const abrirModal = () => { nuevoRegistro.value = { proyectoId: undefined }; mostrarModal.value = true }
const cerrarModal = () => { mostrarModal.value = false }
const confirmarAnadirLinea = () => {
    const p = proyectosRealDB.value.find(x => x.Id === nuevoRegistro.value.proyectoId)
    if (!p) return showToast('Selecciona un proyecto válido', 'error')
    if (filas.value.find(f => f.id === p.Id)) return showToast('El proyecto ya está en la lista', 'error')
    
    filas.value.push({ 
        id: p.Id, 
        cliente: p.ClienteNombre || 'Cliente', 
        proyecto: p.Nombre, 
        horas: [0, 0, 0, 0, 0, 0, 0], 
        seleccionado: false 
    })
    cerrarModal()
}
const borrarLineas = () => {
    filas.value = filas.value.filter(f => !f.seleccionado)
    showToast('Líneas eliminadas de la vista', 'success')
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
    cargarHorasDesdeAPI()
    cargarProyectosParaModal()
    cargarAusenciasAPI() // Llamar nada más entrar
})
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-4 gap-6 relative">
        <div class="flex flex-col gap-3">
            <div class="flex justify-between items-end">
                <div class="flex items-center gap-3">
                    <h1 class="h1-title capitalize">{{ formatoFechaCabecera(lunesActual) }}</h1>
                    <span class="text-sm font-medium text-gray-400 px-2 border-l border-gray-300">
                        Semana {{ lunesActual.getDate() }} - {{ new Date(lunesActual.getTime() + 6 * 24 * 60 * 60 * 1000).getDate() }}
                    </span>
                </div>
                <div class="flex gap-4 items-center">
                    <div class="relative" ref="selectorRef">
                        <button @click="mostrarSelectorJornada = !mostrarSelectorJornada" 
                                class="flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-4 py-2.5 shadow-sm hover:shadow-md transition-all group min-w-[180px] justify-between">
                            <div class="flex items-center gap-3">
                                <Clock class="w-4 h-4 text-blue-600" />
                                <div class="flex flex-col items-start text-left leading-none">
                                    <span class="text-[10px] text-gray-400 font-bold uppercase mb-0.5">Jornada</span>
                                    <span class="text-sm font-bold text-gray-700">{{ horasDiarias }}h / día</span>
                                </div>
                            </div>
                            <ChevronDown class="w-4 h-4 text-gray-400" :class="mostrarSelectorJornada ? 'rotate-180' : ''"/>
                        </button>
                        <div v-if="mostrarSelectorJornada" class="absolute top-full right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border z-50 overflow-hidden">
                            <div v-for="opcion in opcionesHoras" :key="opcion.value" @click="seleccionarHoras(opcion.value)"
                                 class="px-4 py-3 hover:bg-slate-50 cursor-pointer flex items-center gap-3 border-b last:border-0 transition-colors">
                                <div class="w-4 h-4 rounded-full border flex items-center justify-center" :class="horasDiarias === opcion.value ? 'bg-blue-600 border-blue-600' : 'border-gray-300'">
                                    <Check v-if="horasDiarias === opcion.value" class="w-2.5 h-2.5 text-white" stroke-width="3" />
                                </div>
                                <div class="flex flex-col">
                                    <span class="text-sm font-bold text-gray-700">{{ opcion.label }}</span>
                                    <span class="text-xs text-gray-400">{{ opcion.desc }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="h-8 w-px bg-gray-200 mx-2"></div>
                    <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                        <button @click="semanaAnterior" class="p-2 hover:bg-gray-50 text-gray-600 border-r"><ChevronLeft class="w-5 h-5" /></button>
                        <button @click="irAHoy" class="px-4 py-2 text-sm font-bold uppercase tracking-wide hover:bg-gray-50 flex items-center gap-2 min-w-[100px] justify-center text-dark">
                            <RotateCcw v-if="textoBotonCentral !== 'HOY'" class="w-3 h-3 opacity-50" /> {{ textoBotonCentral }}
                        </button>
                        <button @click="semanaSiguiente" class="p-2 hover:bg-gray-50 text-gray-600 border-l"><ChevronRight class="w-5 h-5" /></button>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-7 gap-3 h-32 relative">
                <div v-if="cargando" class="absolute inset-0 z-20 flex items-center justify-center bg-gray-50/50 backdrop-blur-[1px] rounded-xl">
                    <Loader2 class="w-8 h-8 text-primary animate-spin" />
                </div>
                <div v-for="(fecha, index) in diasSemana" :key="index" @click="seleccionarDia(fecha)"
                    class="relative rounded-xl border shadow-sm flex flex-col items-center justify-between p-3 transition-all cursor-pointer group"
                    :class="[
                        esSeleccionado(fecha) ? 'ring-2 ring-offset-2 ring-primary border-primary' : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-md',
                        esHoy(fecha) ? 'bg-blue-50/50' : '',
                        esFinDeSemana(fecha) ? 'bg-slate-100 border-slate-200 cursor-default opacity-60' : '',
                        excedeLimiteDiario(index) ? 'border-red-500 bg-red-50' : ''
                    ]">
                    <span class="text-xs font-bold uppercase tracking-widest" :class="esHoy(fecha) ? 'text-primary' : 'text-gray-400'">{{ nombresDias[index] }}</span>
                    <span class="text-2xl font-bold" :class="esHoy(fecha) ? 'text-dark' : (esFinDeSemana(fecha) ? 'text-gray-400' : 'text-gray-700')">{{ fecha.getDate() }}</span>
                    
                    <div v-if="tiposDiasSemana[index]" class="mt-1">
                        <span class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded shadow-sm" :class="{
                            'bg-orange-100 text-orange-700': tiposDiasSemana[index] === 'festivo',
                            'bg-emerald-100 text-emerald-700': tiposDiasSemana[index] === 'vacaciones',
                            'bg-blue-100 text-blue-700': tiposDiasSemana[index] === 'asuntos'
                        }">{{ labelsDiasSemana[index] }}</span>
                    </div>

                    <div v-else-if="totalDia(index) > 0" class="px-2 py-0.5 rounded-full text-xs font-bold" :class="excedeLimiteDiario(index) ? 'bg-red-100 text-red-700 animate-pulse' : 'bg-blue-100 text-dark'">{{ totalDia(index) }}h</div>
                    <div v-else class="h-5"></div>
                    <div v-if="esHoy(fecha)" class="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary"></div>
                </div>
            </div>
        </div>

        <div class="card flex-1 flex flex-col overflow-hidden p-0 bg-white rounded-2xl shadow-sm border border-gray-200">
            <div class="flex justify-between items-center px-6 py-4 border-b bg-gray-50/50">
                <h2 class="font-bold text-sm uppercase tracking-wider text-dark flex items-center gap-2"><Info class="w-4 h-4 text-primary" /> Detalle de Imputaciones</h2>
                <div class="flex gap-3">
                    <button @click="borrarLineas" class="flex items-center gap-2 px-3 py-1.5 text-xs font-bold text-red-600 hover:bg-red-50 rounded border border-transparent hover:border-red-100 transition uppercase">
                        <Trash2 class="w-3 h-3" /> Borrar
                    </button>
                    <button @click="abrirModal" class="btn-primary flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold bg-primary text-white hover:shadow-lg transition">
                        <Plus class="w-4 h-4" /> Añadir Línea
                    </button>
                </div>
            </div>

            <div class="overflow-x-auto flex-1 relative">
                <div v-if="cargando" class="absolute inset-0 z-10 flex items-center justify-center bg-white/40"><Loader2 class="w-10 h-10 text-primary animate-spin" /></div>
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-white text-xs uppercase tracking-wider border-b-2 border-gray-100 text-dark">
                            <th class="p-3 w-8 text-center"></th>
                            <th class="p-3 font-bold w-1/4">Cliente</th>
                            <th class="p-3 font-bold w-1/3">Proyecto</th>
                            <th v-for="(fecha, i) in diasSemana" :key="i" class="p-2 text-center w-14" :class="[esFinDeSemana(fecha) ? 'bg-slate-50 text-gray-400' : '', excedeLimiteDiario(i) ? 'bg-red-50 text-red-600 font-bold' : '']">
                                <div class="flex flex-col items-center"><span>{{ nombresDias[i] }}</span><span class="text-[10px] opacity-60 font-medium">{{ fecha.getDate() }}</span></div>
                            </th>
                            <th class="p-3 font-bold text-center w-16">Total</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-gray-700 divide-y divide-gray-50">
                        <tr v-if="filas.length === 0 && !cargando"><td colspan="11" class="px-6 py-12 text-center text-gray-400 italic">No hay imputaciones esta semana. Pulsa "Añadir Línea" para comenzar.</td></tr>
                        <tr v-for="fila in filas" :key="fila.id" class="hover:bg-blue-50/20 transition group">
                            <td class="p-3 text-center"><input type="checkbox" v-model="fila.seleccionado" class="rounded border-gray-300 text-primary"></td>
                            <td class="p-2"><div class="flex items-center gap-2 border border-transparent rounded px-2 py-1"><Building2 class="w-3 h-3 text-gray-400" /><span class="text-xs font-medium">{{ fila.cliente }}</span></div></td>
                            <td class="p-2"><span class="text-xs font-bold text-slate-700 px-2">{{ fila.proyecto }}</span></td>
                            
                            <td v-for="(hora, index) in fila.horas" :key="index" class="p-1 text-center relative" :class="[esFinDeSemana(diasSemana[index]) ? 'bg-slate-50' : '']">
                                
                                <div v-if="tiposDiasSemana[index]" class="w-full py-1 flex items-center justify-center cursor-not-allowed" :title="labelsDiasSemana[index]">
                                    <span class="text-[9px] font-black uppercase tracking-wider rounded px-1.5 py-1 w-full border text-center"
                                          :class="{
                                              'bg-emerald-50 text-emerald-700 border-emerald-200': tiposDiasSemana[index] === 'vacaciones',
                                              'bg-orange-50 text-orange-700 border-orange-200': tiposDiasSemana[index] === 'festivo',
                                              'bg-blue-50 text-blue-700 border-blue-200': tiposDiasSemana[index] === 'asuntos'
                                          }">
                                        {{ tiposDiasSemana[index].substring(0, 3) }}
                                    </span>
                                </div>

                                <input v-else type="number" min="0" max="24" step="0.5" v-model="fila.horas[index]" @focus="handleFocus" @blur="(e) => handleBlur(e, fila, index)" :disabled="!esEditable(index)"
                                    class="w-full text-center py-1 rounded transition font-medium text-sm disabled:cursor-not-allowed appearance-none"
                                    :class="{
                                        'text-primary font-bold border border-transparent hover:border-gray-300 bg-transparent': esEditable(index) && fila.horas[index] > 0 && !esPasoInvalido(fila.horas[index]),
                                        'bg-white border border-gray-200 text-primary shadow-sm': esEditable(index) && fila.horas[index] == 0,
                                        'bg-gray-100 text-gray-400 border border-transparent': !esEditable(index),
                                        'border-red-500 bg-red-50 text-red-600 ring-2 ring-red-500 font-black shadow-none': esEditable(index) && (excedeLimiteDiario(index) || esPasoInvalido(fila.horas[index]))
                                    }">
                            </td>
                            
                            <td class="p-3 text-center font-bold text-dark bg-gray-50 text-sm">{{ totalFila(fila) }}</td>
                        </tr>
                    </tbody>
                    <tfoot class="bg-gray-50 border-t border-gray-200 text-xs font-bold text-dark uppercase">
                        <tr>
                            <td colspan="3" class="p-3 text-right">Total Diario:</td>
                            <td v-for="(dia, index) in diasSemana" :key="index" class="p-2 text-center" :class="excedeLimiteDiario(index) ? 'bg-red-100' : ''">
                                <span :class="excedeLimiteDiario(index) ? 'text-red-600 font-extrabold' : (totalDia(index) > 0 ? 'text-primary' : 'text-gray-400')">{{ totalDia(index) }}</span>
                            </td>
                            <td class="p-3 text-center border-l border-blue-100 text-sm" :class="excedeLimiteSemanal ? 'bg-red-600 text-white' : 'bg-blue-50 text-blue-900'">{{ totalSemanal }} / {{ getMaxHorasSemana() }}</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <div class="p-4 bg-gray-50 border-t flex justify-end gap-4 items-center">
                <p v-if="hayErrores" class="text-xs font-bold text-red-600 animate-pulse flex items-center gap-1">
                    <AlertCircle class="w-4 h-4"/> 
                    {{ filas.some(f => f.horas.some(h => esPasoInvalido(h))) ? 'Solo se permiten incrementos de 0.5h (ej. 1.5)' : 'Corrige el exceso de horas' }}
                </p>
                <button @click="guardarCambios" :disabled="hayErrores || cargando" class="btn-primary px-8 py-2.5 rounded-xl font-bold uppercase tracking-widest text-xs shadow-md transition-all" :class="hayErrores ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-slate-900 text-white hover:shadow-xl'">
                    <Save class="w-4 h-4 mr-2" /> Guardar Imputaciones
                </button>
            </div>
        </div>

        <div v-if="mostrarModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in duration-200">
                <div class="bg-slate-50 border-b px-6 py-4 flex justify-between items-center">
                    <h3 class="text-lg font-bold text-slate-800">Añadir Proyecto</h3>
                    <button @click="cerrarModal" class="text-gray-400 hover:text-red-500"><X class="w-5 h-5" /></button>
                </div>
                <div class="p-6 space-y-4">
                    <div>
                        <label class="text-[10px] font-black uppercase text-slate-400 tracking-widest">Proyecto Asignado (Base de Datos)</label>
                        <select v-model="nuevoRegistro.proyectoId" class="w-full border-2 border-slate-100 rounded-xl p-3 mt-2 outline-none focus:border-primary transition bg-slate-50">
                            <option :value="undefined" disabled>Selecciona un proyecto activo...</option>
                            <option v-for="p in proyectosRealDB" :key="p.Id" :value="p.Id">
                                {{ p.Nombre }} - ({{ p.ClienteNombre }})
                            </option>
                        </select>
                    </div>
                </div>
                <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3">
                    <button @click="cerrarModal" class="px-4 py-2 text-sm font-bold text-slate-400 uppercase tracking-widest">Cancelar</button>
                    <button @click="confirmarAnadirLinea" class="bg-primary text-white px-6 py-2 rounded-xl font-bold uppercase tracking-widest text-xs">Añadir a la Tabla</button>
                </div>
            </div>
        </div>

        <transition enter-active-class="transform transition" enter-from-class="translate-y-2 opacity-0" enter-to-class="translate-y-0 opacity-100" leave-active-class="transition" leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="toast.show" class="fixed bottom-6 right-6 z-[200] flex items-center p-4 bg-white rounded-2xl shadow-2xl border border-slate-100 min-w-[300px]">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center mr-4" :class="toast.type === 'success' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'">
                    <component :is="toast.type === 'success' ? CheckCircle2 : AlertCircle" class="w-6 h-6"/>
                </div>
                <div class="text-sm font-bold text-slate-800">{{ toast.message }}</div>
            </div>
        </transition>
    </div>
</template>

<style scoped>
input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
</style>

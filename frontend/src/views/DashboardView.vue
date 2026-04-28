<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '../stores/dataStore'
import MyProjectsAPI from '../services/MyProjectsAPI'
import AbsencesAPI from '../services/AbsencesAPI'
import ToastNotification from '../components/common/ToastNotification.vue'

import {
    ChevronLeft, ChevronRight, Plus, Trash2, Save, Building2, Info, X, RotateCcw,
    Check, AlertCircle, AlertTriangle, CheckCircle2, Loader2, Wand2, Settings2, Briefcase, Clock
} from 'lucide-vue-next'

const route = useRoute()
const store = useDataStore()
const user = store.getCurrentUser()

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null
const cargando = ref(false)

const isSubmittingGuardar = ref(false)
const isAddingProject = ref(false)

const showToast = (message, type = 'success') => {
    toast.value = { show: true, message, type }
    if (toastTimeout) clearTimeout(toastTimeout)
    toastTimeout = setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

const mostrarAvisoSAP = computed(() => {
    const hoy = new Date();
    const anio = hoy.getFullYear();
    const mes = hoy.getMonth();

    const ultimoDiaMes = new Date(anio, mes + 1, 0).getDate();
    const diaActual = hoy.getDate();

    return diaActual === ultimoDiaMes || diaActual === (ultimoDiaMes - 1);
});

const configJornada = ref({
    tipoContrato: '40H',
    horasNormal: [8.5, 8.5, 8.5, 8.5, 6.5],
    horasVerano: [7.0, 7.0, 7.0, 7.0, 7.0]
})

const configJornadaTemp = ref(null)
const mostrarModalJornada = ref(false)

const cargarJornadaBD = async () => {
    if (!user) return
    try {
        const res = await MyProjectsAPI.getJornada(user.id)
        if (res.status === 'success' && res.data) {
            const local = localStorage.getItem(`jornada_custom_${user.id}`)
            if (local) {
                const parsed = JSON.parse(local)
                if (parsed.tipoContrato === (res.data.tipoContrato || '40H')) {
                    configJornada.value = parsed
                    return
                }
            }

            configJornada.value = {
                tipoContrato: res.data.tipoContrato || '40H',
                horasNormal: [
                    res.data.horasInviernoLJ || 8.5,
                    res.data.horasInviernoLJ || 8.5,
                    res.data.horasInviernoLJ || 8.5,
                    res.data.horasInviernoLJ || 8.5,
                    res.data.horasInviernoV || 6.5
                ],
                horasVerano: Array(5).fill(res.data.horasVerano || 7.0)
            }
        }
    } catch (e) {
        console.error("No se pudo cargar la jornada, usando por defecto.", e)
    }
}

const abrirModalJornada = () => {
    configJornadaTemp.value = JSON.parse(JSON.stringify(configJornada.value))
    mostrarModalJornada.value = true
}

const guardarConfigJornada = async () => {
    if (!user) return
    configJornada.value = JSON.parse(JSON.stringify(configJornadaTemp.value))

    localStorage.setItem(`jornada_custom_${user.id}`, JSON.stringify(configJornada.value))

    try {
        const payload = {
            usuario_id: user.id,
            tipoContrato: configJornada.value.tipoContrato,
            horasInviernoLJ: configJornada.value.horasNormal[0],
            horasInviernoV: configJornada.value.horasNormal[4],
            horasVerano: configJornada.value.horasVerano[0]
        }
        const res = await MyProjectsAPI.updateJornada(payload)
        if (res.status === 'success') {
            mostrarModalJornada.value = false
            showToast('Jornada guardada', 'success')
            cargarHorasDesdeAPI()
        }
    } catch (e) {
        showToast('Error al guardar', 'error')
    }
}

const ausenciasPersonales = ref([])

const cargarAusenciasAPI = async () => {
    if (!user) return
    try {
        const m1 = diasSemana.value[0].getMonth() + 1
        const y1 = diasSemana.value[0].getFullYear()
        const m2 = diasSemana.value[6].getMonth() + 1
        const y2 = diasSemana.value[6].getFullYear()

        let todas = []
        const res1 = await AbsencesAPI.getAusenciasMes(m1, y1)
        if (res1.status === 'success') todas = res1.data

        if (m1 !== m2 || y1 !== y2) {
            const res2 = await AbsencesAPI.getAusenciasMes(m2, y2)
            if (res2.status === 'success') todas = todas.concat(res2.data)
        }

        ausenciasPersonales.value = todas.filter(a => String(a.userId) === String(user.id))
    } catch (e) {
        console.error("Error cargando ausencias:", e)
    }
}

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
    if (!user) return
    try {
        const res = await MyProjectsAPI.getProyectosAsignados(user.id)
        if (res.status === 'success') {
            proyectosRealDB.value = res.data
        }
    } catch (e) {
        console.error("Error al obtener proyectos asignados", e)
    }
}

const proyectosAgrupadosParaModal = computed(() => {
    const grupos = {}
    proyectosRealDB.value.forEach(p => {
        const cliente = p.Cliente || 'Sin Cliente asignado'
        if (!grupos[cliente]) grupos[cliente] = []
        grupos[cliente].push(p)
    })

    return Object.keys(grupos).sort().map(cliente => ({
        cliente,
        proyectos: grupos[cliente].sort((a, b) => a.Nombre.localeCompare(b.Nombre))
    }))
})

const cargarHorasDesdeAPI = async () => {
    if (!user) return
    const lunesStr = lunesActual.value.toISOString().split('T')[0]
    try {
        cargando.value = true
        const res = await MyProjectsAPI.getSemana(user.id, lunesStr)
        if (res.status === 'success') {
            const datosBackend = res.data || []
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
        const mensajeError = error.response?.data?.error
            || error.response?.data?.message
            || 'Error de red al cargar';

        showToast(mensajeError, 'error');
    } finally {
        cargando.value = false
    }
}

const guardarCambios = async () => {
    if (hayErrores.value) return showToast('Por favor corrige los errores antes de guardar.', 'error')

    if (isSubmittingGuardar.value) return
    isSubmittingGuardar.value = true

    try {
        filas.value.forEach(f => {
            f.horas = f.horas.map((h, i) => tiposDiasSemana.value[i] ? 0 : h)
        })

        const fechasSemana = diasSemana.value.map(d => d.toISOString().split('T')[0])
        const payload = {
            usuario_id: user.id,
            fechas: fechasSemana,
            filas: filas.value.map(f => ({ id_proyecto: f.id, horas: f.horas }))
        }

        const res = await MyProjectsAPI.guardarImputaciones(payload)
        if (res.status === 'success') {
            showToast('Imputaciones guardadas correctamente', 'success')
            await cargarHorasDesdeAPI()
        } else {
            showToast('Error al guardar: Revisa la consola del servidor', 'error')
        }
    } catch (error) {
        const mensajeError = error.response?.data?.error
            || error.response?.data?.message
            || 'Error de red al guardar';

        showToast(mensajeError, 'error');
    } finally {
        isSubmittingGuardar.value = false
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
    cargarAusenciasAPI()
})

const esJornadaVerano = (date) => { const mes = date.getMonth(); return mes === 6 || mes === 7 }

const getMaxHorasDia = (index) => {
    const date = diasSemana.value[index]
    if (tiposDiasSemana.value[index]) return 0

    const day = date.getDay()
    if (day === 0 || day === 6) return 0

    const isVerano = esJornadaVerano(date)
    const dayIndex = day - 1

    if (configJornada.value.tipoContrato === '40H') {
        if (isVerano) return 7.0;
        if (day === 5) return 6.5;
        return 8.5;
    } else {
        if (isVerano) return configJornada.value.horasVerano[dayIndex];
        return configJornada.value.horasNormal[dayIndex];
    }
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

    if (esFinDeSemana(date) || tiposDiasSemana.value[index]) return false;

    return true;
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
    if (!esEditable(index)) return false;

    const max = getMaxHorasDia(index)
    return max > 0 && totalDia(index) > max
}

const excedeLimiteSemanal = computed(() => totalSemanal.value > getMaxHorasSemana())

const hayErrores = computed(() => {
    const excedeHoras = Array.from({ length: 7 }).some((_, i) => excedeLimiteDiario(i));
    const tieneDecimalesMal = filas.value.some(f => f.horas.some((h, i) => esEditable(i) && esPasoInvalido(h)));

    return excedeHoras || tieneDecimalesMal;
})

const autocompletarFila = (fila) => {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    let diasRellenados = 0;

    for (let i = 0; i < 7; i++) {
        const fechaDia = new Date(diasSemana.value[i]);
        fechaDia.setHours(0, 0, 0, 0);

        if (esEditable(i) && fechaDia <= hoy && (parseFloat(fila.horas[i]) || 0) === 0) {
            const maxDia = getMaxHorasDia(i);

            const horasOtrasFilas = filas.value
                .filter(f => f.id !== fila.id)
                .reduce((acc, f) => acc + (parseFloat(f.horas[i]) || 0), 0);

            const horasDisponibles = Math.max(0, maxDia - horasOtrasFilas);

            if (horasDisponibles > 0) {
                fila.horas[i] = horasDisponibles;
                diasRellenados++;
            }
        }
    }

    if (diasRellenados > 0) {
        showToast(`Se han autocompletado ${diasRellenados} días de la semana hasta hoy.`, 'success');
    } else {
        showToast('No hay días laborables libres hasta hoy para autocompletar.', 'info');
    }
}

const abrirModal = () => { nuevoRegistro.value = { proyectoId: undefined }; mostrarModal.value = true }
const cerrarModal = () => { mostrarModal.value = false }

const confirmarAnadirLinea = async () => {
    if (!nuevoRegistro.value.proyectoId) return showToast('Por favor, selecciona un proyecto de la lista', 'error')

    const p = proyectosRealDB.value.find(x => x.Id === nuevoRegistro.value.proyectoId)
    if (!p) return showToast('Selecciona un proyecto válido', 'error')
    if (filas.value.find(f => f.id === p.Id)) return showToast('El proyecto ya está en la lista', 'error')

    if (isAddingProject.value) return;
    isAddingProject.value = true;

    try {
        filas.value.push({
            id: p.Id,
            cliente: p.Cliente || 'Sin Cliente asignado',
            proyecto: p.Nombre,
            horas: [0, 0, 0, 0, 0, 0, 0],
            seleccionado: false
        })
        cerrarModal()
    } finally {
        isAddingProject.value = false;
    }
}

const borrarLineas = () => {
    const seleccionadas = filas.value.filter(f => f.seleccionado)

    if (seleccionadas.length === 0) {
        return showToast('Selecciona al menos una línea para borrar', 'error')
    }

    const conHoras = seleccionadas.filter(f => totalFila(f) > 0)
    const vacias = seleccionadas.filter(f => totalFila(f) === 0)

    if (conHoras.length > 0) {
        showToast('No puedes quitar proyectos con horas. Ponlas a 0 y guarda los cambios primero.', 'error')
        conHoras.forEach(f => f.seleccionado = false)
    }

    if (vacias.length > 0) {
        filas.value = filas.value.filter(f => !vacias.includes(f))
        if (conHoras.length === 0) {
            showToast('Líneas eliminadas de la vista', 'success')
        }
    }
}

onMounted(() => {
    cargarJornadaBD()
    cargarHorasDesdeAPI()
    cargarProyectosParaModal()
    cargarAusenciasAPI()
})
</script>

<template>
    <div class="h-full flex flex-col font-sans bg-gray-50 p-4 gap-6 relative">
        <div class="flex flex-col gap-3">
            <div class="flex justify-between items-end">
                <div class="flex items-center gap-3">
                    <h1 class="h1-title capitalize">{{ formatoFechaCabecera(lunesActual) }}</h1>
                    <span class="text-sm font-medium text-gray-400 px-2 border-l border-gray-300">
                        Semana {{ lunesActual.getDate() }} - {{ new Date(lunesActual.getTime() + 6 * 24 * 60 * 60 *
                            1000).getDate() }}
                    </span>
                </div>
                <div class="flex gap-4 items-center">

                    <button @click="abrirModalJornada"
                        class="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-4 py-2 shadow-sm hover:shadow-md hover:border-blue-300 transition-all text-sm font-bold text-gray-700">
                        <Settings2 class="w-4 h-4 text-primary" />
                        Contrato: <span class="text-primary font-black uppercase">{{ configJornada.tipoContrato ===
                            '40H' ? 'Completa' : 'Personalizada' }}</span>
                    </button>

                    <div class="h-8 w-px bg-gray-200 mx-2"></div>
                    <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                        <button @click="semanaAnterior" class="p-2 hover:bg-gray-50 text-gray-600 border-r">
                            <ChevronLeft class="w-5 h-5" />
                        </button>
                        <button @click="irAHoy"
                            class="px-4 py-2 text-sm font-bold uppercase tracking-wide hover:bg-gray-50 flex items-center gap-2 min-w-[100px] justify-center text-dark">
                            <RotateCcw v-if="textoBotonCentral !== 'HOY'" class="w-3 h-3 opacity-50" /> {{
                                textoBotonCentral }}
                        </button>
                        <button @click="semanaSiguiente" class="p-2 hover:bg-gray-50 text-gray-600 border-l">
                            <ChevronRight class="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            <div v-if="mostrarAvisoSAP"
                class="bg-amber-50 border border-amber-200 p-4 rounded-xl shadow-sm shrink-0 flex items-start gap-4 animate-pulse-slow">
                <div class="bg-amber-100 p-2 rounded-lg text-amber-600 mt-0.5">
                    <AlertTriangle class="w-6 h-6" />
                </div>
                <div>
                    <h3 class="font-bold text-amber-800 text-lg">Recordatorio de Cierre de Mes</h3>
                    <p class="text-sm text-amber-700 mt-1">
                        Faltan muy pocos días para terminar el mes. Por favor, asegúrate de tener todas tus horas
                        registradas aquí e
                        <span class="font-bold underline">imputadas correctamente en SAP</span> antes del cierre.
                    </p>
                </div>
            </div>

            <div class="grid grid-cols-7 gap-3 h-32 relative">
                <div v-if="cargando"
                    class="absolute inset-0 z-20 flex items-center justify-center bg-gray-50/50 backdrop-blur-[1px] rounded-xl">
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
                    <span class="text-xs font-bold uppercase tracking-widest"
                        :class="esHoy(fecha) ? 'text-primary' : 'text-gray-400'">{{ nombresDias[index] }}</span>
                    <span class="text-2xl font-bold"
                        :class="esHoy(fecha) ? 'text-dark' : (esFinDeSemana(fecha) ? 'text-gray-400' : 'text-gray-700')">{{
                            fecha.getDate() }}</span>

                    <div v-if="tiposDiasSemana[index]" class="mt-1">
                        <span class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded shadow-sm" :class="{
                            'bg-orange-100 text-orange-700': tiposDiasSemana[index] === 'festivo',
                            'bg-emerald-100 text-emerald-700': tiposDiasSemana[index] === 'vacaciones',
                            'bg-blue-100 text-blue-700': tiposDiasSemana[index] === 'asuntos'
                        }">{{ labelsDiasSemana[index] }}</span>
                    </div>

                    <div v-else-if="totalDia(index) > 0" class="px-2 py-0.5 rounded-full text-xs font-bold"
                        :class="excedeLimiteDiario(index) ? 'bg-red-100 text-red-700 animate-pulse' : 'bg-blue-100 text-dark'">
                        {{ totalDia(index) }}h</div>
                    <div v-else class="h-5"></div>
                    <div v-if="esHoy(fecha)" class="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary"></div>
                </div>
            </div>
        </div>

        <div
            class="card flex-1 flex flex-col overflow-hidden p-0 bg-white rounded-2xl shadow-sm border border-gray-200">
            <div class="flex justify-between items-center px-6 py-4 border-b bg-gray-50/50">
                <h2 class="font-bold text-sm uppercase tracking-wider text-dark flex items-center gap-2">
                    <Info class="w-4 h-4 text-primary" /> Detalle de Imputaciones
                </h2>
                <div class="flex gap-3">
                    <button @click="borrarLineas"
                        class="flex items-center gap-2 px-3 py-1.5 text-xs font-bold text-red-600 hover:bg-red-50 rounded border border-transparent hover:border-red-100 transition uppercase">
                        <Trash2 class="w-3 h-3" /> Borrar
                    </button>
                    <button @click="abrirModal"
                        class="btn-primary flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold bg-primary text-white hover:shadow-lg transition">
                        <Plus class="w-4 h-4" /> Añadir Proyecto
                    </button>
                </div>
            </div>

            <div class="overflow-x-auto flex-1 relative scrollbar-thin">
                <div v-if="cargando" class="absolute inset-0 z-10 flex items-center justify-center bg-white/40">
                    <Loader2 class="w-10 h-10 text-primary animate-spin" />
                </div>
                <table class="w-full text-left border-collapse min-w-max">
                    <thead>
                        <tr class="bg-white text-xs uppercase tracking-wider border-b-2 border-gray-100 text-dark">
                            <th class="p-3 w-8 text-center"></th>
                            <th class="p-3 font-bold min-w-[150px]">Cliente</th>
                            <th class="p-3 font-bold min-w-[200px]">Proyecto</th>
                            <th v-for="(fecha, i) in diasSemana" :key="i" class="p-2 text-center w-14"
                                :class="[esFinDeSemana(fecha) ? 'bg-slate-50 text-gray-400' : '', excedeLimiteDiario(i) ? 'bg-red-50 text-red-600 font-bold' : '']">
                                <div class="flex flex-col items-center"><span>{{ nombresDias[i] }}</span><span
                                        class="text-[10px] opacity-60 font-medium">{{ fecha.getDate() }}</span></div>
                            </th>
                            <th class="p-3 font-bold text-center w-16">Total</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-gray-700 divide-y divide-gray-50">
                        <tr v-if="filas.length === 0 && !cargando">
                            <td colspan="11" class="px-6 py-12 text-center text-gray-400 italic">No hay imputaciones
                                esta semana. Pulsa "Añadir Línea" para comenzar.</td>
                        </tr>

                        <tr v-for="fila in filas" :key="fila.id" class="hover:bg-blue-50/20 transition group">
                            <td class="p-3 text-center"><input type="checkbox" v-model="fila.seleccionado"
                                    class="rounded border-gray-300 text-primary"></td>
                            <td class="p-2">
                                <div class="flex items-center gap-2 border border-transparent rounded px-2 py-1">
                                    <Building2 class="w-3 h-3 text-gray-400" /><span class="text-xs font-medium">{{
                                        fila.cliente }}</span>
                                </div>
                            </td>

                            <td class="p-2 relative group/cell">
                                <div class="flex items-center justify-between pr-2">
                                    <span class="text-xs font-bold text-slate-700 px-2">{{ fila.proyecto }}</span>

                                    <button @click="autocompletarFila(fila)"
                                        class="opacity-0 group-hover/cell:opacity-100 p-1.5 text-blue-600 hover:bg-blue-100 rounded-lg transition-all"
                                        title="Autocompletar semana hasta hoy">
                                        <Wand2 class="w-4 h-4" />
                                    </button>
                                </div>
                            </td>

                            <td v-for="(hora, index) in fila.horas" :key="index" class="p-1 text-center relative"
                                :class="[esFinDeSemana(diasSemana[index]) ? 'bg-slate-50' : '']">

                                <div v-if="tiposDiasSemana[index]"
                                    class="w-full py-1 flex items-center justify-center cursor-not-allowed"
                                    :title="labelsDiasSemana[index]">
                                    <span
                                        class="text-[9px] font-black uppercase tracking-wider rounded px-1.5 py-1 w-full border text-center"
                                        :class="{
                                            'bg-emerald-50 text-emerald-700 border-emerald-200': tiposDiasSemana[index] === 'vacaciones',
                                            'bg-orange-50 text-orange-700 border-orange-200': tiposDiasSemana[index] === 'festivo',
                                            'bg-blue-50 text-blue-700 border-blue-200': tiposDiasSemana[index] === 'asuntos'
                                        }">
                                        {{ tiposDiasSemana[index].substring(0, 3) }}
                                    </span>
                                </div>

                                <input v-else type="number" min="0" max="24" step="0.5" v-model="fila.horas[index]"
                                    @focus="handleFocus" @blur="(e) => handleBlur(e, fila, index)"
                                    :disabled="!esEditable(index)"
                                    class="w-full text-center py-1 rounded transition font-medium text-sm disabled:cursor-not-allowed appearance-none"
                                    :class="{
                                        'text-primary font-bold border border-transparent hover:border-gray-300 bg-transparent': esEditable(index) && fila.horas[index] > 0 && !esPasoInvalido(fila.horas[index]),
                                        'bg-white border border-gray-200 text-primary shadow-sm': esEditable(index) && fila.horas[index] == 0,
                                        'bg-gray-100 text-gray-400 border border-transparent': !esEditable(index),
                                        'border-red-500 bg-red-50 text-red-600 ring-2 ring-red-500 font-black shadow-none': esEditable(index) && (excedeLimiteDiario(index) || esPasoInvalido(fila.horas[index]))
                                    }">
                            </td>

                            <td class="p-3 text-center font-bold text-dark bg-gray-50 text-sm">{{ totalFila(fila) }}
                            </td>
                        </tr>
                    </tbody>
                    <tfoot class="bg-gray-50 border-t border-gray-200 text-xs font-bold text-dark uppercase">
                        <tr>
                            <td colspan="3" class="p-3 text-right">Total Diario:</td>
                            <td v-for="(dia, index) in diasSemana" :key="index" class="p-2 text-center"
                                :class="excedeLimiteDiario(index) ? 'bg-red-100' : ''">
                                <span
                                    :class="excedeLimiteDiario(index) ? 'text-red-600 font-extrabold' : (totalDia(index) > 0 ? 'text-primary' : 'text-gray-400')">{{
                                        totalDia(index) }}</span>
                            </td>
                            <td class="p-3 text-center border-l border-blue-100 text-sm"
                                :class="excedeLimiteSemanal ? 'bg-red-600 text-white' : 'bg-blue-50 text-blue-900'">{{
                                    totalSemanal }} / {{ getMaxHorasSemana() }}</td>
                        </tr>
                    </tfoot>
                </table>
            </div>

            <div class="p-4 bg-gray-50 border-t flex justify-end gap-4 items-center">
                <p v-if="hayErrores" class="text-xs font-bold text-red-600 animate-pulse flex items-center gap-1">
                    <AlertCircle class="w-4 h-4" />
                    {{filas.some(f => f.horas.some((h, i) => esEditable(i) && esPasoInvalido(h))) ? 'Solo se permiten incrementos de 0.5h(ej. 1.5)' : 'Corrige el exceso de horas' }}
                </p>

                <button @click="guardarCambios" :disabled="hayErrores || cargando || isSubmittingGuardar"
                    class="btn-primary px-8 py-2.5 rounded-xl font-bold uppercase tracking-widest text-xs shadow-md transition-all flex items-center justify-center disabled:opacity-50"
                    :class="(hayErrores || isSubmittingGuardar) ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-slate-900 text-white hover:shadow-xl'">

                    <svg v-if="isSubmittingGuardar" class="animate-spin w-4 h-4 mr-2 text-gray-500"
                        xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                        </path>
                    </svg>
                    <Save v-else class="w-4 h-4 mr-2" />

                    {{ isSubmittingGuardar ? 'Guardando...' : 'Guardar Imputaciones' }}
                </button>
            </div>
        </div>

        <div v-if="mostrarModalJornada"
            class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
            <div
                class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in duration-200 flex flex-col max-h-[85vh]">
                <div class="bg-slate-50 border-b px-6 py-4 flex justify-between items-center shrink-0">
                    <h3 class="text-lg font-bold text-slate-800 flex items-center gap-2">
                        <Clock class="w-5 h-5 text-primary" /> Configuración de Jornada
                    </h3>
                    <button @click="mostrarModalJornada = false"
                        class="text-gray-400 hover:text-red-500 transition-colors">
                        <X class="w-5 h-5" />
                    </button>
                </div>

                <div class="p-6 flex-1 overflow-y-auto space-y-6">
                    <div class="flex bg-gray-100 p-1 rounded-xl">
                        <button @click="configJornadaTemp.tipoContrato = '40H'"
                            :class="configJornadaTemp.tipoContrato === '40H' ? 'bg-white shadow text-primary font-bold' : 'text-gray-500 hover:text-gray-700'"
                            class="flex-1 py-2 rounded-lg text-sm transition-all">Jornada Completa</button>
                        <button @click="configJornadaTemp.tipoContrato = 'Personalizada'"
                            :class="configJornadaTemp.tipoContrato === 'Personalizada' ? 'bg-white shadow text-primary font-bold' : 'text-gray-500 hover:text-gray-700'"
                            class="flex-1 py-2 rounded-lg text-sm transition-all">Personalizada</button>
                    </div>

                    <div v-if="configJornadaTemp.tipoContrato === '40H'"
                        class="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-800 space-y-2">
                        <p><strong>Jornada Completa:</strong></p>
                        <ul class="list-disc pl-4 space-y-1 text-blue-700">
                            <li>Lunes a Jueves: <strong>8.5h</strong></li>
                            <li>Viernes: <strong>6.5h</strong></li>
                            <li>Verano (Julio - Agosto): <strong>7.0h</strong> diarias</li>
                        </ul>
                    </div>

                    <div v-else class="space-y-5">
                        <p class="text-xs text-gray-500 leading-relaxed">Configura las horas exactas para cada día según
                            tu contrato personalizado.</p>

                        <div>
                            <label
                                class="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-3 block shrink-0">
                                Jornada Normal (Lunes a Viernes)
                            </label>
                            <div class="grid grid-cols-5 gap-2">
                                <div class="text-center" v-for="(diaLabel, idx) in ['Lun', 'Mar', 'Mié', 'Jue', 'Vie']"
                                    :key="'n' + idx">
                                    <label class="text-xs text-gray-500 mb-1 block">{{ diaLabel }}</label>
                                    <input type="number" step="0.5" min="0" max="24"
                                        v-model.number="configJornadaTemp.horasNormal[idx]"
                                        class="w-full text-center border border-gray-300 rounded-lg p-2 text-sm font-bold outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all">
                                </div>
                            </div>
                        </div>

                        <div>
                            <label
                                class="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-3 block shrink-0">
                                Jornada de Verano (Julio y Agosto)
                            </label>
                            <div class="grid grid-cols-5 gap-2">
                                <div class="text-center" v-for="(diaLabel, idx) in ['Lun', 'Mar', 'Mié', 'Jue', 'Vie']"
                                    :key="'v' + idx">
                                    <label class="text-xs text-gray-500 mb-1 block">{{ diaLabel }}</label>
                                    <input type="number" step="0.5" min="0" max="24"
                                        v-model.number="configJornadaTemp.horasVerano[idx]"
                                        class="w-full text-center border border-gray-300 rounded-lg p-2 text-sm font-bold outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3 shrink-0">
                    <button @click="mostrarModalJornada = false"
                        class="px-4 py-2 text-sm font-bold text-slate-400 uppercase tracking-widest hover:text-slate-600">Cancelar</button>
                    <button @click="guardarConfigJornada"
                        class="bg-primary text-white px-6 py-2 rounded-xl font-bold uppercase tracking-widest text-xs hover:bg-blue-700 shadow-md transition-all">Guardar</button>
                </div>
            </div>
        </div>

        <div v-if="mostrarModal"
            class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
            <div
                class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in duration-200 flex flex-col max-h-[85vh]">
                <div class="bg-slate-50 border-b px-6 py-4 flex justify-between items-center shrink-0">
                    <h3 class="text-lg font-bold text-slate-800">Añadir Proyecto</h3>
                    <button @click="cerrarModal" class="text-gray-400 hover:text-red-500 transition-colors">
                        <X class="w-5 h-5" />
                    </button>
                </div>

                <div class="p-6 flex-1 overflow-hidden flex flex-col">
                    <label class="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-3 block shrink-0">
                        Selecciona tu proyecto asignado
                    </label>

                    <div
                        class="flex-1 overflow-y-auto border border-gray-200 rounded-xl bg-white shadow-inner scrollbar-thin relative">
                        <div v-if="proyectosRealDB.length === 0"
                            class="p-8 text-center flex flex-col items-center justify-center text-gray-400">
                            <Loader2 v-if="cargando" class="w-6 h-6 animate-spin mb-2" />
                            <span v-if="!cargando" class="text-sm">No tienes proyectos asignados.</span>
                        </div>

                        <template v-for="grupo in proyectosAgrupadosParaModal" :key="grupo.cliente">
                            <div
                                class="bg-slate-100/90 px-4 py-2.5 text-[10px] font-bold text-slate-500 uppercase tracking-widest sticky top-0 backdrop-blur-sm border-b border-gray-200 flex items-center gap-2 z-10">
                                <Briefcase class="w-3.5 h-3.5 text-slate-400" /> {{ grupo.cliente }}
                            </div>
                            <div v-for="p in grupo.proyectos" :key="p.Id" @click="nuevoRegistro.proyectoId = p.Id"
                                class="px-4 py-3 cursor-pointer border-b border-gray-50 last:border-b-0 hover:bg-blue-50/50 transition-colors flex items-center justify-between group"
                                :class="nuevoRegistro.proyectoId === p.Id ? 'bg-blue-50' : ''">
                                <div class="flex items-center gap-3">
                                    <div class="w-4 h-4 rounded-full border flex items-center justify-center transition-colors"
                                        :class="nuevoRegistro.proyectoId === p.Id ? 'border-primary bg-primary' : 'border-gray-300 group-hover:border-blue-400'">
                                        <Check v-if="nuevoRegistro.proyectoId === p.Id" class="w-3 h-3 text-white"
                                            stroke-width="3" />
                                    </div>
                                    <span class="text-sm font-medium transition-colors"
                                        :class="nuevoRegistro.proyectoId === p.Id ? 'text-primary font-bold' : 'text-gray-700 group-hover:text-blue-800'">
                                        {{ p.Nombre }}
                                    </span>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>

                <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3 shrink-0">
                    <button @click="cerrarModal" :disabled="isAddingProject"
                        class="px-4 py-2 text-sm font-bold text-slate-400 uppercase tracking-widest hover:text-slate-600 disabled:opacity-50">Cancelar</button>

                    <button @click="confirmarAnadirLinea" :disabled="isAddingProject"
                        class="bg-primary text-white px-6 py-2 rounded-xl font-bold uppercase tracking-widest text-xs shadow-md transition-all flex items-center justify-center disabled:opacity-50"
                        :class="isAddingProject ? 'bg-blue-400 cursor-not-allowed opacity-80' : 'hover:bg-blue-700'">

                        <svg v-if="isAddingProject" class="animate-spin w-4 h-4 mr-2 text-white"
                            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                            </circle>
                            <path class="opacity-75" fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                            </path>
                        </svg>

                        {{ isAddingProject ? 'Añadiendo...' : 'Añadir a la Tabla' }}
                    </button>
                </div>
            </div>
        </div>

        <ToastNotification :show="toast.show" :message="toast.message" :type="toast.type" @close="toast.show = false" />
    </div>
</template>

<style scoped>
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

@keyframes pulse-slow {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: .85;
    }
}

.animate-pulse-slow {
    animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
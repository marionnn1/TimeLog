import { reactive, watch } from 'vue' 
import { initialData } from '../data/initialData'

const STORAGE_KEY = 'timeLog_state'

// carga inicial de estado 
const loadState = () => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) return JSON.parse(saved)
    
    return {
        ...initialData,
        imputaciones: initialData.imputaciones || [],
        ausencias: [
            { date: '2026-02-16', userId: 2, nombre: 'Ana', iniciales: 'AR', type: 'vacaciones' },
            { date: '2026-02-16', userId: 3, nombre: 'Pedro', iniciales: 'PS', type: 'vacaciones' },
            { date: '2026-02-16', userId: 4, nombre: 'Laura', iniciales: 'LP', type: 'vacaciones' },
            { date: '2026-02-28', userId: 2, nombre: 'Ana', iniciales: 'AR', type: 'festivo' },
        ]
    }
}

const state = reactive(loadState())

watch(state, (nuevoEstado) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nuevoEstado))
}, { deep: true })


export const useDataStore = () => {

    // --- HELPER INTERNO PARA LOGS ---
    const _addLog = (accion, detalle, gravedad = 'info', actor = null) => {
        state.logs.unshift({
            id: Date.now(),
            fecha: new Date().toLocaleString(),
            actor: actor || state.currentUser?.nombre || 'Sistema',
            accion,
            detalle,
            gravedad
        })
    }

    // --- GETTERS ---
    const getUsers = () => state.usuarios
    const getProjects = () => state.proyectos
    const getTickets = () => state.tickets || []
    const getLogs = () => state.logs
    const getSedes = () => state.sedes
    const getAnuncio = () => state.anuncio
    const getCurrentUser = () => state.currentUser
    const getAusencias = () => state.ausencias

    // --- ACTIONS: USUARIOS ---
    const addUser = (user) => {
        state.usuarios.push({ ...user, id: Date.now() })
        _addLog('CREATE_USER', `Creó al usuario ${user.nombre}`)
    }

    const updateUser = (user) => {
        const index = state.usuarios.findIndex(u => u.id === user.id)
        if (index !== -1) {
            state.usuarios[index] = { ...user }
            _addLog('UPDATE_USER', `Modificó datos de ${user.nombre}`)
        }
    }

    const deleteUser = (id) => {
        const user = state.usuarios.find(u => u.id === id)
        if (user) {
            state.usuarios = state.usuarios.filter(u => u.id !== id)
            _addLog('DELETE_USER', `Eliminó al usuario ${user.nombre}`, 'danger')
        }
    }

    // --- ACTIONS: PROYECTOS ---
    const addProject = (project) => {
        state.proyectos.push({ ...project, id: Date.now() })
        _addLog('CREATE_PROJECT', `Creó proyecto ${project.nombre}`)
    }

    const deleteProject = (id) => {
        state.proyectos = state.proyectos.filter(p => p.id !== id)
        _addLog('DELETE_PROJECT', `Eliminó un proyecto ID: ${id}`, 'warning')
    }

    const saveProject = (project) => {
        if (project.id) {
            const index = state.proyectos.findIndex(p => p.id === project.id)
            if (index !== -1) {
                state.proyectos[index] = { ...project }
                _addLog('UPDATE_PROJECT', `Actualizó proyecto ${project.nombre}`)
                return
            }
        }
        addProject(project)
    }

    // --- ACTIONS: TICKETS ---
    const resolveTicket = (id) => {
        const ticket = state.tickets.find(t => t.id === id)
        if (ticket) {
            ticket.estado = 'resuelto'
            _addLog('RESOLVE_TICKET', `Ticket #${id} resuelto (${ticket.asunto})`)
        }
    }

    const deleteTicket = (id) => {
        state.tickets = state.tickets.filter(t => t.id !== id)
        _addLog('DELETE_TICKET', `Ticket #${id} eliminado`, 'warning')
    }

    // --- ACTIONS: CONFIGURACIÓN ---
    const updateAnuncio = (nuevoAnuncio) => {
        state.anuncio = { ...nuevoAnuncio }
        _addLog('UPDATE_BANNER', 'Actualizó el banner global', 'warning')
    }

    // --- ACTIONS: IMPUTACIONES ---
    const getImputacionesUsuario = (usuarioId) => {
        return state.imputaciones.filter(i => i.usuarioId === usuarioId)
    }

    const addImputacion = (imputacion) => {
        const index = state.imputaciones.findIndex(i => 
            i.usuarioId === imputacion.usuarioId && 
            i.proyectoId === imputacion.proyectoId && 
            i.fecha === imputacion.fecha
        )

        if (index !== -1) {
            state.imputaciones[index] = { ...state.imputaciones[index], horas: imputacion.horas }
        } else {
            state.imputaciones.push({ ...imputacion, id: Date.now() })
        }
    }

    // --- ACTIONS: AUSENCIAS ---
    const addAusencia = (ausencia) => {
        const existe = state.ausencias.find(a => a.date === ausencia.date && a.userId === ausencia.userId)
        if (!existe) {
            state.ausencias.push(ausencia)
            _addLog('SOLICITUD_AUSENCIA', `Solicitó ${ausencia.type} para el ${ausencia.date}`, 'info', ausencia.nombre)
        }
    }

    const removeAusencia = (date, userId) => {
        state.ausencias = state.ausencias.filter(a => !(a.date === date && a.userId === userId))
    }

    const getAusenciaPorFecha = (dateString, userId) => {
        return state.ausencias.find(a => a.date === dateString && a.userId === userId)
    }

    const getAusenciasEquipoPorFecha = (dateString) => {
        return state.ausencias.filter(a => a.date === dateString)
    }

    // --- ESTADÍSTICAS ---
    const getStats = () => ({
        totalUsuarios: state.usuarios.length,
        usuariosMadrid: state.usuarios.filter(u => u.sede === 'Madrid').length,
        proyectosActivos: state.proyectos.filter(p => p.estado === 'Activo').length,
        ticketsPendientes: state.tickets ? state.tickets.filter(t => t.estado === 'pendiente').length : 0,
        ticketsTotales: state.tickets ? state.tickets.length : 0,
        logsCriticos: state.logs.filter(l => l.gravedad === 'danger').length
    })

    const addLog = (actor, accion, detalle, gravedad) => _addLog(accion, detalle, gravedad, actor)

    return {
        state,
        getUsers, addUser, updateUser, deleteUser,
        getProjects, addProject, deleteProject, saveProject,
        getTickets, resolveTicket, deleteTicket,
        getLogs, addLog,
        getSedes, getAnuncio, updateAnuncio,
        getCurrentUser,
        getStats,
        getImputacionesUsuario, addImputacion,
        getAusencias, addAusencia, removeAusencia, getAusenciaPorFecha, getAusenciasEquipoPorFecha
    }
}
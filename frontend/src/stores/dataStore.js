import { reactive } from 'vue'
import { initialData } from '../data/initialData'

// Creamos un estado reactivo global (Single Source of Truth)
const state = reactive({
    ...initialData,
    // Aseguramos que el array exista aunque initialData no lo traiga
    imputaciones: initialData.imputaciones || [],
    
    // --- NUEVO: AUSENCIAS GLOBALES (Vacaciones, Festivos, Asuntos) ---
    ausencias: [
        // Datos Mock Iniciales para pruebas inmediatas
        { date: '2026-02-16', userId: 2, nombre: 'Ana', iniciales: 'AR', type: 'vacaciones' },
        { date: '2026-02-16', userId: 3, nombre: 'Pedro', iniciales: 'PS', type: 'vacaciones' },
        { date: '2026-02-16', userId: 4, nombre: 'Laura', iniciales: 'LP', type: 'vacaciones' },
        { date: '2026-02-28', userId: 2, nombre: 'Ana', iniciales: 'AR', type: 'festivo' },
        // Puedes descomentar la siguiente línea para ver vacaciones asignadas a TU usuario (Mario)
        // { date: '2026-02-12', userId: 1, nombre: 'Mario', iniciales: 'ML', type: 'vacaciones' }
    ]
})

// Exportamos métodos para interactuar con los datos (como si fuera una API)
export const useDataStore = () => {

    // --- USUARIOS ---
    const getUsers = () => state.usuarios

    const addUser = (user) => {
        const newUser = { ...user, id: Date.now() }
        state.usuarios.push(newUser)
        addLog('Admin', 'CREATE_USER', `Creó al usuario ${user.nombre}`, 'info')
    }

    const updateUser = (user) => {
        const index = state.usuarios.findIndex(u => u.id === user.id)
        if (index !== -1) {
            state.usuarios[index] = user
            addLog('Admin', 'UPDATE_USER', `Modificó datos de ${user.nombre}`, 'info')
        }
    }

    const deleteUser = (id) => {
        const user = state.usuarios.find(u => u.id === id)
        if (user) {
            state.usuarios = state.usuarios.filter(u => u.id !== id)
            addLog('Admin', 'DELETE_USER', `Eliminó al usuario ${user.nombre}`, 'danger')
        }
    }

    // --- PROYECTOS ---
    const getProjects = () => state.proyectos

    const addProject = (project) => {
        state.proyectos.push({ ...project, id: Date.now() })
        addLog('Admin', 'CREATE_PROJECT', `Creó proyecto ${project.nombre}`, 'info')
    }

    const deleteProject = (id) => {
        state.proyectos = state.proyectos.filter(p => p.id !== id)
        addLog('Admin', 'DELETE_PROJECT', `Eliminó un proyecto ID: ${id}`, 'warning')
    }

    // --- TICKETS (INCIDENCIAS) ---
    const getTickets = () => state.tickets || []

    const resolveTicket = (id) => {
        const ticket = state.tickets.find(t => t.id === id)
        if (ticket) {
            ticket.estado = 'resuelto'
            addLog('Admin', 'RESOLVE_TICKET', `Ticket #${id} resuelto (${ticket.asunto})`, 'info')
        }
    }

    const deleteTicket = (id) => {
        state.tickets = state.tickets.filter(t => t.id !== id)
        addLog('Admin', 'DELETE_TICKET', `Ticket #${id} eliminado`, 'warning')
    }

    // --- LOGS ---
    const getLogs = () => state.logs

    const addLog = (actor, accion, detalle, gravedad) => {
        const nuevoLog = {
            id: Date.now(),
            fecha: new Date().toLocaleString(),
            actor: actor || state.currentUser.nombre,
            accion,
            detalle,
            gravedad
        }
        state.logs.unshift(nuevoLog)
    }

    // --- CONFIG / MAESTROS ---
    const getSedes = () => state.sedes
    const getAnuncio = () => state.anuncio
    const updateAnuncio = (nuevoAnuncio) => {
        state.anuncio = nuevoAnuncio
        addLog('Admin', 'UPDATE_BANNER', 'Actualizó el banner global', 'warning')
    }

    // --- USUARIO ACTUAL ---
    const getCurrentUser = () => state.currentUser

    // --- ESTADÍSTICAS (DASHBOARD ADMIN) ---
    const getStats = () => {
        return {
            totalUsuarios: state.usuarios.length,
            usuariosMadrid: state.usuarios.filter(u => u.sede === 'Madrid').length,
            proyectosActivos: state.proyectos.filter(p => p.estado === 'Activo').length,
            ticketsPendientes: state.tickets ? state.tickets.filter(t => t.estado === 'pendiente').length : 0,
            ticketsTotales: state.tickets ? state.tickets.length : 0,
            logsCriticos: state.logs.filter(l => l.gravedad === 'danger').length
        }
    }

    // --- IMPUTACIONES (DASHBOARD SEMANAL) ---
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

    // --- NUEVO: GESTIÓN DE AUSENCIAS (CALENDARIO GLOBAL) ---
    
    // Obtener todas las ausencias (para pintar el calendario completo)
    const getAusencias = () => state.ausencias

    // Añadir ausencia (Evitando duplicados)
    const addAusencia = (ausencia) => {
        const existe = state.ausencias.find(a => a.date === ausencia.date && a.userId === ausencia.userId)
        if (!existe) {
            state.ausencias.push(ausencia)
            // Log automático para auditoría
            addLog(ausencia.nombre, 'SOLICITUD_AUSENCIA', `Solicitó ${ausencia.type} para el ${ausencia.date}`, 'info')
        }
    }

    // Borrar ausencia
    const removeAusencia = (date, userId) => {
        state.ausencias = state.ausencias.filter(a => !(a.date === date && a.userId === userId))
    }

    // Obtener si UN usuario tiene vacaciones UN día (Usado por Dashboard para bloquear input)
    const getAusenciaPorFecha = (dateString, userId) => {
        return state.ausencias.find(a => a.date === dateString && a.userId === userId)
    }

    // Obtener quiénes faltan un día (Usado por Calendario para ver concurrencia)
    const getAusenciasEquipoPorFecha = (dateString) => {
        return state.ausencias.filter(a => a.date === dateString)
    }

    return {
        state,
        // Usuarios
        getUsers, addUser, updateUser, deleteUser,
        // Proyectos
        getProjects, addProject, deleteProject,
        // Tickets
        getTickets, resolveTicket, deleteTicket,
        // Logs
        getLogs, addLog,
        // Config
        getSedes, getAnuncio, updateAnuncio,
        // Usuario
        getCurrentUser,
        // Stats
        getStats,
        // Imputaciones
        getImputacionesUsuario, addImputacion,
        // Ausencias / Calendario [NUEVO]
        getAusencias, addAusencia, removeAusencia, getAusenciaPorFecha, getAusenciasEquipoPorFecha
    }
}
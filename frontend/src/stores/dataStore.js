import { reactive } from 'vue'
import { initialData } from '../data/initialData'

// Creamos un estado reactivo global (Single Source of Truth)
const state = reactive({
    ...initialData
})

// Exportamos métodos para interactuar con los datos (como si fuera una API)
export const useDataStore = () => {

    // --- USUARIOS ---
    const getUsers = () => state.usuarios

    const addUser = (user) => {
        // Simulamos generar ID
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

    // --- TICKETS (INCIDENCIAS) --- [NUEVO]
    const getTickets = () => state.tickets || [] // Array vacío por seguridad si no hay tickets

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
        // Añadimos al principio del array
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

    // --- ESTADÍSTICAS (DASHBOARD) --- [NUEVO]
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

    return {
        state, // Acceso directo (opcional)
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
        getStats
    }
}
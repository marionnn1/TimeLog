import { reactive, watch } from 'vue'
import { initialData } from '../data/initialData'

const STORAGE_KEY = 'timeLog_state'

// --- CARGA INICIAL (Persistencia + Datos por defecto) ---
const loadState = () => {
    // 1. Intentamos recuperar del navegador
    const saved = localStorage.getItem(STORAGE_KEY)
    
    // 2. Si existe, lo parseamos y lo usamos
    if (saved) {
        try {
            const parsedState = JSON.parse(saved)
            
            // Fusión de seguridad: asegura que si añadimos campos nuevos al código (como 'maestros'),
            // no se rompa la app al cargar un localStorage antiguo.
            return {
                ...initialData, // Estructura base
                ...parsedState, // Datos guardados
                // Aseguramos que existan estos arrays aunque el localStorage sea viejo
                imputaciones: parsedState.imputaciones || [],
                ausencias: parsedState.ausencias || [
                    { date: '2026-02-16', userId: 2, nombre: 'Ana', iniciales: 'AR', type: 'vacaciones' },
                    { date: '2026-02-16', userId: 3, nombre: 'Pedro', iniciales: 'PS', type: 'vacaciones' },
                    { date: '2026-02-16', userId: 4, nombre: 'Laura', iniciales: 'LP', type: 'vacaciones' },
                    { date: '2026-02-28', userId: 2, nombre: 'Ana', iniciales: 'AR', type: 'festivo' },
                ],
                maestros: parsedState.maestros || {
                    clientes: ['Banco Santander', 'Mapfre', 'Inditex', 'BBVA', 'Naturgy'],
                    proyectos: ['Auditoría Backend', 'Migración Cloud', 'Desarrollo Frontend', 'Mantenimiento Legacy', 'Consultoría de Seguridad']
                }
            }
        } catch (e) {
            console.error('Error cargando estado, reseteando...', e)
        }
    }
    
    // 3. Si no hay nada guardado, usamos los datos iniciales por defecto
    return {
        ...initialData,
        imputaciones: [],
        ausencias: [
            { date: '2026-02-16', userId: 2, nombre: 'Ana', iniciales: 'AR', type: 'vacaciones' },
            { date: '2026-02-28', userId: 2, nombre: 'Ana', iniciales: 'AR', type: 'festivo' },
        ],
        maestros: {
            clientes: ['Banco Santander', 'Mapfre', 'Inditex', 'BBVA', 'Naturgy'],
            proyectos: ['Auditoría Backend', 'Migración Cloud', 'Desarrollo Frontend', 'Mantenimiento Legacy', 'Consultoría de Seguridad']
        }
    }
}

// Creamos el estado reactivo global
const state = reactive(loadState())

// --- VIGILANTE (WATCHER) ---
// Cada vez que 'state' cambie, lo guardamos en el navegador automáticamente
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
    
    // Getters de Maestros (NUEVO)
    const getClientes = () => state.maestros.clientes
    const getTiposProyecto = () => state.maestros.proyectos

    // --- ACTIONS: USUARIOS ---
    const addUser = (user) => {
        state.usuarios.push({ ...user, id: Date.now() })
        _addLog('CREATE_USER', `Creó al usuario ${user.nombre}`)
    }

    // --- ACCIÓN PARA LOGIN EXTERNO (MSAL) ---
    // Esta es la función clave que usará useAuth.js
    const setCurrentUser = (userData) => {
        state.currentUser = userData
        
        // Comprobamos si este usuario ya existe en nuestra "Base de Datos" local
        const existe = state.usuarios.find(u => u.email === userData.email)
        
        if (!existe) {
            // Si es la primera vez que entra, lo registramos automáticamente
            const nuevoUsuario = {
                ...userData,
                id: Date.now(),
                rol: 'user', // Rol por defecto
                sede: 'Madrid', // Sede por defecto
                activo: true
            }
            state.usuarios.push(nuevoUsuario)
            _addLog('AUTO_REGISTER', `Usuario registrado vía Microsoft: ${userData.nombre}`, 'success', 'Sistema')
        } else {
            // Si ya existe, actualizamos su info básica por si cambió en Azure
            existe.nombre = userData.nombre
            existe.oid_azure = userData.oid_azure
        }
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
        getClientes, getTiposProyecto,
        getUsers, addUser, updateUser, deleteUser, setCurrentUser, getCurrentUser,
        getProjects, addProject, deleteProject, saveProject,
        getTickets, resolveTicket, deleteTicket,
        getLogs, addLog,
        getSedes, getAnuncio, updateAnuncio,
        getStats,
        getImputacionesUsuario, addImputacion,
        getAusencias, addAusencia, removeAusencia, getAusenciaPorFecha, getAusenciasEquipoPorFecha
    }
}
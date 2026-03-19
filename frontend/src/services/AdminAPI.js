import api from './API'

export default {
    async getTickets() {
        const res = await api.get('/admin/tickets/')
        return res.data
    },
    async approveTicket(id, horas) {
        const res = await api.put(`/admin/tickets/${id}/approve`, { horas })
        return res.data
    },
    async rejectTicket(id, motivo) {
        const res = await api.put(`/admin/tickets/${id}/reject`, { motivo })
        return res.data
    },

    async getProyectos() {
        const res = await api.get('/proyectos')
        return res.data
    },
    async crearProyecto(payload) {
        const res = await api.post('/proyectos', payload)
        return res.data
    },
    async editarProyecto(id, payload) {
        const res = await api.put(`/proyectos/${id}`, payload)
        return res.data
    },
    async eliminarProyecto(id) {
        const res = await api.delete(`/proyectos/${id}/force`)
        return res.data
    },
    async toggleProyecto(id) {
        const res = await api.put(`/proyectos/${id}/toggle`)
        return res.data
    },

    async getUsuarios() {
        const res = await api.get('/usuarios')
        return res.data
    },
    async crearUsuario(payload) {
        const res = await api.post('/usuarios', payload)
        return res.data
    },
    async editarUsuario(id, payload) {
        const res = await api.put(`/usuarios/${id}`, payload)
        return res.data
    },
    async eliminarUsuario(id) {
        const res = await api.delete(`/usuarios/${id}`)
        return res.data
    },
    async toggleUsuario(id) {
        const res = await api.put(`/usuarios/${id}/toggle`)
        return res.data
    },

    async getAuditoria() {
        const res = await api.get('/auditoria')
        return res.data
    },
    async getDashboardStats() {
        const res = await api.get('/dashboard/stats')
        return res.data
    }
}
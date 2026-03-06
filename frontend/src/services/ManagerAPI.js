import API from './API'

export default {
    getAnalytics(mes) {
        return API().get(`/manager/analytics`, { params: { mes } })
    },

    getClosingData(mes) {
        return API().get(`/manager/closing`, { params: { mes } })
    },
    toggleCierreMes(mes, accion) {
        return API().post(`/manager/closing`, { mes, accion })
    },
    getValidations() {
        return API().get('/manager/validation')
    },
    approveValidation(id, horas) {
        return API().put(`/manager/validation/${id}/approve`, { horas })
    },
    rejectValidation(id, motivo) {
        return API().put(`/manager/validation/${id}/reject`, { motivo })
    },
    getProjectsData() {
        return API().get('/manager/projects/')
    },
    createProject(data) {
        return API().post('/manager/projects/', data)
    },
    updateProject(id, data) {
        return API().put(`/manager/projects/${id}`, data)
    },
    deleteProject(id) {
        return API().delete(`/manager/projects/${id}`)
    },
    assignUserToProject(proyectoId, usuarioId) {
        return API().post(`/manager/projects/${proyectoId}/assign`, { usuarioId })
    }
}
import api from './API';

const BASE_PATH = '/manager';

export default {
    // ANALYTICS
    async getAnalytics(mes) {
        const res = await api.get(`${BASE_PATH}/analytics?mes=${mes}`);
        return { data: res.data.data }; 
    },

    // CLOSING
    async getClosingData(mes) {
        const res = await api.get(`${BASE_PATH}/closing?mes=${mes}`);
        return { data: res.data.data };
    },
    async toggleCierreMes(mes, accion, managerId) {
        const res = await api.post(`${BASE_PATH}/closing`, { mes, accion, manager_id: managerId });
        return { data: res.data };
    },

    // CLIENTES
    async createClient(data) {
        const res = await api.post(`${BASE_PATH}/projects/clients`, data);
        return { data: res.data };
    },
    async editarCliente(id, data) {
        const res = await api.put(`${BASE_PATH}/projects/clients/${id}`, data);
        return { data: res.data };
    },
    async eliminarCliente(id) {
        const res = await api.delete(`${BASE_PATH}/projects/clients/${id}`);
        return { data: res.data };
    },

    // PROYECTOS
    async getProjectsData() {
        const res = await api.get(`${BASE_PATH}/projects`);
        return { data: res.data.data };
    },
    async createProject(data) {
        const res = await api.post(`${BASE_PATH}/projects`, data);
        return { data: res.data };
    },
    async updateProject(id, data) {
        const res = await api.put(`${BASE_PATH}/projects/${id}`, data);
        return { data: res.data };
    },
    async deleteProject(id) {
        const res = await api.delete(`${BASE_PATH}/projects/${id}`);
        return { data: res.data };
    },
    async assignUserToProject(proyectoId, usuarioId) {
        const res = await api.post(`${BASE_PATH}/projects/${proyectoId}/assign`, { usuarioId });
        return { data: res.data };
    },
    async unassignUserFromProject(proyectoId, usuarioId) {
        const res = await api.post(`${BASE_PATH}/projects/${proyectoId}/unassign`, { usuarioId });
        return { data: res.data };
    },

    // VALIDATIONS (TICKETS)
    async getValidations() {
        const res = await api.get(`${BASE_PATH}/validation`);
        return { data: res.data.data };
    },
    async approveValidation(id, horas, managerId) {
        const res = await api.put(`${BASE_PATH}/validation/${id}/approve`, { horas, manager_id: managerId });
        return { data: res.data };
    },
    async rejectValidation(id, motivo, managerId) {
        const res = await api.put(`${BASE_PATH}/validation/${id}/reject`, { motivo, manager_id: managerId });
        return { data: res.data };
    }
};
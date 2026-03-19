import api from './API';

const BASE_PATH = '/manager';

export default {
    // ANALYTICS
    async getAnalytics(mes) {
        const res = await api.get(`${BASE_PATH}/analytics?mes=${mes}`);
        return { data: res.data };
    },

    // CLOSING
    async getClosingData(mes) {
        const res = await api.get(`${BASE_PATH}/closing?mes=${mes}`);
        return { data: res.data };
    },
    async toggleCierreMes(mes, accion) {
        const res = await api.post(`${BASE_PATH}/closing`, { mes, accion });
        return { data: res.data };
    },

    // PROJECTS
    async getProjectsData() {
        const res = await api.get(`${BASE_PATH}/projects`);
        return { data: res.data };
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

    // VALIDATIONS (TICKETS)
    async getValidations() {
        const res = await api.get(`${BASE_PATH}/validation`);
        return { data: res.data };
    },
    async approveValidation(id, horas) {
        const res = await api.put(`${BASE_PATH}/validation/${id}/approve`, { horas });
        return { data: res.data };
    },
    async rejectValidation(id, motivo) {
        const res = await api.put(`${BASE_PATH}/validation/${id}/reject`, { motivo });
        return { data: res.data };
    }
};
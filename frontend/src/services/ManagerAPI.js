const API_URL = 'http://localhost:5000/api/manager';

export default {
    // ANALYTICS
    async getAnalytics(mes) {
        const res = await fetch(`${API_URL}/analytics?mes=${mes}`);
        if (!res.ok) throw new Error('Error fetching analytics');
        return { data: await res.json() };
    },

    // CLOSING
    async getClosingData(mes) {
        const res = await fetch(`${API_URL}/closing?mes=${mes}`);
        if (!res.ok) throw new Error('Error fetching closing data');
        return { data: await res.json() };
    },
    async toggleCierreMes(mes, accion) {
        const res = await fetch(`${API_URL}/closing`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mes, accion })
        });
        if (!res.ok) throw new Error('Error toggling closing month');
        return { data: await res.json() };
    },

    // PROJECTS
    async getProjectsData() {
        const res = await fetch(`${API_URL}/projects`);
        if (!res.ok) throw new Error('Error fetching projects');
        return { data: await res.json() };
    },
    async createProject(data) {
        const res = await fetch(`${API_URL}/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Error creating project');
        return { data: await res.json() };
    },
    async updateProject(id, data) {
        const res = await fetch(`${API_URL}/projects/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Error updating project');
        return { data: await res.json() };
    },
    async deleteProject(id) {
        const res = await fetch(`${API_URL}/projects/${id}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error('Error deleting project');
        return { data: await res.json() };
    },
    async assignUserToProject(proyectoId, usuarioId) {
        const res = await fetch(`${API_URL}/projects/${proyectoId}/assign`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuarioId })
        });
        if (!res.ok) {
            const err = await res.json();
            throw { response: { data: err } }; 
        }
        return { data: await res.json() };
    },

    // VALIDATIONS (TICKETS)
    async getValidations() {
        const res = await fetch(`${API_URL}/validation`);
        if (!res.ok) throw new Error('Error fetching validations');
        return { data: await res.json() };
    },
    async approveValidation(id, horas) {
        const res = await fetch(`${API_URL}/validation/${id}/approve`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ horas })
        });
        if (!res.ok) throw new Error('Error approving validation');
        return { data: await res.json() };
    },
    async rejectValidation(id, motivo) {
        const res = await fetch(`${API_URL}/validation/${id}/reject`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ motivo })
        });
        if (!res.ok) throw new Error('Error rejecting validation');
        return { data: await res.json() };
    }
};
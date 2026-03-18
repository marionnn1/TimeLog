const API_URL = 'http://localhost:5000/api/manager';

export default {
    // ANALYTICS
    async getAnalytics(month) {
        const res = await fetch(`${API_URL}/analytics?month=${month}`);
        if (!res.ok) throw new Error('Error fetching analytics');
        return { data: await res.json() };
    },

    // CLOSING
    async getClosingData(month) {
        const res = await fetch(`${API_URL}/closing?month=${month}`);
        if (!res.ok) throw new Error('Error fetching closing data');
        return { data: await res.json() };
    },
    async toggleClosingMonth(month, action) {
        const res = await fetch(`${API_URL}/closing`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ month, action })
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
    async assignUserToProject(projectId, userId) {
        const res = await fetch(`${API_URL}/projects/${projectId}/assign`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId })
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
    async approveValidation(id, hours) {
        const res = await fetch(`${API_URL}/validation/${id}/approve`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hours })
        });
        if (!res.ok) throw new Error('Error approving validation');
        return { data: await res.json() };
    },
    async rejectValidation(id, reason) {
        const res = await fetch(`${API_URL}/validation/${id}/reject`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason })
        });
        if (!res.ok) throw new Error('Error rejecting validation');
        return { data: await res.json() };
    }
};
const API_URL = 'http://localhost:5000/api/admin/tickets';

export default {
    async getTickets() {
        const res = await fetch(`${API_URL}/`);
        return await res.json();
    },
    async approveTicket(id, horas) {
        const res = await fetch(`${API_URL}/${id}/approve`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ horas })
        });
        return await res.json();
    },
    async rejectTicket(id, motivo) {
        const res = await fetch(`${API_URL}/${id}/reject`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ motivo })
        });
        return await res.json();
    }
};
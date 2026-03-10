const API_URL = 'http://localhost:5000/api/admin/tickets';

export default {
    async getTickets() {
        const res = await fetch(`${API_URL}/`);
        if (!res.ok) throw new Error('Error al obtener los tickets');
        return await res.json();
    },
    
    async approveTicket(id, horas) {
        const res = await fetch(`${API_URL}/${id}/approve`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ horas })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Error al aprobar la solicitud');
        return data;
    },
    
    async rejectTicket(id, motivo) {
        const res = await fetch(`${API_URL}/${id}/reject`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ motivo })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Error al rechazar la solicitud');
        return data;
    }
};
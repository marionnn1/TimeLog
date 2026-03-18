const API_URL = 'http://localhost:5000/api/admin/tickets';

export default {
    async getTickets() {
        const res = await fetch(`${API_URL}/`);
        if (!res.ok) throw new Error('Error fetching tickets');
        return await res.json();
    },
    
    async approveTicket(id, hours) {
        const res = await fetch(`${API_URL}/${id}/approve`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hours }) 
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Error approving request');
        return data;
    },
    
    async rejectTicket(id, reason) {
        const res = await fetch(`${API_URL}/${id}/reject`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Error rejecting request');
        return data;
    }
};
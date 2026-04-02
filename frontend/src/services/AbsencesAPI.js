import api from './API'

export default {
    async getAusenciasMes(mes, anio) {
        const res = await api.get(`/absences?mes=${mes}&anio=${anio}`)
        return res.data
    },

    async crearAusencia(payload) {
        const res = await api.post('/absences', payload)
        return res.data
    },

    async eliminarAusencia(userId, start, end) {
        const res = await api.delete(`/absences`, { data: { usuario_id: userId, fecha_inicio: start, fecha_fin: end } });
        return res.data;
    },

    async getResumenAnual(anio) {
        const res = await api.get(`/absences/annual-summary?anio=${anio}`)
        return res.data
    },

    async obtenerConteoRango(userId, inicio, fin) {
        const res = await api.post('/absences/count', { 
            usuario_id: userId, 
            fecha_inicio: inicio, 
            fecha_fin: fin 
        })
        return res.data
    },
}
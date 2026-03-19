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

    async eliminarAusencia(usuario_id, fecha) {
        const res = await api.delete('/absences', {
            data: { usuario_id, fecha } 
        })
        return res.data
    }
}
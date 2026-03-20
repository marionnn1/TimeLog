import api from './API'

export default {
    async getProyectosActivos() {
        const res = await api.get('/proyectos')
        return res.data
    },
    async getSemana(usuario_id, fecha_lunes) {
        const res = await api.get(`/myprojects/semana?usuario_id=${usuario_id}&fecha_lunes=${fecha_lunes}`)
        return res.data
    },
    
    async getCalendarioMensual(usuario_id, mes, anio) {
        const res = await api.get(`/myprojects/calendario?usuario_id=${usuario_id}&mes=${mes}&anio=${anio}`)
        return res.data
    },

    async guardarImputaciones(payload) {
        const res = await api.post('/myprojects/guardar', payload)
        return res.data
    },

    async solicitarCorreccion(payload) {
        const res = await api.post('/myprojects/solicitar-correccion', payload)
        return res.data
    },

    async getAnaliticaMensual(usuario_id, mes, anio) {
        const res = await api.get(`/myprojects/analitica-mensual?usuario_id=${usuario_id}&mes=${mes}&anio=${anio}`)
        return res.data
    },

    async getJornada(usuario_id) {
        const res = await api.get(`/myprojects/jornada?usuario_id=${usuario_id}`)
        return res.data
    },
    async updateJornada(payload) {
        const res = await api.put('/myprojects/jornada', payload)
        return res.data
    }
}
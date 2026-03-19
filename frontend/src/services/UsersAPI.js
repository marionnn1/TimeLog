import api from './API'

export default {
    async getUsuarios() {
        const res = await api.get('/usuarios')
        return res.data
    },
    async addUser(msalAccount) {
        const payload = {
            oid_azure: msalAccount.localAccountId, 
            email: msalAccount.username,
            nombre: msalAccount.name
        }
        const response = await api.post('/users', payload)
        return response.data
    }
}
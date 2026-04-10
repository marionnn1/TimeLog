import api from './API'

export default {
    async getUsuarios() {
        const res = await api.get('/usuarios')
        return res.data
    },
    async syncUser(msalAccount, accessToken = null) {
        const payload = {
            oid_azure: msalAccount.localAccountId, 
            email: msalAccount.username,
            nombre: msalAccount.name,
            access_token: accessToken
        }
        const response = await api.post('/usuarios/sync', payload)
        return response.data
    }
}
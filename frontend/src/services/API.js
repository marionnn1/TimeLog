import axios from 'axios'
import { msalInstance, graphScopes } from '../auth/AuthConfig'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

api.interceptors.request.use(
    async (config) => {
        const accounts = msalInstance.getAllAccounts()
        if (accounts.length > 0) {
            try {
                const response = await msalInstance.acquireTokenSilent({
                    ...graphScopes,
                    account: accounts[0]
                })
                // CAMBIO CLAVE AQUÍ: Usamos idToken en lugar de accessToken
                config.headers.Authorization = `Bearer ${response.idToken}`
            } catch (error) {
                console.warn('El token silencioso ha fallado.', error)
            }
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

export default api
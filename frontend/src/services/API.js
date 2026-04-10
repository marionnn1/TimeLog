import axios from 'axios'
import { msalInstance, graphScopes } from '../auth/AuthConfig'

const api = axios.create({
    // Eliminamos cualquier barra final para evitar errores de preflight
    baseURL: (import.meta.env.VITE_API_URL || '/api'),
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

api.interceptors.request.use(async (config) => {
    try {
        const activeAccount = msalInstance.getAllAccounts()[0]
        if (activeAccount) {
            const response = await msalInstance.acquireTokenSilent({
                ...graphScopes,
                account: activeAccount
            })
            config.headers.Authorization = `Bearer ${response.idToken}`
        }
    } catch (error) {
        console.warn("Token no disponible o expirado, reintentando...")
    }
    return config
})

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            console.warn("Token inválido")
            console.error(error)
            // localStorage.clear()
        }
        return Promise.reject(error)
    }
)

export default api
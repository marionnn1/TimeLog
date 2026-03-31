import axios from 'axios'
import { msalInstance, graphScopes } from '../auth/AuthConfig'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

api.interceptors.request.use(async (config) => {
    try {
        await msalInstance.initialize()

        const activeAccount = msalInstance.getAllAccounts()[0]

        if (activeAccount) {
            const response = await msalInstance.acquireTokenSilent({
                ...graphScopes,
                account: activeAccount
            })
            config.headers.Authorization = `Bearer ${response.idToken}`
        }
    } catch (error) {
        console.warn("Aviso MSAL interceptor (Token no disponible):", error)
    }

    // MANTENEMOS ESTO TEMPORALMENTE para que el backend no se rompa
    const state = localStorage.getItem('timeLog_state')
    if (state) {
        try {
            const parsed = JSON.parse(state)
            if (parsed.currentUser) {
                config.headers['X-User-Id'] = parsed.currentUser.id
                config.headers['X-User-Name'] = encodeURIComponent(parsed.currentUser.nombre)
            }
        } catch (e) { }
    }
    return config
}, (error) => {
    return Promise.reject(error)
})

export default api
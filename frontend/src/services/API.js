import axios from 'axios'
import { msalInstance, graphScopes } from '../auth/AuthConfig'
import { InteractionRequiredAuthError } from '@azure/msal-browser'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',

    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

api.interceptors.request.use(async (config) => {
    const activeAccount = msalInstance.getAllAccounts()[0]

    if (activeAccount) {
        try {

            const response = await msalInstance.acquireTokenSilent({
                ...graphScopes,
                account: activeAccount
            })
            config.headers.Authorization = `Bearer ${response.idToken}`

        } catch (error) {
            if (error instanceof InteractionRequiredAuthError) {
                console.warn("El token ha expirado y requiere interacción. Redirigiendo...")
                try {
                    await msalInstance.acquireTokenRedirect({
                        ...graphScopes,
                        account: activeAccount
                    })
                } catch (redirectError) {
                    console.error("Error al redirigir para renovar token:", redirectError)
                }
            } else {
                console.error("Error desconocido al renovar token:", error)
            }
        }
    }

    return config
})

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            console.warn("Token rechazado por el backend. Cerrando sesión local.")
            localStorage.clear()
            sessionStorage.clear()
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default api
import axios from 'axios'

// Crea una instancia de Axios con la configuración base
const api = axios.create({
    // Lee la URL del .env o usa localhost por defecto
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

// (Opcional) Interceptor para añadir el token de Azure en cada petición automáticamente
/*
api.interceptors.request.use(async (config) => {
    // Aquí podrías inyectar el token si lo guardaras en localStorage
    // const token = localStorage.getItem('msal_token')
    // if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})
*/

// Exportamos una función que devuelve la instancia
export default () => api
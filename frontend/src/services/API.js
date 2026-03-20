import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:5000/api', 
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

api.interceptors.request.use((config) => {
    const state = localStorage.getItem('timeLog_state')
    if (state) {
        try {
            const parsed = JSON.parse(state)
            if (parsed.currentUser) {
                config.headers['X-User-Id'] = parsed.currentUser.id
                config.headers['X-User-Name'] = encodeURIComponent(parsed.currentUser.nombre)
            }
        } catch (e) {}
    }
    return config
})

export default api
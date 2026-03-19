import axios from 'axios'

const api = axios.create({
    // En el futuro puedes cambiar esto a import.meta.env.VITE_API_URL
    baseURL: 'http://localhost:5000/api', 
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

export default api
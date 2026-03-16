import { reactive, watch } from 'vue'

const STORAGE_KEY = 'timeLog_session'

const loadState = () => {
    const saved = localStorage.getItem(STORAGE_KEY)
    
    if (saved) {
        try {
            const parsedState = JSON.parse(saved)
            return {
                currentUser: parsedState.currentUser || null,
                anuncio: parsedState.anuncio || { visible: false, texto: '', tipo: 'info' },
                sedes: ['Madrid', 'Barcelona', 'Bilbao', 'Valencia', 'Sevilla'],
            }
        } catch (e) {
            console.error('Error cargando estado, reseteando...', e)
        }
    }
    
    return {
        currentUser: null,
        anuncio: { visible: false, texto: '', tipo: 'info' },
        sedes: ['Madrid', 'Barcelona', 'Bilbao', 'Valencia', 'Sevilla'],
    }
}

const state = reactive(loadState())

watch(state, (newState) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newState))
}, { deep: true })

export const useDataStore = () => {

    const getCurrentUser = () => state.currentUser

    const setCurrentUser = (userData) => {
        state.currentUser = userData
        localStorage.setItem('isAuthenticated', 'true')
    }

    const clearSession = () => {
        state.currentUser = null
        localStorage.removeItem('isAuthenticated')
    }

    const getSedes = () => state.sedes
    const getAnuncio = () => state.anuncio
    
    const updateAnuncio = (nuevoAnuncio) => {
        state.anuncio = { ...nuevoAnuncio }
    }

    return {
        state,
        getCurrentUser, 
        setCurrentUser,
        clearSession,
        getSedes, 
        getAnuncio, 
        updateAnuncio
    }
}
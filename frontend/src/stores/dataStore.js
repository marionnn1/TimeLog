import { reactive, watch } from 'vue'

const STORAGE_KEY = 'timeLog_state'

const loadState = () => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
        try {
            const parsedState = JSON.parse(saved)
            return {
                currentUser: parsedState.currentUser || null
            }
        } catch (e) {
            console.error('Error cargando estado, reseteando...', e)
        }
    }
    return {
        currentUser: null
    }
}

const state = reactive(loadState())

watch(state, (nuevoEstado) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nuevoEstado))
}, { deep: true })

export const useDataStore = () => {

    // --- GETTERS ---
    const getCurrentUser = () => state.currentUser

    // --- ACTIONS ---
    const setCurrentUser = (userData) => {
        state.currentUser = userData
    }

    const $reset = () => {
        state.currentUser = null
    }

    return {
        state,
        getCurrentUser,
        setCurrentUser,
        $reset
    }
}
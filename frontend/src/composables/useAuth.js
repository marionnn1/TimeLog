import { ref } from 'vue'
import { msalInstance, state, graphScopes } from '../auth/AuthConfig'
import { useDataStore } from '../stores/dataStore'
import { useRouter } from 'vue-router'
import UsersAPI from '../services/UsersAPI'

export function useAuth() {
  const store = useDataStore()
  const router = useRouter()
  const isLoggingIn = ref(false)
  
  const login = async () => {
    try {
      await msalInstance.initialize()
      await msalInstance.loginRedirect({
        ...graphScopes,
        prompt: 'select_account'
      })
    } catch (error) {
      console.error('Error iniciando sesión:', error)
    }
  }

  const logout = async () => {
    try {
      await msalInstance.initialize()
      localStorage.removeItem('timeLog_state') 
      localStorage.removeItem('isAuthenticated') 
      store.$reset && store.$reset() 
      
      await msalInstance.logoutRedirect({
        postLogoutRedirectUri: import.meta.env.VITE_MSAL_POST_LOGOUT_REDIRECT_URI
      })
    } catch (error) {
      console.error('Error cerrando sesión:', error)
    }
  }

  const handleRedirect = async () => {
    try {
      await msalInstance.initialize()
      const response = await msalInstance.handleRedirectPromise()
      
      if (response) {
        await processLogin(response.account)
        return true 
      } else {
        const currentAccounts = msalInstance.getAllAccounts()
        if (currentAccounts.length > 0) {
            await processLogin(currentAccounts[0], false) 
            return true
        }
      }
    } catch (error) {
      console.error('Error manejando el redirect:', error)
    }
    return false
  }

  const processLogin = async (account, callBackend = true) => {
    state.isAuthenticated = true
    state.user = account

    let userData = {
        id: 1, 
        oid_azure: account.localAccountId,
        nombre: account.name,
        email: account.username,
        iniciales: account.name ? account.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'U',
        rol: 'tecnico' 
    }

    if (callBackend) {
        try {
            const res = await UsersAPI.syncUser(account)
            if (res && res.data) {
                userData.id = res.data.id
                userData.rol = res.data.rol.toLowerCase() 
                userData.sede = res.data.sede
            }
        } catch (e) {
            console.warn('Error al sincronizar con el backend:', e)
        }
    }

    store.setCurrentUser(userData)
    localStorage.setItem('isAuthenticated', 'true')
  }

  return { login, logout, handleRedirect, state }
}
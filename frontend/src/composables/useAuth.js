import { ref } from 'vue'
import { msalInstance, state, graphScopes } from '../auth/AuthConfig'
import { useDataStore } from '../stores/dataStore'
import { useRouter } from 'vue-router'
import UsersAPI from '../services/UsersAPI'

export function useAuth() {
  const store = useDataStore()
  const router = useRouter()
  const isLoggingIn = ref(false)

  const formatUserData = (account) => {
    return {
        id: Date.now(), // Temporal hasta que el backend devuelva el ID real
        oid_azure: account.localAccountId,
        nombre: account.name,
        email: account.username,
        iniciales: account.name 
            ? account.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() 
            : 'U',
        rol: 'user' 
    }
  }
  
  const login = async () => {
    try {
      await msalInstance.initialize()
      await msalInstance.loginRedirect(graphScopes)
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
        const account = response.account
        await processLogin(account)
        return true 
      } 
      
      else {
        const currentAccounts = msalInstance.getAllAccounts()
        if (currentAccounts.length > 0) {
            const account = currentAccounts[0]
            await processLogin(account, false) 
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

    const userData = formatUserData(account)


    if (callBackend) {
        try {
            // Descomenta esto cuando el backend esté levantado
            // const backendUser = await UsersAPI.addUser(account)
            // if (backendUser && backendUser.id) userData.id = backendUser.id
            // if (backendUser && backendUser.rol) userData.rol = backendUser.rol
        } catch (e) {
            console.warn('No se pudo sincronizar con el backend, usando modo offline', e)
        }
    }

    store.setCurrentUser(userData)
    
    localStorage.setItem('isAuthenticated', 'true')
  }

  return {
    login,
    logout,
    handleRedirect,
    state
  }
}
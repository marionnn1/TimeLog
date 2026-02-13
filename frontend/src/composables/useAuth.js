import { ref } from 'vue'
import { msalInstance, state, graphScopes } from '../auth/AuthConfig'
import { useDataStore } from '../stores/dataStore'
import { useRouter } from 'vue-router'
import UsersAPI from '../services/UsersAPI'

export function useAuth() {
  const store = useDataStore()
  const router = useRouter()
  const isLoggingIn = ref(false)

  // Función auxiliar para formatear datos del usuario
  const formatUserData = (account) => {
    return {
        id: Date.now(), // Temporal hasta que el backend devuelva el ID real
        oid_azure: account.localAccountId,
        nombre: account.name,
        email: account.username,
        // Generar iniciales de forma segura
        iniciales: account.name 
            ? account.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() 
            : 'U',
        rol: 'user' 
    }
  }

  // Iniciar proceso de Login
  const login = async () => {
    try {
      await msalInstance.initialize()
      await msalInstance.loginRedirect(graphScopes)
    } catch (error) {
      console.error('Error iniciando sesión:', error)
    }
  }

  // Cerrar Sesión
  const logout = async () => {
    try {
      await msalInstance.initialize()
      
      // Limpieza total
      localStorage.removeItem('timeLog_state') // Limpia el store persistido
      localStorage.removeItem('isAuthenticated') // Limpia el guard del router
      store.$reset && store.$reset() // Si usas Pinia options, o manual:
      
      await msalInstance.logoutRedirect({
        postLogoutRedirectUri: import.meta.env.VITE_MSAL_POST_LOGOUT_REDIRECT_URI
      })
    } catch (error) {
      console.error('Error cerrando sesión:', error)
    }
  }

  // Manejar la vuelta de Microsoft (Redirect) o la Recarga de Página
  const handleRedirect = async () => {
    try {
      await msalInstance.initialize()
      
      // 1. Caso: Volvemos de un redirect (Login exitoso)
      const response = await msalInstance.handleRedirectPromise()
      
      if (response) {
        const account = response.account
        await processLogin(account)
        return true 
      } 
      
      // 2. Caso: Recarga de página (F5) - Recuperar sesión existente
      else {
        const currentAccounts = msalInstance.getAllAccounts()
        if (currentAccounts.length > 0) {
            const account = currentAccounts[0]
            // IMPORTANTE: Volvemos a cargar los datos en el Store
            await processLogin(account, false) // false = no llamar a API si solo es refresh (opcional)
            return true
        }
      }
    } catch (error) {
      console.error('Error manejando el redirect:', error)
    }
    return false
  }

  // Lógica centralizada para establecer usuario
  const processLogin = async (account, callBackend = true) => {
    state.isAuthenticated = true
    state.user = account
    
    // 1. Formatear datos para nuestra APP
    const userData = formatUserData(account)

    // 2. Llamar al Backend (Sincronizar usuario SQL Server)
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

    // 3. Guardar en Pinia (Memoria de la App)
    store.setCurrentUser(userData)
    
    // 4. Persistencia básica para el Router
    localStorage.setItem('isAuthenticated', 'true')
  }

  return {
    login,
    logout,
    handleRedirect,
    state
  }
}
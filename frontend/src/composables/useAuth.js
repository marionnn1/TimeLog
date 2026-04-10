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
      await msalInstance.loginRedirect(graphScopes)
    } catch (error) {
      console.error('Error iniciando sesión:', error)
    }
  }

  const logout = async () => {
    try {
      await msalInstance.initialize()

      localStorage.clear()
      sessionStorage.clear()
      if (store.$reset) store.$reset()

      await msalInstance.logoutRedirect({
        postLogoutRedirectUri: import.meta.env.VITE_MSAL_POST_LOGOUT_REDIRECT_URI,
        account: msalInstance.getAllAccounts()[0]
      })
    } catch (error) {
      console.error('Error cerrando sesión:', error)
      window.location.href = '/login'
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
      } else {
        const currentAccounts = msalInstance.getAllAccounts()
        if (currentAccounts.length > 0) {
          const account = currentAccounts[0]
          await processLogin(account, true)
          return true
        }
      }
    } catch (error) {
      console.error('Error manejando el redirect:', error)
    }
    return false
  }

  const processLogin = async (account, callBackend = true) => {
    // Normalización: Usamos 'tecnico' en minúsculas por defecto
    const rolesAzure = account.idTokenClaims?.roles || ['tecnico']
    const rolPrincipal = rolesAzure[0].toLowerCase() 

    let userData = {
      id: null,
      oid_azure: account.localAccountId,
      nombre: account.name,
      email: account.username,
      iniciales: account.name ? account.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'U',
      rol: rolPrincipal,
      foto: null // NUEVO: Inicializamos la foto
    }

    if (callBackend) {
      try {
        // NUEVO: Intentamos obtener el token para leer el perfil (Graph API)
        let accessToken = null;
        try {
            const tokenResponse = await msalInstance.acquireTokenSilent({
                scopes: ['User.Read'],
                account: account
            });
            accessToken = tokenResponse.accessToken;
        } catch (tokenError) {
            console.warn("No se pudo obtener el token silencioso para la foto:", tokenError);
        }

        // Le pasamos al API el account y el token de acceso que acabamos de conseguir
        const backendRes = await UsersAPI.syncUser(account, accessToken)

        if (backendRes.status === 'success' && backendRes.data) {
          userData.id = backendRes.data.id
          userData.rol = backendRes.data.rol || userData.rol
          userData.iniciales = backendRes.data.iniciales || userData.iniciales
          userData.foto = backendRes.data.foto || null // NUEVO: Guardamos la foto base64
        }
      } catch (e) {
        console.error('Error al sincronizar con el backend:', e)
        alert("No se pudo verificar tu usuario en el sistema.")
        return
      }
    }

    state.isAuthenticated = true
    state.user = account
    store.setCurrentUser(userData)
    localStorage.setItem('isAuthenticated', 'true')
  }

  return { login, logout, handleRedirect, state }
}
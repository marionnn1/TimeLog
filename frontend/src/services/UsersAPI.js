import API from './API'

export default {
  /**
   * Registra o actualiza un usuario en el backend tras el login de Microsoft
   * @param {Object} msalAccount - Objeto de cuenta que devuelve MSAL
   */
  async addUser(msalAccount) {
    try {
      const api = API()

      // Mapeo de datos: MSAL -> Backend (SQL Server)
      // localAccountId es el OID único de Azure AD
      const payload = {
        oid_azure: msalAccount.localAccountId, 
        email: msalAccount.username,
        nombre: msalAccount.name
      }

      // Axios stringifica el JSON automáticamente
      const response = await api.post('/users', payload)
      
      return response.data
    } catch (error) {
      console.error('Error al sincronizar usuario con el backend:', error)
      // Propagamos el error para manejarlo en el componente si es necesario
      throw error
    }
  }
}
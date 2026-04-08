import { reactive } from 'vue'
import { PublicClientApplication, LogLevel } from '@azure/msal-browser'

export const state = reactive({
    isAuthenticated: false,
    user: null
})

export const msalConfig = {
    auth: {
        clientId: import.meta.env.VITE_MSAL_CLIENT_ID,
        authority: `https://login.microsoftonline.com/${import.meta.env.VITE_MSAL_TENANT_ID}`,
        redirectUri: import.meta.env.VITE_MSAL_REDIRECT_URI,
        postLogoutRedirectUri: import.meta.env.VITE_MSAL_POST_LOGOUT_REDIRECT_URI,
    },
    cache: {
        cacheLocation: 'localStorage', // Cambiado a localStorage para mayor persistencia en Azure
        storeAuthStateInCookie: true,  // Habilitado para solucionar problemas de navegación InPrivate/Safari
    },
    system: {
        loggerOptions: {
            loggerCallback: (level, message, containsPii) => {
                if (containsPii) return;
                if (level === LogLevel.Error) console.error(message);
            }
        }
    }
}

export const graphScopes = {
    scopes: ['User.Read', 'email', 'openid', 'profile']
}

export const msalInstance = new PublicClientApplication(msalConfig)
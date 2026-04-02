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
        cacheLocation: 'sessionStorage',
        storeAuthStateInCookie: false,
    },
    system: {
        loggerOptions: {
            loggerCallback: (level, message, containsPii) => {
                if (containsPii) { return; }
                switch (level) {
                    case LogLevel.Error:
                        console.error(message);
                        return;
                    case LogLevel.Info:
                        // console.info(message); // Descomentar para depurar
                        return;
                    case LogLevel.Verbose:
                        // console.debug(message);
                        return;
                    case LogLevel.Warning:
                        console.warn(message);
                        return;
                }
            }
        }
    }
}

export const graphScopes = {
    scopes: ['User.Read', 'email']
}

export const msalInstance = new PublicClientApplication(msalConfig)
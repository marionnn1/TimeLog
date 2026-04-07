FROM node:20-alpine AS build-stage


WORKDIR /app

COPY package*.json ./

RUN npm i


COPY . . 


#Argumentos de build
ARG VITE_MSAL_CLIENT_ID
ARG VITE_MSAL_TENANT_ID
ARG VITE_MSAL_REDIRECT_URI
ARG VITE_MSAL_POST_LOGOUT_REDIRECT_URI

ENV VITE_MSAL_CLIENT_ID=$VITE_MSAL_CLIENT_ID
ENV VITE_MSAL_TENANT_ID=$VITE_MSAL_TENANT_ID
ENV VITE_MSAL_REDIRECT_URI=$VITE_MSAL_REDIRECT_URI
ENV VITE_MSAL_POST_LOGOUT_REDIRECT_URI=$VITE_MSAL_POST_LOGOUT_REDIRECT_URI


RUN npm run build

FROM nginx:alpine AS production-stage


# Copiar archivos build
COPY --from=build-stage /app/dist /usr/share/nginx/html


# Copiar configuración de nginx personalizada
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]


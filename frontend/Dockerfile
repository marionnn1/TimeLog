# Actualizamos a Node 20 para que Vite no se queje
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
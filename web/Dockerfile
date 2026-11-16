# Front para o Cloud Run: build do Vite e nginx servindo os arquivos estáticos.
# A URL da API vem do .env.production (ou da variável VITE_API_URL no build).
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
# O Cloud Run informa a porta em $PORT (8080); o nginx lê pelo template abaixo.
ENV PORT=8080
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080

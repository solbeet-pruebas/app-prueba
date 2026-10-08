# Imagen del frontend. Etapa `build` compila con Node; `runtime` sirve los estáticos
# con nginx sin privilegios (usuario nginx, puerto 8080). Ver docs/decisiones/0001-stack.md.

FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
# Directorio vacío para el include; docker compose monta acá el proxy de /api.
# La imagen corre como uid 101: se vuelve a root solo para crear el directorio.
USER root
RUN mkdir -p /etc/nginx/conf.d/extra
USER 101
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080

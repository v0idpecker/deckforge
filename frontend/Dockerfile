# frontend/Dockerfile

# Stage 1 — сборка
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2 — nginx отдаёт статику
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# конфиг для React Router — все пути отдаём index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

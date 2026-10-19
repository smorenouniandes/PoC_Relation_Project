# Frontend — PoC Relation Project (Next.js App Router)
# Build multi-stage con salida standalone para una imagen liviana.

# ---- Etapa 1: dependencias ----
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# ---- Etapa 2: build ----
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# La URL del backend puede inyectarse en build (variable pública de Next).
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
RUN npm run build

# ---- Etapa 3: runtime ----
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# Copiar solo lo necesario del output standalone.
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0
CMD ["node", "server.js"]

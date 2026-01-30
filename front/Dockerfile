# Build stage
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

ARG VITE_URL_BACKEND=http://localhost/api/vault
ENV VITE_URL_BACKEND=$VITE_URL_BACKEND

# Install dependencies
RUN npm ci

# Copy package files
COPY package*.json ./

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Production stage - use nginx to serve static files
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx-frontend.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

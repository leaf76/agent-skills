# Multi-stage build template
# Adjust based on your project type

# === Python ===
# FROM python:3.12-slim AS builder
# WORKDIR /app
# COPY pyproject.toml .
# RUN pip install --no-cache-dir .
# 
# FROM python:3.12-slim
# WORKDIR /app
# COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# COPY . .
# CMD ["python", "-m", "app"]

# === Node.js ===
# FROM node:20-slim AS builder
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci --only=production
# 
# FROM node:20-slim
# WORKDIR /app
# COPY --from=builder /app/node_modules ./node_modules
# COPY . .
# CMD ["node", "dist/index.js"]

# === Go ===
# FROM golang:1.22-alpine AS builder
# WORKDIR /app
# COPY go.* ./
# RUN go mod download
# COPY . .
# RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server
# 
# FROM alpine:latest
# COPY --from=builder /app/server /server
# CMD ["/server"]

# === Default: Python with uv ===
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv --break-system-packages

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Run
CMD ["uv", "run", "python", "-m", "app"]

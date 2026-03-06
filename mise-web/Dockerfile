FROM node:24-bookworm-slim AS base
WORKDIR /app
ENV NODE_ENV=production

FROM base AS deps
COPY mise-web/package.json mise-web/package-lock.json* mise-web/pnpm-lock.yaml* mise-web/yarn.lock* ./
ENV NODE_ENV=development
RUN set -eux; \
  if [ -f pnpm-lock.yaml ]; then \
    corepack enable; \
    install_cmd="pnpm install --frozen-lockfile"; \
  elif [ -f yarn.lock ]; then \
    install_cmd="yarn install --frozen-lockfile --network-timeout 300000"; \
  elif [ -f package-lock.json ]; then \
    npm config set fetch-retries 5; \
    npm config set fetch-retry-mintimeout 20000; \
    npm config set fetch-retry-maxtimeout 120000; \
    install_cmd="npm ci --prefer-offline --no-audit --progress=false"; \
  else \
    install_cmd="npm install --prefer-offline --no-audit --progress=false"; \
  fi; \
  success=0; \
  for attempt in 1 2 3 4 5; do \
    if sh -lc "$install_cmd"; then success=1; break; fi; \
    echo "Dependency install attempt ${attempt} failed, retrying..."; \
    sleep $((attempt * 5)); \
  done; \
  [ "$success" -eq 1 ]

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY mise-web/ .
RUN npm run build

FROM node:24-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY mise-web/public ./public

EXPOSE 3000
CMD ["node", "server.js"]

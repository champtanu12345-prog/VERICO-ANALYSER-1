FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Build the app for production (optional, since Vite handles dev proxy, but we'll use dev mode for simplicity here as we don't have nginx configured)
# RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]

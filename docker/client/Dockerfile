FROM node:latest as build

WORKDIR /app

COPY client/package*.json ./
RUN npm install
COPY ./client/. /app/
RUN npm run-script build

FROM nginx:latest

COPY --from=build /app/dist/chicken-cam /usr/share/nginx/html

COPY client/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

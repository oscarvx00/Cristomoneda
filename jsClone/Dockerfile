FROM node:16
WORKDIR /api
RUN apt update
RUN apt install npm -y
COPY package*.json ./
RUN npm install
COPY api.js ./
COPY blockchain.js ./
ENTRYPOINT [ "node", "api.js" ]
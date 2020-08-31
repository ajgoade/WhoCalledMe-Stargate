FROM node:12

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json ./

RUN npm install
# If you are building your code for production
# RUN npm ci --only=production

# Bundle app source
COPY ./astraConfig ./astraConfig
COPY ./bin ./bin
COPY ./config ./config
COPY ./gcpConfig ./gcpConfig
COPY ./lib ./lib
COPY ./public ./public
COPY ./routes ./routes
COPY ./views ./views
COPY app.js app.js



EXPOSE 3030
CMD [ "node", "bin/www" ]
FROM node:latest

USER node 

RUN mkdir /home/node/code

WORKDIR /home/node/code

COPY --chown=node:node package-lock.json package.json ./ 

RUN npm install

COPY --chown=node:node . . 

EXPOSE 5173

# you should specify the host to be able to see the page on localhost

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 

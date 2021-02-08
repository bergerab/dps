# pull official base image
FROM node:13.12.0-alpine

# set working directory
WORKDIR /usr/src/dps_ui

# add `/dps_ui/node_modules/.bin` to $PATH
ENV PATH /usr/src/dps_ui/node_modules/.bin:$PATH

RUN yarn install

# start app
CMD ["yarn", "start"]
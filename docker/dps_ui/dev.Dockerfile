# pull official base image
FROM node:13.12.0-alpine

# set working directory
WORKDIR /dps_ui

# add `/dps_ui/node_modules/.bin` to $PATH
ENV PATH /dps_ui/node_modules/.bin:$PATH

COPY . ./

RUN yarn install

# start app
CMD ["yarn", "start", "--silent"]
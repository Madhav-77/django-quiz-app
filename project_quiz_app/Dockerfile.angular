# Step 1: Build the Angular app
FROM node:23.1.0 AS build

# Set working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json first for efficient caching
COPY package.json package-lock.json ./

# Install the Angular dependencies
RUN npm install

# Copy the rest of your Angular project files
COPY . .

# Expose the port Angular will run on (default is 4200)
EXPOSE 4200

# Step 2: Serve the app using Angular CLI in development mode
CMD ["npm", "run", "start"]

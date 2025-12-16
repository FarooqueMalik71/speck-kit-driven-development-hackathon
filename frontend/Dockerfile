# Use Node.js 20 as the base image
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the Docusaurus site
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Start the Docusaurus server
CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0", "--port", "3000"]
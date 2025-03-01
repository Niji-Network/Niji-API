FROM node:22

# Update package lists and install Python, pip, and Redis server.
RUN apt-get update && \
    apt-get install -y python3 python3-pip redis-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PM2 globally via npm.
RUN npm install -g pm2

# Set the working directory.
WORKDIR /app

# Copy the application code to the container.
COPY . .

# Create the "static" directory if it doesn't exist.
RUN mkdir -p static

# Declare the "static" folder as a volume to persist its data.
VOLUME ["/app/static"]

# Install Python dependencies.
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose ports for the FastAPI app and Redis.
EXPOSE 8000 6379

# Start the application using PM2.
CMD ["pm2-runtime", "ecosystem.config.js"]

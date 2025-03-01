FROM node:22

RUN apt-get update && \
    apt-get install -y python3 python3-pip redis-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN npm install -g pm2

WORKDIR /app

COPY . .

RUN mkdir -p static
VOLUME ["/app/static"]

# Use --break-system-packages to bypass the externally managed environment restriction
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

EXPOSE 7000 6379

CMD ["pm2-runtime", "ecosystem.config.js"]

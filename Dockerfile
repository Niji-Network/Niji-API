FROM node:22

# Installer Python, pip, et redis-server
RUN apt-get update && \
    apt-get install -y python3 python3-pip redis-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installer PM2 globalement
RUN npm install -g pm2

WORKDIR /app

# Copier l'application
COPY . .

# Créer le dossier static s'il n'existe pas
RUN mkdir -p static

# Déclarer le volume pour la persistance
VOLUME ["/app/static"]

# Créer un virtualenv et ajouter son bin au PATH
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Installer les dépendances dans le venv avec --break-system-packages si besoin
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

EXPOSE 7000 6379

CMD ["pm2-runtime", "ecosystem.config.js"]

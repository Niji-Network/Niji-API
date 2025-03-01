FROM node:22

# Mise à jour et installation des paquets nécessaires, y compris python3-venv
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv redis-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installer PM2 globalement via npm
RUN npm install -g pm2

WORKDIR /app

# Copier l'ensemble du projet dans le container
COPY . .

# Créer le dossier "static" s'il n'existe pas
RUN mkdir -p static

# Déclarer le volume pour le dossier "static" afin de conserver les fichiers téléchargés
VOLUME ["/app/static"]

# Créer un virtualenv dans /venv et mettre à jour le PATH pour l'activer
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Installer les dépendances Python dans le virtualenv avec l'option --break-system-packages (si nécessaire)
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

EXPOSE 7000 6379

CMD ["pm2-runtime", "ecosystem.config.js"]

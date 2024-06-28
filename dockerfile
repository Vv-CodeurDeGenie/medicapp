# Utiliser une image de base légère de Python
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers requis dans le conteneur
COPY . /app

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn


# Exposer le port sur lequel l'application Flask s'exécute
EXPOSE 5000

# Commande pour exécuter l'application Flask
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

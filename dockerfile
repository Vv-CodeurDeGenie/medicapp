# Utiliser une image de base légère de Python
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers requis dans le conteneur
COPY requirements.txt .
COPY app.py .
COPY templates templates/
COPY static static/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel l'application Flask s'exécute
EXPOSE 5000

# Commande pour exécuter l'application Flask
CMD ["python", "app.py"]

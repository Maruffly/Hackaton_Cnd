# 1. Image de base légère (Python 3.10 version "slim")
FROM python:3.10-slim

# 2. On définit le dossier de travail dans le conteneur
WORKDIR /app

# 3. On installe les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copie du fichier de dépendances
COPY requirements.txt .

# 5. Installation des librairies Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copie du code source et des dossiers
COPY src/ ./src/
# Note : On ne copie pas 'data/' car on va le monter en volume

# 7. Commande de lancement
CMD ["python", "src/main.py"]
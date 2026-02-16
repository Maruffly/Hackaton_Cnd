# 1. Image de base légère (Python 3.10 version "slim")
FROM python:3.10-slim AS builder

# 2. On définit le dossier de travail dans le conteneur
WORKDIR /app

# 3. On installe les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copie du fichier de dépendances
COPY requirements.txt .

# 5. Installation des librairies Python
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim AS runner

WORKDIR /app

# On installe UNIQUEMENT les librairies d'exécution (ex: pour PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# On récupère uniquement ce qui est nécessaire du builder
COPY --from=builder /opt/venv /opt/venv
COPY src/ ./src/

# On force l'utilisation du venv
ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONUNBUFFERED=1

# Non root
RUN useradd -m datauser
USER myuser

CMD ["python", "src/main.py"]
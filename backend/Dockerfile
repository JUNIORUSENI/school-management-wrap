# Dockerfile pour Palmarès Imara Backend
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="palmares-imara@example.com"
LABEL description="Backend Django pour l'application Palmarès Imara"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=palmaresimara.settings

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY palmaresimara/ /app/palmaresimara/
COPY scripts/ /app/scripts/
COPY create_example_excel.py /app/

# Création des répertoires nécessaires
RUN mkdir -p /app/logs /app/media /app/staticfiles

# Collecte des fichiers statiques
RUN python palmaresimara/manage.py collectstatic --noinput

# Création d'un utilisateur non-root
RUN useradd --create-home --shell /bin/bash palmares
RUN chown -R palmares:palmares /app
USER palmares

# Port exposé
EXPOSE 8000

# Script de démarrage
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Commande par défaut
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "palmaresimara.wsgi:application", "--bind", "0.0.0.0:8000"]

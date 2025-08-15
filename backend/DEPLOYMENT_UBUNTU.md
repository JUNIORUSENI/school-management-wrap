# Guide de Déploiement sur VPS Ubuntu

Ce guide vous accompagne dans le déploiement de Palmarès Imara Backend sur un VPS Ubuntu.

## 🚀 Prérequis

### Sur votre VPS Ubuntu
```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances système
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    make \
    curl \
    unzip \
    supervisor

# Installation de Docker (optionnel)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## 📦 Déploiement Manuel

### 1. Cloner le projet
```bash
git clone <votre-repo-git> palmares-backend
cd palmares-backend
```

### 2. Configuration de l'environnement
```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
make install
# ou
pip install -r requirements.txt
```

### 3. Configuration de PostgreSQL
```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données et l'utilisateur
CREATE DATABASE palmares_imara;
CREATE USER palmares_user WITH PASSWORD 'votre_mot_de_passe_fort';
GRANT ALL PRIVILEGES ON DATABASE palmares_imara TO palmares_user;
\q
```

### 4. Configuration des variables d'environnement
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer les variables (utilisez nano, vim, ou votre éditeur préféré)
nano .env
```

Configurez au minimum :
```env
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
DEBUG=False
DATABASE_URL=postgresql://palmares_user:votre_mot_de_passe_fort@localhost:5432/palmares_imara
ALLOWED_HOSTS=votre-domaine.com,votre-ip-vps
CORS_ALLOWED_ORIGINS=http://votre-frontend-domain.com
```

### 5. Configuration de l'application
```bash
# Application des migrations
make migrate

# Collecte des fichiers statiques
make collectstatic

# Création d'un superutilisateur
make superuser
```

### 6. Configuration de Gunicorn
```bash
# Tester Gunicorn
gunicorn palmaresimara.wsgi:application --bind 0.0.0.0:8000

# Créer un fichier de service systemd
sudo nano /etc/systemd/system/palmares.service
```

Contenu du fichier service :
```ini
[Unit]
Description=Palmares Imara Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/palmares-backend
Environment="PATH=/path/to/palmares-backend/venv/bin"
EnvironmentFile=/path/to/palmares-backend/.env
ExecStart=/path/to/palmares-backend/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/palmares.sock \
    palmaresimara.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 7. Configuration de Nginx
```bash
sudo nano /etc/nginx/sites-available/palmares
```

Contenu de la configuration Nginx :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/palmares-backend/palmaresimara;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        root /path/to/palmares-backend/palmaresimara;
        expires 30d;
        add_header Cache-Control "public";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/palmares.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 8. Activation des services
```bash
# Activer la configuration Nginx
sudo ln -s /etc/nginx/sites-available/palmares /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Activer le service Palmares
sudo systemctl start palmares
sudo systemctl enable palmares

# Vérifier le statut
sudo systemctl status palmares
```

## 🐳 Déploiement avec Docker

### Option 1 : Docker Compose (Recommandé)
```bash
# Cloner le projet
git clone <votre-repo-git> palmares-backend
cd palmares-backend

# Configurer les variables d'environnement
cp .env.example .env
nano .env

# Démarrer avec Docker Compose
docker-compose up -d

# Vérifier les logs
docker-compose logs -f web
```

### Option 2 : Docker Build
```bash
# Construire l'image
docker build -t palmares-backend .

# Lancer le conteneur
docker run -d \
  --name palmares-web \
  -p 8000:8000 \
  --env-file .env \
  palmares-backend
```

## 🔒 Configuration HTTPS avec Let's Encrypt

```bash
# Installer certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d votre-domaine.com

# Vérifier le renouvellement automatique
sudo certbot renew --dry-run
```

## 📊 Monitoring et Logs

### Configuration de Supervisor (optionnel)
```bash
sudo nano /etc/supervisor/conf.d/palmares.conf
```

```ini
[program:palmares]
command=/path/to/palmares-backend/venv/bin/gunicorn --workers 3 --bind unix:/run/palmares.sock palmaresimara.wsgi:application
directory=/path/to/palmares-backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/palmares/palmares.log
```

### Gestion des logs
```bash
# Créer un répertoire pour les logs
sudo mkdir -p /var/log/palmares
sudo chown www-data:www-data /var/log/palmares

# Configuration de la rotation des logs
sudo nano /etc/logrotate.d/palmares
```

```
/var/log/palmares/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

## 🔧 Scripts de Maintenance

### Script de sauvegarde
```bash
# Créer un script de sauvegarde
nano backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backups/palmares"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Sauvegarde de la base de données
pg_dump palmares_imara > $BACKUP_DIR/db_backup_$DATE.sql

# Sauvegarde des fichiers media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz palmaresimara/media/

echo "Sauvegarde terminée: $DATE"
```

### Configuration Crontab
```bash
# Éditer la crontab
crontab -e

# Ajouter une sauvegarde quotidienne à 2h du matin
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

## 🚨 Dépannage

### Vérifier les services
```bash
# Status des services
sudo systemctl status palmares
sudo systemctl status nginx
sudo systemctl status postgresql

# Logs des services
sudo journalctl -u palmares -f
sudo tail -f /var/log/nginx/error.log
```

### Problèmes courants

**1. Permission denied sur le socket**
```bash
sudo chown www-data:www-data /run/palmares.sock
```

**2. Erreur de connexion à PostgreSQL**
```bash
# Vérifier la configuration
sudo nano /etc/postgresql/*/main/postgresql.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf
sudo systemctl restart postgresql
```

**3. Fichiers statiques non trouvés**
```bash
# Re-collecter les fichiers statiques
source venv/bin/activate
python palmaresimara/manage.py collectstatic --clear --noinput
```

## ⚡ Performance et Optimisation

### Configuration PostgreSQL optimisée
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

```
# Optimisations de base
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
```

### Configuration Nginx optimisée
```nginx
# Dans le bloc server
client_max_body_size 100M;
keepalive_timeout 65;

# Compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

## 📋 Checklist de Déploiement

- [ ] VPS configuré avec Ubuntu
- [ ] Python 3.8+ installé
- [ ] PostgreSQL configuré
- [ ] Variables d'environnement configurées
- [ ] Migrations appliquées
- [ ] Fichiers statiques collectés
- [ ] Superutilisateur créé
- [ ] Gunicorn configuré
- [ ] Nginx configuré
- [ ] HTTPS configuré (Let's Encrypt)
- [ ] Services systemd activés
- [ ] Logs configurés
- [ ] Sauvegardes automatiques configurées
- [ ] Tests de fonctionnement effectués

## 📞 Support

En cas de problème lors du déploiement, utilisez :

```bash
# Vérifier les configurations
python scripts/deploy_check.py

# Vérifier l'état du système
./make.ps1 status  # Sur Windows
make status        # Sur Linux
```

Ce guide couvre les aspects essentiels du déploiement sur Ubuntu. Adaptez les chemins et configurations selon votre environnement spécifique.

#!/bin/bash
# Script de démarrage Docker pour Palmarès Imara

set -e

echo "🚀 Démarrage de Palmarès Imara Backend..."

# Fonction pour attendre que la base de données soit prête
wait_for_db() {
    echo "⏳ Attente de la disponibilité de la base de données..."
    
    # Extraire les informations de connexion depuis DATABASE_URL
    if [[ -n "$DATABASE_URL" ]]; then
        # Parse DATABASE_URL format: postgres://user:pass@host:port/dbname
        if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
            DB_USER="${BASH_REMATCH[1]}"
            DB_PASSWORD="${BASH_REMATCH[2]}"
            DB_HOST="${BASH_REMATCH[3]}"
            DB_PORT="${BASH_REMATCH[4]}"
            DB_NAME="${BASH_REMATCH[5]}"
            
            export PGPASSWORD=$DB_PASSWORD
            
            until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME; do
                echo "Base de données non disponible - attente..."
                sleep 2
            done
            
            echo "✅ Base de données disponible!"
        else
            echo "⚠️  Format DATABASE_URL non reconnu, passage à la suite..."
        fi
    else
        echo "⚠️  DATABASE_URL non défini, passage à la suite..."
    fi
}

# Fonction pour exécuter les migrations
run_migrations() {
    echo "🔄 Exécution des migrations..."
    python palmaresimara/manage.py migrate --noinput
    echo "✅ Migrations terminées!"
}

# Fonction pour collecter les fichiers statiques
collect_static() {
    echo "📦 Collection des fichiers statiques..."
    python palmaresimara/manage.py collectstatic --noinput --clear
    echo "✅ Fichiers statiques collectés!"
}

# Fonction pour créer un superutilisateur si les variables sont définies
create_superuser() {
    if [[ -n "$DJANGO_SUPERUSER_USERNAME" && -n "$DJANGO_SUPERUSER_EMAIL" && -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
        echo "👤 Création du superutilisateur..."
        python palmaresimara/manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superutilisateur créé avec succès!')
else:
    print('Superutilisateur existe déjà!')
EOF
    else
        echo "⚠️  Variables de superutilisateur non définies, passage à la suite..."
    fi
}

# Fonction de vérification de santé
health_check() {
    echo "🔍 Vérification de santé de l'application..."
    python palmaresimara/manage.py check --deploy
    echo "✅ Vérifications terminées!"
}

# Exécution des étapes de démarrage
main() {
    echo "Environnement: ${DJANGO_SETTINGS_MODULE:-palmaresimara.settings}"
    echo "Debug mode: ${DEBUG:-False}"
    
    # Attendre la base de données
    wait_for_db
    
    # Exécuter les migrations
    run_migrations
    
    # Collecter les fichiers statiques
    collect_static
    
    # Créer un superutilisateur si demandé
    create_superuser
    
    # Vérification de santé
    health_check
    
    echo "🎉 Initialisation terminée avec succès!"
    echo "🚀 Démarrage de l'application..."
    
    # Exécuter la commande passée en argument
    exec "$@"
}

# Point d'entrée principal
if [ "${1}" = 'gunicorn' ]; then
    main "$@"
elif [ "${1}" = 'python' ] && [ "${2}" = 'palmaresimara/manage.py' ]; then
    # Pour les commandes Django directes
    wait_for_db
    exec "$@"
else
    # Pour toute autre commande
    exec "$@"
fi

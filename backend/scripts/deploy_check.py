#!/usr/bin/env python
"""
Script de vérification de configuration pour le déploiement en production.
Usage: python scripts/deploy_check.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status='info'):
    """Affiche un message avec une couleur selon le statut."""
    if status == 'success':
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    elif status == 'error':
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    elif status == 'warning':
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    elif status == 'info':
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def check_environment_variables():
    """Vérifie les variables d'environnement critiques."""
    print(f"\n{Colors.BOLD}1. Variables d'environnement{Colors.END}")
    
    critical_vars = [
        'SECRET_KEY',
        'DEBUG',
        'DATABASE_URL'
    ]
    
    optional_vars = [
        'ALLOWED_HOSTS',
        'CORS_ALLOWED_ORIGINS',
        'LOG_LEVEL'
    ]
    
    all_good = True
    
    for var in critical_vars:
        value = os.getenv(var)
        if not value:
            print_status(f"Variable critique manquante: {var}", 'error')
            all_good = False
        else:
            if var == 'DEBUG' and value.lower() in ['true', '1', 'yes']:
                print_status(f"{var} est activé (attention en production!)", 'warning')
            elif var == 'SECRET_KEY' and 'insecure' in value:
                print_status(f"{var} utilise une clé par défaut non sécurisée", 'error')
                all_good = False
            else:
                print_status(f"{var} configuré", 'success')
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print_status(f"{var} configuré: {value[:50]}...", 'success')
        else:
            print_status(f"{var} non configuré (optionnel)", 'info')
    
    return all_good

def check_database_config():
    """Vérifie la configuration de la base de données."""
    print(f"\n{Colors.BOLD}2. Configuration de la base de données{Colors.END}")
    
    database_url = os.getenv('DATABASE_URL', '')
    
    if 'sqlite' in database_url:
        print_status("SQLite détecté - OK pour développement, PostgreSQL recommandé pour production", 'warning')
        return True
    elif 'postgresql' in database_url:
        print_status("PostgreSQL configuré", 'success')
        return True
    else:
        print_status("Configuration de base de données non détectée ou non supportée", 'error')
        return False

def check_security_settings():
    """Vérifie les paramètres de sécurité."""
    print(f"\n{Colors.BOLD}3. Paramètres de sécurité{Colors.END}")
    
    security_settings = {
        'SECURE_SSL_REDIRECT': 'Redirection HTTPS',
        'SESSION_COOKIE_SECURE': 'Cookies de session sécurisés',
        'CSRF_COOKIE_SECURE': 'Cookies CSRF sécurisés',
        'SECURE_BROWSER_XSS_FILTER': 'Protection XSS',
        'SECURE_CONTENT_TYPE_NOSNIFF': 'Protection MIME'
    }
    
    all_secure = True
    
    for setting, description in security_settings.items():
        value = os.getenv(setting)
        if value and value.lower() in ['true', '1', 'yes']:
            print_status(f"{description} activé", 'success')
        else:
            print_status(f"{description} non activé", 'warning')
            all_secure = False
    
    return all_secure

def check_static_files():
    """Vérifie la configuration des fichiers statiques."""
    print(f"\n{Colors.BOLD}4. Fichiers statiques{Colors.END}")
    
    # Vérifier la présence du répertoire static
    if Path('palmaresimara/static').exists():
        print_status("Répertoire static trouvé", 'success')
    else:
        print_status("Répertoire static manquant", 'warning')
    
    # Vérifier si collectstatic a été exécuté
    if Path('palmaresimara/staticfiles').exists():
        print_status("Fichiers statiques collectés", 'success')
        return True
    else:
        print_status("Fichiers statiques non collectés - exécutez 'make collectstatic'", 'warning')
        return False

def check_requirements():
    """Vérifie les dépendances critiques."""
    print(f"\n{Colors.BOLD}5. Dépendances critiques{Colors.END}")
    
    if not Path('requirements.txt').exists():
        print_status("requirements.txt manquant", 'error')
        return False
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        critical_packages = [
            'Django',
            'djangorestframework',
            'django-cors-headers',
            'python-dotenv'
        ]
        
        all_present = True
        for package in critical_packages:
            if package.lower() in requirements.lower():
                print_status(f"{package} présent", 'success')
            else:
                print_status(f"{package} manquant", 'error')
                all_present = False
        
        return all_present
        
    except Exception as e:
        print_status(f"Erreur lors de la lecture de requirements.txt: {e}", 'error')
        return False

def check_migrations():
    """Vérifie l'état des migrations."""
    print(f"\n{Colors.BOLD}6. Migrations de base de données{Colors.END}")
    
    migrations_dir = Path('palmaresimara/students/migrations')
    
    if not migrations_dir.exists():
        print_status("Répertoire des migrations manquant", 'error')
        return False
    
    migration_files = list(migrations_dir.glob('*.py'))
    migration_files = [f for f in migration_files if f.name != '__init__.py']
    
    if migration_files:
        print_status(f"{len(migration_files)} fichier(s) de migration trouvé(s)", 'success')
        return True
    else:
        print_status("Aucun fichier de migration trouvé", 'warning')
        return False

def generate_production_checklist():
    """Génère une checklist pour la production."""
    print(f"\n{Colors.BOLD}📋 CHECKLIST DE DÉPLOIEMENT EN PRODUCTION{Colors.END}")
    print("=" * 50)
    
    checklist = [
        "□ Configurer DEBUG=False",
        "□ Générer une SECRET_KEY sécurisée unique",
        "□ Configurer une base de données PostgreSQL",
        "□ Configurer ALLOWED_HOSTS avec les domaines autorisés",
        "□ Activer les paramètres de sécurité HTTPS",
        "□ Configurer les variables d'environnement sur le serveur",
        "□ Exécuter les migrations : make migrate",
        "□ Collecter les fichiers statiques : make collectstatic",
        "□ Créer un superutilisateur : make superuser",
        "□ Configurer le serveur web (nginx/Apache)",
        "□ Configurer le serveur d'application (gunicorn)",
        "□ Mettre en place la sauvegarde automatique",
        "□ Configurer le monitoring et les logs",
        "□ Tester toutes les fonctionnalités",
        "□ Configurer SSL/TLS"
    ]
    
    for item in checklist:
        print(f"  {item}")

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 VÉRIFICATION DE CONFIGURATION - PALMARÈS IMARA{Colors.END}")
    print("=" * 60)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('palmaresimara'):
        print_status("Ce script doit être exécuté depuis le répertoire backend", 'error')
        sys.exit(1)
    
    # Charger les variables d'environnement
    env_file = Path('.env')
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print_status("Fichier .env chargé", 'success')
    else:
        print_status("Fichier .env non trouvé", 'warning')
    
    # Exécuter toutes les vérifications
    checks = [
        check_environment_variables(),
        check_database_config(),
        check_security_settings(),
        check_static_files(),
        check_requirements(),
        check_migrations()
    ]
    
    # Résumé
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    print(f"\n{Colors.BOLD}📊 RÉSUMÉ{Colors.END}")
    print("=" * 20)
    
    if passed_checks == total_checks:
        print_status(f"Toutes les vérifications sont passées ({passed_checks}/{total_checks})", 'success')
        print_status("Configuration prête pour le déploiement!", 'success')
    else:
        print_status(f"Certaines vérifications ont échoué ({passed_checks}/{total_checks})", 'error')
        print_status("Veuillez corriger les problèmes avant le déploiement", 'warning')
    
    generate_production_checklist()
    
    print(f"\n{Colors.BLUE}💡 Pour plus d'aide sur le déploiement, consultez le README.md{Colors.END}")

if __name__ == '__main__':
    main()

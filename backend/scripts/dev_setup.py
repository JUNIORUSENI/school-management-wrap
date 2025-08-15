#!/usr/bin/env python
"""
Script de configuration automatique pour l'environnement de développement.
Usage: python scripts/dev_setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Exécute une commande shell."""
    print(f"Exécution: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erreur lors de l'exécution de: {command}")
        print(f"Sortie d'erreur: {result.stderr}")
        return False
    print(f"✓ {command}")
    return True

def setup_environment():
    """Configure l'environnement de développement."""
    print("🚀 Configuration de l'environnement de développement Palmarès Imara")
    print("=" * 60)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('palmaresimara'):
        print("❌ Erreur: Ce script doit être exécuté depuis le répertoire backend")
        sys.exit(1)
    
    # Vérifier l'environnement virtuel
    if not os.path.exists('venv'):
        print("❌ Erreur: Environnement virtuel 'venv' non trouvé")
        print("Créez d'abord un environnement virtuel avec: python -m venv venv")
        sys.exit(1)
    
    # Chemins
    venv_python = Path('venv/Scripts/python.exe')
    venv_pip = Path('venv/Scripts/pip.exe')
    
    if not venv_python.exists():
        print("❌ Erreur: Python dans l'environnement virtuel non trouvé")
        sys.exit(1)
    
    print("📦 Installation des dépendances...")
    if not run_command(f'{venv_pip} install -r requirements.txt'):
        sys.exit(1)
    
    # Créer le fichier .env s'il n'existe pas
    if not os.path.exists('.env'):
        print("📝 Création du fichier .env...")
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✓ Fichier .env créé depuis .env.example")
        else:
            print("⚠️  Fichier .env.example non trouvé, création d'un .env basique")
            with open('.env', 'w') as f:
                f.write('SECRET_KEY=django-insecure-dev-key-change-in-production\n')
                f.write('DEBUG=True\n')
                f.write('ALLOWED_HOSTS=127.0.0.1,localhost\n')
    
    # Migrations
    print("🔄 Application des migrations...")
    manage_cmd = f'{venv_python} palmaresimara/manage.py'
    
    if not run_command(f'{manage_cmd} makemigrations'):
        sys.exit(1)
    
    if not run_command(f'{manage_cmd} migrate'):
        sys.exit(1)
    
    # Créer des répertoires nécessaires
    os.makedirs('logs', exist_ok=True)
    os.makedirs('palmaresimara/media', exist_ok=True)
    
    print("\n✅ Configuration terminée avec succès!")
    print("\n📋 Prochaines étapes:")
    print("1. Créer un superutilisateur: make superuser")
    print("2. Démarrer le serveur: make run")
    print("3. Visiter http://127.0.0.1:8000/admin/ pour l'interface d'administration")
    print("4. Tester l'API: http://127.0.0.1:8000/api/")

if __name__ == '__main__':
    setup_environment()

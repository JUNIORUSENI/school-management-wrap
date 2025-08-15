#!/usr/bin/env python
"""
Script de sauvegarde et restauration de la base de données.
Usage: 
  python scripts/backup_restore.py backup [nom_fichier]
  python scripts/backup_restore.py restore nom_fichier.json
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

def run_django_command(command):
    """Exécute une commande Django."""
    venv_python = Path('venv/Scripts/python.exe')
    manage_cmd = f'{venv_python} palmaresimara/manage.py'
    
    full_command = f'{manage_cmd} {command}'
    print(f"Exécution: {full_command}")
    
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
    return result

def backup_database(filename=None):
    """Sauvegarde la base de données."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.json"
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Créer le répertoire de sauvegarde
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / filename
    
    print(f"🔄 Sauvegarde de la base de données vers {backup_path}")
    
    # Utiliser Django dumpdata
    result = run_django_command(f'dumpdata --indent=2 --natural-foreign --natural-primary > {backup_path}')
    
    if result.returncode == 0:
        print(f"✅ Sauvegarde réussie: {backup_path}")
        
        # Informations sur la sauvegarde
        file_size = backup_path.stat().st_size
        print(f"📊 Taille du fichier: {file_size / 1024:.1f} KB")
        
        return True
    else:
        print(f"❌ Erreur lors de la sauvegarde:")
        print(result.stderr)
        return False

def restore_database(filename):
    """Restaure la base de données."""
    backup_path = Path('backups') / filename
    
    if not backup_path.exists():
        print(f"❌ Fichier de sauvegarde non trouvé: {backup_path}")
        return False
    
    print(f"🔄 Restauration de la base de données depuis {backup_path}")
    print("⚠️  ATTENTION: Cette opération va écraser les données existantes!")
    
    response = input("Continuer? (y/N): ").strip().lower()
    if response != 'y':
        print("Restauration annulée.")
        return False
    
    # Vider la base de données (flush)
    print("🗑️  Vidage de la base de données...")
    result = run_django_command('flush --noinput')
    
    if result.returncode != 0:
        print("❌ Erreur lors du vidage de la base de données:")
        print(result.stderr)
        return False
    
    # Charger les données
    print("📥 Chargement des données...")
    result = run_django_command(f'loaddata {backup_path}')
    
    if result.returncode == 0:
        print(f"✅ Restauration réussie depuis {backup_path}")
        return True
    else:
        print(f"❌ Erreur lors de la restauration:")
        print(result.stderr)
        return False

def list_backups():
    """Liste les sauvegardes disponibles."""
    backup_dir = Path('backups')
    
    if not backup_dir.exists():
        print("📂 Aucun répertoire de sauvegarde trouvé.")
        return
    
    backups = list(backup_dir.glob('*.json'))
    
    if not backups:
        print("📂 Aucune sauvegarde trouvée.")
        return
    
    print("📋 Sauvegardes disponibles:")
    for backup in sorted(backups, reverse=True):
        size = backup.stat().st_size
        modified = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  • {backup.name} ({size / 1024:.1f} KB, {modified.strftime('%Y-%m-%d %H:%M')})")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/backup_restore.py backup [nom_fichier]")
        print("  python scripts/backup_restore.py restore nom_fichier.json")
        print("  python scripts/backup_restore.py list")
        sys.exit(1)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('palmaresimara'):
        print("❌ Erreur: Ce script doit être exécuté depuis le répertoire backend")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'backup':
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        backup_database(filename)
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Erreur: Nom du fichier de sauvegarde requis")
            sys.exit(1)
        
        filename = sys.argv[2]
        restore_database(filename)
    
    elif command == 'list':
        list_backups()
    
    else:
        print(f"❌ Commande inconnue: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()

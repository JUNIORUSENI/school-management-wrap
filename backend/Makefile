# Makefile pour le backend Palmarès Imara
# Usage: make <target>
# Compatible Windows et Linux/macOS

# Détection du système d'exploitation
ifeq ($(OS),Windows_NT)
	DETECTED_OS := Windows
	VENV_BIN = $(VENV)/Scripts
	PYTHON_EXT = .exe
	RM = del /Q
	RMDIR = rmdir /S /Q
	COPY = copy
	MKDIR = if not exist
	PATH_SEP = \\
	NULL = nul
	ENV_FILE_CHECK = if not exist ".env"
	DB_FILE = palmaresimara$(PATH_SEP)db.sqlite3
	PAUSE_CMD = pause >nul
	FIND_CMD = findstr -i
	PYCACHE_CLEAN = @for /r . %%i in (*.pyc) do del "%%i" 2>nul || true
else
	DETECTED_OS := $(shell uname -s)
	VENV_BIN = $(VENV)/bin
	PYTHON_EXT =
	RM = rm -f
	RMDIR = rm -rf
	COPY = cp
	MKDIR = mkdir -p
	PATH_SEP = /
	NULL = /dev/null
	ENV_FILE_CHECK = [ ! -f ".env" ]
	DB_FILE = palmaresimara$(PATH_SEP)db.sqlite3
	PAUSE_CMD = read -p "Appuyez sur Entrée pour continuer..." dummy
	FIND_CMD = grep -i
	PYCACHE_CLEAN = find . -name "*.pyc" -delete 2>/dev/null || true
endif

# Variables
PYTHON = python
VENV = venv
VENV_PYTHON = $(VENV_BIN)/python$(PYTHON_EXT)
VENV_PIP = $(VENV_BIN)/pip$(PYTHON_EXT)
VENV_COVERAGE = $(VENV_BIN)/coverage$(PYTHON_EXT)
MANAGE = "$(VENV_PYTHON)" palmaresimara/manage.py

# Couleurs pour l'affichage (fonctionnent sur la plupart des terminaux)
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m

# Détection de la couleur (disable sur certains terminaux)
ifneq ($(TERM),)
	ifeq ($(TERM),dumb)
		BLUE =
		GREEN =
		YELLOW =
		RED =
		NC =
	endif
endif

.PHONY: help install setup migrate test run clean dev-server import-example os-info

# Target par défaut
help:
	@echo "$(BLUE)Palmarès Imara Backend - Commandes disponibles ($(DETECTED_OS)):$(NC)"
	@echo ""
	@echo "$(GREEN)Setup et installation:$(NC)"
	@echo "  make install         - Installer les dépendances"
	@echo "  make setup          - Configuration complète du projet"
	@echo "  make migrate        - Exécuter les migrations"
	@echo "  make superuser      - Créer un superutilisateur"
	@echo ""
	@echo "$(GREEN)Développement:$(NC)"
	@echo "  make run            - Démarrer le serveur de développement"
	@echo "  make dev-server     - Démarrer avec auto-reload"
	@echo "  make shell          - Ouvrir le shell Django"
	@echo "  make dbshell        - Ouvrir le shell de base de données"
	@echo ""
	@echo "$(GREEN)Tests et qualité:$(NC)"
	@echo "  make test           - Exécuter tous les tests"
	@echo "  make test-models    - Tester uniquement les modèles"
	@echo "  make test-api       - Tester uniquement l'API"
	@echo "  make test-import    - Tester la commande d'import"
	@echo "  make coverage       - Tests avec couverture de code"
	@echo ""
	@echo "$(GREEN)Import et données:$(NC)"
	@echo "  make import-example - Créer et importer un fichier Excel d'exemple"
	@echo ""
	@echo "$(GREEN)Maintenance:$(NC)"
	@echo "  make clean          - Nettoyer les fichiers temporaires"
	@echo "  make reset-db       - Réinitialiser la base de données"
	@echo "  make collectstatic  - Collecter les fichiers statiques"
	@echo "  make os-info        - Afficher les infos système"

# Information système
os-info:
	@echo "$(BLUE)Informations système:$(NC)"
	@echo "OS détecté: $(DETECTED_OS)"
	@echo "Environnement virtuel: $(VENV_BIN)"
	@echo "Python: $(VENV_PYTHON)"
	@echo "Pip: $(VENV_PIP)"

# Installation des dépendances
install:
	@echo "$(BLUE)Installation des dépendances...$(NC)"
	$(VENV_PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dépendances installées$(NC)"

# Configuration complète du projet
setup: install
	@echo "$(BLUE)Configuration du projet...$(NC)"
ifeq ($(OS),Windows_NT)
	@$(ENV_FILE_CHECK) $(COPY) ".env.example" ".env"
else
	@$(ENV_FILE_CHECK) && $(COPY) .env.example .env || true
endif
	$(MANAGE) makemigrations
	$(MANAGE) migrate
	@$(MKDIR) logs$(NULL) || true
	@$(MKDIR) palmaresimara$(PATH_SEP)media$(NULL) || true
	@echo "$(GREEN)✓ Projet configuré$(NC)"
	@echo "$(YELLOW)N'oubliez pas de créer un superutilisateur avec: make superuser$(NC)"

# Migrations
migrate:
	@echo "$(BLUE)Exécution des migrations...$(NC)"
	$(MANAGE) makemigrations
	$(MANAGE) migrate
	@echo "$(GREEN)✓ Migrations terminées$(NC)"

# Créer un superutilisateur
superuser:
	@echo "$(BLUE)Création d'un superutilisateur...$(NC)"
	$(MANAGE) createsuperuser

# Démarrer le serveur de développement
run:
	@echo "$(BLUE)Démarrage du serveur de développement...$(NC)"
	$(MANAGE) runserver

# Serveur avec auto-reload
dev-server:
	@echo "$(BLUE)Démarrage du serveur avec auto-reload...$(NC)"
	$(MANAGE) runserver --settings=palmaresimara.settings

# Shell Django
shell:
	$(MANAGE) shell

# Shell de base de données
dbshell:
	$(MANAGE) dbshell

# Tests
test:
	@echo "$(BLUE)Exécution de tous les tests...$(NC)"
	$(MANAGE) test students.tests --verbosity=1

test-models:
	@echo "$(BLUE)Test des modèles...$(NC)"
	$(MANAGE) test students.tests.test_models --verbosity=2

test-api:
	@echo "$(BLUE)Test de l'API...$(NC)"
	$(MANAGE) test students.tests.test_api --verbosity=2

test-import:
	@echo "$(BLUE)Test de la commande d'import...$(NC)"
	$(MANAGE) test students.tests.test_import_command --verbosity=2

# Coverage
coverage:
	@echo "$(BLUE)Tests avec couverture de code...$(NC)"
	$(VENV_COVERAGE) run --source='palmaresimara' palmaresimara/manage.py test students.tests
	$(VENV_COVERAGE) report
	$(VENV_COVERAGE) html
	@echo "$(GREEN)✓ Rapport de couverture généré dans htmlcov/$(NC)"

# Import d'exemple
import-example:
	@echo "$(BLUE)Création d'un fichier Excel d'exemple...$(NC)"
	$(VENV_PYTHON) create_example_excel.py
	@echo "$(BLUE)Import du fichier d'exemple...$(NC)"
	$(MANAGE) import_excel example_students.xlsx --dry-run
	@echo "$(YELLOW)Import en mode simulation terminé. Pour l'import réel: make import-real$(NC)"

import-real:
	@echo "$(BLUE)Import réel du fichier d'exemple...$(NC)"
	$(MANAGE) import_excel example_students.xlsx
	@echo "$(GREEN)✓ Import terminé$(NC)"

# Collecte des fichiers statiques
collectstatic:
	@echo "$(BLUE)Collecte des fichiers statiques...$(NC)"
	$(MANAGE) collectstatic --noinput

# Nettoyage
clean:
	@echo "$(BLUE)Nettoyage des fichiers temporaires...$(NC)"
ifeq ($(OS),Windows_NT)
	@if exist "palmaresimara\\__pycache__" $(RMDIR) "palmaresimara\\__pycache__" 2>nul || true
	@if exist "palmaresimara\\students\\__pycache__" $(RMDIR) "palmaresimara\\students\\__pycache__" 2>nul || true
	@if exist "htmlcov" $(RMDIR) "htmlcov" 2>nul || true
	@if exist ".coverage" $(RM) ".coverage" 2>nul || true
else
	@$(RMDIR) palmaresimara/__pycache__ 2>/dev/null || true
	@$(RMDIR) palmaresimara/students/__pycache__ 2>/dev/null || true  
	@$(RMDIR) htmlcov 2>/dev/null || true
	@$(RM) .coverage 2>/dev/null || true
endif
	$(PYCACHE_CLEAN)
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

# Réinitialisation de la base de données
reset-db:
	@echo "$(RED)ATTENTION: Cette action va supprimer toutes les données !$(NC)"
	@echo "$(YELLOW)Appuyez sur Ctrl+C pour annuler, ou Entrée pour continuer...$(NC)"
	@$(PAUSE_CMD)
	@$(RM) "$(DB_FILE)" 2>$(NULL) || true
	@echo "$(BLUE)Recréation de la base de données...$(NC)"
	$(MANAGE) migrate
	@echo "$(GREEN)✓ Base de données réinitialisée$(NC)"

# Affichage de l'état du projet
status:
	@echo "$(BLUE)État du projet:$(NC)"
	@echo ""
	@echo "$(GREEN)Environnement virtuel:$(NC)"
	@$(VENV_PYTHON) --version
	@echo ""
	@echo "$(GREEN)Packages installés:$(NC)"
	@$(VENV_PIP) list | $(FIND_CMD) "django\|pandas" || echo "Packages non trouvés"
	@echo ""
	@echo "$(GREEN)Migrations:$(NC)"
	@$(MANAGE) showmigrations --list || echo "Erreur lors de l'affichage des migrations"
	@echo ""
	@echo "$(GREEN)URLs disponibles:$(NC)"
	@echo "  http://127.0.0.1:8000/api/ - API REST"
	@echo "  http://127.0.0.1:8000/admin/ - Interface d'administration"

# Lancement rapide pour développement
dev: setup superuser run

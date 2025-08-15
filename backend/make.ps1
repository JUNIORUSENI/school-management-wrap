# Script PowerShell équivalent au Makefile pour Windows
# Usage: .\make.ps1 <target>

param(
    [Parameter(Position=0)]
    [string]$Target = "help"
)

# Variables
$VENV = "venv"
$VENV_PYTHON = "$VENV\Scripts\python.exe"
$VENV_PIP = "$VENV\Scripts\pip.exe"
$MANAGE = "$VENV_PYTHON palmaresimara\manage.py"

# Couleurs PowerShell
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Blue { Write-ColorOutput Blue $args }
function Write-Green { Write-ColorOutput Green $args }
function Write-Yellow { Write-ColorOutput Yellow $args }
function Write-Red { Write-ColorOutput Red $args }

# Fonctions des tâches
function Show-Help {
    Write-Blue "Palmarès Imara Backend - Commandes disponibles (Windows PowerShell):"
    Write-Host ""
    Write-Green "Setup et installation:"
    Write-Host "  .\make.ps1 install         - Installer les dépendances"
    Write-Host "  .\make.ps1 setup           - Configuration complète du projet"
    Write-Host "  .\make.ps1 migrate         - Exécuter les migrations"
    Write-Host "  .\make.ps1 superuser       - Créer un superutilisateur"
    Write-Host ""
    Write-Green "Développement:"
    Write-Host "  .\make.ps1 run             - Démarrer le serveur de développement"
    Write-Host "  .\make.ps1 shell           - Ouvrir le shell Django"
    Write-Host "  .\make.ps1 dbshell         - Ouvrir le shell de base de données"
    Write-Host ""
    Write-Green "Tests et qualité:"
    Write-Host "  .\make.ps1 test            - Exécuter tous les tests"
    Write-Host "  .\make.ps1 test-models     - Tester uniquement les modèles"
    Write-Host "  .\make.ps1 test-api        - Tester uniquement l'API"
    Write-Host "  .\make.ps1 test-import     - Tester la commande d'import"
    Write-Host "  .\make.ps1 coverage        - Tests avec couverture de code"
    Write-Host ""
    Write-Green "Import et données:"
    Write-Host "  .\make.ps1 import-example  - Créer et importer un fichier Excel d'exemple"
    Write-Host ""
    Write-Green "Maintenance:"
    Write-Host "  .\make.ps1 clean           - Nettoyer les fichiers temporaires"
    Write-Host "  .\make.ps1 reset-db        - Réinitialiser la base de données"
    Write-Host "  .\make.ps1 collectstatic   - Collecter les fichiers statiques"
    Write-Host "  .\make.ps1 status          - Afficher l'état du projet"
}

function Install-Dependencies {
    Write-Blue "Installation des dépendances..."
    & $VENV_PIP install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Green "✓ Dépendances installées"
    }
}

function Setup-Project {
    Install-Dependencies
    Write-Blue "Configuration du projet..."
    
    if (!(Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Green "✓ Fichier .env créé depuis .env.example"
        }
    }
    
    & $VENV_PYTHON palmaresimara\manage.py makemigrations
    & $VENV_PYTHON palmaresimara\manage.py migrate
    
    # Créer des répertoires
    New-Item -ItemType Directory -Force -Path "logs" | Out-Null
    New-Item -ItemType Directory -Force -Path "palmaresimara\media" | Out-Null
    
    Write-Green "✓ Projet configuré"
    Write-Yellow "N'oubliez pas de créer un superutilisateur avec: .\make.ps1 superuser"
}

function Run-Migrations {
    Write-Blue "Exécution des migrations..."
    & $VENV_PYTHON palmaresimara\manage.py makemigrations
    & $VENV_PYTHON palmaresimara\manage.py migrate
    Write-Green "✓ Migrations terminées"
}

function Create-Superuser {
    Write-Blue "Création d'un superutilisateur..."
    & $VENV_PYTHON palmaresimara\manage.py createsuperuser
}

function Start-Server {
    Write-Blue "Démarrage du serveur de développement..."
    & $VENV_PYTHON palmaresimara\manage.py runserver
}

function Open-Shell {
    & $VENV_PYTHON palmaresimara\manage.py shell
}

function Open-DbShell {
    & $VENV_PYTHON palmaresimara\manage.py dbshell
}

function Run-Tests {
    Write-Blue "Exécution de tous les tests..."
    & $VENV_PYTHON palmaresimara\manage.py test students.tests --verbosity=1
}

function Run-TestModels {
    Write-Blue "Test des modèles..."
    & $VENV_PYTHON palmaresimara\manage.py test students.tests.test_models --verbosity=2
}

function Run-TestApi {
    Write-Blue "Test de l'API..."
    & $VENV_PYTHON palmaresimara\manage.py test students.tests.test_api --verbosity=2
}

function Run-TestImport {
    Write-Blue "Test de la commande d'import..."
    & $VENV_PYTHON palmaresimara\manage.py test students.tests.test_import_command --verbosity=2
}

function Run-Coverage {
    Write-Blue "Tests avec couverture de code..."
    & $VENV\Scripts\coverage.exe run --source="palmaresimara" palmaresimara\manage.py test students.tests
    & $VENV\Scripts\coverage.exe report
    & $VENV\Scripts\coverage.exe html
    Write-Green "✓ Rapport de couverture généré dans htmlcov/"
}

function Import-Example {
    Write-Blue "Création d'un fichier Excel d'exemple..."
    & $VENV_PYTHON create_example_excel.py
    Write-Blue "Import du fichier d'exemple..."
    & $VENV_PYTHON palmaresimara\manage.py import_excel example_students.xlsx --dry-run
    Write-Yellow "Import en mode simulation terminé. Pour l'import réel: .\make.ps1 import-real"
}

function Import-Real {
    Write-Blue "Import réel du fichier d'exemple..."
    & $VENV_PYTHON palmaresimara\manage.py import_excel example_students.xlsx
    Write-Green "✓ Import terminé"
}

function Collect-Static {
    Write-Blue "Collecte des fichiers statiques..."
    & $VENV_PYTHON palmaresimara\manage.py collectstatic --noinput
}

function Clean-Files {
    Write-Blue "Nettoyage des fichiers temporaires..."
    
    $paths = @(
        "palmaresimara\__pycache__",
        "palmaresimara\students\__pycache__",
        "htmlcov",
        ".coverage"
    )
    
    foreach ($path in $paths) {
        if (Test-Path $path) {
            Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    # Supprimer tous les fichiers .pyc
    Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    
    Write-Green "✓ Nettoyage terminé"
}

function Reset-Database {
    Write-Red "ATTENTION: Cette action va supprimer toutes les données !"
    $response = Read-Host "Continuer? (y/N)"
    
    if ($response -eq "y") {
        if (Test-Path "palmaresimara\db.sqlite3") {
            Remove-Item "palmaresimara\db.sqlite3" -Force
        }
        Write-Blue "Recréation de la base de données..."
        & $VENV_PYTHON palmaresimara\manage.py migrate
        Write-Green "✓ Base de données réinitialisée"
    } else {
        Write-Host "Opération annulée."
    }
}

function Show-Status {
    Write-Blue "État du projet:"
    Write-Host ""
    Write-Green "Environnement virtuel:"
    & $VENV_PYTHON --version
    Write-Host ""
    Write-Green "Packages installés:"
    & $VENV_PIP list | Select-String "django|pandas" 
    Write-Host ""
    Write-Green "Migrations:"
    & $VENV_PYTHON palmaresimara\manage.py showmigrations --list
    Write-Host ""
    Write-Green "URLs disponibles:"
    Write-Host "  http://127.0.0.1:8000/api/ - API REST"
    Write-Host "  http://127.0.0.1:8000/admin/ - Interface d'administration"
}

# Dispatch des commandes
switch ($Target.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "setup" { Setup-Project }
    "migrate" { Run-Migrations }
    "superuser" { Create-Superuser }
    "run" { Start-Server }
    "shell" { Open-Shell }
    "dbshell" { Open-DbShell }
    "test" { Run-Tests }
    "test-models" { Run-TestModels }
    "test-api" { Run-TestApi }
    "test-import" { Run-TestImport }
    "coverage" { Run-Coverage }
    "import-example" { Import-Example }
    "import-real" { Import-Real }
    "collectstatic" { Collect-Static }
    "clean" { Clean-Files }
    "reset-db" { Reset-Database }
    "status" { Show-Status }
    default {
        Write-Red "Commande inconnue: $Target"
        Write-Host "Utilisez '.\make.ps1 help' pour voir les commandes disponibles."
    }
}

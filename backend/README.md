# Backend - Palmarès Imara

Backend Django REST Framework pour l'application de gestion scolaire Palmarès Imara.

## 🚀 Démarrage rapide

### Prérequis

- Python 3.11+
- PostgreSQL (pour production) ou SQLite (pour développement)
- Git

### Installation

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd SchoolProject/backend
   ```

2. **Créer et activer l'environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration de l'environnement**
   ```bash
   cp .env.example .env
   # Modifier .env avec vos paramètres
   ```

5. **Migrations de la base de données**
   ```bash
   cd palmaresimara
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

7. **Démarrer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

L'API sera disponible sur `http://127.0.0.1:8000/api/`

## 📁 Structure du projet

```
backend/
├── palmaresimara/                 # Projet Django principal
│   ├── palmaresimara/            # Configuration Django
│   │   ├── settings.py           # Paramètres Django
│   │   ├── urls.py              # URLs principales
│   │   └── wsgi.py              # Configuration WSGI
│   ├── students/                 # App principale
│   │   ├── models.py            # Modèles de données
│   │   ├── serializers.py       # Serializers DRF
│   │   ├── views.py             # ViewSets API
│   │   ├── filters.py           # Filtres personnalisés
│   │   ├── admin.py             # Interface d'administration
│   │   ├── urls.py              # URLs de l'app
│   │   ├── management/          # Commandes Django
│   │   │   └── commands/
│   │   │       └── import_excel.py
│   │   └── tests/               # Tests
│   │       ├── test_models.py
│   │       ├── test_api.py
│   │       └── test_import_command.py
│   ├── analytics/               # App d'analyse
│   │   ├── views.py            # Endpoints analytics
│   │   └── urls.py             # URLs analytics
│   ├── uploads/                 # App de gestion des fichiers
│   └── logs/                    # Logs de l'application
├── requirements.txt             # Dépendances Python
├── .env.example                # Template variables d'environnement
└── README.md                   # Cette documentation
```

## 🗄️ Modèles de données

### SchoolYear (Année scolaire)
- `year`: Année au format "YYYY-YYYY" (ex: "2023-2024")
- Unique, ordonné par année décroissante

### Classe 
- `name`: Nom de la classe (ex: "Terminale", "Première")
- Unique

### Section
- `name`: Nom de la section (ex: "S", "ES", "L")
- Unique

### Student (Élève)
- `full_name`: Nom complet (indexé pour recherche)
- Relation one-to-many avec Enrollment

### Enrollment (Inscription)
- Relations ForeignKey vers Student, SchoolYear, Classe, Section
- `percentage`: Moyenne/pourcentage de l'élève
- Contrainte unique: (student, school_year)
- Suppression en cascade si Student supprimé
- Protection si SchoolYear/Classe/Section référencé

## 🔌 API Endpoints

### Authentification
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}

Response: {"token": "d678c28efeb2e54cbfb586f536d7252fe4713651"}
```

### Students (Élèves)
```http
# Liste avec recherche et pagination
GET /api/students/?search=marie&page=1

# Détail avec historique des inscriptions
GET /api/students/1/

# Inscriptions d'un élève
GET /api/students/1/enrollments/

# Création (admin seulement)
POST /api/students/
Authorization: Token d678c28e...
{
  "full_name": "KOUAME Jean Marie"
}
```

### Enrollments (Inscriptions)
```http
# Liste avec filtres
GET /api/enrollments/?year=2023-2024&classe_name=Terminale&search=kouame

# Top étudiants
GET /api/enrollments/top_students/?limit=10&year=2023-2024

# Inscriptions par classe
GET /api/enrollments/by_class/?year=2023-2024&classe=Terminale

# Création (admin seulement)
POST /api/enrollments/
Authorization: Token d678c28e...
{
  "student": 1,
  "school_year": 1,
  "classe": 1,
  "section": 1,
  "percentage": 85.5
}
```

### Analytics
```http
# Statistiques globales
GET /api/analytics/

# Statistiques avec filtres
GET /api/analytics/?year=2023-2024&classe=Terminale

# Statistiques d'une classe spécifique
GET /api/analytics/classes/1/?year=2023-2024
```

### Autres endpoints
```http
# Années scolaires
GET /api/school-years/

# Classes
GET /api/classes/

# Sections  
GET /api/sections/
```

## 📊 Import Excel

### Commande d'import
```bash
# Import avec simulation
python manage.py import_excel fichier.xlsx --dry-run

# Import réel
python manage.py import_excel fichier.xlsx

# Import avec mise à jour des doublons
python manage.py import_excel fichier.xlsx --update

# Import par lots
python manage.py import_excel fichier.xlsx --batch-size=50
```

### Format Excel attendu
Le fichier Excel doit contenir les colonnes suivantes :
- `nom_complet` : Nom complet de l'élève
- `annee` : Année scolaire (ex: "2023-2024")
- `classe` : Classe (ex: "Terminale")
- `section` : Section (ex: "S")
- `pourcentage` : Moyenne (0-100)

### Exemples de colonnes acceptées
La commande accepte plusieurs variantes de noms de colonnes :
- Nom : `nom_complet`, `nom`, `full_name`
- Année : `annee`, `année`, `year`
- Pourcentage : `pourcentage`, `moyenne`, `percentage`

## 🧪 Tests

### Exécuter tous les tests
```bash
python manage.py test
```

### Tests par catégorie
```bash
# Tests des modèles
python manage.py test students.tests.test_models

# Tests des APIs
python manage.py test students.tests.test_api

# Tests de la commande d'import
python manage.py test students.tests.test_import_command
```

### Tests avec couverture
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Génère un rapport HTML
```

## 👨‍💼 Interface d'administration

Accédez à l'interface d'administration Django : `http://127.0.0.1:8000/admin/`

### Fonctionnalités disponibles :
- ✅ Gestion complète des étudiants avec inline des inscriptions
- ✅ Recherche full-text sur les noms d'étudiants
- ✅ Filtres par année, classe, section
- ✅ Affichage coloré des pourcentages selon la performance
- ✅ Export CSV avec action d'administration
- ✅ Pagination et optimisation des requêtes

## 🔧 Configuration

### Variables d'environnement (.env)
```bash
# Base de données
POSTGRES_DB=palmaresimara_db
POSTGRES_USER=palmaresimara_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Django
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS (pour frontend)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Base de données

#### SQLite (développement - par défaut)
Aucune configuration supplémentaire nécessaire.

#### PostgreSQL (production)
```bash
# Installation PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Création de la base
sudo -u postgres createdb palmaresimara_db
sudo -u postgres createuser palmaresimara_user
sudo -u postgres psql
ALTER USER palmaresimara_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE palmaresimara_db TO palmaresimara_user;
```

## 🚀 Déploiement

### Préparation pour la production
```bash
# Variables d'environnement de production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Collecte des fichiers statiques
python manage.py collectstatic

# Migration en production
python manage.py migrate --settings=palmaresimara.settings.production
```

### Serveur Gunicorn
```bash
# Installation
pip install gunicorn

# Démarrage
gunicorn palmaresimara.wsgi:application --bind 0.0.0.0:8000
```

## 📝 Logs

Les logs sont configurés pour écrire dans `logs/backend.log` avec les niveaux :
- INFO : Actions importantes (authentification, imports)
- ERROR : Erreurs d'application
- DEBUG : Informations de débogage (développement seulement)

## 🔒 Sécurité

### Authentification
- Token-based authentication (DRF)
- Permissions : lecture publique, écriture admin seulement
- Session-based auth pour l'interface d'administration

### CORS
- Configuré pour autoriser le frontend Next.js
- Origins configurables via variables d'environnement

### Validation
- Validation des pourcentages (0-100)
- Contraintes d'unicité en base
- Sanitisation des entrées utilisateur

## 🐛 Résolution de problèmes

### Problèmes courants

1. **Erreur "ModuleNotFoundError"**
   ```bash
   # Vérifier l'activation de l'environnement virtuel
   which python  # Linux/Mac
   where python  # Windows
   ```

2. **Erreur de base de données**
   ```bash
   # Reset des migrations
   python manage.py migrate --fake students zero
   python manage.py migrate
   ```

3. **Import Excel qui échoue**
   ```bash
   # Vérifier le format du fichier et les colonnes
   python manage.py import_excel fichier.xlsx --dry-run -v 2
   ```

### Support

Pour tout problème :
1. Vérifiez les logs dans `logs/backend.log`
2. Utilisez le mode verbose : `python manage.py <commande> -v 2`
3. Consultez la documentation Django REST Framework

## 📚 Technologies utilisées

- **Django 5.2** : Framework web Python
- **Django REST Framework 3.16** : API REST
- **pandas** : Traitement des fichiers Excel  
- **openpyxl** : Lecture des fichiers Excel
- **django-filter** : Filtrage avancé des APIs
- **django-cors-headers** : Gestion CORS
- **python-dotenv** : Variables d'environnement

## 🤝 Contribution

1. Créer une branche feature : `git checkout -b feature/nom-feature`
2. Commiter les changements : `git commit -m "Description"`
3. Exécuter les tests : `python manage.py test`
4. Push et créer une Pull Request

---

## 📞 Contact

Pour toute question technique, consultez les logs ou créez une issue dans le repository.

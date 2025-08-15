import os
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
import pandas as pd
import openpyxl
from students.models import Student, SchoolYear, Classe, Section, Enrollment

# Configuration du logging
logger = logging.getLogger('students')


class Command(BaseCommand):
    help = 'Import des données Excel vers la base de données'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Chemin vers le fichier Excel à importer'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Exécute une simulation sans sauvegarder en base'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Met à jour les enregistrements existants'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Taille des lots pour l\'import (défaut: 100)'
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        dry_run = options['dry_run']
        update_existing = options['update']
        batch_size = options['batch_size']

        # Vérifier l'existence du fichier
        if not os.path.exists(excel_file):
            raise CommandError(f'Le fichier {excel_file} n\'existe pas')

        self.stdout.write(self.style.SUCCESS(f'Démarrage de l\'import depuis {excel_file}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODE SIMULATION ACTIVÉ - Aucune donnée ne sera sauvegardée'))

        try:
            # Lire le fichier Excel
            df = self._read_excel_file(excel_file)
            
            # Valider les données
            validated_data = self._validate_data(df)
            
            # Importer les données
            result = self._import_data(validated_data, dry_run, update_existing, batch_size)
            
            # Afficher les résultats
            self._display_results(result)
            
        except Exception as e:
            logger.error(f'Erreur lors de l\'import: {str(e)}', exc_info=True)
            raise CommandError(f'Erreur lors de l\'import: {str(e)}')

    def _read_excel_file(self, excel_file):
        """Lit le fichier Excel et retourne un DataFrame pandas"""
        self.stdout.write('Lecture du fichier Excel...')
        
        try:
            # Essayer de lire avec différents moteurs
            try:
                df = pd.read_excel(excel_file, engine='openpyxl')
            except:
                df = pd.read_excel(excel_file, engine='xlrd')
            
            self.stdout.write(f'Fichier lu avec succès: {len(df)} lignes trouvées')
            return df
            
        except Exception as e:
            raise CommandError(f'Erreur lors de la lecture du fichier Excel: {str(e)}')

    def _validate_data(self, df):
        """Valide les données du DataFrame"""
        self.stdout.write('Validation des données...')
        
        # Colonnes requises (adaptation selon votre format Excel)
        required_columns = ['nom_complet', 'annee', 'classe', 'section', 'pourcentage']
        
        # Vérifier la présence des colonnes
        missing_columns = []
        for col in required_columns:
            # Chercher la colonne avec différentes variantes
            column_found = False
            for df_col in df.columns:
                if any(variant in df_col.lower() for variant in [
                    col.replace('_', ' '), col, 
                    'nom' if col == 'nom_complet' else col,
                    'année' if col == 'annee' else col,
                    'pourcentage' if col == 'pourcentage' else 'moyenne'
                ]):
                    # Renommer la colonne pour standardiser
                    df.rename(columns={df_col: col}, inplace=True)
                    column_found = True
                    break
            
            if not column_found:
                missing_columns.append(col)
        
        if missing_columns:
            raise CommandError(f'Colonnes manquantes: {", ".join(missing_columns)}')
        
        # Nettoyer et valider les données
        validated_rows = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Nettoyage des données
                nom_complet = str(row['nom_complet']).strip()
                annee = str(row['annee']).strip()
                classe = str(row['classe']).strip()
                section = str(row['section']).strip()
                
                # Validation du pourcentage
                try:
                    pourcentage = float(row['pourcentage'])
                    if pourcentage < 0 or pourcentage > 100:
                        raise ValueError(f'Pourcentage invalide: {pourcentage}')
                except (ValueError, TypeError):
                    raise ValueError(f'Pourcentage invalide: {row["pourcentage"]}')
                
                # Validation des champs requis
                if not nom_complet or nom_complet == 'nan':
                    raise ValueError('Nom complet manquant')
                if not annee or annee == 'nan':
                    raise ValueError('Année manquante')
                if not classe or classe == 'nan':
                    raise ValueError('Classe manquante')
                if not section or section == 'nan':
                    raise ValueError('Section manquante')
                
                validated_rows.append({
                    'nom_complet': nom_complet,
                    'annee': annee,
                    'classe': classe,
                    'section': section,
                    'pourcentage': pourcentage,
                    'ligne': index + 2  # +2 car pandas commence à 0 et il y a l'en-tête
                })
                
            except Exception as e:
                errors.append(f'Ligne {index + 2}: {str(e)}')
        
        if errors:
            self.stdout.write(self.style.ERROR(f'{len(errors)} erreurs de validation trouvées:'))
            for error in errors[:10]:  # Afficher seulement les 10 premières erreurs
                self.stdout.write(f'  - {error}')
            if len(errors) > 10:
                self.stdout.write(f'  ... et {len(errors) - 10} autres erreurs')
            
            if len(errors) >= len(validated_rows):
                raise CommandError('Trop d\'erreurs de validation, import annulé')
        
        self.stdout.write(f'Validation terminée: {len(validated_rows)} lignes valides, {len(errors)} erreurs')
        return validated_rows

    def _import_data(self, validated_data, dry_run, update_existing, batch_size):
        """Importe les données validées en base"""
        self.stdout.write('Import des données...')
        
        result = {
            'students_created': 0,
            'students_updated': 0,
            'school_years_created': 0,
            'classes_created': 0,
            'sections_created': 0,
            'enrollments_created': 0,
            'enrollments_updated': 0,
            'duplicates_found': 0,
            'errors': []
        }
        
        if dry_run:
            # Mode simulation - on fait juste les vérifications
            for data in validated_data:
                self._simulate_import_row(data, result)
            return result
        
        # Import réel avec transaction
        with transaction.atomic():
            processed = 0
            for data in validated_data:
                try:
                    self._import_row(data, result, update_existing)
                    processed += 1
                    
                    if processed % batch_size == 0:
                        self.stdout.write(f'Traité: {processed}/{len(validated_data)} lignes')
                        
                except Exception as e:
                    error_msg = f'Ligne {data["ligne"]}: {str(e)}'
                    result['errors'].append(error_msg)
                    logger.error(error_msg)
            
            self.stdout.write(f'Import terminé: {processed} lignes traitées')
        
        return result

    def _simulate_import_row(self, data, result):
        """Simule l'import d'une ligne (mode dry-run)"""
        # Vérifier si l'étudiant existe
        if not Student.objects.filter(full_name=data['nom_complet']).exists():
            result['students_created'] += 1
        
        # Vérifier si l'année scolaire existe
        if not SchoolYear.objects.filter(year=data['annee']).exists():
            result['school_years_created'] += 1
        
        # Vérifier si la classe existe
        if not Classe.objects.filter(name=data['classe']).exists():
            result['classes_created'] += 1
        
        # Vérifier si la section existe
        if not Section.objects.filter(name=data['section']).exists():
            result['sections_created'] += 1
        
        # Vérifier les doublons d'inscription
        try:
            student = Student.objects.get(full_name=data['nom_complet'])
            school_year = SchoolYear.objects.get(year=data['annee'])
            if Enrollment.objects.filter(student=student, school_year=school_year).exists():
                result['duplicates_found'] += 1
                result['enrollments_updated'] += 1
            else:
                result['enrollments_created'] += 1
        except:
            result['enrollments_created'] += 1

    def _import_row(self, data, result, update_existing):
        """Importe une ligne de données"""
        # Créer ou récupérer l'étudiant
        student, created = Student.objects.get_or_create(
            full_name=data['nom_complet']
        )
        if created:
            result['students_created'] += 1
        
        # Créer ou récupérer l'année scolaire
        school_year, created = SchoolYear.objects.get_or_create(
            year=data['annee']
        )
        if created:
            result['school_years_created'] += 1
        
        # Créer ou récupérer la classe
        classe, created = Classe.objects.get_or_create(
            name=data['classe']
        )
        if created:
            result['classes_created'] += 1
        
        # Créer ou récupérer la section
        section, created = Section.objects.get_or_create(
            name=data['section']
        )
        if created:
            result['sections_created'] += 1
        
        # Créer ou mettre à jour l'inscription
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            school_year=school_year,
            defaults={
                'classe': classe,
                'section': section,
                'percentage': data['pourcentage']
            }
        )
        
        if created:
            result['enrollments_created'] += 1
        else:
            if update_existing:
                # Mettre à jour les données existantes
                enrollment.classe = classe
                enrollment.section = section
                enrollment.percentage = data['pourcentage']
                enrollment.save()
                result['enrollments_updated'] += 1
            else:
                result['duplicates_found'] += 1

    def _display_results(self, result):
        """Affiche les résultats de l'import"""
        self.stdout.write(self.style.SUCCESS('\n=== RÉSULTATS DE L\'IMPORT ==='))
        
        self.stdout.write(f'Étudiants créés: {result["students_created"]}')
        self.stdout.write(f'Étudiants mis à jour: {result["students_updated"]}')
        self.stdout.write(f'Années scolaires créées: {result["school_years_created"]}')
        self.stdout.write(f'Classes créées: {result["classes_created"]}')
        self.stdout.write(f'Sections créées: {result["sections_created"]}')
        self.stdout.write(f'Inscriptions créées: {result["enrollments_created"]}')
        self.stdout.write(f'Inscriptions mises à jour: {result["enrollments_updated"]}')
        
        if result['duplicates_found'] > 0:
            self.stdout.write(self.style.WARNING(f'Doublons trouvés: {result["duplicates_found"]}'))
        
        if result['errors']:
            self.stdout.write(self.style.ERROR(f'\n{len(result["errors"])} erreurs:'))
            for error in result['errors'][:5]:
                self.stdout.write(f'  - {error}')
            if len(result['errors']) > 5:
                self.stdout.write(f'  ... et {len(result["errors"]) - 5} autres erreurs')
        
        # Log vers un fichier
        log_file = f'import_log_{timezone.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f'Import effectué le {timezone.now()}\n')
            f.write(f'Étudiants créés: {result["students_created"]}\n')
            f.write(f'Inscriptions créées: {result["enrollments_created"]}\n')
            f.write(f'Erreurs: {len(result["errors"])}\n')
            if result['errors']:
                f.write('\nDétail des erreurs:\n')
                for error in result['errors']:
                    f.write(f'{error}\n')
        
        self.stdout.write(f'Log détaillé sauvegardé dans: {log_file}')
        self.stdout.write(self.style.SUCCESS('\nImport terminé avec succès!'))

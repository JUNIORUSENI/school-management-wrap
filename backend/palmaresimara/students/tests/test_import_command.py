import os
import tempfile
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
import pandas as pd
from students.models import Student, SchoolYear, Classe, Section, Enrollment


class ImportExcelCommandTest(TestCase):
    """Tests pour la commande import_excel"""

    def setUp(self):
        """Préparation des données de test"""
        # Créer un fichier Excel temporaire pour les tests
        self.test_data = [
            {"nom_complet": "KOUAME Jean Marie", "annee": "2023-2024", "classe": "Terminale", "section": "S", "pourcentage": 85.5},
            {"nom_complet": "BAMBA Marie Claire", "annee": "2023-2024", "classe": "Terminale", "section": "ES", "pourcentage": 92.0},
            {"nom_complet": "TRAORE Salimata", "annee": "2022-2023", "classe": "Première", "section": "L", "pourcentage": 78.5},
        ]
        
        # Créer un fichier temporaire
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df = pd.DataFrame(self.test_data)
        df.to_excel(self.temp_file.name, index=False, engine='openpyxl')
        self.temp_file.close()

    def tearDown(self):
        """Nettoyage après les tests"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_import_excel_dry_run(self):
        """Test import en mode simulation"""
        # Vérifier qu'il n'y a aucune donnée au début
        self.assertEqual(Student.objects.count(), 0)
        self.assertEqual(Enrollment.objects.count(), 0)
        
        # Exécuter la commande en mode dry-run
        call_command('import_excel', self.temp_file.name, '--dry-run')
        
        # Vérifier qu'aucune donnée n'a été créée
        self.assertEqual(Student.objects.count(), 0)
        self.assertEqual(Enrollment.objects.count(), 0)

    def test_import_excel_real_import(self):
        """Test import réel"""
        # Vérifier qu'il n'y a aucune donnée au début
        self.assertEqual(Student.objects.count(), 0)
        self.assertEqual(Enrollment.objects.count(), 0)
        
        # Exécuter la commande
        call_command('import_excel', self.temp_file.name)
        
        # Vérifier que les données ont été créées
        self.assertEqual(Student.objects.count(), 3)
        self.assertEqual(SchoolYear.objects.count(), 2)  # 2023-2024 et 2022-2023
        self.assertEqual(Classe.objects.count(), 2)      # Terminale et Première
        self.assertEqual(Section.objects.count(), 3)     # S, ES, L
        self.assertEqual(Enrollment.objects.count(), 3)
        
        # Vérifier quelques données spécifiques
        student = Student.objects.get(full_name="KOUAME Jean Marie")
        enrollment = student.enrollments.first()
        self.assertEqual(enrollment.percentage, 85.5)
        self.assertEqual(enrollment.school_year.year, "2023-2024")

    def test_import_excel_duplicate_handling(self):
        """Test gestion des doublons"""
        # Premier import
        call_command('import_excel', self.temp_file.name)
        initial_count = Enrollment.objects.count()
        
        # Deuxième import (sans --update)
        call_command('import_excel', self.temp_file.name)
        
        # Le nombre d'inscriptions ne devrait pas changer
        self.assertEqual(Enrollment.objects.count(), initial_count)

    def test_import_excel_with_update(self):
        """Test import avec mise à jour"""
        # Premier import
        call_command('import_excel', self.temp_file.name)
        
        # Modifier les données pour le test de mise à jour
        modified_data = [
            {"nom_complet": "KOUAME Jean Marie", "annee": "2023-2024", "classe": "Terminale", "section": "S", "pourcentage": 90.0},  # Changé de 85.5 à 90.0
        ]
        
        # Créer un nouveau fichier avec données modifiées
        temp_file2 = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df = pd.DataFrame(modified_data)
        df.to_excel(temp_file2.name, index=False, engine='openpyxl')
        temp_file2.close()
        
        try:
            # Import avec mise à jour
            call_command('import_excel', temp_file2.name, '--update')
            
            # Vérifier la mise à jour
            enrollment = Enrollment.objects.get(
                student__full_name="KOUAME Jean Marie",
                school_year__year="2023-2024"
            )
            self.assertEqual(enrollment.percentage, 90.0)
            
        finally:
            os.unlink(temp_file2.name)

    def test_import_excel_invalid_file(self):
        """Test avec fichier inexistant"""
        with self.assertRaises(CommandError):
            call_command('import_excel', 'nonexistent_file.xlsx')

    def test_import_excel_invalid_data(self):
        """Test avec données invalides"""
        # Créer un fichier avec données invalides
        invalid_data = [
            {"nom_complet": "KOUAME Jean Marie", "annee": "2023-2024", "classe": "Terminale", "section": "S", "pourcentage": 150.0},  # Pourcentage invalide
            {"nom_complet": "", "annee": "2023-2024", "classe": "Terminale", "section": "S", "pourcentage": 85.0},  # Nom manquant
        ]
        
        temp_file_invalid = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df = pd.DataFrame(invalid_data)
        df.to_excel(temp_file_invalid.name, index=False, engine='openpyxl')
        temp_file_invalid.close()
        
        try:
            # L'import devrait échouer avec trop d'erreurs de validation
            with self.assertRaises(CommandError):
                call_command('import_excel', temp_file_invalid.name)
            
            # Vérifier qu'aucune donnée n'a été importée
            self.assertEqual(Student.objects.count(), 0)
            
        finally:
            os.unlink(temp_file_invalid.name)

    def test_import_excel_missing_columns(self):
        """Test avec colonnes manquantes"""
        # Créer un fichier avec colonnes manquantes
        incomplete_data = [
            {"nom_complet": "KOUAME Jean Marie", "annee": "2023-2024"},  # Manque classe, section, pourcentage
        ]
        
        temp_file_incomplete = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df = pd.DataFrame(incomplete_data)
        df.to_excel(temp_file_incomplete.name, index=False, engine='openpyxl')
        temp_file_incomplete.close()
        
        try:
            with self.assertRaises(CommandError):
                call_command('import_excel', temp_file_incomplete.name)
                
        finally:
            os.unlink(temp_file_incomplete.name)

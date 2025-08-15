from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from students.models import Student, SchoolYear, Classe, Section, Enrollment


class SchoolYearModelTest(TestCase):
    """Tests pour le modèle SchoolYear"""

    def test_create_school_year(self):
        """Test de création d'une année scolaire"""
        year = SchoolYear.objects.create(year="2023-2024")
        self.assertEqual(str(year), "2023-2024")
        self.assertEqual(year.year, "2023-2024")

    def test_school_year_unique_constraint(self):
        """Test de la contrainte d'unicité sur l'année"""
        SchoolYear.objects.create(year="2023-2024")
        with self.assertRaises(IntegrityError):
            SchoolYear.objects.create(year="2023-2024")

    def test_school_year_ordering(self):
        """Test de l'ordre des années scolaires"""
        year1 = SchoolYear.objects.create(year="2022-2023")
        year2 = SchoolYear.objects.create(year="2023-2024")
        
        years = list(SchoolYear.objects.all())
        self.assertEqual(years[0], year2)  # Plus récent en premier
        self.assertEqual(years[1], year1)


class ClasseModelTest(TestCase):
    """Tests pour le modèle Classe"""

    def test_create_classe(self):
        """Test de création d'une classe"""
        classe = Classe.objects.create(name="Terminale")
        self.assertEqual(str(classe), "Terminale")
        self.assertEqual(classe.name, "Terminale")

    def test_classe_unique_constraint(self):
        """Test de la contrainte d'unicité sur le nom de classe"""
        Classe.objects.create(name="Terminale")
        with self.assertRaises(IntegrityError):
            Classe.objects.create(name="Terminale")


class SectionModelTest(TestCase):
    """Tests pour le modèle Section"""

    def test_create_section(self):
        """Test de création d'une section"""
        section = Section.objects.create(name="S")
        self.assertEqual(str(section), "S")
        self.assertEqual(section.name, "S")

    def test_section_unique_constraint(self):
        """Test de la contrainte d'unicité sur le nom de section"""
        Section.objects.create(name="S")
        with self.assertRaises(IntegrityError):
            Section.objects.create(name="S")


class StudentModelTest(TestCase):
    """Tests pour le modèle Student"""

    def test_create_student(self):
        """Test de création d'un étudiant"""
        student = Student.objects.create(full_name="KOUAME Jean Marie")
        self.assertEqual(str(student), "KOUAME Jean Marie")
        self.assertEqual(student.full_name, "KOUAME Jean Marie")

    def test_student_full_name_index(self):
        """Test que l'index sur full_name fonctionne"""
        students = [
            Student.objects.create(full_name="ADOU Marie"),
            Student.objects.create(full_name="BAMBA Jean"),
            Student.objects.create(full_name="COULIBALY Fatou")
        ]
        
        # Test recherche avec icontains
        found = Student.objects.filter(full_name__icontains="marie")
        self.assertEqual(found.count(), 1)
        self.assertEqual(found.first(), students[0])


class EnrollmentModelTest(TestCase):
    """Tests pour le modèle Enrollment"""

    def setUp(self):
        """Préparation des données de test"""
        self.student = Student.objects.create(full_name="TRAORE Salimata")
        self.school_year = SchoolYear.objects.create(year="2023-2024")
        self.classe = Classe.objects.create(name="Terminale")
        self.section = Section.objects.create(name="S")

    def test_create_enrollment(self):
        """Test de création d'une inscription"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.5
        )
        
        expected_str = f"{self.student.full_name} - {self.school_year.year} ({self.classe.name} {self.section.name})"
        self.assertEqual(str(enrollment), expected_str)
        self.assertEqual(enrollment.percentage, 85.5)

    def test_enrollment_unique_together_constraint(self):
        """Test de la contrainte unique_together (student, school_year)"""
        Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.5
        )
        
        # Même étudiant, même année -> doit échouer
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                school_year=self.school_year,
                classe=self.classe,
                section=self.section,
                percentage=90.0
            )

    def test_enrollment_different_years_allowed(self):
        """Test qu'un même étudiant peut s'inscrire sur plusieurs années"""
        year1 = SchoolYear.objects.create(year="2022-2023")
        year2 = self.school_year  # Utilise l'année créée dans setUp
        
        enrollment1 = Enrollment.objects.create(
            student=self.student,
            school_year=year1,
            classe=self.classe,
            section=self.section,
            percentage=80.0
        )
        
        enrollment2 = Enrollment.objects.create(
            student=self.student,
            school_year=year2,
            classe=self.classe,
            section=self.section,
            percentage=85.0
        )
        
        self.assertEqual(Enrollment.objects.count(), 2)
        self.assertNotEqual(enrollment1, enrollment2)

    def test_enrollment_cascade_delete_student(self):
        """Test que la suppression d'un étudiant supprime ses inscriptions"""
        Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.5
        )
        
        self.assertEqual(Enrollment.objects.count(), 1)
        self.student.delete()
        self.assertEqual(Enrollment.objects.count(), 0)

    def test_enrollment_protect_delete_school_year(self):
        """Test que la suppression d'une année est protégée si des inscriptions existent"""
        Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.5
        )
        
        # Ne devrait pas pouvoir supprimer l'année
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            self.school_year.delete()

    def test_class_section_property(self):
        """Test de la propriété class_section"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.5
        )
        
        expected = f"{self.classe.name} {self.section.name}"
        self.assertEqual(enrollment.class_section, expected)

    def test_enrollment_ordering(self):
        """Test de l'ordre des inscriptions"""
        student2 = Student.objects.create(full_name="BAMBA Jean")
        
        enrollment1 = Enrollment.objects.create(
            student=self.student,  # TRAORE Salimata
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=75.0
        )
        
        enrollment2 = Enrollment.objects.create(
            student=student2,  # BAMBA Jean
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.0
        )
        
        enrollments = list(Enrollment.objects.all())
        # Ordre: percentage DESC, puis full_name ASC
        self.assertEqual(enrollments[0], enrollment2)  # 85.0 > 75.0
        self.assertEqual(enrollments[1], enrollment1)


class ModelRelationshipsTest(TestCase):
    """Tests pour les relations entre modèles"""

    def setUp(self):
        self.student = Student.objects.create(full_name="Test Student")
        self.school_year = SchoolYear.objects.create(year="2023-2024")
        self.classe = Classe.objects.create(name="Terminale")
        self.section = Section.objects.create(name="S")

    def test_student_enrollments_relationship(self):
        """Test de la relation student -> enrollments"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.0
        )
        
        self.assertEqual(self.student.enrollments.count(), 1)
        self.assertEqual(self.student.enrollments.first(), enrollment)

    def test_school_year_enrollments_relationship(self):
        """Test de la relation school_year -> enrollments"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.0
        )
        
        self.assertEqual(self.school_year.enrollments.count(), 1)
        self.assertEqual(self.school_year.enrollments.first(), enrollment)

    def test_classe_enrollments_relationship(self):
        """Test de la relation classe -> enrollments"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.0
        )
        
        self.assertEqual(self.classe.enrollments.count(), 1)
        self.assertEqual(self.classe.enrollments.first(), enrollment)

    def test_section_enrollments_relationship(self):
        """Test de la relation section -> enrollments"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.0
        )
        
        self.assertEqual(self.section.enrollments.count(), 1)
        self.assertEqual(self.section.enrollments.first(), enrollment)

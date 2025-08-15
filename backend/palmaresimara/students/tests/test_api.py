from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from students.models import Student, SchoolYear, Classe, Section, Enrollment


class APITestCase(TestCase):
    """Classe de base pour les tests d'API"""

    def setUp(self):
        self.client = APIClient()
        
        # Créer un utilisateur admin
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.admin_token = Token.objects.create(user=self.admin_user)
        
        # Créer un utilisateur normal
        self.normal_user = User.objects.create_user(
            username='user',
            password='testpass123'
        )
        self.user_token = Token.objects.create(user=self.normal_user)
        
        # Créer des données de test
        self.school_year = SchoolYear.objects.create(year="2023-2024")
        self.classe = Classe.objects.create(name="Terminale")
        self.section = Section.objects.create(name="S")
        self.student = Student.objects.create(full_name="KOUAME Jean Marie")
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section,
            percentage=85.5
        )

    def authenticate_admin(self):
        """Authentifier avec le token admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')

    def authenticate_user(self):
        """Authentifier avec le token utilisateur normal"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')

    def unauthenticated(self):
        """Supprimer l'authentification"""
        self.client.credentials()


class SchoolYearAPITest(APITestCase):
    """Tests pour l'API des années scolaires"""

    def test_list_school_years_unauthenticated(self):
        """Test lecture des années scolaires sans authentification"""
        url = reverse('schoolyear-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_school_year_admin(self):
        """Test création d'année scolaire par admin"""
        self.authenticate_admin()
        url = reverse('schoolyear-list')
        data = {'year': '2024-2025'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SchoolYear.objects.count(), 2)

    def test_create_school_year_user_forbidden(self):
        """Test que l'utilisateur normal ne peut pas créer d'année"""
        self.authenticate_user()
        url = reverse('schoolyear-list')
        data = {'year': '2024-2025'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_school_year_unauthenticated_forbidden(self):
        """Test que l'utilisateur non authentifié ne peut pas créer d'année"""
        url = reverse('schoolyear-list')
        data = {'year': '2024-2025'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StudentAPITest(APITestCase):
    """Tests pour l'API des étudiants"""

    def test_list_students(self):
        """Test liste des étudiants"""
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], "KOUAME Jean Marie")

    def test_search_students(self):
        """Test recherche d'étudiants"""
        # Créer plus d'étudiants
        Student.objects.create(full_name="BAMBA Marie Claire")
        Student.objects.create(full_name="TRAORE Salimata")
        
        url = reverse('student-list')
        response = self.client.get(url, {'search': 'marie'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_student_admin(self):
        """Test création d'étudiant par admin"""
        self.authenticate_admin()
        url = reverse('student-list')
        data = {'full_name': 'OUATTARA Sekou'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 2)

    def test_student_detail_with_enrollments(self):
        """Test détail d'un étudiant avec ses inscriptions"""
        url = reverse('student-detail', kwargs={'pk': self.student.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], "KOUAME Jean Marie")
        self.assertEqual(len(response.data['enrollments']), 1)
        self.assertEqual(response.data['total_enrollments'], 1)
        self.assertEqual(response.data['average_percentage'], 85.5)


class EnrollmentAPITest(APITestCase):
    """Tests pour l'API des inscriptions"""

    def test_list_enrollments(self):
        """Test liste des inscriptions"""
        url = reverse('enrollment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_enrollments_by_year(self):
        """Test filtrage des inscriptions par année"""
        # Créer une inscription pour une autre année
        year2 = SchoolYear.objects.create(year="2022-2023")
        student2 = Student.objects.create(full_name="BAMBA Jean")
        Enrollment.objects.create(
            student=student2,
            school_year=year2,
            classe=self.classe,
            section=self.section,
            percentage=75.0
        )
        
        url = reverse('enrollment-list')
        response = self.client.get(url, {'year': '2023-2024'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_enrollments_by_student_name(self):
        """Test recherche d'inscriptions par nom d'étudiant"""
        url = reverse('enrollment-list')
        response = self.client.get(url, {'search': 'kouame'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_enrollment_admin(self):
        """Test création d'inscription par admin"""
        self.authenticate_admin()
        student2 = Student.objects.create(full_name="TRAORE Aminata")
        
        url = reverse('enrollment-list')
        data = {
            'student': student2.pk,
            'school_year': self.school_year.pk,
            'classe': self.classe.pk,
            'section': self.section.pk,
            'percentage': 90.5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 2)

    def test_create_duplicate_enrollment_validation(self):
        """Test validation des doublons d'inscription"""
        self.authenticate_admin()
        
        url = reverse('enrollment-list')
        data = {
            'student': self.student.pk,
            'school_year': self.school_year.pk,  # Même étudiant, même année
            'classe': self.classe.pk,
            'section': self.section.pk,
            'percentage': 90.5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_percentage_validation(self):
        """Test validation des pourcentages invalides"""
        self.authenticate_admin()
        student2 = Student.objects.create(full_name="Test Student")
        
        url = reverse('enrollment-list')
        data = {
            'student': student2.pk,
            'school_year': self.school_year.pk,
            'classe': self.classe.pk,
            'section': self.section.pk,
            'percentage': 150.0  # Invalide
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_top_students_endpoint(self):
        """Test endpoint top students"""
        # Créer plus d'inscriptions
        for i, percentage in enumerate([95.0, 88.0, 76.0], 1):
            student = Student.objects.create(full_name=f"Student {i}")
            Enrollment.objects.create(
                student=student,
                school_year=self.school_year,
                classe=self.classe,
                section=self.section,
                percentage=percentage
            )
        
        url = reverse('enrollment-top-students')
        response = self.client.get(url, {'limit': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Vérifier l'ordre (du plus haut au plus bas)
        self.assertEqual(response.data[0]['percentage'], 95.0)
        self.assertEqual(response.data[1]['percentage'], 88.0)


class AnalyticsAPITest(APITestCase):
    """Tests pour l'API d'analytics"""

    def setUp(self):
        super().setUp()
        # Créer plus de données pour les analytics
        self.student2 = Student.objects.create(full_name="BAMBA Marie")
        self.section2 = Section.objects.create(name="ES")
        self.enrollment2 = Enrollment.objects.create(
            student=self.student2,
            school_year=self.school_year,
            classe=self.classe,
            section=self.section2,
            percentage=92.0
        )

    def test_analytics_unauthenticated(self):
        """Test accès aux analytics sans authentification"""
        url = reverse('analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analytics_data_structure(self):
        """Test structure des données analytics"""
        url = reverse('analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la structure de la réponse
        self.assertIn('general_stats', response.data)
        self.assertIn('entity_counts', response.data)
        self.assertIn('top_students', response.data)
        self.assertIn('stats_by_class', response.data)
        self.assertIn('stats_by_section', response.data)
        self.assertIn('stats_by_year', response.data)
        self.assertIn('grade_distribution', response.data)

    def test_analytics_calculations(self):
        """Test calculs des analytics"""
        url = reverse('analytics')
        response = self.client.get(url)
        
        general_stats = response.data['general_stats']
        self.assertEqual(general_stats['total_enrollments'], 2)
        self.assertAlmostEqual(general_stats['average_percentage'], 88.75)  # (85.5 + 92.0) / 2
        self.assertEqual(general_stats['max_percentage'], 92.0)
        self.assertEqual(general_stats['min_percentage'], 85.5)

    def test_analytics_filter_by_year(self):
        """Test filtrage des analytics par année"""
        url = reverse('analytics')
        response = self.client.get(url, {'year': '2023-2024'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['filters_applied']['year'], '2023-2024')


class AuthenticationTest(APITestCase):
    """Tests d'authentification"""

    def test_login_endpoint(self):
        """Test endpoint de login"""
        url = reverse('api_token_auth')
        data = {
            'username': 'admin',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_invalid_credentials(self):
        """Test login avec des identifiants invalides"""
        url = reverse('api_token_auth')
        data = {
            'username': 'admin',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_authentication_works(self):
        """Test que l'authentification par token fonctionne"""
        self.authenticate_admin()
        url = reverse('student-list')
        data = {'full_name': 'New Student'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PaginationTest(APITestCase):
    """Tests de pagination"""

    def setUp(self):
        super().setUp()
        # Créer beaucoup d'étudiants pour tester la pagination
        for i in range(30):
            Student.objects.create(full_name=f"Student {i:02d}")

    def test_pagination_students_list(self):
        """Test pagination de la liste des étudiants"""
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la structure de pagination
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Vérifier la taille de page (25 par défaut)
        self.assertEqual(len(response.data['results']), 25)
        self.assertEqual(response.data['count'], 31)  # 30 créés + 1 dans setUp

    def test_pagination_next_page(self):
        """Test pagination page suivante"""
        url = reverse('student-list')
        response = self.client.get(url, {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 6)  # Reste 6 sur la page 2

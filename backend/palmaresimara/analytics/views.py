from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count, Max, Min, Q
from students.models import Enrollment, Student, SchoolYear, Classe, Section
from students.views import IsAdminOrReadOnly


class AnalyticsView(APIView):
    """
    Endpoint pour les analyses et statistiques
    """
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request):
        """
        Retourne des statistiques globales sur les données
        """
        try:
            year_filter = request.query_params.get('year')
            classe_filter = request.query_params.get('classe')
            section_filter = request.query_params.get('section')
            
            # Base queryset
            enrollments = Enrollment.objects.select_related(
                'student', 'school_year', 'classe', 'section'
            )
            
            # Appliquer les filtres
            if year_filter:
                enrollments = enrollments.filter(school_year__year=year_filter)
            if classe_filter:
                enrollments = enrollments.filter(classe__name__icontains=classe_filter)
            if section_filter:
                enrollments = enrollments.filter(section__name__icontains=section_filter)
            
            # Statistiques générales
            general_stats = enrollments.aggregate(
                total_enrollments=Count('id'),
                average_percentage=Avg('percentage'),
                max_percentage=Max('percentage'),
                min_percentage=Min('percentage')
            )
            
            # Top 10 étudiants
            top_students = enrollments.order_by('-percentage')[:10].values(
                'student__full_name',
                'percentage',
                'school_year__year',
                'classe__name',
                'section__name'
            )
            
            # Statistiques par classe
            stats_by_class = enrollments.values(
                'classe__name'
            ).annotate(
                total_students=Count('student', distinct=True),
                average_percentage=Avg('percentage'),
                max_percentage=Max('percentage'),
                min_percentage=Min('percentage')
            ).order_by('-average_percentage')
            
            # Statistiques par section
            stats_by_section = enrollments.values(
                'section__name'
            ).annotate(
                total_students=Count('student', distinct=True),
                average_percentage=Avg('percentage'),
                max_percentage=Max('percentage'),
                min_percentage=Min('percentage')
            ).order_by('-average_percentage')
            
            # Statistiques par année
            stats_by_year = enrollments.values(
                'school_year__year'
            ).annotate(
                total_students=Count('student', distinct=True),
                average_percentage=Avg('percentage'),
                max_percentage=Max('percentage'),
                min_percentage=Min('percentage')
            ).order_by('-school_year__year')
            
            # Distribution des notes (par tranches)
            grade_distribution = {
                'excellent': enrollments.filter(percentage__gte=90).count(),
                'tres_bien': enrollments.filter(percentage__gte=80, percentage__lt=90).count(),
                'bien': enrollments.filter(percentage__gte=70, percentage__lt=80).count(),
                'assez_bien': enrollments.filter(percentage__gte=60, percentage__lt=70).count(),
                'passable': enrollments.filter(percentage__gte=50, percentage__lt=60).count(),
                'insuffisant': enrollments.filter(percentage__lt=50).count(),
            }
            
            # Nombre total d'entités
            entity_counts = {
                'total_students': Student.objects.count(),
                'total_school_years': SchoolYear.objects.count(),
                'total_classes': Classe.objects.count(),
                'total_sections': Section.objects.count(),
            }
            
            response_data = {
                'general_stats': general_stats,
                'entity_counts': entity_counts,
                'top_students': list(top_students),
                'stats_by_class': list(stats_by_class),
                'stats_by_section': list(stats_by_section),
                'stats_by_year': list(stats_by_year),
                'grade_distribution': grade_distribution,
                'filters_applied': {
                    'year': year_filter,
                    'classe': classe_filter,
                    'section': section_filter
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du calcul des statistiques: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClassAnalyticsView(APIView):
    """
    Endpoint pour les analyses spécifiques à une classe
    """
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request, classe_id):
        """
        Retourne des statistiques détaillées pour une classe spécifique
        """
        try:
            # Vérifier que la classe existe
            try:
                classe = Classe.objects.get(id=classe_id)
            except Classe.DoesNotExist:
                return Response(
                    {'error': 'Classe non trouvée'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            year_filter = request.query_params.get('year')
            
            # Base queryset pour cette classe
            enrollments = Enrollment.objects.filter(classe=classe)
            
            if year_filter:
                enrollments = enrollments.filter(school_year__year=year_filter)
            
            # Statistiques générales pour cette classe
            class_stats = enrollments.aggregate(
                total_enrollments=Count('id'),
                total_students=Count('student', distinct=True),
                average_percentage=Avg('percentage'),
                max_percentage=Max('percentage'),
                min_percentage=Min('percentage')
            )
            
            # Évolution par année pour cette classe
            evolution_by_year = enrollments.values(
                'school_year__year'
            ).annotate(
                students_count=Count('student', distinct=True),
                average_percentage=Avg('percentage')
            ).order_by('school_year__year')
            
            # Statistiques par section dans cette classe
            stats_by_section = enrollments.values(
                'section__name'
            ).annotate(
                students_count=Count('student', distinct=True),
                average_percentage=Avg('percentage')
            ).order_by('-average_percentage')
            
            response_data = {
                'classe_info': {
                    'id': classe.id,
                    'name': classe.name
                },
                'class_stats': class_stats,
                'evolution_by_year': list(evolution_by_year),
                'stats_by_section': list(stats_by_section),
                'filters_applied': {
                    'year': year_filter
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du calcul des statistiques: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

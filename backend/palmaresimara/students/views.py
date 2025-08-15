from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import SchoolYear, Classe, Section, Student, Enrollment
from .serializers import (
    SchoolYearSerializer, ClasseSerializer, SectionSerializer,
    StudentSerializer, StudentWithEnrollmentsSerializer,
    EnrollmentSerializer, EnrollmentDetailSerializer
)
from .filters import StudentFilter, EnrollmentFilter


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée qui permet la lecture à tous
    mais l'écriture seulement aux admins
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class SchoolYearViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les années scolaires
    """
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['year']
    ordering_fields = ['year', 'created_at']
    ordering = ['-year']


class ClasseViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les classes
    """
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class SectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les sections
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les élèves
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ['full_name']
    ordering_fields = ['full_name', 'created_at']
    ordering = ['full_name']
    
    def get_serializer_class(self):
        """
        Retourne le serializer approprié selon l'action
        """
        if self.action == 'retrieve':
            return StudentWithEnrollmentsSerializer
        return StudentSerializer
    
    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """
        Retourne les inscriptions d'un élève spécifique
        """
        student = self.get_object()
        enrollments = student.enrollments.all().order_by('-school_year__year')
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les inscriptions
    """
    queryset = Enrollment.objects.select_related(
        'student', 'school_year', 'classe', 'section'
    ).all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EnrollmentFilter
    search_fields = ['student__full_name']
    ordering_fields = ['percentage', 'created_at', 'school_year__year']
    ordering = ['-percentage']
    
    def get_serializer_class(self):
        """
        Retourne le serializer approprié selon l'action
        """
        if self.action == 'retrieve':
            return EnrollmentDetailSerializer
        return EnrollmentSerializer
    
    @action(detail=False, methods=['get'])
    def top_students(self, request):
        """
        Retourne le top 10 des élèves par moyenne
        """
        limit = int(request.query_params.get('limit', 10))
        year = request.query_params.get('year')
        
        queryset = self.get_queryset()
        if year:
            queryset = queryset.filter(school_year__year=year)
        
        top_enrollments = queryset.order_by('-percentage')[:limit]
        serializer = EnrollmentDetailSerializer(top_enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """
        Retourne les inscriptions groupées par classe
        """
        year = request.query_params.get('year')
        classe = request.query_params.get('classe')
        
        queryset = self.get_queryset()
        if year:
            queryset = queryset.filter(school_year__year=year)
        if classe:
            queryset = queryset.filter(classe__name__icontains=classe)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

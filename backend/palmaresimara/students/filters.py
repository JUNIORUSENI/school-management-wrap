import django_filters
from .models import Student, Enrollment, SchoolYear, Classe, Section


class StudentFilter(django_filters.FilterSet):
    """Filtres pour les étudiants"""
    full_name = django_filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Student
        fields = ['full_name']
    
    def filter_search(self, queryset, name, value):
        """Recherche full-text dans le nom complet"""
        if value:
            return queryset.filter(full_name__icontains=value)
        return queryset


class EnrollmentFilter(django_filters.FilterSet):
    """Filtres pour les inscriptions"""
    school_year = django_filters.ModelChoiceFilter(queryset=SchoolYear.objects.all())
    classe = django_filters.ModelChoiceFilter(queryset=Classe.objects.all())
    section = django_filters.ModelChoiceFilter(queryset=Section.objects.all())
    
    # Filtres par nom d'année/classe/section (plus pratique pour l'API)
    year = django_filters.CharFilter(field_name='school_year__year', lookup_expr='exact')
    classe_name = django_filters.CharFilter(field_name='classe__name', lookup_expr='icontains')
    section_name = django_filters.CharFilter(field_name='section__name', lookup_expr='icontains')
    
    # Filtres sur les pourcentages
    percentage_min = django_filters.NumberFilter(field_name='percentage', lookup_expr='gte')
    percentage_max = django_filters.NumberFilter(field_name='percentage', lookup_expr='lte')
    percentage_range = django_filters.RangeFilter(field_name='percentage')
    
    # Recherche par nom d'élève
    student_name = django_filters.CharFilter(field_name='student__full_name', lookup_expr='icontains')
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Enrollment
        fields = [
            'school_year', 'classe', 'section', 'year', 'classe_name', 'section_name',
            'percentage_min', 'percentage_max', 'student_name'
        ]
    
    def filter_search(self, queryset, name, value):
        """Recherche globale dans le nom de l'élève"""
        if value:
            return queryset.filter(student__full_name__icontains=value)
        return queryset

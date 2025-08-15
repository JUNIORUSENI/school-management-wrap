from django.contrib import admin
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from .models import SchoolYear, Classe, Section, Student, Enrollment
import csv
import datetime


def export_to_csv(modeladmin, request, queryset):
    """
    Action d'administration pour exporter en CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model._meta.model_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # En-tête
    field_names = [field.name for field in modeladmin.model._meta.fields]
    writer.writerow(field_names)
    
    # Données
    for obj in queryset:
        row = []
        for field in field_names:
            value = getattr(obj, field)
            if value is None:
                value = ''
            row.append(str(value))
        writer.writerow(row)
    
    return response

export_to_csv.short_description = "Exporter en CSV"


@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    """
    Administration des années scolaires
    """
    list_display = ['year', 'created_at', 'enrollment_count']
    list_filter = ['created_at']
    search_fields = ['year']
    ordering = ['-year']
    actions = [export_to_csv]
    
    def enrollment_count(self, obj):
        """Retourne le nombre d'inscriptions pour cette année"""
        return obj.enrollments.count()
    enrollment_count.short_description = "Nombre d'inscriptions"


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    """
    Administration des classes
    """
    list_display = ['name', 'created_at', 'enrollment_count']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['name']
    actions = [export_to_csv]
    
    def enrollment_count(self, obj):
        """Retourne le nombre d'inscriptions pour cette classe"""
        return obj.enrollments.count()
    enrollment_count.short_description = "Nombre d'inscriptions"


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """
    Administration des sections
    """
    list_display = ['name', 'created_at', 'enrollment_count']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['name']
    actions = [export_to_csv]
    
    def enrollment_count(self, obj):
        """Retourne le nombre d'inscriptions pour cette section"""
        return obj.enrollments.count()
    enrollment_count.short_description = "Nombre d'inscriptions"


class EnrollmentInline(admin.TabularInline):
    """
    Inline pour afficher les inscriptions dans l'admin des étudiants
    """
    model = Enrollment
    extra = 0
    fields = ['school_year', 'classe', 'section', 'percentage']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-school_year__year']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Administration des étudiants
    """
    list_display = ['full_name', 'created_at', 'enrollment_count', 'latest_enrollment']
    list_filter = ['created_at', 'enrollments__school_year', 'enrollments__classe', 'enrollments__section']
    search_fields = ['full_name']
    ordering = ['full_name']
    inlines = [EnrollmentInline]
    actions = [export_to_csv]
    
    def enrollment_count(self, obj):
        """Retourne le nombre d'inscriptions pour cet étudiant"""
        return obj.enrollments.count()
    enrollment_count.short_description = "Nombre d'inscriptions"
    
    def latest_enrollment(self, obj):
        """Retourne la dernière inscription de l'étudiant"""
        latest = obj.enrollments.order_by('-school_year__year').first()
        if latest:
            return f"{latest.school_year.year} - {latest.classe.name} {latest.section.name} ({latest.percentage}%)"
        return "Aucune inscription"
    latest_enrollment.short_description = "Dernière inscription"


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """
    Administration des inscriptions
    """
    list_display = [
        'student', 'school_year', 'classe', 'section', 
        'percentage', 'colored_percentage', 'created_at'
    ]
    list_filter = [
        'school_year', 'classe', 'section', 
        'created_at', 'percentage'
    ]
    search_fields = [
        'student__full_name', 'school_year__year', 
        'classe__name', 'section__name'
    ]
    ordering = ['-percentage', 'student__full_name']
    list_per_page = 25
    actions = [export_to_csv]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('student', 'school_year', 'classe', 'section')
        }),
        ('Résultats', {
            'fields': ('percentage',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def colored_percentage(self, obj):
        """Affichage coloré du pourcentage selon la performance"""
        percentage = obj.percentage
        if percentage >= 90:
            color = 'green'
        elif percentage >= 80:
            color = 'blue'
        elif percentage >= 70:
            color = 'orange'
        elif percentage >= 60:
            color = 'darkorange'
        else:
            color = 'red'
        
        return mark_safe(f'<span style="color: {color}; font-weight: bold;">{percentage}%</span>')
    colored_percentage.short_description = "Pourcentage"
    colored_percentage.admin_order_field = 'percentage'
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related"""
        return super().get_queryset(request).select_related(
            'student', 'school_year', 'classe', 'section'
        )


# Configuration de l'admin
admin.site.site_header = "Administration Palmares Imara"
admin.site.site_title = "Palmares Imara"
admin.site.index_title = "Gestion des données scolaires"

from django.db import models


class SchoolYear(models.Model):
    """Année scolaire (ex: 2023-2024)"""
    year = models.CharField(max_length=9, unique=True, help_text="Format: YYYY-YYYY")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year']
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"
    
    def __str__(self):
        return self.year


class Classe(models.Model):
    """Classe (ex: Terminale, Première, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
    
    def __str__(self):
        return self.name


class Section(models.Model):
    """Section (ex: S, ES, L, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Section"
        verbose_name_plural = "Sections"
    
    def __str__(self):
        return self.name


class Student(models.Model):
    """Élève avec nom complet et recherche full-text"""
    full_name = models.CharField(max_length=255, db_index=True, help_text="Nom complet de l'élève")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['full_name']
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"
    
    def __str__(self):
        return self.full_name


class Enrollment(models.Model):
    """Inscription d'un élève dans une classe pour une année donnée"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT, related_name='enrollments')
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name='enrollments')
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='enrollments')
    percentage = models.FloatField(help_text="Pourcentage/moyenne de l'élève")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'school_year')
        ordering = ['-percentage', 'student__full_name']
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        indexes = [
            models.Index(fields=['school_year', 'classe', 'section']),
            models.Index(fields=['percentage']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.school_year.year} ({self.classe.name} {self.section.name})"
    
    @property
    def class_section(self):
        """Retourne la classe et section formatées"""
        return f"{self.classe.name} {self.section.name}"

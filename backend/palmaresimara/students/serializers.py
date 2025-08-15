from rest_framework import serializers
from .models import SchoolYear, Classe, Section, Student, Enrollment


class SchoolYearSerializer(serializers.ModelSerializer):
    """Serializer pour les années scolaires"""
    
    class Meta:
        model = SchoolYear
        fields = ['id', 'year', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ClasseSerializer(serializers.ModelSerializer):
    """Serializer pour les classes"""
    
    class Meta:
        model = Classe
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SectionSerializer(serializers.ModelSerializer):
    """Serializer pour les sections"""
    
    class Meta:
        model = Section
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class StudentSerializer(serializers.ModelSerializer):
    """Serializer pour les élèves"""
    
    class Meta:
        model = Student
        fields = ['id', 'full_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class StudentSummarySerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les élèves (pour les vues imbriquées)"""
    
    class Meta:
        model = Student
        fields = ['id', 'full_name']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer pour les inscriptions"""
    # Champs imbriqués pour la lecture
    student_detail = StudentSummarySerializer(source='student', read_only=True)
    school_year_detail = SchoolYearSerializer(source='school_year', read_only=True)
    classe_detail = ClasseSerializer(source='classe', read_only=True)
    section_detail = SectionSerializer(source='section', read_only=True)
    class_section = serializers.ReadOnlyField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'school_year', 'classe', 'section', 'percentage',
            'student_detail', 'school_year_detail', 'classe_detail', 'section_detail',
            'class_section', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'class_section']
    
    def validate(self, data):
        """Validation personnalisée pour l'unicité élève-année scolaire"""
        student = data.get('student')
        school_year = data.get('school_year')
        
        # Vérifier l'unicité uniquement lors de la création ou si l'un des champs change
        if self.instance is None:  # Création
            if Enrollment.objects.filter(student=student, school_year=school_year).exists():
                raise serializers.ValidationError(
                    f"L'élève {student.full_name} est déjà inscrit pour l'année {school_year.year}"
                )
        else:  # Modification
            # Vérifier seulement si l'élève ou l'année change
            if (student != self.instance.student or school_year != self.instance.school_year):
                if Enrollment.objects.filter(student=student, school_year=school_year).exists():
                    raise serializers.ValidationError(
                        f"L'élève {student.full_name} est déjà inscrit pour l'année {school_year.year}"
                    )
        
        return data
    
    def validate_percentage(self, value):
        """Validation du pourcentage"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Le pourcentage doit être entre 0 et 100")
        return value


class EnrollmentDetailSerializer(EnrollmentSerializer):
    """Serializer détaillé pour les inscriptions (avec toutes les informations)"""
    student_detail = StudentSerializer(source='student', read_only=True)
    
    class Meta(EnrollmentSerializer.Meta):
        pass


class StudentWithEnrollmentsSerializer(serializers.ModelSerializer):
    """Serializer pour un élève avec son historique d'inscriptions"""
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    total_enrollments = serializers.SerializerMethodField()
    average_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'full_name', 'created_at', 'updated_at',
            'enrollments', 'total_enrollments', 'average_percentage'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_enrollments(self, obj):
        """Retourne le nombre total d'inscriptions"""
        return obj.enrollments.count()
    
    def get_average_percentage(self, obj):
        """Retourne la moyenne des pourcentages"""
        enrollments = obj.enrollments.all()
        if enrollments:
            return round(sum(e.percentage for e in enrollments) / len(enrollments), 2)
        return None

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolYearViewSet, ClasseViewSet, SectionViewSet,
    StudentViewSet, EnrollmentViewSet
)

# Création du router DRF
router = DefaultRouter()
router.register(r'school-years', SchoolYearViewSet, basename='schoolyear')
router.register(r'classes', ClasseViewSet, basename='classe')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]

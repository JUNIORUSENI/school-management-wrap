from django.urls import path
from .views import AnalyticsView, ClassAnalyticsView

urlpatterns = [
    path('', AnalyticsView.as_view(), name='analytics'),
    path('classes/<int:classe_id>/', ClassAnalyticsView.as_view(), name='class-analytics'),
]

from . import views
from student_app.views import (
    ProjectListCreateView,
    StudentListCreateView,
    StudentDetailView,
    GroupPreferenceListCreateView,
    StudentViewSet, 
    ProjectViewSet, 
    project_view
)
from django.urls import path, include
from django.contrib import admin
from django.conf import settings 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'students', StudentViewSet, basename='student')

app_name = "student_app"

urlpatterns = [
    path('', views.landing_page, name='student_home'),
    path('student_application/', views.student_form, name="student_form"),
    path('projects/', ProjectListCreateView.as_view(), name='project_list'),
    path('students/', StudentListCreateView.as_view(), name='student_list'),
    path('section/<int:id>/', views.section_detail, name='section_detail'),
]

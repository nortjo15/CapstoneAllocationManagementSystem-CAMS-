from django.urls import path, include
from django.contrib import admin
from django.conf import settings 
from rest_framework.routers import DefaultRouter
from .import views
from student_app.views import StudentViewSet, ProjectViewSet, project_view

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'students', StudentViewSet, basename='student')

app_name = 'student_app'
urlpatterns = [
    path('', views.capstone_information, name="student_home"),

    #API endpoint
    path('', include(router.urls)),
    #Project views
    path('projectInformation/', project_view, name="project_information"),
    #path('<str:student_id>/', StudentDetailView.as_view()),
    #path('preferences/', GroupPreferenceListCreateView.as_view()),
    path('student_application/', views.student_form, name="student_form"),
    #path('projects/', ProjectListCreateView.as_view(), name="project_list"),
    #path('students/', StudentListCreateView.as_view(), name="student_list"),
    path('capstone_information/', views.capstone_information, name="capstone_information"),
]

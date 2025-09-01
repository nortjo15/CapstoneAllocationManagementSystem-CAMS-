from django.urls import path, include
from django.contrib import admin
from django.conf import settings 
from .import views
from student_app.views import ProjectListCreateView, StudentListCreateView, StudentDetailView, GroupPreferenceListCreateView


app_name = 'student_app'
urlpatterns = [
    path('', views.capstone_information, name="student_home"),
    #path('<str:student_id>/', StudentDetailView.as_view()),
    #path('preferences/', GroupPreferenceListCreateView.as_view()),
    path('student_application/', views.student_application_view, name="student_form"),
    path('projects/', ProjectListCreateView.as_view(), name="project_list"),
    path('students/', StudentListCreateView.as_view(), name="student_list"),
    path('capstone_information/', views.capstone_information, name="capstone_information"),
]

from . import views
from student_app.views import (
    StudentViewSet, 
    ProjectViewSet, 
    MajorViewSet,
    student_form_view,
    project_view,
    autocomplete_users,
    landing_page,
    section_detail

)
from django.urls import path, include
from django.contrib import admin
from django.conf import settings 
from rest_framework.routers import DefaultRouter
from .import views
from student_app.views import StudentViewSet, ProjectViewSet, project_view

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'majors', MajorViewSet, basename='major' )

app_name = 'student_app'

urlpatterns = [
    path('', views.landing_page, name="student_home"),

    #API endpoint
    path('', include(router.urls)),
    #Project views
    path('projectInformation/', project_view, name="project_information"),
    #Student Form
    path('student_application/', views.student_form_view, name="student_form"),
    #Information Views
    #path('capstone_information/', views.capstone_information, name="capstone_information"),
    path('section/<int:id>/', views.section_detail, name='section_detail')
]

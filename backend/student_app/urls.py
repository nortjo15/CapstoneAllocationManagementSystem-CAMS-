from django.urls import path, include
from django.contrib import admin
from django.conf import settings 
from rest_framework.routers import DefaultRouter
from student_app.views import StudentViewSet, ProjectViewSet, project_view, autocomplete_users, capstone_information, student_form_view

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'students', StudentViewSet, basename='student')

app_name = 'student_app'

urlpatterns = [
    path('', capstone_information, name="student_home"),

    #API endpoint
    path('', include(router.urls)),
    #Project views
    path('projectInformation/', project_view, name="project_information"),
    #Form views
    path('studentForm', student_form_view, name="student_form"),
    #Information views
    path('capstone_information/', capstone_information, name="capstone_information"),
    path('autocomplete-results/', autocomplete_users, name='autocomplete_users'),
]

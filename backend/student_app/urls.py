from django.urls import path, include
from . import views

app_name = 'student_app'

urlpatterns = [
    #Root view
    path('', views.landing_page, name="student_home"),
    #Project views
    path('projectInformation/', views.project_view, name="project_information"),
    #Student Form
    #path('student_application/', views.student_form_view, name="student_form"),
    path('student_application/<int:round_id>/', views.student_form_view, name="student_form"), 
    path('application-success/', views.student_form_success, name="application_success"),
    path('autocomplete-results/', views.autocomplete_users, name="autocomplete"),
    #Information Views
    path('section/<int:id>/', views.section_detail, name='section_detail'),
]

"""
URL configuration for CAS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings 
from django.urls import path, include
#Import all required views
from admin_app.view import admin_views, auth_views, information_views, section_views, round_views, student_views, project_views, group_views, degree_views

#App namespace
app_name = 'admin_app'

urlpatterns = [
    #Auth_views
    path('register/', auth_views.register_view, name="register"),
    path('login/', auth_views.login_view, name="login"),
    path('logout/', auth_views.logout_view, name="logout"),
    path('login_success/', auth_views.login_success, name="login_success"),
    path('change_password/', auth_views.change_password, name='change_password'),
    #Email View
    path("email/page/", admin_views.email_page, name="email_page"),
    #Round_views
    path('rounds/', round_views.round_view, name='round_view'),
    #Student_views
    path("viewStudents/", student_views.student_page, name="student_view"),
    #Project_views
    path('projectDashboard/', project_views.project_view, name='project_dashboard'),
    #Group_views
    #Group Template
    path("suggested_groups_view/", group_views.GroupListView.as_view(), name="groups_view"),
    #Settings_views
    path('settings/', admin_views.settings_view, name='settings'),
    #Information CRUD
    path('information/',              information_views.information_list,  name='information_list'),
    path('information/new/',          information_views.information_create, name='information_create'),
    path('information/<int:pk>/edit/',   information_views.information_edit,   name='information_edit'),
    path('information/<int:pk>/delete/', information_views.information_delete, name='information_delete'),
    #Sections CRUD
    path('sections/',                section_views.section_list,  name='section_list'),
    path('sections/new/',            section_views.section_create, name='section_create'),
    path('sections/<int:pk>/edit/',  section_views.section_edit,   name='section_edit'),
    path('sections/<int:pk>/delete/',section_views.section_delete, name='section_delete'),
    #Degree and Major
    path('degreeDashboard/', degree_views.degree_view, name='degree_dashboard'),
    #Information and Sections
    path('informationDashboard/', information_views.information_view, name='information_dashboard'),
]
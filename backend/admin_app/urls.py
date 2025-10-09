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
from admin_app.view import admin_views, auth_views, communications_section_views, round_views, student_views, project_views, group_views, degree_views, communications_views
from django.views.generic import RedirectView

#App namespace
app_name = 'admin_app'

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="admin_app:login_success", permanent=False)),
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
    path('information/',              communications_views.communications_list,  name='communications_list'),
    path('information/new/',          communications_views.communications_create, name='communications_create'),
    path('information/<int:pk>/edit/',   communications_views.communications_edit,   name='communications_edit'),
    path('information/<int:pk>/delete/', communications_views.communications_delete, name='communications_delete'),
    #Sections CRUD
    path('sections/',                communications_section_views.communications_section_list,  name='communications_section_list'),
    path('sections/new/',            communications_section_views.communications_section_create, name='communications_section_create'),
    path('sections/<int:pk>/edit/',  communications_section_views.communications_section_edit,   name='communications_section_edit'),
    path('sections/<int:pk>/delete/',communications_section_views.communications_section_delete, name='communications_section_delete'),
    #Degree and Major
    path('degreeDashboard/', degree_views.degree_view, name='degree_dashboard'),
]
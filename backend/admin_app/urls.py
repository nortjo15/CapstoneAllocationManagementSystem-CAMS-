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
from rest_framework.routers import DefaultRouter

#Import all required views
from .view.project_views import project_view, ProjectViewSet
from .view.auth_views import register_view, login_view, logout_view, login_success, change_password
from .view.admin_views import AdminLogListCreateView #, SendNotificationView
from .view.round_views import round_view
from .view.group_views import SuggestedGroupListCreateView, SuggestedGroupMemberListCreateView, FinalGroupListCreateView, FinalGroupMemberListCreateView
from .view.settings_views import settings_view
from .view.information_views import (
    information_list, information_create, information_edit, information_delete
)
from .view.section_views import section_list, section_create, section_edit, section_delete

from admin_app.view import admin_views

from admin_app.view.email_views import MailtoLinkView
from .view.student_views import *
from .view.admin_views import (
    SendRoundStartView,
    SendRoundClosedView,
    SendApplicationSuccessView,
    SendAllocationReleasedView,
)

app_name = 'admin_app'
urlpatterns = [
    #Auth_views
    path('register/', register_view, name="register"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('login_success/', login_success, name="login_success"),
    path('change_password/', change_password, name='change_password'),
    #Admin_views
    path('admin/logs/', AdminLogListCreateView.as_view()),
    path("email/mailto/", MailtoLinkView.as_view(), name="mailto_link"),
    path("email/page/", admin_views.email_page, name="email_page"),

    path("notify/round-start/<int:round_id>/", SendRoundStartView.as_view(), name="notify_round_start"),
    path("notify/round-closed/<int:round_id>/", SendRoundClosedView.as_view(), name="notify_round_closed"),
    path("notify/application-success/<str:student_id>/", SendApplicationSuccessView.as_view(), name="notify_application_success"),
    path("notify/allocation-released/<int:final_group_id>/", SendAllocationReleasedView.as_view(), name="notify_allocation_released"),
    
    #Round_views
    path('rounds/', round_view, name='round_view'),

    #Student_views
    path('student_view/', StudentListView.as_view(), name='student_view'),
    path('students/create/', StudentCreateView.as_view(), name='admin_student_create'),
    path('students/import/', StudentImportView.as_view(), name='admin_student_import'),
    path('student/update-notes/', update_student_notes, name='update_student_notes'),
    #Project_views
    path('projectDashboard/', project_view, name='project_dashboard'),
   
    #Group_views
    path('suggested/', SuggestedGroupListCreateView.as_view()),
    path('suggested/members/', SuggestedGroupMemberListCreateView.as_view()),
    path('final/', FinalGroupListCreateView.as_view()),
    path('final/members/', FinalGroupMemberListCreateView.as_view()),
    #Settings_views
    path('settings/', settings_view, name='settings'),

    
    #Information CRUD
    path('information/',              information_list,  name='information_list'),
    path('information/new/',          information_create, name='information_create'),
    path('information/<int:pk>/edit/',   information_edit,   name='information_edit'),
    path('information/<int:pk>/delete/', information_delete, name='information_delete'),
    #Sections CRUD
    path('sections/',                section_list,  name='section_list'),
    path('sections/new/',            section_create, name='section_create'),
    path('sections/<int:pk>/edit/',  section_edit,   name='section_edit'),
    path('sections/<int:pk>/delete/',section_delete, name='section_delete'),

    #api endpoint
    path('', include('admin_app.api.urls')),
]
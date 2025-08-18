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
from django.urls import path
from django.conf import settings 
from django.urls import path
#Import all required views
from .view.project_views import ProjectListCreateView, ProjectPreferenceListCreateView
from .view.auth_views import register_view, login_view, logout_view, login_success
from .view.admin_views import AdminLogListCreateView, SendNotificationView
from .view.round_views import round_view
from .view.group_views import SuggestedGroupListCreateView, SuggestedGroupMemberListCreateView, FinalGroupListCreateView, FinalGroupMemberListCreateView
from .view.settings_views import settings_view
from .view.student_views import *
 
urlpatterns = [
    #Auth_views
    path('register/', register_view, name="register"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('login_success/', login_success, name="login_success"),
    #Admin_views
    path('admin/logs/', AdminLogListCreateView.as_view()),
    path('send-notification/', SendNotificationView.as_view(), name='send_notification'),
    #Student_views
    path('student_view/', StudentListView.as_view(), name='student_view'),
    path('student/create/', StudentCreateView.as_view(), name='admin_student_create'),
    path('student/import/', admin_student_import, name='admin_student_import'),
    #Project_views
    path('projects/', ProjectListCreateView.as_view()),
    path('preferences/', ProjectPreferenceListCreateView.as_view()),
    #Group_views
    path('suggested/', SuggestedGroupListCreateView.as_view()),
    path('suggested/members/', SuggestedGroupMemberListCreateView.as_view()),
    path('final/', FinalGroupListCreateView.as_view()),
    path('final/members/', FinalGroupMemberListCreateView.as_view()),
    #Settings_views
    path('settings/', settings_view, name='settings'),
    #Round_views
    path('rounds/', round_view, name='round_view'),
]
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
from django.urls import path, include
from rest_framework.routers import DefaultRouter

#Import all required views
from .view.project_views import project_view, ProjectViewSet
from .view.auth_views import register_view, login_view, logout_view, login_success, change_password
from .view.admin_views import AdminLogListCreateView #, SendNotificationView
from .view.round_views import round_view
from .view.group_views import SuggestedGroupListCreateView, SuggestedGroupMemberListCreateView, FinalGroupListCreateView, FinalGroupMemberListCreateView
from .view.settings_views import settings_view
from .view.announcements_views import (
    announcement_list, announcement_create, announcement_edit, announcement_delete
)
from admin_app.view import admin_views

from admin_app.view.email_views import MailtoLinkView
from .view.student_views import *
from .view.admin_views import (
    SendRoundStartView,
    SendRoundClosedView,
    SendApplicationSuccessView,
    SendAllocationReleasedView,
)


# router = DefaultRouter()
# router.register(r'projects', ProjectViewSet, basename='project')

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
    path("notify/round-start/<int:round_id>/", SendRoundStartView.as_view(), name="notify_round_start"),
    path("notify/round-closed/<int:round_id>/", SendRoundClosedView.as_view(), name="notify_round_closed"),
    path("notify/application-success/<str:student_id>/", SendApplicationSuccessView.as_view(), name="notify_application_success"),
    path("notify/allocation-released/<int:final_group_id>/", SendAllocationReleasedView.as_view(), name="notify_allocation_released"),
    #Student_views
    path('student_view/', StudentListView.as_view(), name='student_view'),
    path('students/create/', StudentCreateView.as_view(), name='admin_student_create'),
    path('students/import/', StudentImportView.as_view(), name='admin_student_import'),
    path('student/update-notes/', update_student_notes, name='update_student_notes'),
    #Project_views
    path('', include('admin_app.api.urls')),
    path('projectDashboard/', project_view, name='project_dashboard'),
   
    #Group_views
    path('suggested/', SuggestedGroupListCreateView.as_view()),
    path('suggested/members/', SuggestedGroupMemberListCreateView.as_view()),
    path('final/', FinalGroupListCreateView.as_view()),
    path('final/members/', FinalGroupMemberListCreateView.as_view()),
    #Settings_views
    path('settings/', settings_view, name='settings'),

    #Round_views
    path('rounds/', round_view, name='round_view'),
    #Announcements CRUD
    path('announcements/',              announcement_list,  name='announcement_list'),
    path('announcements/new/',          announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/edit/',   announcement_edit,   name='announcement_edit'),
    path('announcements/<int:pk>/delete/', announcement_delete, name='announcement_delete'),
]
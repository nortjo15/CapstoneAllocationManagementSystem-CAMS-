from django.urls import path
from django.conf import settings 

from django.contrib import admin

from .views import *

urlpatterns = [
    path('', ProjectListCreateView.as_view()),
    path('admin/', admin.site.urls),
    path('preferences/', ProjectPreferenceListCreateView.as_view()),
    path('suggested/', SuggestedGroupListCreateView.as_view()),
    path('suggested/members/', SuggestedGroupMemberListCreateView.as_view()),
    path('final/', FinalGroupListCreateView.as_view()),
    path('final/members/', FinalGroupMemberListCreateView.as_view()),
]

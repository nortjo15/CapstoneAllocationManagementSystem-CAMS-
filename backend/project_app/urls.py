from django.urls import path
from .views import *

urlpatterns = [
    path('', ProjectListCreateView.as_view()),
    path('preferences/', ProjectPreferenceListCreateView.as_view()),
    path('suggested/', SuggestedGroupListCreateView.as_view()),
    path('suggested/members/', SuggestedGroupMemberListCreateView.as_view()),
    path('final/', FinalGroupListCreateView.as_view()),
    path('final/members/', FinalGroupMemberListCreateView.as_view()),
]

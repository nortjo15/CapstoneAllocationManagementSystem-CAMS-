from django.urls import path
from .views import *

urlpatterns = [
    path('', StudentListCreateView.as_view()),
    path('<str:student_id>/', StudentDetailView.as_view()),
    path('preferences/', GroupPreferenceListCreateView.as_view()),
]

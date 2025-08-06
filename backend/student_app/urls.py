from django.urls import path, include
from django.contrib import admin
from django.conf import settings 


from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', StudentListCreateView.as_view()),
    path('<str:student_id>/', StudentDetailView.as_view()),
    path('preferences/', GroupPreferenceListCreateView.as_view()),
]

from django.urls import path, include
from django.contrib import admin
from django.conf import settings 
from .import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', StudentListCreateView.as_view()),
    #path('<str:student_id>/', StudentDetailView.as_view()),
    #path('preferences/', GroupPreferenceListCreateView.as_view()),
    path('studentApplication/', views.student_form, name="student_form"),
]

from django.urls import path, include
from django.contrib import admin
from django.conf import settings 
from .import views
from student_app.views import ProjectListCreateView, StudentListCreateView

urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('<str:student_id>/', StudentDetailView.as_view()),
    #path('preferences/', GroupPreferenceListCreateView.as_view()),
    path('studentApplication/', views.student_form, name="student_form"),
    path('projects/', ProjectListCreateView.as_view(), name="project_list"),
    path('students/', StudentListCreateView.as_view(), name="student_list"),
]

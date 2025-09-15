from django.urls import path
from . import views
from student_app.views import (
    ProjectListCreateView,
    StudentListCreateView,
    StudentDetailView,
    GroupPreferenceListCreateView,
)

app_name = "student_app"

urlpatterns = [
    path("", views.landing_page, name="student_home"),
    path("student_application/", views.student_form, name="student_form"),
    path("projects/", ProjectListCreateView.as_view(), name="project_list"),
    path("students/", StudentListCreateView.as_view(), name="student_list"),
    path("section/<int:id>/", views.section_detail, name="section_detail"),
]

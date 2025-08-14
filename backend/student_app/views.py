from rest_framework import generics
from django.shortcuts import render
from .models import Student, GroupPreference
from .serializers import StudentSerializer, GroupPreferenceSerializer
from project_app.models import Project
from project_app.serializers import ProjectSerializer

class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'

class GroupPreferenceListCreateView(generics.ListCreateAPIView):
    queryset = GroupPreference.objects.all()
    serializer_class = GroupPreferenceSerializer

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

def student_form(request):
    students = Student.objects.values('name')
    projects = Project.objects.values('title')
    return render(request, "student_form.html", {'students': students, 'projects': projects})
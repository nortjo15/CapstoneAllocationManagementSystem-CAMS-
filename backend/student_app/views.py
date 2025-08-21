from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import Student, GroupPreference
from .serializers import StudentSerializer, GroupPreferenceSerializer
from admin_app.models import Project, Major
from admin_app.serializers import ProjectSerializer
from django.http import JsonResponse


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
    if request.method =='POST':
        studentId = request.POST.get("studentID")
        # projects = request.POST.getlist('projects[]')
        Student.objects.filter(student_id=studentID).update(
            cwa = request.POST.get("cwa"),
            major = request.POST.get("major"),
            application_submitted=true,
            email = request.POST.get("email"),
            resume = request.POST.get("filename")
        )
        print("Form data received: ", data)
        return JsonResponse({"received_data" : data})
    else: 
        students = Student.objects.values('name')
        projects = Project.objects.values('title')
        majors = Major.objects.values('name')
        return render(request, "student_form.html", {'students': students, 'projects': projects, 'majors': majors})

    

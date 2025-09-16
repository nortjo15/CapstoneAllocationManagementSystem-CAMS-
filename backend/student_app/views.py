from rest_framework import viewsets
from django.shortcuts import render
from .models import Student
from admin_app.models import Project
from .serializers import StudentSerializer, ProjectSerializer
from admin_app.models import Project, Major, CapstoneInformationSection, CapstoneInformationContent, UnitContacts
from admin_app.serializers import ProjectSerializer
from django.http import JsonResponse
from django.db.models import Prefetch
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

def project_view(request):
    return render(request, "project_information.html")

def student_form(request):
    if request.method =='POST':
        studentID = request.POST.get("studentID")
        # projects = request.POST.getlist('projects[]')
        Student.objects.filter(student_id=studentID).update(
            cwa = request.POST.get("cwa"),
            major = request.POST.get("major"),
            application_submitted=True,
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

def capstone_information(request):
    sections = (CapstoneInformationSection.objects
                .prefetch_related(
                    Prefetch(
                        'contents',
                        queryset=(CapstoneInformationContent.objects
                                  .order_by('-pinned', 'priority', '-published_at'))
                    )
                ))
    return render(request, "capstone_information.html", {"sections": sections})


from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import Student, GroupPreference
from .serializers import StudentSerializer, GroupPreferenceSerializer
from admin_app.models import Project, Major, CapstoneInformationSection, CapstoneInformationContent, UnitContacts
from admin_app.serializers import ProjectSerializer
from django.http import JsonResponse
from django.db.models import Prefetch
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from student_app.forms import ProjectApplicationForm



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

def student_application_view(request):
    if request.method == 'POST':
        form = ProjectApplicationForm(request.POST, request.FILES)
        if form.is_Valid():
            student = form.save()   
            return render(request, 'Success.html', {'student': student})
    else: 
        form = ProjectApplicationForm()

    projects = Project.objects.all().values('project_id', 'title')
    students = Student.objects.all().order_by('name').values('student_id', 'name')
    return render(request, 'student_application.html', {'form':form, 'projects': projects, 'students': students})

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


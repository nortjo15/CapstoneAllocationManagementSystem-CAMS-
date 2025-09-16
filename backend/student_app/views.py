from rest_framework import viewsets
from django.shortcuts import render
from .models import Student
from admin_app.models import Project
from .serializers import StudentSerializer, ProjectSerializer
from admin_app.models import Project, Major, CapstoneInformationSection, CapstoneInformationContent, UnitContacts
from admin_app.serializers import ProjectSerializer
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Prefetch
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from student_app.forms import ProjectApplicationForm

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

# def student_application_view(request):
#     if request.method == 'POST':
#         form = ProjectApplicationForm(request.POST, request.FILES)
#         if form.is_Valid():
#             student = form.save()   
#             return render(request, 'Success.html', {'student': student})

def student_form_view(request):
    return render(request, "student_form.html")
    
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
        form = ProjectApplicationForm()

    projects = Project.objects.all().values('project_id', 'title')
    students = Student.objects.all().order_by('name').values('student_id', 'name')
    return render(request, 'student_application.html', {'form':form, 'projects': projects, 'students': students})

@require_GET #Only respond to get requests
def autocomplete_users(request):
    #extracts query from URL
    query = request.GET.get('q', '')
    #limit matches to 10
    results = Student.objects.filter(name__icontains=query)[:10]
    return JsonResponse([{'student_id': u.student_id, 'name': u.name} for u in results], safe=False)

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


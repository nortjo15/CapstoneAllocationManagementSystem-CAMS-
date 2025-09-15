from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import Student, GroupPreference
from .serializers import StudentSerializer, GroupPreferenceSerializer
from admin_app.models import Project, Major, CapstoneInformationSection, CapstoneInformationContent, UnitContacts
from admin_app.serializers import ProjectSerializer
from django.http import JsonResponse 
from django.db.models import Prefetch, Q
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from admin_app.models import (
    CapstoneInformationSection,
    CapstoneInformationContent,
)



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

def landing_page(request):
    sections = (CapstoneInformationSection.objects
                .prefetch_related(
                    Prefetch(
                        'contents',
                        queryset=(CapstoneInformationContent.objects
                                  .order_by('-pinned', 'priority', '-published_at'))
                    )
                ))
    return render(request, "capstone_information.html", {"sections": sections})

def section_detail(request, id):
    section = get_object_or_404(CapstoneInformationSection, id=id)
    now = timezone.now()

    qs = (
        CapstoneInformationContent.objects
        .select_related("section_id")
        .filter(section_id=section, status="published")
        .filter(
            Q(published_at__lte=now) | Q(published_at__isnull=True),
            Q(expires_at__gt=now)    | Q(expires_at__isnull=True),
        )
        .order_by("-pinned", "priority", "-published_at", "id")
    )

    page = Paginator(qs, 20).get_page(request.GET.get("page"))
    subsections = section.subsections.order_by("order", "id")

    return render(
        request,
        "capstone_info/section_detail.html",  # <-- matches template location above
        {
            "section": section,
            "contents": page.object_list,
            "subsections": subsections,
            "page": page,
        },
    )

from rest_framework import viewsets
from django.shortcuts import render
from .models import Student
from admin_app.models import Project
from .serializers import StudentSerializer, ProjectSerializer, MajorSerializer
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

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer

def student_form_view(request):
    return render(request, "student_form.html")
    
def project_view(request):
    return render(request, "project_information.html")

@require_GET #Only respond to get requests
def autocomplete_users(request):
    #extracts query from URL
    query = request.GET.get('q', '')
    #limit matches to 10
    results = Student.objects.filter(name__icontains=query)[:10]
    return JsonResponse([{'student_id': u.student_id, 'name': u.name} for u in results], safe=False)

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
        "section_detail.html",
        {
            "section": section,
            "contents": page.object_list,
            "subsections": subsections,
            "page": page,
        },
    )

from .models import Student
from admin_app.models import Project
from admin_app.models import Project, Major, CapstoneInformationSection, CapstoneInformationContent
from django.http import JsonResponse 
from django.db.models import Prefetch, Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from admin_app.models import CapstoneInformationSection, CapstoneInformationContent
from django.http import JsonResponse
from django.db.models import Prefetch, Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET

#Render Templates
# def student_form_view(request):
#     return render(request, "student_form.html")

def student_form_view(request, round_id):
    return render(request, "student_form.html")

def student_form_success(request):
    return render(request, "student_form_success.html")
    
def project_view(request):
    return render(request, "project_information.html")

#Root view/Landing page
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

#Search Functionality
@require_GET #Only respond to get requests
def autocomplete_users(request):
    #extracts query from URL
    query = request.GET.get('q', '')
    #limit matches to 10
    results = Student.objects.filter(name__icontains=query)[:10]
    return JsonResponse([{'student_id': u.student_id, 'name': u.name} for u in results], safe=False)

#Capstone Information views
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

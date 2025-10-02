# admin_app/view/informations_views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from admin_app.models import CapstoneInformationContent, CapstoneInformationSection
from admin_app.forms.admin_forms import InformationForm

@login_required
def information_view(request):
    return render(request, 'information_dashboard.html')

@staff_member_required
def information_list(request):
    """Admin list with filters + search + pagination."""
    now = timezone.now()

    # accept ?status=...&status=... or single ?status=...
    statuses = request.GET.getlist("status")
    if not statuses:
        single = request.GET.get("status")
        statuses = [single] if single else ["published"]

    qs = (CapstoneInformationContent.objects
          .select_related("section_id")
          .filter(
              Q(status__in=statuses),
              Q(published_at__lte=now) | Q(published_at__isnull=True),
              Q(expires_at__gt=now)    | Q(expires_at__isnull=True),
          ))

    if q := request.GET.get("q"):
        qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q) | Q(author__icontains=q))

    if sec := request.GET.get("section"):
        qs = qs.filter(section_id_id=sec)

    qs = qs.order_by("-pinned", "priority", "-published_at", "id")

    # Pagination
    page = Paginator(qs, 20).get_page(request.GET.get("page"))

    sections = CapstoneInformationSection.objects.order_by("order", "id")
    return render(request, "information_list.html", {
        "page": page,
        "items": page.object_list,
        "sections": sections,
    })

@staff_member_required
def information_create(request):
    if not CapstoneInformationSection.objects.exists():
        messages.warning(request, "Please create a section before adding an information section.")
        return redirect("admin_app:section_create")
    if request.method == "POST":
        form = InformationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.author and request.user.is_authenticated:
                obj.author = request.user.get_full_name() or request.user.username
            if not obj.published_at:
                obj.published_at = timezone.now()
            obj.save()
            messages.success(request, f"Information section “{obj.title}” created.")
            # (Optional) call admin log helper here
            return redirect("admin_app:information_list")
    else:
        form = InformationForm()
    return render(request, "information_form.html", {"form": form})

@staff_member_required
def information_edit(request, pk):
    obj = get_object_or_404(CapstoneInformationContent, pk=pk)
    if request.method == "POST":
        form = InformationForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.author and request.user.is_authenticated:
                obj.author = request.user.get_full_name() or request.user.username
            if not obj.published_at:
                obj.published_at = timezone.now()
            obj.save()
            messages.success(request, f"Updated “{obj.title}”.")
            # (Optional) call admin log helper here
            return redirect("admin_app:information_list")
    else:
        form = InformationForm(instance=obj)
    return render(request, "information_form.html", {"form": form})

@staff_member_required
def information_delete(request, pk):
    obj = get_object_or_404(CapstoneInformationContent, pk=pk)
    if request.method == "POST":
        title = obj.title
        obj.delete()
        messages.success(request, f"Deleted “{title}”.")
        # (Optional) call admin log helper here
        return redirect("admin_app:information_list")
    return render(request, "information_confirm_delete.html", {"obj": obj})

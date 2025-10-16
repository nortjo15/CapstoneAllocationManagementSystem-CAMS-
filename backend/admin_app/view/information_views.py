from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q, Case, When, Value, BooleanField
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from admin_app.models import CapstoneInformationContent, CapstoneInformationSection
from admin_app.forms.admin_forms import InformationForm

@login_required
def information_list(request):
    """Admin list with filters + search + pagination."""
    now = timezone.now()

    # Normalize status param(s)
    raw = request.GET.getlist("status") or ([request.GET.get("status")] if "status" in request.GET else [])
    statuses = [s for s in raw if s]  # drop blanks

    qs = CapstoneInformationContent.objects.select_related("section_id")

    # Status-only filtering. Do not time-gate so admins can see expired items.
    if statuses:
        qs = qs.filter(status__in=statuses)
    elif "status" not in request.GET:
        qs = qs.filter(status="published")

    if q := request.GET.get("q"):
        qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q) | Q(author__icontains=q))

    if sec := request.GET.get("section"):
        qs = qs.filter(section_id_id=sec)

    # Annotate expiry flag for row styling
    qs = qs.annotate(
        expired_flag=Case(
            When(expires_at__isnull=True, then=Value(False)),
            When(expires_at__lte=now, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    ).order_by("-pinned", "priority", "-published_at", "id")

    page = Paginator(qs, 20).get_page(request.GET.get("page"))
    sections = CapstoneInformationSection.objects.order_by("order", "id")

    # For dropdown selection state
    if "status" in request.GET:
        current_status = request.GET.get("status", "")
    else:
        current_status = "published"

    return render(request, "information_list.html", {
        "page": page,
        "items": page.object_list,
        "sections": sections,
        "current_status": current_status,
    })

@login_required
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
            obj.save()  # published_at auto-stamped in model.save()
            messages.success(request, f"Information section “{obj.title}” created.")
            return redirect("admin_app:information_list")
    else:
        form = InformationForm()
    return render(request, "information_form.html", {"form": form})

@login_required
def information_edit(request, pk):
    obj = get_object_or_404(CapstoneInformationContent, pk=pk)
    if request.method == "POST":
        form = InformationForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.author and request.user.is_authenticated:
                obj.author = request.user.get_full_name() or request.user.username
            obj.save()  # published_at auto-stamped in model.save()
            messages.success(request, f"Updated “{obj.title}”.")
            return redirect("admin_app:information_list")
    else:
        form = InformationForm(instance=obj)
    return render(request, "information_form.html", {"form": form})

@login_required
def information_delete(request, pk):
    obj = get_object_or_404(CapstoneInformationContent, pk=pk)
    if request.method == "POST":
        title = obj.title
        obj.delete()
        messages.success(request, f"Deleted “{title}”.")
        return redirect("admin_app:information_list")
    return render(request, "information_confirm_delete.html", {"obj": obj})

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from admin_app.models import CapstoneInformationSection
from admin_app.forms.admin_forms import SectionForm

@login_required
def section_list(request):
    sections = CapstoneInformationSection.objects.order_by("order", "id")
    return render(request, "section_list.html", {"sections": sections})

@login_required
def section_create(request):
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Section “{obj.name}” created.')
            return redirect("admin_app:section_list")
    else:
        form = SectionForm()
    return render(request, "section_form.html", {"form": form})

@login_required
def section_edit(request, pk):
    obj = get_object_or_404(CapstoneInformationSection, pk=pk)
    if request.method == "POST":
        form = SectionForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Section “{obj.name}” updated.')
            return redirect("admin_app:section_list")
    else:
        form = SectionForm(instance=obj)
    return render(request, "section_form.html", {"form": form})

@login_required
def section_delete(request, pk):
    obj = get_object_or_404(CapstoneInformationSection, pk=pk)
    if request.method == "POST":
        name = obj.name
        obj.delete()
        messages.success(request, f'Section “{name}” deleted.')
        return redirect("admin_app:section_list")
    return render(request, "section_confirm_delete.html", {"obj": obj})

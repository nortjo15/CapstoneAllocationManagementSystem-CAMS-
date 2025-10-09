from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from admin_app.models import CapstoneInformationSection
from admin_app.forms.admin_forms import CommunicationsSectionForm

@staff_member_required
def communications_section_list(request):
    sections = CapstoneInformationSection.objects.order_by("order", "id")
    return render(request, "communications_section_list.html", {"sections": sections})

@staff_member_required
def communications_section_create(request):
    if request.method == "POST":
        form = CommunicationsSectionForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Section “{obj.name}” created.')
            return redirect("admin_app:communications_section_list")
    else:
        form = CommunicationsSectionForm()
    return render(request, "communications_section_form.html", {"form": form})

@staff_member_required
def communications_section_edit(request, pk):
    obj = get_object_or_404(CapstoneInformationSection, pk=pk)
    if request.method == "POST":
        form = CommunicationsSectionForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Section “{obj.name}” updated.')
            return redirect("admin_app:communications_section_list")
    else:
        form = CommunicationsSectionForm(instance=obj)
    return render(request, "communications_section_form.html", {"form": form})

@staff_member_required
def communications_section_delete(request, pk):
    obj = get_object_or_404(CapstoneInformationSection, pk=pk)
    if request.method == "POST":
        name = obj.name
        obj.delete()
        messages.success(request, f'Section “{name}” deleted.')
        return redirect("admin_app:communications_section_list")
    return render(request, "communications_section_confirm_delete.html", {"obj": obj})

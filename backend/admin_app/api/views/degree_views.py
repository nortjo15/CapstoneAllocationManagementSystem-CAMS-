from rest_framework import viewsets
from ..serializers import DegreeSerializer, MajorSerializer
from django.core.paginator import Paginator
from django.db.models import Count
from admin_app.models import Degree, Major

class DegreeViewSet(viewsets.ModelViewSet):
    queryset = Degree.objects.all().order_by('name')
    serializer_class = DegreeSerializer

class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.select_related('degree').annotate(
        student_count=Count('students')
    ).order_by('degree__name', 'name')
    serializer_class = MajorSerializer

# LOGIN_DECORATOR = method_decorator(login_required, name="dispatch")

# def _twopane_success_url(selected_degree_id=None, page=None):
#     base = reverse("admin_app:degree_twopane")
#     parts = []
#     if page:
#         parts.append(f"page={page}")
#     if selected_degree_id:
#         parts.append(f"degree_id={selected_degree_id}")
#     return f"{base}?{'&'.join(parts)}" if parts else base

# @LOGIN_DECORATOR
# class DegreeTwoPaneView(TemplateView):
#     """
#     Two-pane: left = paginated Degrees; right = Majors for selected degree.
#     Query params:
#       - page (int): 20 per page
#       - degree_id (int): selected degree for the right pane
#     """
#     template_name = "degrees/twopane.html"
#     PAGE_SIZE = 20

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)

#         # Degrees (alphabetical, paginated like announcements page style)
#         qs = Degree.objects.annotate(majors_count=Count("majors")).order_by("name")
#         paginator = Paginator(qs, self.PAGE_SIZE)
#         page_number = self.request.GET.get("page") or 1
#         page_obj = paginator.get_page(page_number)

#         ctx["page"] = page_obj  # mirrors announcements template pagination block
#         ctx["degrees"] = page_obj.object_list
#         ctx["total_degrees"] = paginator.count

#         # Selected degree for right pane
#         selected_id = self.request.GET.get("degree_id")
#         if selected_id:
#             selected = get_object_or_404(Degree, pk=selected_id)
#         else:
#             selected = page_obj.object_list[0] if page_obj.object_list else None

#         ctx["selected_degree"] = selected
#         ctx["majors"] = selected.majors.order_by("name") if selected else []
#         ctx["no_degrees"] = paginator.count == 0
#         ctx["no_majors"] = (selected is not None) and (selected.majors.count() == 0)

#         # Fresh instances for slide-overs
#         ctx["degree_form"] = DegreeForm()
#         ctx["major_form"] = MajorForm(initial={"degree": selected}) if selected else MajorForm()

#         return ctx

# @LOGIN_DECORATOR
# class DegreeCreateView(CreateView):
#     model = Degree
#     form_class = DegreeForm
#     template_name = "degrees/degree_form.html"  # used for edit/create fallbacks

#     def form_valid(self, form):
#         obj = form.save()
#         page = self.request.GET.get("page")
#         return redirect(_twopane_success_url(selected_degree_id=obj.id, page=page))

# @LOGIN_DECORATOR
# class DegreeUpdateView(UpdateView):
#     model = Degree
#     form_class = DegreeForm
#     template_name = "degrees/degree_form.html"

#     def form_valid(self, form):
#         obj = form.save()
#         page = self.request.GET.get("page")
#         return redirect(_twopane_success_url(selected_degree_id=obj.id, page=page))

# @LOGIN_DECORATOR
# class DegreeDeleteView(DeleteView):
#     model = Degree
#     template_name = "degrees/degree_confirm_delete.html"

#     def get_success_url(self):
#         # Return to two-pane, no selection retained
#         page = self.request.GET.get("page")
#         return _twopane_success_url(page=page)

# @LOGIN_DECORATOR
# class MajorCreateView(CreateView):
#     model = Major
#     form_class = MajorForm
#     template_name = "degrees/major_form.html"

#     def get_initial(self):
#         initial = super().get_initial()
#         initial["degree"] = get_object_or_404(Degree, pk=self.kwargs["degree_id"])
#         return initial

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         ctx["degree"] = get_object_or_404(Degree, pk=self.kwargs["degree_id"])
#         return ctx

#     def form_valid(self, form):
#         obj = form.save()
#         page = self.request.GET.get("page")
#         return redirect(_twopane_success_url(selected_degree_id=obj.degree_id, page=page))

# @LOGIN_DECORATOR
# class MajorUpdateView(UpdateView):
#     model = Major
#     form_class = MajorForm
#     template_name = "degrees/major_form.html"

#     def form_valid(self, form):
#         obj = form.save()
#         page = self.request.GET.get("page")
#         return redirect(_twopane_success_url(selected_degree_id=obj.degree_id, page=page))

# @LOGIN_DECORATOR
# class MajorDeleteView(DeleteView):
#     model = Major
#     template_name = "degrees/major_confirm_delete.html"

#     def get_success_url(self):
#         degree_id = self.object.degree_id
#         page = self.request.GET.get("page")
#         return _twopane_success_url(selected_degree_id=degree_id, page=page)

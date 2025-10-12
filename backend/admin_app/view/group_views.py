from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from admin_app.models import SuggestedGroup, Major

# Webpage
class GroupListView(LoginRequiredMixin, ListView):
    model = SuggestedGroup
    template_name = "students/suggested_groups_view.html"  
    context_object_name = "suggested_groups"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Build degree -> majors dict
        degree_major_pairs = {}
        for major in Major.objects.all():
            degree_major_pairs.setdefault(major.degree.name, []).append((major.id, major.name))

        context["degree_major_pairs"] = degree_major_pairs
        context["selected_majors"] = self.request.GET.getlist("major")
        context["filter_target_url"] = self.request.path
        context["groups_page"] = True #Used to filter the table

        return context
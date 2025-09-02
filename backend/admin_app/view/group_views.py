from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from admin_app.models import *

class GroupListView(LoginRequiredMixin, ListView):
    model = SuggestedGroup
    template_name = "suggested_groups_view.html"  
    context_object_name = "suggested_groups"
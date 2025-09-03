from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from admin_app.models import *
from admin_app.serializers import *
from rest_framework import generics  

# Webpage
class GroupListView(LoginRequiredMixin, ListView):
    model = SuggestedGroup
    template_name = "suggested_groups_view.html"  
    context_object_name = "suggested_groups"

# List + create suggested groups
class SuggestedGroupListCreateView(generics.ListCreateAPIView):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer

# Retrieve one suggested group by ID
class SuggestedGroupDetailView(generics.RetrieveAPIView):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer
    lookup_field = 'suggestedgroup_id'

# GroupMember 
class SuggestedGroupMemberListCreateView(generics.ListCreateAPIView):
    queryset = SuggestedGroupMember.objects.all()
    serializer_class = SuggestedGroupMemberSerializer
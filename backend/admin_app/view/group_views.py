from rest_framework import generics
from admin_app.models import *
from django.views.generic import ListView
from admin_app.serializers import SuggestedGroupSerializer, SuggestedGroupMemberSerializer, FinalGroupSerializer, FinalGroupMemberSerializer

class SuggestedGroupListCreateView(generics.ListCreateAPIView):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer

class SuggestedGroupMemberListCreateView(generics.ListCreateAPIView):
    queryset = SuggestedGroupMember.objects.all()
    serializer_class = SuggestedGroupMemberSerializer

class FinalGroupListCreateView(generics.ListCreateAPIView):
    queryset = FinalGroup.objects.all()
    serializer_class = FinalGroupSerializer

class FinalGroupMemberListCreateView(generics.ListCreateAPIView):
    queryset = FinalGroupMember.objects.all()
    serializer_class = FinalGroupMemberSerializer

class GroupListView(ListView):
    model = SuggestedGroup
    template_name = "admin_app/suggested_groups.html"  
    context_object_name = "suggested_groups"
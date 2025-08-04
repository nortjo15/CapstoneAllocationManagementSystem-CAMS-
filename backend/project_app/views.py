from rest_framework import generics
from .models import *
from .serializers import *

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectPreferenceListCreateView(generics.ListCreateAPIView):
    queryset = ProjectPreference.objects.all()
    serializer_class = ProjectPreferenceSerializer

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

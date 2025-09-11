from admin_app.serializers import ProjectSerializer, ProjectPreferenceSerializer
from admin_app.models import Project, ProjectPreference
from rest_framework import generics

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectPreferenceListCreateView(generics.ListCreateAPIView):
    queryset = ProjectPreference.objects.all()
    serializer_class = ProjectPreferenceSerializer

    
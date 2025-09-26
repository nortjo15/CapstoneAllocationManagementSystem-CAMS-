from admin_app.serializers import ProjectSerializer, ProjectPreferenceSerializer
from admin_app.models import Project, ProjectPreference
from rest_framework import viewsets

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectPreferencesViewSet(viewsets.ModelViewSet):
    queryset = ProjectPreference.objects.all()
    serializer_class = ProjectPreferenceSerializer

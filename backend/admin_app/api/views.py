# This is where you create your API's views. Instead of Django's regular views that return HTML,
# these views will return API responses. DRF provides powerful generic class-based views and
# ViewSets that handle common CRUD operations with minimal code. For example, a ModelViewSet
# can handle listing, creating, retrieving, updating, and deleting a resource automatically.

from rest_framework import viewsets
from ..models import *
from .serializers import *

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectPreferencesViewSet(viewsets.ModelViewSet):
    queryset = ProjectPreference.objects.all()
    serializer_class = ProjectPreferenceSerializer

class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

class SuggestedGroupViewSet(viewsets.ModelViewSet):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer

class SuggestedGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = SuggestedGroupMember.objects.all()
    serializer_class = SuggestedGroupMember

class FinalGroupViewSet(viewsets.ModelViewSet):
    queryset = FinalGroup.objects.all()
    serializer_class = FinalGroupSerializer

class FinalGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = FinalGroup.objects.all()
    serializer_class = FinalGroupMember

class DegreeViewSet(viewsets.ModelViewSet):
    queryset = Degree.objects.all()
    serializer_class = DegreeSerializer

class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer
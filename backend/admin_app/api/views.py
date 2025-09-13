# This is where you create your API's views. Instead of Django's regular views that return HTML,
# these views will return API responses. DRF provides powerful generic class-based views and
# ViewSets that handle common CRUD operations with minimal code. For example, a ModelViewSet
# can handle listing, creating, retrieving, updating, and deleting a resource automatically.

from rest_framework import viewsets
from ..models import *
from .serializers import *

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializers_class = ProjectSerializer

class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

class SuggestedGroupViewSet(viewsets.ModelViewSet):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer
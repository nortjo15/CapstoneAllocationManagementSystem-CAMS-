from rest_framework import viewsets
from admin_app.api.serializers import DegreeSerializer, MajorSerializer
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


from rest_framework import viewsets, status
from rest_framework.response import Response
from admin_app.api.serializers import DegreeSerializer, MajorSerializer
from django.core.paginator import Paginator
from django.db.models import Count
from admin_app.models import Degree, Major
from django.db.models import ProtectedError

class DegreeViewSet(viewsets.ModelViewSet):
    queryset = Degree.objects.all().order_by('name')
    serializer_class = DegreeSerializer

class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.select_related('degree').annotate(
        student_count=Count('students')
    ).order_by('degree__name', 'name')
    serializer_class = MajorSerializer

    def destroy(self, request, *args, **kwargs):
        major = self.get_object()

        try:
            major.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ProtectedError:
            error_message = {
                "detail":"This major cannot be deleted because it is assigned to one or more students"
            }
            return Response(error_message, status=status.HTTP_409_CONFLICT)

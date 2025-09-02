import django_filters

from rest_framework import generics
from student_app.models import Student
from student_app.serializers import *
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status

class StudentNotesUpdateAPIView(generics.UpdateAPIView):
    """
    PATCH /api/students/<pk>/notes/ → update notes for one student
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer  # reuse existing serializer

    def patch(self, request, *args, **kwargs):
        student = self.get_object()
        notes = request.data.get("notes", "")
        student.notes = notes
        student.save()
        return Response({"success": True, "notes": student.notes}, status=status.HTTP_200_OK)

class StudentFilter(filters.FilterSet):
    cwa_min = filters.NumberFilter(field_name="cwa", lookup_expr="gte")
    cwa_max = filters.NumberFilter(field_name="cwa", lookup_expr="lte")
    major = filters.NumberFilter(field_name="major__id")
    application_submitted = filters.BooleanFilter(field_name="application_submitted")
    allocated_group = filters.BooleanFilter(field_name="allocated_group")

    class Meta:
        model = Student
        fields = ["cwa_min", "cwa_max", "major", "application_submitted", "allocated_group"]

class StudentListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/students/  → list students
    POST /api/students/ → create student
    """
    queryset = Student.objects.all().select_related("major")
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFilter

class StudentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET     /api/students/<pk>/  → retrieve
    PUT     /api/students/<pk>/  → update
    PATCH   /api/students/<pk>/  → partial update
    DELETE  /api/students/<pk>/  → delete
    """
    queryset = Student.objects.all().select_related("major")
    serializer_class = StudentSerializer
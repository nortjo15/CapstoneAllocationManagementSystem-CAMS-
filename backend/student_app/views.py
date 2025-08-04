from rest_framework import generics
from .models import Student, GroupPreference
from .serializers import StudentSerializer, GroupPreferenceSerializer

class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'

class GroupPreferenceListCreateView(generics.ListCreateAPIView):
    queryset = GroupPreference.objects.all()
    serializer_class = GroupPreferenceSerializer

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Student
from .serializers import StudentSerializer, ProjectSerializer, MajorSerializer, FullFormSerializer
from admin_app.models import Project, Major, Round
from admin_app.api.serializers import RoundSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer

class RoundViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

# class RoundViewSet(viewsets.ModelViewSet):

class StudentApplicationView(APIView):
    def post(self, request):
        serializer = FullFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Application submitted successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
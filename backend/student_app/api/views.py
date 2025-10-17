from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Student
from .serializers import StudentSerializer, ProjectSerializer, MajorSerializer, FullFormSerializer
from admin_app.models import Project, Major, Round
from admin_app.api.serializers import RoundSerializer
from admin_app.models import AdminLog
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

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
            # Save and capture returned Student instance
            obj = serializer.save()

            # Resolve the student target
            student_obj = None
            if isinstance(obj, Student):
                student_obj = obj
            else:
                # Fallback lookup by student_id from payload
                sid = request.data.get('student_id')
                if sid:
                    student_obj = Student.objects.filter(student_id=sid).first()

            # Resolve or create the 'student' user for logging
            try:
                log_user = User.objects.filter(username='student').first()
                if log_user is None:
                    log_user = User(username='student', is_active=False)
                    log_user.set_unusable_password()
                    log_user.save()

                if student_obj is not None:
                    AdminLog.objects.create(
                        user=log_user,
                        action='STUDENT_APPLIED',
                        target_content_type=ContentType.objects.get_for_model(Student),
                        target_id=student_obj.pk,
                        notes=f"Student {student_obj.student_id} submitted application"
                    )
            except Exception as e:
                # Do not block submission on logging issues
                print(f"[AdminLog] STUDENT_APPLIED log skipped: {e}")

            return Response({"message": "Application submitted successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
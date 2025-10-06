import django_filters
import pprint

from rest_framework import generics
from student_app.models import *
from student_app.api.serializers import *
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
import csv
from io import TextIOWrapper
from django.db.models import Exists, OuterRef

class StudentImportAPIView(APIView):
    """
    POST /api/students/import/ → import students from CSV file
    """
    parser_classes = [MultiPartParser]  # handle file upload

    def post(self, request, *args, **kwargs):
        if "csv_file" not in request.FILES:
            return Response({"success": False, "error": "CSV file is required."}, status=400)

        csv_file = request.FILES["csv_file"]
        data_set = TextIOWrapper(csv_file.file, encoding="utf-8")
        reader = csv.DictReader(data_set)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]

        errors, created_count, updated_count = [], 0, 0

        required_columns = {"student_id", "name"}
        if not required_columns.issubset(set(reader.fieldnames)):
            return Response(
                {"success": False, "error": "CSV must contain 'student_id' and 'name' columns."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for i, row in enumerate(reader, start=1):
            if not any(row.values()):
                continue

            student_id = row.get("student_id", "").strip()
            name = row.get("name", "").strip()

            if not student_id.isdigit() or len(student_id) != 8:
                errors.append(f"Row {i}: student_id must be exactly 8 digits.")
                continue

            # Validate major
            major_obj = None
            major_name = row.get("major", "").strip()
            if major_name:
                try:
                    major_obj = Major.objects.get(name=major_name)
                except Major.DoesNotExist:
                    errors.append(f"Row {i}: Major '{major_name}' does not exist.")
                    continue

            # Validate CWA
            cwa = row.get("cwa")
            try:
                cwa = float(cwa) if cwa and cwa.strip() else None
                if cwa is not None and (cwa < 0 or cwa > 100):
                    errors.append(f"Row {i}: CWA must be between 0 and 100.")
                    continue
            except ValueError:
                errors.append(f"Row {i}: CWA must be a number.")
                continue

            email = row.get("email")
            notes = row.get("notes")

            student, created = Student.objects.update_or_create(
                student_id=student_id,
                defaults={
                    "name": name,
                    "cwa": cwa,
                    "major": major_obj,
                    "email": email,
                    "notes": notes,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        return Response(
            {
                "success": True,
                "created_count": created_count,
                "updated_count": updated_count,
                "errors": errors,
                "skipped_count": len(errors),
            },
            status=status.HTTP_200_OK,
        )

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

    major = filters.ModelMultipleChoiceFilter(
        field_name="major",
        queryset=Major.objects.all(),
        to_field_name="id"
    )
    
    application_submitted = filters.BooleanFilter(field_name="application_submitted")
    allocated_group = filters.BooleanFilter(field_name="allocated_group")

    # Filter by student_id (substring match)
    student_id = filters.CharFilter(field_name="student_id", lookup_expr="istartswith")

    class Meta:
        model = Student
        fields = ["cwa_min", "cwa_max", "major", "application_submitted", "allocated_group", "student_id"]

class StudentListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/students/  → list students
    POST /api/students/ → create student
    """
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFilter

    def get_queryset(self):
        print("allocated_group param:", self.request.query_params.get("allocated_group"))
        
        qs = (
            Student.objects.all()
            .select_related("major")
            .annotate(
                has_preferences=Exists(
                    ProjectPreference.objects.filter(student=OuterRef("pk"))
                ),
                has_teamPref=Exists(
                    GroupPreference.objects.filter(student=OuterRef("pk"))
                ),
            )
        )
       
        # Pre-fetch
        if self.request.method != "GET":
            qs = qs.prefetch_related(
                "preferences__project",
                "given_preferences__target_student",
                "received_preferences__student",
                )
        return qs

    # Use lightweight serializer for GET requests
    def get_serializer_class(self):
        if self.request.method == "GET":
            return StudentListSerializer   
        return StudentSerializer          

class StudentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET     /api/students/<pk>/  → retrieve
    PUT     /api/students/<pk>/  → update
    PATCH   /api/students/<pk>/  → partial update
    DELETE  /api/students/<pk>/  → delete
    """
    queryset = (
        Student.objects.all()
        .select_related("major")
        .prefetch_related(
            "preferences__project",
            "given_preferences__target_student",
            "received_preferences__student",
        )
    )
    
    serializer_class = StudentSerializer
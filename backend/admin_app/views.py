import csv
from rest_framework import generics
from .models import AdminLog
from .serializers import AdminLogSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from student_app.models import Student 
from .studentFilters import StudentFilter
from django.views.decorators.http import require_http_methods
from .forms import addStudentForm, importStudentForm
from django.http import JsonResponse
from io import TextIOWrapper
from .models import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render 
from .serializers import *

class AdminLogListCreateView(generics.ListCreateAPIView):
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer

def test_view(request):
    return render(request, "base.html")

def round_view(request):
   return render(request, "rounds.html")

class SuggestedGroupListCreateView(generics.ListCreateAPIView):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer

class SuggestedGroupMemberListCreateView(generics.ListCreateAPIView):
    queryset = SuggestedGroupMember.objects.all()
    serializer_class = SuggestedGroupMemberSerializer

class FinalGroupListCreateView(generics.ListCreateAPIView):
    queryset = FinalGroup.objects.all()
    serializer_class = FinalGroupSerializer

class FinalGroupMemberListCreateView(generics.ListCreateAPIView):
    queryset = FinalGroupMember.objects.all()
    serializer_class = FinalGroupMemberSerializer


# Adding a basic students view page 
# Ensures only authenticated users can access it 
@login_required
def student_view(request):
    filter_object = StudentFilter(request.GET) #Initialise Filter with GET params
    students = filter_object.get_filtered_queryset() # Apply filters to queryset
    degree_major_pairs = filter_object.get_degree_major_pairs()

    # List of string representing current filter selections
    selected_pairs = request.GET.getlist('degree_major')
    
    # Persist CWA Min/Max Values in the selection
    cwa_min = request.GET.get('cwa_min', '')
    cwa_max = request.GET.get('cwa_max', '')
    
    # Booleans 
    application_submitted = request.GET.get('application_submitted', '')
    group_status  = request.GET.get('group_status', 'all').lower()

    # Create student form
    add_form = addStudentForm()
    import_form = importStudentForm()
        
    context = {
        'students': students,
        'degree_major_pairs': degree_major_pairs,
        'selected_pairs': selected_pairs,
        'cwa_min': cwa_min,
        'cwa_max': cwa_max,
        'application_submitted': application_submitted,
        'group_status': group_status,
        'add_form': add_form,
        'import_form': import_form,
    } 
    return render(request, 'student_view.html', context)

#Settings view - user needs to be logged in
@login_required
def settings_view(request):
    return render(request, 'settings.html')
    

@require_http_methods(["GET", "POST"])
@login_required
def student_create(request):
    if request.method == "POST":
        form = addStudentForm(request.POST)
        if form.is_valid():
            # Set Default values
            student = form.save(commit=False) # Don't add yet 
            student.application_submitted = False 
            student.allocated_group = False
            student.save() 

            # Handle AJAX request 
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success":True})
            # Normal form submission redirect
            return redirect('admin_dashboard:admin_student_list')
    
        else: 
            # Return errors if form is invalid
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)

    else: 
        # GET request -> show the empty form
        form = addStudentForm()

    return render(request, 'admin_app/student_create_modal.html', {'form': form})

@require_http_methods(["GET", "POST"])
@login_required 
def admin_student_import(request):
    if request.method == "POST":
        form = importStudentForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']

            # Convert uploaded file to text fo csv.reader
            data_set = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(data_set) #access columns by name
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            # Avoid whitespace issues

            errors = []
            created_count = 0
            updated_count = 0

            # Check required columns
            required_columns = {'student_id', 'name'}
            if not required_columns.issubset(set(reader.fieldnames)):
                errors.append("CSV must contain 'student_id' and 'name' columns.")

                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({
                        "success": False,
                        "created_count": 0,
                        "skipped_count": 0,
                        "errors": errors,
                        'updated_count': 0
                    })
                
                # Non-AJAX
                return render(request, 'admin_app/student_importCSV.html', {
                    'form': form,
                    'errors': errors,
                    'created_count': 0,
                    'skipped_count': 0,
                    'updated_count': 0
                })
            

            for i, row in enumerate(reader, start=1):
                # Skip completely empty rows
                if not any(row.values()):
                    continue

                #Validation 
                student_id = row.get('student_id', '').strip()
                name = row.get('name', '').strip()
                # Needs to be adjusted for full name and last name

                # Store errors for invalid lines 
                if not student_id.isdigit() or len(student_id) != 8:
                    errors.append(f"Row {i}: student_id must be exactly 8 digits.")
                    continue 

                # Foreign Key Validation for Major
                major_name = row.get('major', '').strip()
                major_obj = None 
                if major_name: 
                    try: 
                        major_obj = Major.objects.get(name=major_name)
                    except Major.DoesNotExist:
                        errors.append(f"Row {i}: Major '{major_name}' does not exist.")
                        continue

                # Optional fields
                cwa = row.get('cwa')
                
                try:
                    cwa = float(cwa) if cwa and cwa.strip() else None
                    
                    if cwa is not None and (cwa < 0 or cwa > 100):
                        errors.append(f"Row {i}: CWA must be between 0 and 100")
                        continue

                except ValueError:
                    errors.append(f"Row {i}: CWA must be a number.")

                email = row.get('email')
                notes = row.get('notes')

                if Student.objects.filter(student_id=student_id.strip()).exists():
                    student = Student.objects.get(student_id=student_id)
                    # Update this student
                    if name: 
                        student.name = name
                    if cwa is not None: 
                        student.cwa = cwa 
                    if major_obj is not None: 
                        student.major = major_obj
                    if email:
                        student.email = email
                    if notes: 
                        student.notes = notes 
                    student.save()

                    updated_count += 1
                    continue

                # Create Student
                Student.objects.create(
                    student_id=student_id,
                    name=name,
                    cwa=cwa if cwa else None,
                    major=major_obj if major_obj else None, 
                    email=email if email else None, 
                    notes=notes if notes else None
                )
                created_count += 1 

            skipped_count = len(errors)

            # AJAX Response
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": created_count + updated_count > 0,
                    "errors": errors,
                    "created_count": created_count,
                    "skipped_count": skipped_count,
                    'updated_count': updated_count
                })
            
            # Normal form response
            if errors:
                return render(request, 'admin_app/student_importCSV.html', {
                    'form': form,
                    'errors': errors,
                    'created_count': created_count,
                    'skipped_count': skipped_count,
                    'updated_count': updated_count
                })
            
            messages.success(request, f"{created_count} students imported successfully!")
            return redirect('admin_dashboard:admin_student_list')
        
        else:
            #Form Invalid
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
        
    else: 
        # Form Valid
        form = importStudentForm()

    return render(request, 'admin_app/student_importCSV.html', {'form': form})

TEMPLATE_MAP = {
    "round_closed": "emails/round_closed.txt",
    "application_success": "emails/application_success.txt",
    "allocation_released": "emails/allocation_released.txt",
    "generic_notice": "emails/generic_notice.txt",
}


class SendNotificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        """
        POST JSON:
        {
            "subject": "Your Subject Here",
            "template_key": "round_closed",
            "audience": "students" | "hosts" | "final_group" | "custom",
            "round_name": "Round 1",
            "project_name": "Project X",
            "final_group_id": 5,
            "emails": ["test@example.com"],
            "message_body": "Optional extra message"
        }
        """
        data = request.data
        subject = data.get("subject")
        template_key = data.get("template_key")
        audience = data.get("audience")

        if not subject or not template_key or not audience:
            return Response({"error": "Missing required fields"}, status=400)

        template_path = TEMPLATE_MAP.get(template_key)
        if not template_path:
            return Response({"error": f"Unknown template_key '{template_key}'"}, status=400)

        context = {
            "round_name": data.get("round_name", ""),
            "project_name": data.get("project_name", ""),
            "message_body": data.get("message_body", ""),
        }

        recipients = []
        if audience == "students":
            recipients = list(
                Student.objects.exclude(email__isnull=True).exclude(email="").values_list("email", flat=True)
            )
        elif audience == "hosts":
            recipients = list(
                Project.objects.exclude(host_email__isnull=True).exclude(host_email="").values_list("host_email", flat=True)
            )
        elif audience == "final_group":
            if not data.get("final_group_id"):
                return Response({"error": "final_group_id required for audience=final_group"}, status=400)
            members = FinalGroupMember.objects.filter(final_group_id=data["final_group_id"]).select_related("student")
            recipients = [m.student.email for m in members if m.student.email]
        elif audience == "custom":
            recipients = data.get("emails", [])
        else:
            return Response({"error": "Invalid audience"}, status=400)

        if not recipients:
            return Response({"error": "No recipients found"}, status=400)

        message = render_to_string(template_path, context)
        sent = 0
        for email in recipients:
            sent += send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

        return Response({"ok": True, "sent": sent})

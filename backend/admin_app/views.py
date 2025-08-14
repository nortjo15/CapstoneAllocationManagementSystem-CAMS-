import csv
from rest_framework import generics
from .models import AdminLog
from .serializers import AdminLogSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, UserCreationForm
from django.contrib.auth import login 
from django.contrib import messages
from student_app.models import Student 
from .studentFilters import StudentFilter
from django.views.decorators.http import require_http_methods
from .forms import addStudentForm, importStudentForm
from django.http import JsonResponse
from io import TextIOWrapper
from project_app.models import Major

from django.contrib.auth.decorators import login_required
from django.shortcuts import render 

class AdminLogListCreateView(generics.ListCreateAPIView):
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer

#View for registering a user, may not need this
def register_view(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("posts:list")
    else:
        form = UserCreationForm()
    return render(request, "", {"form": form})

#View for logging in user
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # LOGIN 
            user = form.get_user() # Get validated user 
            login(request, user)   # Log the user in 
            return redirect("login_success") # Changed to use URL name, not template filename
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

@login_required
def login_success(request):
    return render(request, "login_success.html")

def test_view(request):
    return render(request, "base.html")

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
            return redirect('admin_student_list')
    
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
            duplicate_count = 0

            for i, row in enumerate(reader, start=1):
                #Validation 
                student_id = row.get('student_id', '').strip()
                name = row.get('name', '').strip()
                # Needs to be adjusted for full name and last name

                if not student_id or not name: 
                    errors.append(f"Row {i}: student_id and name are required.")
                    continue 

                 # Store errors for invalid lines 
                if not student_id.isdigit() or len(student_id) != 8:
                    errors.append(f"Row {i}: student_id must be exactly 8 digits.")
                    continue 

                if Student.objects.filter(student_id=student_id).exists():
                    errors.append(f"Row {i}: student_id {student_id} already exists.")
                    duplicate_count += 1
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

                if cwa is not None and (cwa < 0 or cwa > 100):
                    errors.append(f"Row {i}: CWA must be between 0 and 100")
                    continue
                
                try:
                    cwa = float(cwa) if cwa and cwa.strip() else None
                except ValueError:
                    errors.append(f"Row {i}: CWA must be a number.")

                major = row.get('major')
                email = row.get('email')
                notes = row.get('notes')

                # Create Student
                Student.objects.create(
                    student_id=student_id,
                    name=name,
                    cwa=cwa if cwa else None,
                    major=major if major else None, 
                    email=email if email else None, 
                    notes=notes if notes else None
                )
                created_count += 1 

            # Get Totals
            total_rows = created_count + len(errors)
            skipped_count = len(errors)

            # AJAX Response
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": created_count > 0,
                    "errors": errors,
                    "created_count": created_count,
                    "skipped_count": skipped_count,
                    "duplicate_count": duplicate_count,
                    "total_rows": total_rows
                }, status=200 if len(errors) == 0 else 400)
            
            # Normal form response
            if errors:
                return render(request, 'student_importCSV.html', {
                    'form': form,
                    'errors': errors,
                    'created_count': created_count
                })
            
            messages.success(request, f"{created_count} students imported successfully!")
            return redirect('admin_student_list')
        
        else:
            #Form Invalid
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
        
    else: 
        # Form Valid
        form = importStudentForm()

    return render(request, 'admin_app/student_importCSV.html', {'form': form})
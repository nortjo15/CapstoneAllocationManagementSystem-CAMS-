from rest_framework import generics
from .models import AdminLog
from .serializers import AdminLogSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, UserCreationForm
from django.contrib.auth import login 
from student_app.models import Student 
from .studentFilters import StudentFilter
from django.views.decorators.http import require_http_methods
from .forms import addStudentForm
from django.http import JsonResponse

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
        
    context = {
        'students': students,
        'degree_major_pairs': degree_major_pairs,
        'selected_pairs': selected_pairs,
        'cwa_min': cwa_min,
        'cwa_max': cwa_max,
        'application_submitted': application_submitted,
        'group_status': group_status,
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
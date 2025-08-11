from rest_framework import generics
from .models import AdminLog
from .serializers import AdminLogSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, UserCreationForm
from django.contrib.auth import login 
from student_app.models import Student 
from .studentFilters import StudentFilter

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

    context = {
        'students': students,
        'degree_major_pairs': degree_major_pairs,
        'selected_degree': request.GET.get('degree', ''),
        'selected_major': request.GET.get('major', ''),
    } 
    return render(request, 'student_view.html', context)
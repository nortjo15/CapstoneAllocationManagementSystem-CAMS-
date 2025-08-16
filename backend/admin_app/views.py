from rest_framework import generics
from .models import AdminLog
from .serializers import AdminLogSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from student_app.models import Student 

from django.contrib.auth.decorators import login_required
from django.shortcuts import render 

class AdminLogListCreateView(generics.ListCreateAPIView):
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer

#View for registering a user, may not need this
def register_view(request):
    if request.method == "POST":               # validate request method is post
        form = UserCreationForm(request.POST)  # Create a form instance with the submitted data
        if form.is_valid():
            form.save()
        return redirect("login_success")                     #if user registration passes, redirect to login success page
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

#View for logging in user
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # LOGIN 
            user = form.get_user()                          # Get validated user 
            login(request, user)                            # Log the user in 
            return redirect("login_success")                # Changed to use URL name, not template filename
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

@login_required
def login_success(request):
    return render(request, "login_success.html")

#View to log the user out
def logout_view(request):
    logout(request)
    return redirect("login")

def test_view(request):
    return render(request, "base.html")

# Adding a basic students view page 
# Ensures only authenticated users can access it 
@login_required
def student_view(request):
    sort_param = request.GET.get('sort', '') # sort paramater or an empty string 

    if sort_param == 'cwa_desc':
        students = Student.objects.order_by('-cwa')
    elif sort_param == 'cwa:asc':
        students = Student.objects.order_by('cwa')
    else:
        students = Student.objects.all()

    return render(request, 'student_view.html', {'students': students})

#Settings view - user needs to be logged in
@login_required
def settings_view(request):
    return render(request, 'settings.html')

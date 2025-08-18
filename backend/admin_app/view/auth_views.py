from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

#View for registering a user, may not need this
def register_view(request):
    if request.method == "POST":               # validate request method is post
        form = UserCreationForm(request.POST)  # Create a form instance with the submitted data
        if form.is_valid():
            form.save()
        return redirect("admin_dashboard:login_success") #if user registration passes, redirect to login success page
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

#View for logging in user
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # LOGIN 
            user = form.get_user()             # Get validated user 
            login(request, user)               # Log the user in 
            return redirect("admin_dashboard:login_success")   # Changed to use URL name, not template filename
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

@login_required
def login_success(request):
    return render(request, "login_success.html")

#View to log the user out
def logout_view(request):
    logout(request)
    return redirect("admin_dashboard:login")
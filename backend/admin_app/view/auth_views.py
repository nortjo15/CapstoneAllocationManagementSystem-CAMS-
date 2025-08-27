from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from admin_app.models import AdminLog
from django.contrib.contenttypes.models import ContentType


#View for registering a user, may not need this
def register_view(request):
    if request.method == "POST":               # validate request method is post
        form = UserCreationForm(request.POST)  # Create a form instance with the submitted data
        if form.is_valid():
            newUser = form.save()

            # Log the creation of a new user in the admin log
            user_content_type = ContentType.objects.get_for_model(newUser)
            AdminLog.objects.create(
                user=request.user, # The currently logged-in admin user
                action='USER_CREATED',
                target_content_type=user_content_type,
                target_id=newUser.id,
                notes=f"New user created: {newUser.username}"
            )
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
    # Log action - user login
    user_content_type = ContentType.objects.get_for_model(request.user)
    AdminLog.objects.create(
        user=request.user, # The currently logged-in admin user
        action='LOGIN',
        target_content_type=user_content_type,
        target_id=request.user.id,
        notes=f"user login: {request.user.username}"
    )
    return render(request, "login_success.html")

#View to log the user out
@login_required
def logout_view(request):
    logout(request)
    # Log action - user logout
    user_content_type = ContentType.objects.get_for_model(request.user)
    AdminLog.objects.create(
        user=request.user, # The currently logged-in admin user
        action='LOGOUT',
        target_content_type=user_content_type,
        target_id=request.user.id,
        notes=f"user logout: {request.user.username}"
    )
    return redirect("admin_dashboard:login")
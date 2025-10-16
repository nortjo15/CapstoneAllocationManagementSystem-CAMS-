from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, UserCreationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from admin_app.models import AdminLog
from django.contrib.contenttypes.models import ContentType

@login_required
def register_view(request):
    if request.method == "POST":               
        form = UserCreationForm(request.POST)  
        if form.is_valid():
            newUser = form.save()

            user_content_type = ContentType.objects.get_for_model(newUser)
            AdminLog.objects.create(
                user=request.user, 
                action='USER_CREATED',
                target_content_type=user_content_type,
                target_id=newUser.id,
                notes=f"New user created: {newUser.username}"
            )
        return redirect("admin_dashboard:login_success") 
    
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()            
            login(request, user)             
            return redirect("admin_dashboard:login_success")  
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

@login_required
def login_success(request):
    user_content_type = ContentType.objects.get_for_model(request.user)
    AdminLog.objects.create(
        user=request.user, 
        action='LOGIN',
        target_content_type=user_content_type,
        target_id=request.user.id,
        notes=f"user login: {request.user.username}"
    )
    return render(request, "login_success.html")

@login_required
def logout_view(request):
    
    user_content_type = ContentType.objects.get_for_model(request.user)
    AdminLog.objects.create(
        user=request.user, 
        action='LOGOUT',
        target_content_type=user_content_type,
        target_id=request.user.id,
        notes=f"user logout: {request.user.username}"
    )
    logout(request)
    return redirect("admin_dashboard:login")

@login_required
def change_password(request):
    if request.method == 'POST':
        form = AdminPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            return redirect('password_change_done')
    else:
        form = AdminPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

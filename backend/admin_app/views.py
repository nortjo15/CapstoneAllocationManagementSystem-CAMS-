from rest_framework import generics
from .models import AdminLog
from .serializers import AdminLogSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, UserCreationForm


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
            return redirect("login_success.html")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def login_success(request):
    return render(request, "login_success.html")

def test_view(request):
    return render(request, "test.html")
# Create your views here.

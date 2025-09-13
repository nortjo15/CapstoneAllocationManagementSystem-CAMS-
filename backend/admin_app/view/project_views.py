from admin_app.serializers import ProjectSerializer
from admin_app.models import Project, ProjectPreference
from django.shortcuts import render, redirect
from rest_framework import generics
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from django.views.generic import TemplateView

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

@login_required
def project_view(request):
   return render(request, "project_dashboard.html")



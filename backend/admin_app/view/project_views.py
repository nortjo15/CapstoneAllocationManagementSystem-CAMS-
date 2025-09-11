from admin_app.serializers import ProjectSerializer, ProjectPreferenceSerializer
from admin_app.models import Project, ProjectPreference
from admin_app.forms.project_forms import addProjectForm
from django.shortcuts import render, redirect
from rest_framework import generics
from django.contrib.auth.decorators import login_required

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectPreferenceListCreateView(generics.ListCreateAPIView):
    queryset = ProjectPreference.objects.all()
    serializer_class = ProjectPreferenceSerializer

@login_required
def project_view(request):
   return render(request, "project_list.html")

def addProject(request):
    if request.method == 'POST':
        form = addProjectForm(request.POST)
        if form.is_Valid():
            form.save()
            #return redirect('project_list')
    else:
        form = addProjectForm()
    return render(request, 'project_list.html', {'form':form})


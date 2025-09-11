from django import forms 
from admin_app.models import Project

class addProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
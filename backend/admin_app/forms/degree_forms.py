from django import forms
from admin_app.models import Degree, Major

class DegreeForm(forms.ModelForm):
    class Meta:
        model = Degree
        fields = ["name"]

class MajorForm(forms.ModelForm):
    class Meta:
        model = Major
        fields = ["degree", "name"]

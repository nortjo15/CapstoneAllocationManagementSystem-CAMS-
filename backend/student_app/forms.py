from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from student_app.models import Student, GroupPreference
from admin_app.models import Project, ProjectPreference, Major
import json
import re

class ProjectApplicationForm(forms.Form):
    student_id = forms.CharField(label="Student ID", max_length=8, required=True, widget=forms.TextInput(attrs={'pattern': r'\d{8}', 'title': 'Enter an 8-digit Student ID'}))
    email = forms.EmailField(label="Student Email", required=True, widget=forms.EmailInput(attrs={'pattern': r'[a-zA-Z0-9._%+-]+@[a-zA-Z]+\.(student\.curtin\.edu\.au)$', 'title': 'Enter a Curtin student email (e.g., firstname.lastname@student.curtin.edu.au)'}))
    major = forms.ModelChoiceField(label="Major", queryset=Major.objects.all(), required=True)
    cwa = forms.DecimalField(label="cwa", max_digits=5, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'step': '1.00', 'min': '0', 'max': '100'}))
    resume = forms.FileField(label="Resume", required=False, validators=[FileExtensionValidator(allowed_extensions=['pdf'])], widget=forms.FileInput(attrs={'accept': 'application/pdf'}))
    terms = forms.BooleanField(label="Agree to terms", required=True)
    project_preference = forms.CharField(widget=forms.HiddenInput(), required=False)
    desirable_students = forms.CharField(widget=forms.HiddenInput(), required=False)
    undesirable_students = forms.CharField(widget=forms.HiddenInput(), required=False)

    #Field validators
    def clean_student_id(self):
        student_id = self.cleaned_data.get("student_id")
        if not student_id or not re.match(r'^\d{8}$', student_id):
            raise ValidationError("Student ID must be exactly 8 digits")
        return student_id
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@student\.curtin\.edu\.au$', email):
            raise ValidationError("Please enter a valid Curtin Student Email E.g. john.smith@student.curtin.edu.au")
        return email
    
    # def clean_resume(self):
    #     resume = self.cleaned_data.get("resume")

    #     if not resume:
    #         raise ValidationError("Please upload a resume file")
    #     fileName = resume.name
    #     if not re.match(r'^[A-Za-z]+-[A-Za-z]+_\d{8}_resume$', fileName):
    #         raise ValidationError("Filename must be in the format: FirstName-LastName_studentId_resume")
    #     if not filename.lower().endswith('.pdf'):
    #         raise ValidationError("You can only upload PDF files")

    # def clean(self):
    #     cleaned_data = super().clean()

    #     try: 
    #         project_ids = json.loads(self.data.get("project_preference", "[]"))
    #         desirable_ids = json.loads(self.data.get("desirable_students", "[]"))
    #         undesirable_ids = json.loads(self.data.get("undesirable_students","[]"))
    #     except json.JSONDecoderError:
    #         raise ValidationError("Invalid JSON input in Form")
        
    #     #Validate project preferences
    #     if not (3 < len(project_ids) > 6):
    #         raise ValidationError("Please select between 3 and 6 project preferences")
    #     if len(set(project_ids)) < len(project_ids):
    #         raise ValidationError("Duplicate project preferences are not allowed")
    #     cleaned_data["projects"] = Project.objects.filter(id__in=project_ids)

    #     #Validate group preferences
    #     if set(desirable_ids) & set(undesirable_ids):
    #         raise ValidationError("A student cannot be both desirable and undesirable.")

    #     if len(set(desirable_ids)) < len(desirable_ids):
    #         raise ValidationError("Duplicate group preferences are not allowed")
    #     cleaned_data["desirable_students"] = Student.objects.filter(student_id__in=desirable_ids)

    #     if len(set(undesirable_ids)) < len(undesirable_ids):
    #         raise ValidationError("Duplicate group preferences are not allowed")
    #     cleaned_data["undesirable_students"] = Student.objects.filter(student_id__in=undesirable_ids)

    #     return cleaned_data
    
    # def save(self):
    #     data = self.cleaned_data
    #     student = Student.objects.get(student_id=data['student_id'])
    #     student.email = data['email']
    #     student.major = data['major']
    #     student.cwa = data['cwa']
    #     student.resume = data['resume']
    #     student.application_submitted = True
    #     student.save()

    #     #Save project preferences
    #     ProjectPreference.objects.filter(student=student).delete()
    #     for rank, project_id in enumerate(data["projects"], start=1):
    #         ProjectPreference.objects.create(student=student, project=project, rank=rank)

    #     #Save group preferences
    #     GroupPreference.objects.filter(student=student).delete()
    #     for s in data["desirable_students"]:
    #         GroupPreference.objects.create(student=student, target_student=s, preference_type='like')
    #     for s in data["undesirable_students"]:
    #         GroupPreference.objects.create(student=student, target_student=s, preference_type='avoid')    
        
    #     return student

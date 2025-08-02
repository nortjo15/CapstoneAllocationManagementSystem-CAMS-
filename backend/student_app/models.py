from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Student Information 
# StudentID is the primary key 
# name, major, application_submitted not allowed to be null 
# cwa, email, notes, cv, resume allowed to be null fields 
class Student(models.Model):
    student_id = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=100, null=False)
    cwa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    major = models.CharField(max_length=100, null=False)
    application_submitted = models.BooleanField(default=False)
    email = models.EmailField(unique=True, null=True)
    notes = models.TextField(null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    cv = models.FileField(upload_to='cvs/', null=True, blank=True)
    # Settings.py should configure media settings 

    def __str__(self):
        return f"{self.student_id} - {self.name}"
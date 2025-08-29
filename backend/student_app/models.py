from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError 

# Student Information 
# StudentID is the primary key 
# name, major, application_submitted not allowed to be null 
# cwa, email, notes, cv, resume allowed to be null fields 
class Student(models.Model):
    student_id = models.CharField(max_length=8, primary_key=True, db_index=True)
    name = models.CharField(max_length=100, null=False)
    cwa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        db_index=True, 
        blank=True
    )
    major = models.ForeignKey('admin_app.Major', on_delete=models.PROTECT, null=True, related_name='students')
    application_submitted = models.BooleanField(default=False)
    allocated_group = models.BooleanField(default=False)
    email = models.EmailField(unique=True, null=True)
    notes = models.TextField(null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    #cv = models.FileField(upload_to='cvs/', null=True, blank=True)
    # Settings.py should configure media settings 

    def __str__(self):
        return f"{self.student_id} - {self.name}"
    
# Stores information on a Student's Group Preferences 
# Can access who a student has preferred or avoided (given preferences)
# Can access who has preferred or avoided this student (received preferences)
class GroupPreference(models.Model):
    PREFERENCE_TYPES = [
        ('like', 'Would Like to Work With'),
        ('avoid', 'Would Prefer to Avoid'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='given_preferences')
    target_student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='received_preferences')
    preference_type = models.CharField(max_length=10, choices=PREFERENCE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'target_student')

    # Student should not be able to preference themselves
    def clean(self):
        if self.student_id is not None and self.target_student_id is not None:
            if self.student_id == self.target_student_id:
                raise ValidationError("A student cannot preference themselves.")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} → {self.target_student} ({self.preference_type})"


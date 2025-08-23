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
    
# Contains any unit contacts for the capstone unit
# This can be used to store information about unit coordinators, administrative contacts, etc.
# More for later, in case there is more than one manager
class UnitContacts(models.Model):
    id = models.serial(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True, null=False)
    phone = models.CharField(max_length=15)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#Section dividers for Capstone Information information
# Can be used to create subsections for information
class CapstoneInformationSection(models.Model):
    id = models.serial(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    parent_section = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subsections')
    order = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Stores actual information that is displayed on Capstone Information pages
# Each section can have multiple pieces of content, and each piece can be pinned or have a priority
# Content can be published, archived or in draft state
class CapstoneInformationContent(models.Model):
    id = models.serial(primary_key=True)
    section_id = models.ForeignKey(CapstoneInformationSection, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200, null=False)
    body = models.TextField(null=False)
    status = models.CharField(max_length=20, default= 'published', 
        choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
        ])
    pinned = models.BooleanField(default=False)
    priority = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)    # Content needs to be converted to archived after this date
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.charField(max_length=120, null=False)


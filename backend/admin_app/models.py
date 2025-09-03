from django.db import models
from django.contrib.auth.models import User 
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# from networkx import project
from student_app.models import Student
from django.core.validators import MinValueValidator

# Links to Django built-in User model (admin accounts)

# ADminLog links to any model instance (Student, Project, SuggestedGroup)
# using GenericForeignKey. Allows flexible logging for edits made across
# different parts of the system. 

# Stores
# - content_type: model class of object
# - object_id: primary key of the instance 
# - target: relation bcombining the two, allows easy access to object
class AdminLog(models.Model): 
    ACTION_CHOICES = [ # Expand as needed
        ('CREATE', 'Create'),
        ('EDIT', 'Edit'),
        ('DELETE', 'Delete'),
        ('ASSIGN', 'Assign Student'),
        ('USER_CREATED', 'User Created'),
        ('LOGIN', 'User Logged In'),
        ('LOGOUT', 'User Logged Out')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes=models.TextField(null=True, blank=True)

    # Generic relation to any target model
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveBigIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_content_type', 'target_id')

    def __str__(self):
        return f"{self.user.username} - {self.action} {self.target} @ {self.timestamp}"
    
# Capstone Rounds
class Round(models.Model):
    round_id = models.AutoField(primary_key=True)
    round_name = models.CharField(max_length=100, null=False)
    projects = models.ManyToManyField(
        'Project',
        related_name='rounds',
        blank=True,
    )

    # Admin will manually activate a round by clicking a GUI button
    is_active = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('upcoming', 'Upcoming'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    
    open_date = models.DateTimeField()
    close_date = models.DateTimeField()

    def __str__(self):
        return f"Round {self.round_id} - {self.status}"


# Project Information
# Primary key is configured and incremented automatically 
# Title & Description can be null, Capacity cannot be
class Project(models.Model):
    project_id = models.AutoField(primary_key=True) #Automatic PK, increments
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True, blank=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    host_name = models.CharField(max_length=100, null=False)
    host_email = models.EmailField(null=False)
    host_phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.project_id} - {self.title}"
    
# Stores information about a Student's Project Preference
# Foreign Key to Student & Project
class ProjectPreference(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    rank = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta: 
        unique_together = (
            ('student', 'rank'), # multiple projects can't be given the same rank
            ('student', 'project'), # prevent duplicate preferences
        )
        ordering = ['rank']

    def __str__(self):
        return f"{self.student} - {self.project} (Rank {self.rank})"
    
# Stores information on a SuggestedGroup
# Can be Strong, medium or weak (adjust for further functionality as needed  later)
class SuggestedGroup(models.Model):
    STRENGTH_CHOICES = [
        ('strong', 'Strong Group'),
        ('medium', 'Medium Group'),
        ('weak', 'Weak Group'),
    ]

    suggestedgroup_id = models.AutoField(primary_key=True)
    strength = models.CharField(max_length=6, choices=STRENGTH_CHOICES)
    notes=models.TextField(null=True, blank=True)
    name=models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self):
        return f"SuggestedGroup {self.suggestedgroup_id} ({self.get_strength_display()})"
    
# Stores information on each member of a SuggestedGroup
# Can be used to track students already part of suggestions 
class SuggestedGroupMember(models.Model):
    suggested_group = models.ForeignKey(SuggestedGroup, on_delete=models.CASCADE, related_name='members')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='suggested_groups')
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta: 
        unique_together = ('suggested_group', 'student')
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student} in {self.suggested_group}"
    
# Similar to SuggestedGroup but a finalised one
class FinalGroup(models.Model):
    finalgroup_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='final_groups')
    created_by_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    name=models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self):
        return f"FinalGroup {self.finalgroup_id} for {self.project.title}"
    
class FinalGroupMember(models.Model):
    final_group = models.ForeignKey(FinalGroup, on_delete=models.CASCADE, related_name='members')
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='final_group_member')

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student} in {self.final_group}"

# Allow Django to handle the primary key, just use foreign keys when necessary
class Degree(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Major(models.Model):
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='majors')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('degree', 'name') #Same major name can exist under different degrees

    def __str__(self):
        return f"{self.name} ({self.degree.name})"

# Contains any unit contacts for the capstone unit
# This can be used to store information about unit coordinators, administrative contacts, etc.
# More for later, in case there is more than one manager
class UnitContacts(models.Model):
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True, null=False)
    phone = models.CharField(max_length=15)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#Section dividers for Capstone Information information
# Can be used to create subsections for information
class CapstoneInformationSection(models.Model):
    name = models.CharField(max_length=100, null=False)
    parent_section = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subsections')
    order = models.IntegerField(default=0, validators=[MinValueValidator(0)]) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

# Stores actual information that is displayed on Capstone Information pages
# Each section can have multiple pieces of content, and each piece can be pinned or have a priority
# Content can be published, archived or in draft state
class CapstoneInformationContent(models.Model):
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
    author = models.CharField(max_length=120, null=False)

    class Meta:
        indexes = [
            models.Index(fields=["section_id", "-pinned", "priority", "-published_at"]),
            models.Index(fields=["status", "published_at", "expires_at"]),
        ]
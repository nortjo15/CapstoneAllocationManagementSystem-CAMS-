from django.db import models
from student_app.models import Student
from django.core.validators import MinValueValidator

# Project Information
# Primary key is configured and incremented automatically 
# Title & Description can be null, Capacity cannot be
class Project(models.Model):
    project_id = models.AutoField(primary_key=True) #Automatic PK, increments
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True, blank=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.project_id} - {self.title}"
    
# Stores information about a Student's Project Preference
# Foreign Key to Student & Project
class ProjectPreference(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    rank = models.PositiveBigIntegerField()

    class Meta: 
        unique_together = ('student', 'rank') # multiple projects can't be given the same rank
        ordering = ['rank']

    def __str__(self):
        return f"{self.student} - {self.project} (Rank {self.rank})"
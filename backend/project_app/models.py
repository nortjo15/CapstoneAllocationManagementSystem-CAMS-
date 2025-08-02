from django.db import models
from django.core.validators import MinValueValidator

# Project Information
class Project(models.Model):
    project_id = models.AutoField(primary_key=True) #Automatic PK, increments
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True, blank=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.project_id} - {self.title}"
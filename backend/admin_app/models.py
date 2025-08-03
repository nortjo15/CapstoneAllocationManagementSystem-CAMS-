from django.db import models
from django.contrib.auth.models import User 
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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
        ('ASSIGN', 'Assign Student')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes=models.TextField(null=True, blank=True)

    # Generic relation to any target model
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_object_id = models.PositiveBigIntegerField()
    target = GenericForeignKey('target_content_type', 'target_object_id')

    def __str__(self):
        return f"{self.user.username} - {self.action} {self.target} @ {self.timestamp}"
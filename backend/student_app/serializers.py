from rest_framework import serializers
from student_app.models import *
from admin_app.models import *

class MajorSerializer(serializers.ModelSerializer):
    """Serializer for Major model (minimal fields needed for display)."""
    class Meta:
        model = Major
        fields = ["id", "name"] 

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ["student_id"]

class GroupPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPreference
        fields = '__all__'

class ProjectPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPreference
        fields = '__all__'

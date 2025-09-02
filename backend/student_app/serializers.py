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

        def create(self, validated_data):
            # enforce defaults
            validated_data.setdefault("application_submitted", False)
            validated_data.setdefault("allocated_group", False)
            return super().create(validated_data)

class GroupPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPreference
        fields = '__all__'

class ProjectPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPreference
        fields = '__all__'

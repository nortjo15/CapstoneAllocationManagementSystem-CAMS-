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

    def create(self, validated_data):
        # enforce defaults
        validated_data.setdefault("application_submitted", False)
        validated_data.setdefault("allocated_group", False)
        return super().create(validated_data)
    
    # Validate unique student_id gracefully
    def validate_student_id(self, value):
        if Student.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("A student with this ID already exists.")
        return value
    
    # Allow optional fields to be blank
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    cwa = serializers.FloatField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    resume = serializers.FileField(required=False, allow_null=True)

class GroupPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPreference
        fields = '__all__'

class ProjectPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPreference
        fields = '__all__'

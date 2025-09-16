from rest_framework import serializers
from student_app.models import *
from admin_app.models import *

class ProjectPreferenceNestedSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)

    class Meta:
        model = ProjectPreference
        fields = ["rank", "project_title"]

class GroupPreferenceNestedSerializer(serializers.ModelSerializer):
    target_id = serializers.CharField(source="target_student.student_id", read_only=True)
    target_name = serializers.CharField(source="target_student.name", read_only=True)

    class Meta:
        model = GroupPreference
        fields = ["preference_type", "target_id", "target_name"]


# Recieved Preferences
class GroupPreferenceReceivedSerializer(serializers.ModelSerializer):
    source_id = serializers.CharField(source="student.student_id", read_only=True)
    source_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = GroupPreference
        fields = ["preference_type", "source_id", "source_name"]

class MajorSerializer(serializers.ModelSerializer):
    """Serializer for Major model (minimal fields needed for display)."""

    class Meta:
        model = Major
        fields = ["id", "name"] 

# Handle "" inputs for CWA
class NullableFloatField(serializers.FloatField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None
        return super().to_internal_value(data)

class StudentSerializer(serializers.ModelSerializer):
    major = MajorSerializer(read_only=True)
    preferences = ProjectPreferenceNestedSerializer(many=True, read_only=True) 

    group_preferences = GroupPreferenceNestedSerializer(
        many=True, 
        read_only=True, 
        source="given_preferences"
    )

    received_group_preferences = GroupPreferenceReceivedSerializer(
        many=True,
        read_only=True,
        source="received_preferences"  # what others say about this student
    )

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
    
    def validate_email(self, value):
        if value in ("", None):
            return None #force DB NULL
        
        # Enforce uniqueness check
        if Student.objects.filter(email=value).exists():
            raise serializers.ValidationError("A student with this email already exists.")
        return value
    
    # Allow optional fields to be blank
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    cwa = NullableFloatField(required=False, allow_null=True)
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
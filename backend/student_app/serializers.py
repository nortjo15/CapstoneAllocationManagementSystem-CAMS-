from rest_framework import serializers
from student_app.models import *
from admin_app.models import *
from student_app.models import Student
from admin_app.models import Project, Major
from student_app.models import Student, GroupPreference
from admin_app.models import Project, Major, ProjectPreference


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = 'all'
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = 'all'

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

    
class StudentListSerializer(serializers.ModelSerializer):
    major = MajorSerializer(read_only=True)
    has_preferences = serializers.BooleanField(read_only=True)
    has_teamPref = serializers.BooleanField(read_only=True)

    class Meta:
        model = Student
        fields = [
            "student_id",
            "name",
            "cwa",
            "major",
            "application_submitted",
            "allocated_group",
            "notes",
            "has_preferences",
            "has_teamPref",
        ]

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
        model = Project
        fields = '__all__'

class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = '__all__'
        

class FullFormSerializer(serializers.Serializer):
    #Student fields
    student_id = serializers.CharField(max_length=8)
    #name = serializers.CharField(max_length=100)
    major = serializers.PrimaryKeyRelatedField(queryset=Major.objects.all())
    cwa = serializers.FloatField()
    email = serializers.EmailField()
    resume = serializers.FileField()
    cv = serializers.FileField(required=False, allow_null=True)
    application_submitted = serializers.BooleanField(default=False)
    #Project Preference List
    project_preferences = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, max_length=6, required=False
    )
    #Group preference Lists
    preferred_students = serializers.ListField(
        child=serializers.CharField(max_length=8), allow_empty=True, required=False
    )
    avoided_students = serializers.ListField(
        child=serializers.CharField(max_length=8), allow_empty=True, required=False
    )

    def create(self, validated_data):
        student_id = validated_data.pop('student_id')
        project_preference_ids = validated_data.pop('project_preferences', [])
        preferred_preference_ids = validated_data.pop('preferred_students', [])
        avoided_preference_ids = validated_data.pop('avoided_students', [])

        #Get student instance
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student_id":"A student with this ID does not exist"})
        #check if student exists

        #update student details
        Student.objects.filter(student_id=student_id).update(**validated_data)

        #Clear old preferences
        ProjectPreference.objects.filter(student=student).delete()
        for i, project_id in enumerate(project_preference_ids):
            project = Project.objects.get(pk=project_id)
            ProjectPreference.objects.create(student=student, project=project, rank=i+1)
        
        GroupPreference.objects.filter(student=student).delete()
        for i, student_id in enumerate(preferred_preference_ids):
            targetStudent = Student.objects.get(pk=student_id)
            GroupPreference.objects.create(student=student, target_student=targetStudent, preference_type='like')
        for i, student_id in enumerate(avoided_preference_ids):
            targetStudent = Student.objects.get(pk=student_id)
            GroupPreference.objects.create(student=student, target_student=targetStudent, preference_type='avoid')
        
        return student



#Production endpoints
# class StudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = ['student_id', 'name', 'cwa', 'major', 'email', 'resume', 'application_submitted']

# class GroupPreferenceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GroupPreference
#         fields = ['student', 'target_student', 'preference_type']

# class ProjectPreferenceSerializer(serializers.ModelSerializer);
#     class Meta:
#         model = ProjectPreference
#         fields = ['student', 'project', 'rank']

# model = ProjectPreference
#        fields = '__all__'
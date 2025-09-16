from rest_framework import serializers
from .models import Student
from admin_app.models import Project

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

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



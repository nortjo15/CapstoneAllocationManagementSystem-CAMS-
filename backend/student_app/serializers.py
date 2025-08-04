from rest_framework import serializers
from .models import Student, GroupPreference

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class GroupPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPreference
        fields = '__all__'

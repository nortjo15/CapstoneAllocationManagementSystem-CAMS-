from rest_framework import serializers
from ..models import Project, ProjectPreference, Round, SuggestedGroup, SuggestedGroupMember, FinalGroup, FinalGroupMember, Degree, Major, AdminLog
from django.contrib.auth import get_user_model

class AdminLogSerializer(serializers.ModelSerializer):
    #Get the string representation of user
    user = serializers.StringRelatedField(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    target = serializers.SerializerMethodField()

    class Meta:
        model = AdminLog
        fields = ['id', 'user', 'action', 'action_display', 'target', 'timestamp', 'notes']
    
    def get_target(self, obj):
        if obj.target:
            return str(obj.target)
        return None

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class ProjectPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPreference
        fields = '__all__'

class SuggestedGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestedGroup
        fields = '__all__'

class SuggestedGroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestedGroupMember
        fields = '__all__'

class FinalGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalGroup
        fields = '__all__'

class FinalGroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalGroupMember
        fields = '__all__'

class RoundSerializer(serializers.ModelSerializer):
    project_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Project.objects.all(),
        write_only=True
    )
    projects = ProjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Round
        fields = '__all__'

    def create(self, validated_data):
        project_ids = validated_data.pop('project_ids', [])
        round_instance = Round.objects.create(**validated_data)
        round_instance.projects.set(project_ids)
        return round_instance
    
    
    def update(self, instance, validated_data):
        project_ids = validated_data.pop('project_ids', None)

        # update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # update many-to-many if provided
        if project_ids is not None:
            instance.projects.set(project_ids)

        return instance

class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = '__all__'

class MajorSerializer(serializers.ModelSerializer):
    degree_name = serializers.CharField(source='degree.name', read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Major
        fields = ['id', 'name', 'degree', 'degree_name', 'student_count']
from rest_framework import serializers
from .models import AdminLog

class AdminLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminLog
        fields = '__all__'

from .models import Project, ProjectPreference, SuggestedGroup, SuggestedGroupMember, FinalGroup, FinalGroupMember, Round

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
    projects = ProjectSerializer(many=True, read_only=True)
    class Meta:
        model = Round
        fields = '__all__'
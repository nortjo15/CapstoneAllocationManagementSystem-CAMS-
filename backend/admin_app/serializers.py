from rest_framework import serializers
from .models import AdminLog
from student_app.serializers import StudentSerializer, StudentListSerializer, GroupPreferenceNestedSerializer, GroupPreferenceReceivedSerializer
from .models import Project, ProjectPreference, SuggestedGroup, SuggestedGroupMember, FinalGroup, FinalGroupMember, Round

class AdminLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminLog
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    is_assigned = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
        extra_fields = ['is_assigned']

    def get_is_assigned(self, obj):
        # True if this  project has at least one FinalGroup
        return obj.final_groups.exists()

class ProjectPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPreference
        fields = '__all__'

# ---- SuggestedGroup ----
class SuggestedGroupMemberSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    group_preferences = GroupPreferenceNestedSerializer(
        many=True,
        read_only=True,
        source="student.given_preferences"
    )

    received_group_preferences = GroupPreferenceReceivedSerializer(
        many=True,
        read_only=True,
        source="student.received_preferences"
    )

    class Meta:
        model = SuggestedGroupMember
        fields = ['id', 'student', "group_preferences", "received_group_preferences"]

class SuggestedGroupSerializer(serializers.ModelSerializer):
    members = SuggestedGroupMemberSerializer(many=True, read_only=True)
    project = ProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source="project",
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = SuggestedGroup
        fields = [
            'name',
            'suggestedgroup_id', 
            'strength', 
            'notes', 
            'has_anti_preference',
            'project',
            'project_id',
            'members',
            'is_manual']
        
# Light Seralizer for faster group reload
class SuggestedGroupMemberLiteSerializer(serializers.ModelSerializer):
    student = StudentListSerializer(read_only=True)

    class Meta:
        model = SuggestedGroupMember
        fields = ["id", "student"]

class SuggestedGroupLiteSerializer(serializers.ModelSerializer):
    members = SuggestedGroupMemberLiteSerializer(many=True, read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = SuggestedGroup
        fields = [
            "suggestedgroup_id",
            "name",
            "strength",
            "project",
            "members",
            "is_manual",
        ]
# --------------------------------------------------------------------

class FinalGroupCreateSerializer(serializers.ModelSerializer):
    suggested_group_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FinalGroup
        fields = ["id", "name", "notes", "suggested_group_id"]

    def create(self, validated_data):
        suggested_group_id = validated_data.pop("suggested_group_id")
        sg = SuggestedGroup.objects.prefetch_related("members__student", "project").get(id=suggested_group_id)

        # Create Final Group
        final_group = FinalGroup.objects.create(
            name=validated_data.get("name"),
            notes=validated_data.get("notes"),
            project=sg.project,
        )

        # Copy members
        from admin_app.models import SuggestedGroupMember, FinalGroupMember
        members = sg.members.all()
        for m in members:
            FinalGroupMember.objects.create(
                group=final_group,
                student=m.student,
            )
            # Mark student as allocated
            m.student.is_allocated = True 
            m.student.save()

        # Delete suggested group and its  members
        sg.delete()

        return final_group


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
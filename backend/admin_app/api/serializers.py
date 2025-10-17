from rest_framework import serializers
from student_app.api.serializers import StudentSerializer, StudentListSerializer, GroupPreferenceNestedSerializer, GroupPreferenceReceivedSerializer
from student_app.models import Student
from ..models import Project, ProjectPreference, Round, SuggestedGroup, SuggestedGroupMember, FinalGroup, FinalGroupMember, Degree, Major, AdminLog, CapstoneInformationContent, CapstoneInformationSection, UnitContacts
from django.db import transaction
from admin_app.models import AdminLog
from django.contrib.contenttypes.models import ContentType

class AdminLogSerializer(serializers.ModelSerializer):
    #Get the string representation of user
    user = serializers.StringRelatedField(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    target = serializers.SerializerMethodField()

    class Meta:
        model = AdminLog
        fields = ['id', 'user', 'action', 'action_display', 'target', 'timestamp', 'notes']
    
    def get_target(self, obj):
        target = obj.target
        if not target:
            return None

        # For Student targets, show just the student_id (not the __str__ with name)
        if isinstance(target, Student):
            return target.student_id

        # Default fallback
        return str(target)

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
    display_name = serializers.SerializerMethodField()
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
            "suggestedgroup_id",
            "name",
            "display_name",      # <-- ensure this stays in
            "strength",
            "notes",
            "has_anti_preference",
            "project",
            "project_id",
            "members",
            "is_manual",
        ]

    def get_display_name(self, obj):
        if obj.project:
            label = "Manual" if obj.is_manual else "Auto"
            return f"{obj.project.title} - {label}"
        return obj.name

class SuggestedGroupMemberLiteSerializer(serializers.ModelSerializer):
    student = StudentListSerializer(read_only=True)

    class Meta:
        model = SuggestedGroupMember
        fields = ["id", "student"]


class SuggestedGroupLiteSerializer(serializers.ModelSerializer):
    members = SuggestedGroupMemberLiteSerializer(many=True, read_only=True)
    project = ProjectSerializer(read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = SuggestedGroup
        fields = [
            "suggestedgroup_id",
            "name",
            "strength",
            "project",
            "members",
            "is_manual",
            "display_name",
        ]
        
    def get_display_name(self, obj):
        if obj.project:
            label = "(Manual)" if obj.is_manual else "(Auto)"
            return f"{obj.project.title} {label}"
        return obj.name

class FinalGroupCreateSerializer(serializers.ModelSerializer):
    suggestedgroup_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FinalGroup
        fields = ["finalgroup_id", "name", "notes", "suggestedgroup_id"]

    @transaction.atomic  # ensures all-or-nothing database updates
    def create(self, validated_data):
        suggestedgroup_id = validated_data.pop("suggestedgroup_id")

        # Prefetch for efficiency
        sg = SuggestedGroup.objects.prefetch_related(
            "members__student",
            "project"
        ).get(suggestedgroup_id=suggestedgroup_id)

        # --- Create the FinalGroup ---
        final_group = FinalGroup.objects.create(
            name=validated_data.get("name"),
            notes=validated_data.get("notes"),
            project=sg.project,
        )

        # Log suggested group before deletion
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            ct = ContentType.objects.get_for_model(final_group)
            AdminLog.objects.create(
                user=request.user,
                action="GROUP_CREATED",
                target_content_type=ct,
                target_id=final_group.pk,
                notes=(
                    f"Final group created: name='{final_group.name}',strength='{getattr(sg, 'strength', '')}', notes='{final_group.notes or ''}' | "
                    f"from SuggestedGroup(id={sg.suggestedgroup_id}, name='{getattr(sg, 'name', '')}', "
                    f"strength='{getattr(sg, 'strength', '')}', notes='{getattr(sg, 'notes', '')}', "
                    f"members={list(sg.members.values_list('student__student_id', flat=True))})"
                ),
            )

        # --- Copy members and mark as allocated ---
        for m in sg.members.all():
            FinalGroupMember.objects.create(final_group=final_group, student=m.student)
            m.student.allocated_group = True
            m.student.save()

        # --- Delete the suggested group being finalized ---
        sg.delete()

        allocated_student_ids = list(
            final_group.members.values_list("student__student_id", flat=True)
        )
        assigned_project = final_group.project

        # Remove groups sharing any allocated student
        SuggestedGroup.objects.filter(
            members__student__student_id__in=allocated_student_ids
        ).delete()

        # Remove groups with the same project
        if assigned_project:
            SuggestedGroup.objects.filter(project=assigned_project).delete()

        return final_group

    def to_representation(self, instance):
        return FinalGroupSerializer(instance, context=self.context).data
    
class FinalGroupMemberSerializer(serializers.ModelSerializer):
    student = StudentListSerializer(read_only=True) 

    class Meta:
        model = FinalGroupMember
        fields = ["id", "student"]

class FinalGroupSerializer(serializers.ModelSerializer):
    members = FinalGroupMemberSerializer(many=True, read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = FinalGroup
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

    @transaction.atomic
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

class informationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapstoneInformationContent
        fields = '__all__'

class sectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapstoneInformationSection
        fields = '__all__'

class contactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitContacts
        fields = '__all__'
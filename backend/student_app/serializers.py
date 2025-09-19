from rest_framework import serializers
from student_app.models import Student, GroupPreference
from admin_app.models import Project, Major, ProjectPreference

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
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



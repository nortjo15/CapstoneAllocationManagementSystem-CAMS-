from django.test import TestCase
from student_app.models import Student 
from project_app.models import ( 
    FinalGroup, FinalGroupMember, SuggestedGroup, SuggestedGroupMember, Student, Project
)

class ReverseRelationTests(TestCase):
    def setUp(self):
        # Create students
        self.student1 = Student.objects.create(
            student_id="S100001",
            name="Student One",
            major="CS",
            application_submitted=True,
            email="s1@example.com"
        )
        self.student2 = Student.objects.create(
            student_id="S100002",
            name="Student Two",
            major="Math",
            application_submitted=True,
            email="s2@example.com"
        )
        # Create project
        self.project = Project.objects.create(
            title="Sample Project",
            capacity=3,
            host_name="Host A",
            host_email="host@example.com"
        )
        # Create final group
        self.final_group = FinalGroup.objects.create(project=self.project)
        # Create suggested group
        self.suggested_group = SuggestedGroup.objects.create(strength="strong")

        # Create members
        self.final_member1 = FinalGroupMember.objects.create(
            final_group=self.final_group,
            student=self.student1
        )
        self.suggested_member1 = SuggestedGroupMember.objects.create(
            suggested_group=self.suggested_group,
            student=self.student1
        )
        self.suggested_member2 = SuggestedGroupMember.objects.create(
            suggested_group=self.suggested_group,
            student=self.student2
        )

    def test_final_group_reverse_members_access(self):
        members = self.final_group.members.all()
        self.assertIn(self.final_member1, members)
        self.assertEqual(members.count(), 1)

    def test_final_group_member_reverse_to_student(self):
        # Student should have suggested_group_memberships via related_name
        membership = getattr(self.student1, 'final_group_member', None)
        self.assertIsNotNone(membership)
        self.assertEqual(membership.final_group, self.final_group)

    def test_suggested_group_reverse_members_access(self):
        members = self.suggested_group.members.all()
        self.assertEqual(members.count(), 2)
        self.assertIn(self.suggested_member1, members)
        self.assertIn(self.suggested_member2, members)

    def test_suggested_group_member_reverse_to_student(self):
        memberships = self.student1.suggested_groups.all()  # queryset of SuggestedGroupMember
        groups = [member.suggested_group for member in memberships]
        self.assertIn(self.suggested_group, groups)
        self.assertEqual(len(groups), 1)

    def test_final_group_reverse_to_project(self):
        project_final_groups = self.project.final_groups.all()
        self.assertIn(self.final_group, project_final_groups)
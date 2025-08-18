from django.test import TestCase 
from django.db import IntegrityError
from student_app.models import Student
from admin_app.models import *


class SuggestedGroupModelTests(TestCase):
    def setUp(self):
        self.group = SuggestedGroup.objects.create(
            strength='medium',
            notes='Test notes for group'
        )

    def test_create_suggested_group(self):
        self.assertIsNotNone(self.group.suggestedgroup_id)
        self.assertEqual(self.group.strength, 'medium')
        self.assertEqual(self.group.notes, 'Test notes for group')

    def test_str_method_contains_id_and_strength(self):
        string = str(self.group)
        self.assertIn(str(self.group.suggestedgroup_id), string)
        self.assertIn('Medium Group', string)  # uses get_strength_display()

class SuggestedGroupMemberModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            student_id='S0000001',
            name='Test Student',
            major='Computer Science',
            application_submitted=True,
            email='student@example.com'
        )
        self.group = SuggestedGroup.objects.create(strength='strong')

    def test_create_suggested_group_member(self):
        member = SuggestedGroupMember.objects.create(
            suggested_group=self.group,
            student=self.student
        )
        self.assertEqual(member.suggested_group, self.group)
        self.assertEqual(member.student, self.student)
        self.assertIsNotNone(member.created_at)

    def test_unique_constraint_prevents_duplicates(self):
        SuggestedGroupMember.objects.create(
            suggested_group=self.group,
            student=self.student
        )
        with self.assertRaises(IntegrityError):
            SuggestedGroupMember.objects.create(
                suggested_group=self.group,
                student=self.student
            )

    def test_cascade_delete_removes_members_when_group_deleted(self):
        member = SuggestedGroupMember.objects.create(
            suggested_group=self.group,
            student=self.student
        )
        self.group.delete()
        self.assertFalse(SuggestedGroupMember.objects.filter(pk=member.pk).exists())

    def test_cascade_delete_removes_members_when_student_deleted(self):
        member = SuggestedGroupMember.objects.create(
            suggested_group=self.group,
            student=self.student
        )
        self.student.delete()
        self.assertFalse(SuggestedGroupMember.objects.filter(pk=member.pk).exists())

    def test_ordering_by_student_id(self):
        # Create additional student and member to test ordering
        student2 = Student.objects.create(
            student_id='S0000002',
            name='Another Student',
            major='Math',
            application_submitted=True,
            email='student2@example.com'
        )
        member1 = SuggestedGroupMember.objects.create(
            suggested_group=self.group,
            student=student2
        )
        member2 = SuggestedGroupMember.objects.create(
            suggested_group=self.group,
            student=self.student
        )
        members = list(self.group.members.all())
        self.assertEqual(members[0].student.student_id, 'S0000001')  # because of ordering by student_id
        self.assertEqual(members[1].student.student_id, 'S0000002')

    def test_str_method(self):
        member = SuggestedGroupMember.objects.create(
            suggested_group=self.group,
            student=self.student
        )
        string = str(member)
        self.assertIn(self.student.name, string)
        self.assertIn(str(self.group.suggestedgroup_id), string)

class FinalGroupModelTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            title="Test Project",
            capacity=5,
            host_name="Host Name",
            host_email="host@example.com"
        )
        self.final_group = FinalGroup.objects.create(
            project=self.project,
            created_by_admin=True,
            notes="Final group notes"
        )

    def test_create_final_group(self):
        self.assertIsNotNone(self.final_group.finalgroup_id)
        self.assertEqual(self.final_group.project, self.project)
        self.assertTrue(self.final_group.created_by_admin)
        self.assertEqual(self.final_group.notes, "Final group notes")
        self.assertIsNotNone(self.final_group.created_at)

    def test_str_method(self):
        string = str(self.final_group)
        self.assertIn(str(self.final_group.finalgroup_id), string)
        self.assertIn(self.project.title, string)


class FinalGroupMemberModelTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            title="Another Project",
            capacity=10,
            host_name="Host 2",
            host_email="host2@example.com"
        )
        self.final_group = FinalGroup.objects.create(project=self.project)
        self.student = Student.objects.create(
            student_id="S0001001",
            name="Final Member Student",
            major="Engineering",
            application_submitted=True,
            email="finalmember@example.com"
        )

    def test_create_final_group_member(self):
        member = FinalGroupMember.objects.create(
            final_group=self.final_group,
            student=self.student
        )
        self.assertEqual(member.final_group, self.final_group)
        self.assertEqual(member.student, self.student)

    def test_one_to_one_student_constraint(self):
        # Create one member for student
        FinalGroupMember.objects.create(
            final_group=self.final_group,
            student=self.student
        )
        # Attempt to add the same student to another final group should fail
        another_final_group = FinalGroup.objects.create(project=self.project)
        with self.assertRaises(IntegrityError):
            FinalGroupMember.objects.create(
                final_group=another_final_group,
                student=self.student
            )

    def test_cascade_delete_final_group_removes_members(self):
        member = FinalGroupMember.objects.create(
            final_group=self.final_group,
            student=self.student
        )
        self.final_group.delete()
        self.assertFalse(FinalGroupMember.objects.filter(pk=member.pk).exists())

    def test_cascade_delete_student_removes_members(self):
        member = FinalGroupMember.objects.create(
            final_group=self.final_group,
            student=self.student
        )
        self.student.delete()
        self.assertFalse(FinalGroupMember.objects.filter(pk=member.pk).exists())

    def test_ordering_by_student_id(self):
        student2 = Student.objects.create(
            student_id="S0001002",
            name="Second Student",
            major="Math",
            application_submitted=True,
            email="secondstudent@example.com"
        )
        member1 = FinalGroupMember.objects.create(
            final_group=self.final_group,
            student=student2
        )
        member2 = FinalGroupMember.objects.create(
            final_group=self.final_group,
            student=self.student
        )
        members = list(self.final_group.members.all())
        self.assertEqual(members[0].student.student_id, "S0001001")
        self.assertEqual(members[1].student.student_id, "S0001002")

    def test_str_method(self):
        member = FinalGroupMember.objects.create(
            final_group=self.final_group,
            student=self.student
        )
        string = str(member)
        self.assertIn(self.student.name, string)
        self.assertIn(str(self.final_group.finalgroup_id), string)
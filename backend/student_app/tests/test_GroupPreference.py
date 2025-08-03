from django.test import TestCase 
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from student_app.models import Student, GroupPreference
from project_app.models import Project, SuggestedGroup

# GroupPreference Model Tests
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from student_app.models import Student, GroupPreference

class GroupPreferenceModelTests(TestCase):
    def setUp(self):
        self.student1 = Student.objects.create(
            student_id="S0000001", name="Alice", major="CS", application_submitted=True, email="alice@example.com"
        )
        self.student2 = Student.objects.create(
            student_id="S0000002", name="Bob", major="IT", application_submitted=False, email="bob@example.com"
        )
        self.student3 = Student.objects.create(
            student_id="S0000003", name="Charlie", major="CS", application_submitted=True, email="charlie@example.com"
        )

    def test_create_valid_like_preference(self):
        gp = GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='like'
        )
        self.assertEqual(gp.preference_type, 'like')

    def test_create_valid_avoid_preference(self):
        gp = GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='avoid'
        )
        self.assertEqual(gp.preference_type, 'avoid')

    def test_invalid_preference_type_raises_validation_error(self):
        gp = GroupPreference(
            student=self.student1,
            target_student=self.student2,
            preference_type='friend'  # invalid
        )
        with self.assertRaises(ValidationError):
            gp.full_clean()

    def test_self_preference_raises_validation_error(self):
        gp = GroupPreference(
            student=self.student1,
            target_student=self.student1,
            preference_type='like'
        )
        with self.assertRaises(ValidationError) as context:
            gp.clean()
        self.assertIn("A student cannot preference themselves.", str(context.exception))

    def test_save_calls_clean_and_prevents_self_preference(self):
        gp = GroupPreference(
            student=self.student1,
            target_student=self.student1,
            preference_type='like'
        )
        with self.assertRaises(ValidationError):
            gp.save()

    def test_unique_constraint_prevents_duplicate(self):
        GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='like'
        )
        with self.assertRaises(IntegrityError):
            GroupPreference.objects.create(
                student=self.student1,
                target_student=self.student2,
                preference_type='avoid'
            )

    def test_student_and_target_student_null_raises_integrity_error(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                GroupPreference.objects.create(
                    student=None,
                    target_student=self.student2,
                    preference_type='like'
                )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                GroupPreference.objects.create(
                    student=self.student1,
                    target_student=None,
                    preference_type='like'
                )

    def test_multiple_preferences_with_different_targets_allowed(self):
        GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='like'
        )
        gp2 = GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student3,
            preference_type='avoid'
        )
        self.assertEqual(GroupPreference.objects.filter(student=self.student1).count(), 2)

    def test_multiple_preferences_with_different_students_allowed(self):
        GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='like'
        )
        gp2 = GroupPreference.objects.create(
            student=self.student3,
            target_student=self.student2,
            preference_type='avoid'
        )
        self.assertEqual(GroupPreference.objects.filter(target_student=self.student2).count(), 2)

    def test_given_preferences_related_name(self):
        GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='like'
        )
        self.assertEqual(self.student1.given_preferences.count(), 1)

    def test_received_preferences_related_name(self):
        GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='avoid'
        )
        self.assertEqual(self.student2.received_preferences.count(), 1)

    def test_str_representation(self):
        gp = GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='like'
        )
        expected_str = f"{self.student1} → {self.student2} (like)"
        self.assertEqual(str(gp), expected_str)

    def test_cascading_delete_student_removes_preferences(self):
        gp = GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='like'
        )
        self.student1.delete()
        self.assertEqual(GroupPreference.objects.count(), 0)

    def test_cascading_delete_target_student_removes_preferences(self):
        gp = GroupPreference.objects.create(
            student=self.student1,
            target_student=self.student2,
            preference_type='like'
        )
        self.student2.delete()
        self.assertEqual(GroupPreference.objects.count(), 0)
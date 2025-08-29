from django.test import TestCase 
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from student_app.models import Student
from admin_app.models import Project, ProjectPreference

# Test creation of Project instance
class ProjectModelTest(TestCase):
    def test_project_creation_and_str(self): 
        project = Project.objects.create(
            title="Cybersec Capstone",
            capacity=7,
            host_name="Dr.Smith",
            host_email="smith@example.com"
        )

        self.assertEqual(project.title, "Cybersec Capstone")
        self.assertEqual(project.capacity, 7)
        self.assertEqual(str(project), f"{project.project_id} - Cybersec Capstone")

# ProjectPreference Model Tests
class ProjectPreferenceModelTest(TestCase):
    def setUp(self):
        # Create student and projects 
        self.student = Student.objects.create(student_id="S001", name="Alice", major="CS", application_submitted=True)
        self.project1 = Project.objects.create(title="Project 1", capacity=5, host_name="Host A", host_email="hosta@example.com")
        self.project2 = Project.objects.create(title="Project 2", capacity=5, host_name="Host B", host_email="hostb@example.com")

    # Test creation of valid ProjectPreference
    def test_create_preference(self):
        pref = ProjectPreference.objects.create(student=self.student, project=self.project1, rank=1)
        self.assertEqual(pref.student, self.student)
        self.assertEqual(pref.project, self.project1)
        self.assertEqual(pref.rank, 1)

    def test_unique_student_rank_constraint(self):
        ProjectPreference.objects.create(student=self.student, project=self.project1, rank=1)
        with self.assertRaises(IntegrityError):
            # Same student, same rank -> should fail unique_together constraint
            ProjectPreference.objects.create(student=self.student, project=self.project2, rank=1)

    def test_unique_student_project_constraint(self):
        ProjectPreference.objects.create(student=self.student, project=self.project1, rank=1)
        with self.assertRaises(IntegrityError):
            # Same student, same project -> should fail unique_together constraint
            ProjectPreference.objects.create(student=self.student, project=self.project1, rank=2)

    def test_ordering_by_rank(self):
        ProjectPreference.objects.create(student=self.student, project=self.project1, rank=2)
        ProjectPreference.objects.create(student=self.student, project=self.project2, rank=1)
        prefs = ProjectPreference.objects.filter(student=self.student)
        ranks = [p.rank for p in prefs]
        self.assertEqual(ranks, sorted(ranks))  # Should be ordered by rank ascending

    def test_str_method(self):
        pref = ProjectPreference.objects.create(student=self.student, project=self.project1, rank=1)
        expected_str = f"{self.student} - {self.project1} (Rank 1)"
        self.assertEqual(str(pref), expected_str)

    def test_capacity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            project = Project(
                title="Invalid Capacity",
                capacity=0,
                host_name="Host",
                host_email="host@example.com"
            )
            project.full_clean()  # triggers model validation

        with self.assertRaises(ValidationError):
            project = Project(
                title="Negative Capacity",
                capacity=-5,
                host_name="Host",
                host_email="host@example.com"
            )
            project.full_clean()

    def test_title_cannot_be_null(self):
        with self.assertRaises(ValidationError):
            project = Project(
                title=None,
                capacity=5,
                host_name="Host",
                host_email="host@example.com"
            )
            project.full_clean()

    def test_invalid_host_email(self):
        with self.assertRaises(ValidationError):
            project = Project(
                title="Invalid Email",
                capacity=5,
                host_name="Host",
                host_email="not-an-email"
            )
            project.full_clean()

class ProjectPreferenceEdgeCaseTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(student_id="20154259", name="Brian", major="Computer Science", application_submitted=True)
        self.project = Project.objects.create(title="Capstone Project 1", capacity=5, host_name="Host", host_email="host@example.com")

    def test_rank_must_be_positive(self):
        with self.assertRaises(ValidationError):
            pref = ProjectPreference(student=self.student, project=self.project, rank=0)
            pref.full_clean()
            pref.save()

        with self.assertRaises(ValidationError):
            pref = ProjectPreference(student=self.student, project=self.project, rank=-1)
            pref.full_clean()
            pref.save()

    def test_cascade_delete_student(self):
        pref = ProjectPreference.objects.create(student=self.student, project=self.project, rank=1)
        self.student.delete()
        self.assertFalse(ProjectPreference.objects.filter(pk=pref.pk).exists())

    def test_cascade_delete_project(self):
        pref = ProjectPreference.objects.create(student=self.student, project=self.project, rank=1)
        self.project.delete()
        self.assertFalse(ProjectPreference.objects.filter(pk=pref.pk).exists())
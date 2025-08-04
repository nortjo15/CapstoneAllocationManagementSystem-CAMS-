from django.test import TestCase 
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from student_app.models import Student

class StudentModelTests(TestCase):
    def test_create_student_successfully(self):
        student = Student.objects.create(
            student_id="S0000001",
            name="Alice",
            major="Computer Science",
            application_submitted=True,
            email="alice@example.com",
            cwa=85.5
        )
        self.assertEqual(student.student_id, "S0000001")
        self.assertEqual(student.name, "Alice")
        self.assertEqual(student.major, "Computer Science")
        self.assertTrue(student.application_submitted)
        self.assertEqual(student.email, "alice@example.com")
        self.assertEqual(float(student.cwa), 85.5)

    def test_cwa_field_accepts_null_and_blank(self):
        student = Student.objects.create(
            student_id="S0000002",
            name="Bob",
            major="Information Technology",
            application_submitted=False,
            email="bob@example.com",
            cwa=None
        )
        self.assertIsNone(student.cwa)

    def test_cwa_field_validates_min_and_max(self):
        student = Student(
            student_id="S0000003",
            name="Charlie",
            major="Engineering",
            application_submitted=False,
            email="charlie@example.com",
            cwa=50
        )
        student.full_clean()  # should not raise

        student.cwa = -1
        with self.assertRaises(ValidationError):
            student.full_clean()

        student.cwa = 150
        with self.assertRaises(ValidationError):
            student.full_clean()

    def test_email_unique_constraint(self):
        Student.objects.create(
            student_id="S0000004",
            name="David",
            major="Math",
            application_submitted=True,
            email="david@example.com"
        )
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                student_id="S0000005",
                name="Eve",
                major="Physics",
                application_submitted=False,
                email="david@example.com"  # duplicate email
            )

    def test_name_major_and_application_submitted_cannot_be_null(self):
        student = Student(
            student_id="S0000006",
            name=None,
            major="Physics",
            application_submitted=True,
            email="eve@example.com"
        )
        with self.assertRaises(ValidationError):
            student.full_clean()

        student.name = "Eve"
        student.major = None
        with self.assertRaises(ValidationError):
            student.full_clean()

        student.major = "Physics"
        student.application_submitted = None
        with self.assertRaises(ValidationError):
            student.full_clean()

    def test_str_method_returns_expected_string(self):
        student = Student.objects.create(
            student_id="S0000007",
            name="Frank",
            major="CS",
            application_submitted=False,
            email="frank@example.com"
        )
        expected = "S0000007 - Frank"
        self.assertEqual(str(student), expected)

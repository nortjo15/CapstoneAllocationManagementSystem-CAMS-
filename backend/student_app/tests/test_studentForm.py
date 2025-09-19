from django.test import TestCase
from student_app.forms import ProjectApplicationForm
from admin_app.models import Degree, Major
from django.core.files.uploadedfile import SimpleUploadedFile


class StudentFormTest(TestCase):
    def setUp(self):
        # Create degree and major
        self.degree = Degree.objects.create(name="Computing")
        self.major = Major.objects.create(degree=self.degree, name="Computer Science")

        # Dummy PDF file for resume field
        self.valid_file = SimpleUploadedFile(
            "John-Doe_12345678_resume.pdf",
            b"Dummy resume content",
            content_type="application/pdf"
        )

        # Base valid payload
        self.valid_payload = {
            "student_id": "12345678",
            "email": "j.doe@student.curtin.edu.au",
            "major": self.major.id,
            "cwa": "89.54",
            "terms": True,
        }

    # Student ID tests
    def test_valid_studentId(self):
        """Form accepts valid 8-digit student IDs"""
        form = ProjectApplicationForm(data=self.valid_payload)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertEqual(form.cleaned_data["student_id"], "12345678")

    def test_too_short_studentId(self):
        """Form should reject fewer than 8 digits"""
        data = self.valid_payload.copy()
        data["student_id"] = "1234567"
        form = ProjectApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("student_id", form.errors)
        self.assertIn("Student ID must be exactly 8 digits", form.errors["student_id"])

    def test_invalid_characters_studentId(self):
        """Form should reject non-digit entries"""
        data = self.valid_payload.copy()
        data["student_id"] = "12a34567"
        form = ProjectApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("student_id", form.errors)

    # Email tests
    def test_valid_email(self):
        """Form accepts valid email in form name@student.curtin.edu.au"""
        form = ProjectApplicationForm(data=self.valid_payload)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertEqual(form.cleaned_data["email"], "j.doe@student.curtin.edu.au")

    def test_middle_name_email(self):
        """Form should accept emails like j.m.t@student.curtin.edu.au"""
        data = self.valid_payload.copy()
        data["email"] = "j.m.t@student.curtin.edu.au"
        form = ProjectApplicationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_middle_name_number_email(self):
        """Form should accept emails like j.m.t1@student.curtin.edu.au"""
        data = self.valid_payload.copy()
        data["email"] = "j.m.t1@student.curtin.edu.au"
        form = ProjectApplicationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_invalid_email(self):
        """Form rejects non-Curtin emails"""
        data = self.valid_payload.copy()
        data["email"] = "john.doe@gmail.com.au"
        form = ProjectApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn(
            "Please enter a valid Curtin Student Email E.g. john.smith@student.curtin.edu.au",
            form.errors["email"]
        )

    # Resume tests
    # def test_valid_file_upload(self):
    #     """Form accepts a correctly formatted resume filename"""
    #     good_file = SimpleUploadedFile(
    #         name="John-Doe_12345678_resume.pdf",
    #         content=b"Dummy PDF content",
    #         content_type="application/pdf"
    #     )
    #     form = ProjectApplicationForm(
    #         data=self.valid_payload, 
    #         files={"resume": good_file}
    #     )
    #     self.assertTrue(form.is_valid(), form.errors.as_json())
    #     self.assertEqual(form.cleaned_data["resume"].name, "John-Doe_12345678_resume.pdf")

    # def test_invalid_filename_format(self):
    #     """Form rejects incorrect resume filename format"""
    #     bad_file = SimpleUploadedFile(
    #         name="JohnDoe_12345678_resume.pdf",  # missing hyphen
    #         content=b"Dummy PDF content",
    #         content_type="application/pdf"
    #     )
    #     form = ProjectApplicationForm(
    #         data=self.valid_payload, 
    #         files={"resume": bad_file}
    #     )
    #     self.assertFalse(form.is_valid())
    #     self.assertIn("resume", form.errors)
    #     self.assertIn(
    #         "Filename must be in the format: FirstName-LastName_studentId_resume.pdf",
    #         form.errors["resume"]
    #     )

    # def test_no_file_uploaded(self):
    #     """Form allows no resume file if optional"""
    #     form = ProjectApplicationForm(data=self.valid_payload)
    #     self.assertTrue(form.is_valid(), form.errors.as_json())
    #     self.assertIsNone(form.cleaned_data.get("resume"))










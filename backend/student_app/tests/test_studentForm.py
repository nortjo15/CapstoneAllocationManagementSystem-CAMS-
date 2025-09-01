from django.test import TestCase
from student_app.forms import ProjectApplicationForm
from admin_app.models import Degree, Major
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile


class studentFormTest(TestCase):
    def setUp(self):
        self.degree = Degree.objects.create(name="Computing")
        self.major = Major.objects.create(degree=self.degree, name="Computer Science")

        self.valid_payload = {
            "student_id" : "12345678",
            "email" : "j.doe@student.curtin.edu.au",
            "major" : self.major.id,
            "cwa" : "89.54",
            "terms" : True,
        }
    
    #Unit test for student Id
    def test_valid_studentId(self):
        """Form accepts valid 8-digit student IDs"""
        form = ProjectApplicationForm(data=self.valid_payload)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertEqual(form.cleaned_data["student_id"], "12345678")

    def test_too_short_studentId(self):
        """Form should reject fewer than 8 digits"""
        data = self.valid_payload.copy()
        data["student_id"] ="1234567"
        form = ProjectApplicationForm(data=data)
        self.assertFalse(form.is_valid(), form.errors.as_json())
        self.assertIn("student_id", form.errors)
        self.assertIn("Student ID must be exactly 8 digits", form.errors["student_id"])

    def test_invalid_characters(self):
        """Form should reject non digit entries"""
        data = self.valid_payload.copy()
        form = ProjectApplicationForm(data=data)
        data["student_id"] = "12a34567"
        self.assertFalse(form.is_valid(), form.errors.as_json())
        self.assertIn("student_id", form.errors)

    #Unit test for emails
    def test_valid_email(self):
        """Form accepts valid email in form name@student.curtin.edu.au"""
        data = self.valid_payload.copy()
        form = ProjectApplicationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertEqual(form.cleaned_data["email"], "j.doe@student.curtin.edu.au")
    
    def test_middle_name_validation_email(self):
        """Form should be able to accept email with j.m.t@student.curtin.edu.au"""
        data = self.valid_payload.copy()
        form = ProjectApplicationForm(data=data)
        data["email"] = "j.m.t@student.curtin.edu.au"
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_middle_name_validation_number_email(self):
        """Form should be able to accept email with j.m.t1@student.curtin.edu.au"""
        data = self.valid_payload.copy()
        form = ProjectApplicationForm(data=data)
        data["email"] = "j.m.t1@student.curtin.edu.au"
        self.assertTrue(form.is_valid(), form.errors.as_json()) 
    
    def test_invalid_email(self):
        """Form rejects incorrect form email"""
        data = self.valid_payload.copy()
        form = ProjectApplicationForm(data=data)
        data["email"] = "john.doe@gmail.com.au"
        self.assertFalse(form.is_valid(), form.errors.as_json())
        self.assertIn("email", form.errors)
        self.assertIn("Please enter a valid Curtin Student Email E.g. john.smith@student.curtin.edu.au", form.errors["email"])
    
    #Unit tests for resume









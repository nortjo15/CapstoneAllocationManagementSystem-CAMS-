# insert_placeholder_emails.py
from student_app.models import Student
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.CAS.settings")
django.setup()

# List of student IDs to update
student_ids = ["10000003", "20000029", "20000031", "20000040", "30000031"]

for sid in student_ids:
    try:
        student = Student.objects.get(student_id=sid)

        # Set placeholder email if not already set
        if not student.email:
            student.email = f"{sid}@example.com"
            student.save(update_fields=["email"])
            print(f"✉️ Placeholder email set for {sid}: {student.email}")
        else:
            print(f"ℹ️ Student {sid} already has an email: {student.email}")

    except Student.DoesNotExist:
        print(f"⚠️ Student {sid} not found")
    except Exception as e:
        print(f"❌ Error for {sid}: {e}")

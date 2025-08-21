from admin_app import email_service

from student_app.models import Student


# Test Application Success
student = Student.objects.first()
email_service.send_application_success(student)

# Test Allocation Released
email_service.send_allocation_released(final_group_id=1)

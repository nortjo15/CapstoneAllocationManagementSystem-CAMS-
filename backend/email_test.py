from admin_app import email_service
from student_app.models import Student
from admin_app.models import Round, FinalGroup

# --- Test Application Success ---
student = Student.objects.first()
if student:
    result = email_service.send_application_success(student)
    print(f"[Application Success] Sent {result} emails to {student.email}")
else:
    print("No Student found in DB.")

# --- Test Allocation Released ---
final_group = FinalGroup.objects.first()
if final_group:
    result = email_service.send_allocation_released(final_group.finalgroup_id)
    print(f"[Allocation Released] Sent {result} emails to group {final_group.finalgroup_id}")
else:
    print("No FinalGroup found in DB.")

# --- Test Round Start ---
rnd = Round.objects.first()
if rnd:
    result = email_service.send_round_start(rnd)
    print(f"[Round Start] Sent {result} emails for round '{rnd.round_name}'")
else:
    print("No Round found in DB.")

# --- Test Round Closed ---
if rnd:
    result = email_service.send_round_closed(rnd)
    print(f"[Round Closed] Sent {result} emails for round '{rnd.round_name}'")

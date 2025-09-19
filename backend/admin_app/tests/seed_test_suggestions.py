from student_app.models import Student, GroupPreference
from admin_app.models import Project, ProjectPreference

student_ids = [
    "41000011",
    "41000012",
    "41000013",
    "41000014",
    "41000015",
]

# Load students
students = {s.student_id: s for s in Student.objects.filter(student_id__in=student_ids)}

# --- Group Preferences ---
# Every student likes every other student
for sid, student in students.items():
    for tid, target in students.items():
        if sid == tid:
            continue
        GroupPreference.objects.get_or_create(
            student=student,
            target_student=target,
            preference_type="like",
        )

# --- Project Preferences ---
projects_order = [
    "AI Chatbot Assistant",
    "Smart Campus Scheduler",
    "Secure File Vault",
]

projects = {p.title: p for p in Project.objects.filter(title__in=projects_order)}

for student in students.values():
    for rank, title in enumerate(projects_order, start=1):
        ProjectPreference.objects.get_or_create(
            student=student,
            project=projects[title],
            rank=rank,
        )

print("✅ Preferences seeded: mutual likes + identical project preferences.")
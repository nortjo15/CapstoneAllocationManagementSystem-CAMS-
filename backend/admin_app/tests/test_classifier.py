from student_app.models import Student, GroupPreference
from admin_app.models import Project, ProjectPreference
from admin_app.group_utils import classify_group

# --- Create 5 students ---
students_data = [
    ("50000001", "Liam Scott", 78.45),
    ("50000002", "Emma Clark", 91.32),
    ("50000003", "Noah Wilson", 85.20),
    ("50000004", "Olivia Brown", 72.10),
    ("50000005", "Ethan Harris", 88.75),
]
students = {}
for sid, name, cwa in students_data:
    s, _ = Student.objects.get_or_create(
        student_id=sid,
        defaults={"name": name, "cwa": cwa, "application_submitted": True}
    )
    students[sid] = s

# --- Fetch existing projects (assume they are already created) ---
projects = {i: Project.objects.get(title=title) for i, title in enumerate([
    "AI Chatbot Assistant",
    "Cyber Threat Analyzer",
    "Smart Campus Scheduler",
    "Secure File Vault",
    "Cloud Backup Manager",
], start=1)}

# --- Strong group: 50000001 + 50000002 ---
s1, s2 = students["50000001"], students["50000002"]
p1 = projects[1]  # AI Chatbot Assistant

# identical project order, both rank p1 as #1
ProjectPreference.objects.update_or_create(student=s1, project=p1, defaults={"rank": 1})
ProjectPreference.objects.update_or_create(student=s2, project=p1, defaults={"rank": 1})

# mutual likes
GroupPreference.objects.update_or_create(student=s1, target_student=s2, defaults={"preference_type": "like"})
GroupPreference.objects.update_or_create(student=s2, target_student=s1, defaults={"preference_type": "like"})

print("Strong group:", classify_group([s1, s2], project_capacity=5))

# --- Medium group: 50000003 + 50000004 ---
s3, s4 = students["50000003"], students["50000004"]
p2, p3 = projects[2], projects[3]  # Cyber Threat Analyzer, Smart Campus Scheduler

# same set {p2, p3}, different order
ProjectPreference.objects.update_or_create(student=s3, project=p2, defaults={"rank": 1})
ProjectPreference.objects.update_or_create(student=s3, project=p3, defaults={"rank": 2})

ProjectPreference.objects.update_or_create(student=s4, project=p3, defaults={"rank": 1})
ProjectPreference.objects.update_or_create(student=s4, project=p2, defaults={"rank": 2})

# mutual likes
GroupPreference.objects.update_or_create(student=s3, target_student=s4, defaults={"preference_type": "like"})
GroupPreference.objects.update_or_create(student=s4, target_student=s3, defaults={"preference_type": "like"})

print("Medium group:", classify_group([s3, s4], project_capacity=6))

# --- Weak group (project overlap only): 50000005 + 50000001 ---
s5 = students["50000005"]

# both rank project 4 somewhere
ProjectPreference.objects.update_or_create(student=s5, project=projects[4], defaults={"rank": 1})
ProjectPreference.objects.update_or_create(student=s1, project=projects[4], defaults={"rank": 2})

# no likes/avoids between them
GroupPreference.objects.filter(student=s5, target_student=s1).delete()
GroupPreference.objects.filter(student=s1, target_student=s5).delete()

print("Weak group (project only):", classify_group([s5, s1], project_capacity=7))
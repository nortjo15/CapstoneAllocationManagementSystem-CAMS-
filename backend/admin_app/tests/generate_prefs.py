import random
from student_app.models import Student, GroupPreference
from admin_app.models import Project, ProjectPreference

# Reset preferences
GroupPreference.objects.all().delete()
ProjectPreference.objects.all().delete()
print("Deleted all existing GroupPreference and ProjectPreference records.")

students = list(Student.objects.all())
random.shuffle(students)

groups = []
i = 0
while i < len(students):
    group_size = random.randint(4, 6)
    group = students[i:i+group_size]
    if group:  # avoid empty group
        groups.append(group)
    i += group_size

created_group_count = 0

# Within each group, everyone likes everyone else
for group in groups:
    for student in group:
        for target in group:
            if student != target:
                GroupPreference.objects.create(
                    student=student,
                    target_student=target,
                    preference_type="like",
                )
                created_group_count += 1

# Add random avoids (≈10% of students get one avoid each)
num_avoiders = max(1, len(students) // 10)
avoiders = random.sample(students, num_avoiders)

for student in avoiders:
    group = next((g for g in groups if student in g), [])
    others = [s for s in students if s not in group and s != student]
    if not others:
        continue
    target = random.choice(others)
    GroupPreference.objects.create(
        student=student,
        target_student=target,
        preference_type="avoid",
    )
    created_group_count += 1

# -------------------------------
# Project Preferences Generation
# -------------------------------
projects = list(Project.objects.all())
created_project_count = 0

if projects:
    for group in groups:
        # 50% of groups will have identical preferences
        if random.random() < 0.3:
            num_prefs = random.randint(3, min(5, len(projects)))
            shared_prefs = random.sample(projects, num_prefs)
            for student in group:
                for rank, project in enumerate(shared_prefs, start=1):
                    ProjectPreference.objects.create(
                        student=student,
                        project=project,
                        rank=rank,
                    )
                    created_project_count += 1
        else:
            # Everyone in this group gets their own unique preferences
            for student in group:
                num_prefs = random.randint(3, min(5, len(projects)))
                preferred = random.sample(projects, num_prefs)
                for rank, project in enumerate(preferred, start=1):
                    ProjectPreference.objects.create(
                        student=student,
                        project=project,
                        rank=rank,
                    )
                    created_project_count += 1

print(f"Generated {created_group_count} group preferences across {len(groups)} groups.")
print(f"Generated {created_project_count} project preferences across {len(students)} students.")

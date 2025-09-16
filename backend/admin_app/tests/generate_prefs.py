import random
from student_app.models import Student, GroupPreference

# Reset preferences
GroupPreference.objects.all().delete()
print("Deleted all existing GroupPreference records.")

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

created_count = 0

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
                created_count += 1

# Add random avoids (≈10% of students get one avoid each)
num_avoiders = max(1, len(students) // 10)
avoiders = random.sample(students, num_avoiders)

for student in avoiders:
    # pick someone not in the same group to avoid
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
    created_count += 1

print(f"Generated {created_count} group preferences across {len(groups)} groups.")
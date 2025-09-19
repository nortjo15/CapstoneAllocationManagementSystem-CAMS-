# Generates some sample groups 
# Usage: 
# - make bash 
# - python manage.py shell < seed_suggested_groups.py 
from admin_app.models import SuggestedGroup, SuggestedGroupMember
from student_app.models import Student

groups = {
    "Group A": ["40000001", "40000002", "40000003"],  
    "Group B": ["40000004", "40000005", "40000006"],  
    "Group C": ["40000007", "40000008", "40000009"],  
}

for notes, student_ids in groups.items():
    group, created = SuggestedGroup.objects.get_or_create(
        notes=notes, strength="strong"
    )
    for sid in student_ids:
        try:
            student = Student.objects.get(student_id=sid)
            SuggestedGroupMember.objects.get_or_create(
                suggested_group=group, student=student
            )
        except Student.DoesNotExist:
            print(f"Student {sid} not found in DB")

    print(f"Group {group.suggestedgroup_id} ({notes}) members:",
          list(group.members.values_list("student__student_id", flat=True)))
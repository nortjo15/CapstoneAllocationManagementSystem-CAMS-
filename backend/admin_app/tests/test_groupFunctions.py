from admin_app.group_utils import (
    have_identical_project_order,
    have_same_project_set,
    overlap_in_top_n_projects,
    are_mutual_likes,
    has_anti_preference
)
from student_app.models import Student

s1 = Student.objects.get(student_id="10000001")
s2 = Student.objects.get(student_id="10000002")

print(have_identical_project_order(s1, s2))   # Expect False
print(have_same_project_set(s1, s2))          # Expect True (same 5 projects)
print(overlap_in_top_n_projects(s1, s2, 3))   # Expect True (projects 1 & 3 overlap in top-3)
print(are_mutual_likes(s1, s2))               # Expect False
print(has_anti_preference(s1, s2))            # Expect False
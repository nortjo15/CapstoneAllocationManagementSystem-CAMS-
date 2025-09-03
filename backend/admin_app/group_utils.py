from student_app.models import Student, GroupPreference
from admin_app.models import ProjectPreference

# Contains code to retrieve student preferences 
def get_student_project_prefs(student):
    return list(
        ProjectPreference.objects.filter(student=student).order_by("rank")
    )

def get_student_group_likes(student):
    return list(
        GroupPreference.objects.filter(student=student, preference_type="like")
    )

def get_student_group_avoids(student):
    return list(
        GroupPreference.objects.filter(student=student, preference_type="avoid")
    )

# Check if two students mutually prefer each other
def are_mutual_likes(student_a, student_b):
    return (
        GroupPreference.objects.filter(student=student_a, target_student=student_b, preference_type="like").exists()
        and GroupPreference.objects.filter(student=student_b, target_student=student_a, preference_type="like").exists()
    )

# See if there is an anti-preference from a->b or b->a
def has_anti_preference(student_a, student_b):
    return (
        GroupPreference.objects.filter(student=student_a, target_student=student_b, preference_type="avoid").exists()
        or GroupPreference.objects.filter(student=student_b, target_student=student_a, preference_type="avoid").exists()
    )

# Returns true if both students ranked the same projects in the same exact order
# Includes logic to check for subsets - not all students will submit the same number of preferences
def have_identical_project_order(student_a, student_b):
    prefs_a = list(ProjectPreference.objects.filter(student=student_a).order_by("rank").values_list("project_id", flat=True))
    prefs_b = list(ProjectPreference.objects.filter(student=student_b).order_by("rank").values_list("project_id", flat=True))
    min_len = min(len(prefs_a), len(prefs_b))
    return prefs_a[:min_len] == prefs_b[:min_len]

def have_same_project_set(student_a, student_b):
    prefs_a = set(ProjectPreference.objects.filter(student=student_a).values_list("project_id", flat=True))
    prefs_b = set(ProjectPreference.objects.filter(student=student_b).values_list("project_id", flat=True))
    return prefs_a.issubset(prefs_b) or prefs_b.issubset(prefs_a)

# Returns True if the top-N ranked projects overlap between two students
def overlap_in_top_n_projects(student_a, student_b, n=3):
    prefs_a = list(ProjectPreference.objects.filter(student=student_a).order_by("rank").values_list("project_id", flat=True)[:n])
    prefs_b = list(ProjectPreference.objects.filter(student=student_b).order_by("rank").values_list("project_id", flat=True)[:n])
    return prefs_a == prefs_b


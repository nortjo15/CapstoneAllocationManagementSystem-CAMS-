from student_app.models import Student, GroupPreference
from admin_app.models import ProjectPreference
from itertools import combinations

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
    prefs_a = list(
        ProjectPreference.objects.filter(student=student_a)
        .order_by("rank")
        .values_list("project_id", flat=True)[:n]
    )
    prefs_b = list(
        ProjectPreference.objects.filter(student=student_b)
        .order_by("rank")
        .values_list("project_id", flat=True)[:n]
    )
    return bool(set(prefs_a) & set(prefs_b))

# Classify a group of students as 'strong', 'medium' or 'weak'
# Return a dict with strength & flag
def classify_group(students, project_capacity=None, top_n=3):
    if len(students) < 2:
        raise ValueError("Groups must contain at least 2 students")
    
    has_anti = False
    mutual_like_count = 0
    pair_count = 0
    
    # Go through pairwise relationships
    for a, b in combinations(students, 2):
        pair_count += 1
        if has_anti_preference(a, b):
            has_anti = True
        if are_mutual_likes(a, b):
            mutual_like_count += 1

    # Reject if group is larger than project capacity
    if project_capacity and len(students) > project_capacity:
        return {"strength": "invalid", "has_anti_preference": has_anti}
    
    # --- All Mutual likes ---
    if mutual_like_count == pair_count:
        ref = students[0]
        identical_order = all(have_identical_project_order(ref, s) for s in students[1:])
        same_set = all(have_same_project_set(ref, s) for s in students[1:])
        overlap_top = all(overlap_in_top_n_projects(ref, s, top_n) for s in students[1:])

        if identical_order:
            prefs = list(ProjectPreference.objects.filter(student=ref).order_by("rank"))
            if prefs and prefs[0].rank in [1, 2]:
                return {"strength": "medium" if has_anti else "strong", "has_anti_preference": has_anti}
            
        if same_set or overlap_top:
            return {"strength": "weak" if has_anti else "medium", "has_anti_preference": has_anti}
        
    # To Confirm: 
    # - Weaker groups encompass everything - either students who have preferenced each other 
    # - Or students who have some matching preferences
    # --- Some or no mutual likes ----
    if mutual_like_count > 0:
        return {"strength": "weak", "has_anti_preference": has_anti}
    else:
        # No likes at all, check for project overlap
        ref = students[0]
        overlap_top = all(overlap_in_top_n_projects(ref, s, top_n) for s in students[1:])

        if overlap_top:
            return {"strength": "weak", "has_anti_preference": has_anti}
        else: 
            return {"strength": "invalid", "has_anti_preference": has_anti}
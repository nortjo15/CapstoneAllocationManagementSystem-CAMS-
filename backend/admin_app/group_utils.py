from student_app.models import Student, GroupPreference
from admin_app.models import ProjectPreference, Project
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

# Compute project intersection across a group
def get_group_project_intersection(students):
    project_sets = []
    for s in students:
        prefs = set(
            ProjectPreference.objects.filter(student=s).values_list("project_id", flat=True)
        )
        project_sets.append(prefs)

    if not project_sets:
        return set()

    return set.intersection(*project_sets)

# Classify a group of students as 'strong', 'medium' or 'weak'
# Return a dict with strength & flag
def classify_group(students, top_n=3):
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

    # Find all projects that every student in this group has preferenced 
    common_projects = get_group_project_intersection(students)
    if not common_projects:
        # No shared projects, nothing to classify 
        return [{"project": None, "strength": "invalid", "has_anti_preference": has_anti}]
    
    results = []

    # Loop once per common project
    for project_id in common_projects:
        project = Project.objects.get(pk=[project_id])

        # Reject if group is larger than project capacity
        if len(students) > project.capacity:
            results.append({
                "project": project,
                "strength": "invalid",
                "has_anti_preference": has_anti
            })
            continue
    
    # --- All Mutual likes ---
        if mutual_like_count == pair_count:
            ref = students[0]
            identical_order = all(have_identical_project_order(ref, s) for s in students[1:])
            same_set = all(have_same_project_set(ref, s) for s in students[1:])
            overlap_top = all(overlap_in_top_n_projects(ref, s, top_n) for s in students[1:])

            if identical_order:
                pref = ProjectPreference.objects.filter(student=ref, project=project).first()
                if pref and pref.rank in [1,2]:
                    if len(students) == project.capacity:
                        results.append({
                            "project": project,
                            "strength": "medium" if has_anti else "strong",
                            "has_anti_preference": has_anti
                        })
                        continue 
                    else: 
                        # Doesn't match capacity, medium group
                        results.append({
                            "project": project,
                            "strength": "medium",
                            "has_anti_preference": has_anti
                        })
                        continue
            
            if same_set or overlap_top:
                results.append({
                    "project": project,
                    "strength": "medium",
                    "has_anti_preference": has_anti
                })

        # Partial Likes or Project Overlap only
        results.append({
            "project": project,
            "strength": "weak",
            "has_anti_preference": has_anti
        })

    return results

        
# Builds an adjacency list for mutual 'like' preferences 
# Returns a dict: {student_id: set([liked_student_ids, ...])}
def build_likes_graph():
    graph =  {}
    likes = GroupPreference.objects.filter(preference_type="like")

    for pref in likes: 
        graph.setdefault(pref.student_id, set()).add(pref.target_student_id)

    return graph

# Obtain list of Student objects that form a mutual-like group
def find_mutual_like_groups(graph, students):
    # Map IDs -> Student Objects
    id_to_student = {s.student_id: s for s in students}
    student_ids = list(id_to_student.keys())

    # from size 2 up to N
    for r in range(2, len(student_ids) + 1):
        for combo in combinations(student_ids, r):
            # Check if all pairs in the combo are mutual likes 
            is_group = True 
            for a, b in combinations(combo, 2):
                if not (
                    b in graph.get(a, set()) and
                    a in graph.get(b, set())
                ):
                    is_group = False 
                    break 
            if is_group: 
                yield [id_to_student[sid] for sid in combo]

# Generates candidate groups from mutual-like groups, classifies them, returns results
def generate_suggestions_from_likes():
    # Get students not in a final group
    students = list(Student.objects.filter(allocated_group=False))
    graph = build_likes_graph()

    suggestions = []

    for group in find_mutual_like_groups(graph, students):
        results = classify_group(group)
        for result in results:
            if result["strength"] != "invalid":

                suggestions.append({
                    "students": [s.student_id for s in group],
                    "project": result["project"].title if result["project"] else None,
                    "strength": result["strength"],
                    "has_anti_preference": result["has_anti_preference"],
                })

                # Code here to actually create the SuggestedGroups later
    
    return suggestions
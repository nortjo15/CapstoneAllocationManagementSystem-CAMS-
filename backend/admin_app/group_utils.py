from student_app.models import Student, GroupPreference
from admin_app.models import ProjectPreference, Project, SuggestedGroup, SuggestedGroupMember
from itertools import combinations
import networkx as nx

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
        project = Project.objects.get(pk=project_id)

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

# Builds an undirected graph of students with mutual 'like' edges 
def build_mutual_like_graph():
    G = nx.Graph()

    # Add all students as nodes
    for s in Student.objects.filter(allocated_group=False):
        G.add_node(s)

    # Add edge if like is mutual 
    likes = GroupPreference.objects.filter(preference_type="like")
    for pref in likes: 
        if GroupPreference.objects.filter(
            student=pref.target_student, 
            target_student=pref.student, 
            preference_type="like"
        ).exists():
            G.add_edge(pref.student, pref.target_student)

    return G

# Generates candidate groups from mutual-like groups, classifies them, returns results
def generate_suggestions_from_likes():
    # Get students not in a final group
    students = list(Student.objects.filter(allocated_group=False))
    graph = build_mutual_like_graph()

    suggestions = []

    for clique in nx.find_cliques(graph):
        if len(clique) < 2:
            continue # Skip, can't have a group of 1 student

        results = classify_group(clique)

        for result in results:
            if result["strength"] == "invalid":
                continue 

            # --- SAVE SuggestedGroup in the DB ---
            sg = SuggestedGroup.objects.create(
                strength=result["strength"],
                has_anti_preference=result["has_anti_preference"],
                project=result["project"],
            )

            # Assign auto-generated name
            sg.name = f"group_{sg.suggestedgroup_id}"
            sg.save(update_fields=["name"])

            # Save members in SuggestedGroupMember
            for s in clique:
                SuggestedGroupMember.objects.create(
                    suggested_group=sg,
                    student=s
                )

            # Send dict as response
            suggestions.append({
                "suggested_group_id": sg.suggestedgroup_id, 
                "students": [s.student_id for s in clique],
                "project": result["project"].title, 
                "strength": result["strength"],
                "has_anti_preference": result["has_anti_preference"],
            })

    return suggestions
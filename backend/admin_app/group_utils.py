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

"""
Bulk Load group preferences, project preferences and projects for a set of students
Returns: 
    - group_likes 
    - group_avoids
    - project_prefs
    - projects

Significantly reduces amount of DB querying to improve operation performance
Uses pre-fetched data instead
"""
def prefetch_student_data(students):
    student_ids = [s.student_id for s in students]

    # Load Group Preferences
    prefs = GroupPreference.objects.filter(student_id__in=student_ids)
    group_likes, group_avoids = {}, {}
    for p in prefs:
        if p.preference_type == "like":
            group_likes.setdefault(p.student_id, set()).add(p.target_student_id)
        elif p.preference_type == "avoid":
            group_avoids.setdefault(p.student_id, set()).add(p.target_student_id)

    # Load project preferences
    proj_prefs = ProjectPreference.objects.filter(student_id__in=student_ids).order_by("rank")
    project_prefs = {}
    for pp in proj_prefs:
        project_prefs.setdefault(pp.student_id, []).append((pp.rank, pp.project_id))

    # Load all projects
    all_projects = Project.objects.all()
    projects  = {p.project_id: p for p in all_projects}

    return group_likes, group_avoids, project_prefs, projects

"""
Classify a group of students as 'strong', 'medium' or 'weak'
Return a dict with strength & flag
"""
def classify_group(students, group_likes, group_avoids, project_prefs, projects, top_n=3):
    if len(students) < 2:
        raise ValueError("Groups must contain at least 2 students")
    
    has_anti = False
    mutual_like_count = 0
    pair_count = 0
    ids = [s.student_id for s in students]

    # Pair by pair, check mutual like/avoid
    for i, a in enumerate(ids):
        for b in ids[i+1:]:
            pair_count += 1
            if b in group_avoids.get(a, set()) or a in group_avoids.get(b, set()):
                has_anti = True # Found an anti-preference
            if b in group_likes.get(a, set()) and a in group_likes.get(b, set()):
                mutual_like_count += 1

    # Common Projects
    sets = [set(pid for _, pid in project_prefs.get(sid, [])) for sid in ids] 
    if not sets or not all(sets):
        return [{"project": None, "strength": "invalid", "has_anti_preference": has_anti}]
    common_projects = set.intersection(*sets)
        
    results = []
    for project_id in common_projects:
        project = projects.get(project_id) 

        # If group is too large, skip it 
        if len(students) > project.capacity:
            results.append({
                "project": project,
                "strength": "invalid",
                "has_anti_preference": has_anti
            })
            continue 

        if mutual_like_count == pair_count: 
            ref_id = ids[0] # take first student as reference

            # Compare ordering 
            def prefs_as_list(sid): return [pid for _, pid in project_prefs.get(sid, [])]
            ref_prefs = prefs_as_list(ref_id)

            # For each student, compare preferences list with the prefix of ref_prefs of the same length, allowing for subset matches
            identical_order = all(ref_prefs[:len(prefs_as_list(sid))] == prefs_as_list(sid) for sid in ids[1:])
            # Compare projects sets (instead of order)
            same_set = all(
                set(ref_prefs).issubset(set(prefs_as_list(sid))) 
                or set(prefs_as_list(sid)).issubset(set(ref_prefs)) for sid in ids[1:]
                )
            # Compare top 3 projects
            overlap_top = all(
                bool(set(ref_prefs[:top_n]) & set(prefs_as_list(sid)[:top_n]))
                for sid in ids[1:]
            )

            if identical_order:
                rank_lookup = dict(project_prefs.get(ref_id, []))
                rank = rank_lookup.get(project_id)
                if rank in [1, 2]:
                    # Should generate a strong group, since top 1 or 2 project
                    if len(students) == project.capacity:
                        results.append({
                            "project": project,
                            "strength": "medium" if has_anti else "strong",
                            "has_anti_preference": has_anti
                        })
                        continue 
                    else: 
                        # Medium group for projects at preference 3 onwards
                        results.append({
                            "project": project,
                            "strength": "medium",
                            "has_anti_preference": has_anti
                        })
                        continue

            # Not identical order, but the top 3 projects overlap 
            if same_set or overlap_top:
                results.append({
                    "project": project, 
                    "strength": "medium",
                    "has_anti_preference": has_anti
                })

        # No matches - fallback to weak group
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
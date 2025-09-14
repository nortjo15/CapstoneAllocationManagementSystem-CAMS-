from student_app.models import Student, GroupPreference
from admin_app.models import ProjectPreference, Project, SuggestedGroup, SuggestedGroupMember
from itertools import combinations
from django.db import transaction
import networkx as nx

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
        # These students have group preferences, but no project preferences 
        if mutual_like_count == pair_count:
            return [{"project": None, "strength": "medium", "has_anti_preference": has_anti}]
        else:
            return [{"project": None, "strength": "weak", "has_anti_preference": has_anti}]
    
    common_projects = set.intersection(*sets)
        
    results = []
    for project_id in common_projects:
        project = projects.get(project_id) 

        if not project:
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
                        # Also catches overfill group
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

"""
Project-only grouping for students with no member preferences
- Group students who have no mutual likes but share the same top project(s)
- Always classified as weak
"""
def generate_project_only_groups(students, project_prefs, projects, top_n=1):
    groups = []
    project_bins = {}

    for s in students:
        prefs = project_prefs.get(s.student_id, [])
        if not prefs:
            continue # skip students with no preferences at all

        # Take their top-N projects
        top_projects = [pid for rank, pid in prefs if rank <= top_n]
        for pid in top_projects:
            project_bins.setdefault(pid, []).append(s)

    # Build groups 
    for pid, members in project_bins.items():
        if len(members) < 2:
            continue # Skip if less than 2 people
        project = projects.get(pid)
        if not project:
            continue

        sg = SuggestedGroup.objects.create(
            strength="weak",
            has_anti_preference=False,
            project=project,
        )
        sg.name = f"project_only_{sg.suggestedgroup_id}"
        sg.save(update_fields=["name"])

        # Add members 
        for s in members:
            SuggestedGroupMember.objects.create(suggested_group=sg, student=s)

        groups.append({
            "suggestedgroup_id": sg.suggestedgroup_id,
            "students": [s.student_id for s in members],
            "project": project.title,
            "strength": "weak",
            "has_anti_preference": False,
        })

    return groups
    
# Builds an undirected graph of students with mutual 'like' edges 
def build_mutual_like_graph():
    G = nx.Graph()

    # pre-fetch
    students = list(Student.objects.filter(allocated_group=False))
    id_to_student = {s.student_id: s for s in students}

    # Add as nodes
    G.add_nodes_from(students)

    # pre-fetch all like edges
    likes = GroupPreference.objects.filter(preference_type="like").values_list(
        "student_id", "target_student_id"
    )
    like_set = set(likes)

    # Add undirected edge if mutual
    for a, b in like_set:
        if a in id_to_student and b in id_to_student and (b, a) in like_set:
            G.add_edge(id_to_student[a], id_to_student[b])
    
    return G

# Generates candidate groups from mutual-like groups, classifies them, returns results
@transaction.atomic
def generate_suggestions_from_likes():
    # Clear out old suggested groups & members
    SuggestedGroupMember.objects.all().delete()
    SuggestedGroup.objects.all().delete()

    # Get students not in a final group
    students = list(Student.objects.filter(allocated_group=False))
    graph = build_mutual_like_graph()

    suggestions = []
    group_likes, group_avoids, project_prefs, projects = prefetch_student_data(students)

    for clique in nx.find_cliques(graph):
        if len(clique) < 2:
            continue # Skip, can't have a group of 1 student

        results = classify_group(clique, group_likes, group_avoids, project_prefs, projects)

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
                "suggestedgroup_id": sg.suggestedgroup_id, 
                "students": [s.student_id for s in clique],
                "project": result["project"].title, 
                "strength": result["strength"],
                "has_anti_preference": result["has_anti_preference"],
            })

    # Handle students not covered by any group preferences 
    # - They only have project preferences
    grouped_ids = {sid for g in suggestions for sid in g["students"]}
    remaining_students = [s for s in students if s.student_id not in grouped_ids]

    project_groups = generate_project_only_groups(remaining_students, project_prefs, projects, top_n=1) 
    suggestions.extend(project_groups)

    return suggestions

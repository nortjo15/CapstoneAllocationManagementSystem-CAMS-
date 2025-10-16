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

def classify_group(students, group_likes, group_avoids, project_prefs, projects, top_n=3):
    """
    Determines the classification strength of a potential group of students.
    Returns a list of result dictionaries, each describing the suggested
    project association and strength level.

    Classification summary:
        - Strongest: all members mutually like each other, identical project order,
          project within top 3 preferences, group size matches project capacity,
          and at least four distinct majors.
        - Strong: all members mutually like each other, same set of projects (not identical order),
          project within top 3 preferences, capacity match, and at least two distinct majors.
        - Medium: meets most strong conditions but has rank >=4, smaller size, or partial overlap
          in preferences. Also covers mutual-like groups without project data.
        - Weak: minimal alignment, partial likes or no shared project preferences.
    """

    if len(students) < 2:
        raise ValueError("Groups must contain at least 2 students")

    ids = [s.student_id for s in students]

    # Pairwise checks for mutual liking and anti-preferences
    pair_count = 0
    mutual_like_count = 0
    has_anti = False
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            pair_count += 1
            if b in group_avoids.get(a, set()) or a in group_avoids.get(b, set()):
                has_anti = True
            if b in group_likes.get(a, set()) and a in group_likes.get(b, set()):
                mutual_like_count += 1

    if has_anti:
        return []

    all_mutual_likes = mutual_like_count == pair_count

    # Utility: ordered preferences
    def prefs_as_list(sid):
        return [pid for _, pid in sorted(project_prefs.get(sid, []), key=lambda x: x[0])]

    # Metrics: diversity and CWA
    major_ids = set(s.major_id for s in students if s.major_id)
    major_diversity = len(major_ids)
    avg_cwa = sum(float(s.cwa or 0) for s in students) / len(students)

    # Handle no project preferences
    if not any(project_prefs.get(sid) for sid in ids):
        strength = "medium" if all_mutual_likes else "weak"
        return [{
            "project": None,
            "strength": strength,
            "has_anti_preference": False
        }]

    # Find common projects
    sets = [set(prefs_as_list(sid)) for sid in ids if prefs_as_list(sid)]
    common_projects = set.intersection(*sets) if sets else set()

    # If no common projects, check for similar CWAs (Weak fallback)
    if not common_projects:
        # CWA similarity: within ±5 or ±10 tolerance
        if len(students) > 1:
            min_cwa = min(float(s.cwa or 0) for s in students)
            max_cwa = max(float(s.cwa or 0) for s in students)
            diff = max_cwa - min_cwa
            if diff <= 5:
                strength = "medium" if all_mutual_likes else "weak"
            elif diff <= 10:
                strength = "weak"
            else:
                strength = "weak"
        else:
            strength = "weak"

        return [{
            "project": None,
            "strength": strength,
            "has_anti_preference": False
        }]

    # Project-based classification
    results = []

    for project_id in common_projects:
        project = projects.get(project_id)
        if not project:
            continue

        ref_id = ids[0]
        ref_prefs = prefs_as_list(ref_id)
        rank_lookup = {pid: rank for rank, pid in project_prefs.get(ref_id, [])}
        rank = rank_lookup.get(project_id)

        identical_order = all(ref_prefs == prefs_as_list(sid) for sid in ids[1:])
        same_set = all(set(ref_prefs) == set(prefs_as_list(sid)) for sid in ids[1:])
        # overlap ratio of shared top projects
        overlap_ratio = sum(
            1 for sid in ids[1:]
            if set(ref_prefs[:top_n]) & set(prefs_as_list(sid)[:top_n])
        ) / max(1, len(ids) - 1)

        # Rule hierarchy
        if all_mutual_likes:
            if (
                identical_order
                and rank is not None and rank <= 3
                and len(students) == project.capacity
                and major_diversity >= 4
            ):
                strength = "strongest"
            elif (
                same_set
                and rank is not None and rank <= 3
                and len(students) == project.capacity
                and 2 <= major_diversity < 4
            ):
                strength = "strong"
            elif (
                len(students) < project.capacity
                or (rank is not None and rank > 3)
                or overlap_ratio < 1.0
            ):
                # Sub-case: smaller than capacity or rank≥4
                strength = "medium"
            else:
                strength = "weak"
        else:
            # No full mutual liking → Weak by default
            strength = "weak"

        results.append({
            "project": project,
            "strength": strength,
            "has_anti_preference": False
        })

    # -------------------------------------------------
    # Limit to three strongest project matches per clique
    # Also refine tie-break using capacity, diversity, avg CWA
    # -------------------------------------------------
    if results:
        results = sorted(
            results,
            key=lambda r: (
                abs(len(students) - (r["project"].capacity if r["project"] else 0)),
                -major_diversity,
                -avg_cwa
            )
        )[:3]

    return results
    
def generate_project_only_groups(students, project_prefs, projects, top_n=1):
    """
    Creates weaker fallback groups for any remaining students who were not part
    of a mutual-like clique. Groups are primarily based on shared top project
    preferences, while also considering project capacity, balancing coverage,
    and CWA similarity.

    Behaviour summary:
        - Groups students who share the same top-N project preferences.
        - Respects project capacity limits.
        - Prioritises projects that currently have the fewest suggested groups.
        - Adds CWA-based matching when filling groups.
        - Remaining ungrouped students form diverse weak groups (4–5, ±CWA 5–10).
    """

    groups = []
    project_bins = {}

    # Group remaining students by their top-N project preferences
    for s in students:
        prefs = project_prefs.get(s.student_id, [])
        if not prefs:
            continue
        top_projects = [pid for rank, pid in prefs if rank <= top_n]
        for pid in top_projects:
            project_bins.setdefault(pid, []).append(s)

    # Determine which projects are least represented so far
    existing_counts = (
        SuggestedGroup.objects.filter(project__isnull=False, is_manual=False)
        .values_list("project_id")
    )
    project_usage = {}
    for pid, in existing_counts:
        project_usage[pid] = project_usage.get(pid, 0) + 1

    sorted_projects = sorted(
        project_bins.items(),
        key=lambda kv: project_usage.get(kv[0], 0)
    )

    allocated_students = set()

    # Create groups for each project
    for pid, members in sorted_projects:
        project = projects.get(pid)
        if not project:
            continue

        # Remove already grouped students
        members = [s for s in members if s.student_id not in allocated_students]
        if len(members) < 2:
            continue

        # Sort by descending CWA for balanced capacity
        members.sort(key=lambda s: float(s.cwa or 0), reverse=True)

        max_size = project.capacity or len(members)

        while members:
            # Take subset by capacity
            group_members = members[:max_size]
            members = members[max_size:]

            # Compute internal CWA range
            cwas = [float(s.cwa or 0) for s in group_members]
            diff = max(cwas) - min(cwas) if cwas else 0

            # Determine strength: "medium" if all CWAs within ±5, else "weak"
            strength = "medium" if diff <= 5 else "weak"

            sg = SuggestedGroup.objects.create(
                strength=strength,
                has_anti_preference=False,
                project=project,
            )
            sg.name = f"project_only_{sg.suggestedgroup_id}"
            sg.save(update_fields=["name"])

            for s in group_members:
                SuggestedGroupMember.objects.create(suggested_group=sg, student=s)
                allocated_students.add(s.student_id)

            groups.append({
                "suggestedgroup_id": sg.suggestedgroup_id,
                "students": [s.student_id for s in group_members],
                "project": project.title,
                "strength": strength,
                "has_anti_preference": False,
            })

    # Handle leftover ungrouped students with CWA-based fallback
    leftovers = [s for s in students if s.student_id not in allocated_students]

    # Sort by CWA to form similar-range clusters
    leftovers.sort(key=lambda s: float(s.cwa or 0), reverse=True)

    while leftovers:
        # take next 4–5 students near same CWA
        base_cwa = float(leftovers[0].cwa or 0)
        cluster = [s for s in leftovers if abs(float(s.cwa or 0) - base_cwa) <= 5]

        if len(cluster) < 2:
            # widen tolerance to ±10
            cluster = [s for s in leftovers if abs(float(s.cwa or 0) - base_cwa) <= 10]

        # limit cluster size to 5
        group_members = cluster[:5]
        # remove them from leftovers
        ids_to_remove = {s.student_id for s in group_members}
        leftovers = [s for s in leftovers if s.student_id not in ids_to_remove]

        if len(group_members) < 2:
            continue

        sg = SuggestedGroup.objects.create(
            strength="weak",
            has_anti_preference=False,
            project=None,
        )
        sg.name = f"fallback_{sg.suggestedgroup_id}"
        sg.save(update_fields=["name"])

        for s in group_members:
            SuggestedGroupMember.objects.create(suggested_group=sg, student=s)
            allocated_students.add(s.student_id)

        groups.append({
            "suggestedgroup_id": sg.suggestedgroup_id,
            "students": [s.student_id for s in group_members],
            "project": None,
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
    # Clear old autogenerated suggestions
    SuggestedGroupMember.objects.filter(
        suggested_group__is_manual=False
    ).delete()
    SuggestedGroup.objects.filter(is_manual=False).delete()

    students = list(Student.objects.filter(allocated_group=False))
    graph = build_mutual_like_graph()

    suggestions = []
    group_likes, group_avoids, project_prefs, projects = prefetch_student_data(students)

    # Iterate over all mutual-like cliques
    for clique in nx.find_cliques(graph):
        if len(clique) < 2:
            continue

        # Determine dominant project capacity (for over-capacity split)
        candidate_projects = set.intersection(
            *[
                set(pid for _, pid in project_prefs.get(s.student_id, []))
                for s in clique
                if project_prefs.get(s.student_id)
            ]
        )
        capacity = None
        if candidate_projects:
            sample_project = projects.get(next(iter(candidate_projects)))
            capacity = sample_project.capacity if sample_project else None

        # split clique by CWA if it exceeds capacity
        subgroups = split_clique_by_cwa(clique, capacity) if capacity else [clique]

        for subgroup in subgroups:
            if len(subgroup) < 2:
                continue

            # Classify subgroup based on mutual likes, prefs, and capacity
            results = classify_group(
                subgroup, group_likes, group_avoids, project_prefs, projects
            )

            # Create SuggestedGroup entries for each classified project result
            for result in results:
                sg = SuggestedGroup.objects.create(
                    strength=result["strength"],
                    has_anti_preference=result["has_anti_preference"],
                    project=result["project"],
                )
                sg.name = f"group_{sg.suggestedgroup_id}"
                sg.save(update_fields=["name"])

                for s in subgroup:
                    SuggestedGroupMember.objects.create(suggested_group=sg, student=s)

                suggestions.append({
                    "suggestedgroup_id": sg.suggestedgroup_id,
                    "students": [s.student_id for s in subgroup],
                    "project": result["project"].title if result["project"] else None,
                    "strength": result["strength"],
                    "has_anti_preference": result["has_anti_preference"],
                })

    # Handle ungrouped students to project-based or fallback Weak groups
    grouped_ids = {sid for g in suggestions for sid in g["students"]}
    remaining_students = [s for s in students if s.student_id not in grouped_ids]

    project_groups = generate_project_only_groups(
        remaining_students, project_prefs, projects, top_n=1
    )
    suggestions.extend(project_groups)

    return suggestions

def split_clique_by_cwa(students, project_capacity):
    """
    Split a mutual-like clique into subgroups if it exceeds a project's capacity.
    Groups higher CWA students together (descending sort).
    Balances leftover size (prefers even split: e.g., 5+4 over 6+3).
    """
    if project_capacity is None or len(students) <= project_capacity:
        return [students]

    # Sort descending by CWA (None -> 0.0)
    ordered = sorted(students, key=lambda s: float(s.cwa or 0), reverse=True)

    groups = []
    total = len(ordered)
    while total > 0:
        # When remainder smaller than half capacity, balance sizes
        if total - project_capacity < project_capacity / 2:
            size = (total + 1) // 2 if total > project_capacity else total
        else:
            size = project_capacity

        groups.append(ordered[:size])
        ordered = ordered[size:]
        total = len(ordered)

    return groups
GROUP CLASSIFICATION AND SORTING LOGIC

The system analyses student preferences, academic performance, and program diversity to automatically generate suggested groups. Each suggested group is classified into one of four strength levels: Strongest, Strong, Medium, or Weak. The goal is to maximise compatibility between students while ensuring balanced project allocation and major diversity.

1. STRONGEST GROUP
A “Strongest” group represents the highest-quality match between students and project preferences. Every condition below must be met:
• Mutual liking: Every member of the group has expressed a “like” for every other member, and there are no “avoid” preferences between any two students.
• Identical project preferences: All members have the exact same project preference order, meaning they ranked their preferred projects in the same sequence.
• Top-3 project match: The associated project appears within the top three preferences of every member.
• Exact capacity match: The total number of students in the group exactly matches the capacity of the associated project.
• Major diversity: The group contains at least four distinct majors. The system dynamically determines major diversity based on the data available, without relying on specific major names.
• Multiple projects: If all other conditions are met, up to three Strongest groups may be generated for the same set of students, one for each of their top three shared projects.
• Ordering within Strongest: If multiple Strongest groups exist, they are internally ranked by (1) how precisely they match project capacity, (2) the number of distinct majors.

1. STRONG GROUP
A “Strong” group meets most of the criteria of a Strongest group but with minor deviations. It represents a well-matched, reliable combination of students. A group will be classified as Strong if it satisfies the following:
• Mutual liking: All members mutually “like” each other, and there are no anti-preferences.
• Shared project set: All members have the same set of project preferences, but not necessarily in identical order.
• Top-3 project match: The associated project appears within the top three preferences of all members.
• Exact capacity match: The group size equals the capacity of the associated project.
• Moderate major diversity: The group includes at least two distinct majors but fewer than four.

1. MEDIUM GROUP
Medium groups represent combinations that are still viable but less optimal than Strong or Strongest. These groups typically have slightly weaker project alignment or incomplete capacity. A group will be classified as Medium if it meets any of the following:
• Meets Strongest criteria except group size is smaller than project capacity.
• Meets Strongest criteria except the associated project is ranked fourth or lower for one or more members.
• Members have mutual likes but differing or overlapping project preferences (shared subsets, not full matches).
• Members all mutually like each other but have no project preferences recorded.
• The group has been filled using additional students with similar project preferences or CWA alignment to reach capacity.

1. WEAK GROUP
Weak groups are fallback combinations created to ensure that all remaining students are included in a suggestion, even if they lack clear mutual preferences or shared projects. A group will be classified as Weak if it meets any of the following:
• Members share partial mutual liking but do not have any common projects.
• Members have similar top project choices but do not mutually like each other.
• Remaining students who are not part of any other suggestion are grouped together based on a mix of major diversity
• Weak groups are not automatically linked to a project at creation. The administrator may later assign a suitable project manually.

1. ADDITIONAL RULES
• Anti-preferences: If any two students have an “avoid” relationship, no suggestion will be created containing both students.
• Oversized cliques: If a group of mutually liking students exceeds the capacity of their preferred project, the system will automatically split them into smaller subgroups, sorted by CWA, while trying to keep strongly connected pairs together.
• Capacity balancing: When forming Medium or Weak groups, the system prioritises projects that currently have the fewest suggested groups, helping ensure balanced coverage across available projects.
• Leftover handling: Any students still ungrouped after all project-linked suggestions are created will be placed into small, diverse Weak groups (typically 4–5 members each).

This structured approach ensures that every student is considered, every project receives fair representation, and administrators can easily distinguish between the most and least compatible groupings.
# Group Suggestions Logic 
- Group Suggestion must map students -> project
- Multiple group suggestions could be generated for the same set of students
  - For each of their ranked preference 

## Strong Group 
- All students mutually preference each other
- Group Size <= Project Capacity
- Students rank the same project(s) in identical order
- Associated  project is ranked #1 or #2 by all students  
- has_anti_preference = False

## Medium Group
- All students mutually preference each other 
- Group size <= project capacity
- All students have the same set of project preferences, order may differ
- All students overlap on their top 3 projects, order may differ
- Meets strong group criteria but has_anti_preference = True

## Weak Group
- Partially preferenced students 
- Project preferences do not fully match (some overlap, but not across all students)
- OR has_anti_preference = True

# Capacity Constraint
- Group size should not exceed associated project's capacity 
- If a set of students exceeds the capacity, split into subsets I 

# Strongest Group
- All Members mutually like each other 
- All members have identical project preference ordering 
- The associated project is one of their top **3** preferences 
  - 3 groups would be generated in this case, one per project. May have different strengths depending on project capacity.
  - After accepting / creating a group, allocated students will be removed from the suggestions pool
  - Any suggestions referencing allocated students or assigned projects will be removed 
- Group size matches associated project capacity exactly 
- Group will have a mix of at least 4 majors 
  - Since the software is designed to be flexible and support admin-added majors/degrees, cannot be hard-coded to specify specific majors. 

# Strong Group 
- Matches all criteria of "Strongest" but weakened due to one of the following
  - Group is a mix of < 4 majors but at least 2 different ones are present
  - All members have the exact same projects preferenced, but not in identical order

# Medium Group 
- Same as "Strongest" but group size < project capacity 
- Same as "Strongest" but the associated project is at rank 4 or higher for the students
- Group size < project capacity but the group is filled with other students with similar/same project preferences
- Students with all mutual likes and no project preferences 
- Groups of students with same subsets of project preferences - prioritised & ordered group assignment by CWA 

# Weak Group
- Grouping of students by partial mutual liking for team members & no common projects
- Grouping of students by similar top projects
- Remaining students not yet part of a suggestion, grouped by CWA and mix of majors where possible. 

## Other Points of Note
- Where a member anti-preference occurs, a suggestion will not be formed with those students in it 
- For a large group of students who mutually prefer each other, but exceed the capacity of their preferred projects, the software will split the group evenly and find appropriate students to fill them with. Where relevant, CWA will be used as a prioritisation factor. 
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
- All students overlap on their top 3 probjects, order may differ
- Meets strong group criteria but has_anti_preference = True

## Weak Group
- Partially preferenced students 
- Project preferences do not fully match (some overlap, but not across all students)
- OR has_anti_preference = True

# Capacity Constraint
- Group size should not exceed associated project's capacity 
- If a set of students exceeds the capacity, split into subsets 
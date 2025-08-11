from student_app.models import Student 

class StudentFilter:
    """
    Encapsulates filtering logic for Student queryset.

    Allows filtering by CWA range, Degree, Major
    """
    def __init__(self, params):
        """
        params: QueryDict from request.GET
        """
        self.params = params

    def get_filtered_queryset(self):
        # All Students
        qs = Student.objects.all()

        # Filtering for CWA 
        # Get 'cwa_min' param, default to 0 if it's missing or invalid
        try: 
            cwa_min = float(self.params.get('cwa_min', 0))
        except ValueError: 
            cwa_min = 0

        # Get cwa_max param, default to 100 if missing or invalid
        cwa_max_raw = self.params.get('cwa_max')
        try: 
            cwa_max = float(cwa_max_raw) if cwa_max_raw is not None and cwa_max_raw != '' else 100
        except ValueError:
            cwa_max = 100

        # Filter queryset to students with cwa between the min & max
        qs = qs.filter(cwa__gte=cwa_min, cwa__lte=cwa_max)

        # Degree and Major filtering 
        # Recieve pair and split it 
        degree_major = self.params.get('degree_major', '').strip()
        if degree_major: 
                try: 
                    degree, major = degree_major.split('||', 1)
                    qs = qs.filter(degree=degree, major=major)
                except ValueError: 
                    pass #If it doesn't split correctly, skip it 

        # Sorting 
        sort_param = self.params.get('sort', '')
        # Ascending or descending based on filters
        sort_mapping = {
            'cwa_desc': '-cwa',
            'cwa_asc': 'cwa',
            'name_desc': '-name',
            'name_asc': 'name',
            'major_desc': '-major',
            'major_asc': 'major',
        }
        order_by = sort_mapping.get(sort_param, 'name')
        qs = qs.order_by(order_by)

        return qs; 

    # Get distinct degree, major pairs  from all students
    # Useful for populating dropdown filter options 
    # Returns a list of dicts with keys 'degree' and 'major'
    def get_degree_major_pairs(self):
        pairs = {}
        for item in Student.objects.order_by('degree', 'major').values('degree', 'major').distinct():
                degree = item.get('degree') or 'Unknown Degree'
                major = item.get('major') or 'Unknown Major'
                if degree not in pairs: 
                     pairs[degree] = []
                if major not in pairs[degree]:
                    pairs[degree].append(major)
        return pairs
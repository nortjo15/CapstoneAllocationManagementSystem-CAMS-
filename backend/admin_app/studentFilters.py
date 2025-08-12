from student_app.models import Student 
from django.db.models import Q

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
        degree_major_vals = self.params.getlist('degree_major')
        if degree_major_vals:
                # Container for query criteria and combining queries
                filters = Q()
                for val in degree_major_vals:
                    try: 
                        degree_name, major_name = val.split('||', 1)
                        filters |= Q(major__degree__name=degree_name, major__name=major_name) #Build an OR of selected pairs
                    except ValueError: 
                        continue 
                           
                qs = qs.filter(filters)

        # Filtering by application_submitted option 
        application_submitted = self.params.get('application_submitted', '').lower()
        if application_submitted == 'yes':
            qs = qs.filter(application_submitted=True)
        elif application_submitted == 'no':
            qs = qs.filter(application_submitted=False)

        # Group Status Column - Drop Down
        group_status = self.params.get('group_status', 'all').lower()

        if group_status == 'assigned':
            qs = qs.filter(allocated_group=True)
        elif group_status == 'unassigned':
            qs = qs.filter(allocated_group=False)
        # default else -> no filter for this option
             
        # Sorting 
        sort_param = self.params.get('sort', '')
        # Ascending or descending based on filters
        sort_mapping = {
            'cwa_desc': '-cwa',
            'cwa_asc': 'cwa',
            'name_desc': '-name',
            'name_asc': 'name',
            'major_desc': ('-degree', '-major'),
            'major_asc': ('degree', 'major'),
        }
        order_by = sort_mapping.get(sort_param, 'name')
        if isinstance(order_by, (list, tuple)):
            qs = qs.order_by(*order_by)
        else:
            qs = qs.order_by(order_by)
            
        return qs; 

    # Get distinct degree, major pairs  from all students
    # Useful for populating dropdown filter options 
    # Returns a list of dicts with keys 'degree' and 'major'
    def get_degree_major_pairs(self):
        pairs = {}

        from project_app.models import Degree 

        for degree in Degree.objects.prefetch_related('majors').order_by('name'):
            degree_name = degree.name or 'Unknown Degree'
            majors = degree.majors.order_by('name').values_list('name', flat=True)
            pairs[degree_name] = list(majors) or ['Unknown Major']

        return pairs
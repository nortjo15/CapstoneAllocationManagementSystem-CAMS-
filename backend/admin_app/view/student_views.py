import csv
from django.shortcuts import render, redirect
from student_app.models import Student 
from admin_app.models import *
from admin_app.studentFilters import StudentFilter
from django.views.decorators.http import require_http_methods
from admin_app.forms.student_forms import addStudentForm, importStudentForm
from io import TextIOWrapper
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render 
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

# Adding a basic students view page 
# Ensures only authenticated users can access it 
class StudentListView(LoginRequiredMixin, ListView):
    model = Student 
    template_name = "student_view.html"
    context_object_name = "students"

    def get_queryset(self):
        filter_object = StudentFilter(self.request.GET) #Initialises filter
        return filter_object.get_filtered_queryset() #Return filtered q-set
    
    # Context for template rendering 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_object = StudentFilter(self.request.GET)

        context.update({
            'degree_major_pairs': filter_object.get_degree_major_pairs(),
            'selected_pairs': self.request.GET.getlist('degree_major'),
            'cwa_min': self.request.GET.get('cwa_min', ''),
            'cwa_max': self.request.GET.get('cwa_max', ''),
            'application_submitted': self.request.GET.get('application_submitted', ''),
            'group_status': self.request.GET.get('group_status', 'all').lower(),
            'add_form': addStudentForm(),
            'import_form': importStudentForm(),
            'filter_target_url': reverse_lazy('admin_dashboard:student_view')
        })
        return context
    
# Creating a Student when Admin selects "Add Student"
class StudentCreateView(LoginRequiredMixin, CreateView):
    form_class = addStudentForm 
    template_name = 'admin_app/student_create_modal.html'
    success_url = reverse_lazy('admin_dashboard:admin_student_list') #Redirect upon success

    # Defines what happens when form is valid (POST with valid data)
    def form_valid(self, form):
        student = form.save(commit=False)
        student.application_submitted = False 
        student.allocated_group = False
        student.save()

        #Handle AJAX Request
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})
        
        return super().form_valid(form) #Default redirect
    
    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return super().form_invalid(form)  # Default re-render with errors
    
class StudentImportView(LoginRequiredMixin, FormView):
    template_name = 'admin_app/student_importCSV.html'
    form_class = importStudentForm
    success_url = reverse_lazy('admin_dashboard:admin_student_list')

    def form_valid(self, form):
        # CSV handling logic 
        csv_file = form.cleaned_data['csv_file']
        data_set = TextIOWrapper(csv_file.file, encoding='utf-8')
        reader = csv.DictReader(data_set)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]

        errors = []
        created_count = 0
        updated_count = 0

        # Check required columns
        required_columns = {'student_id', 'name'}
        if not required_columns.issubset(set(reader.fieldnames)):
            errors.append("CSV must contain 'student_id' and 'name' columns.")
            return self._handle_response(errors, created_count, updated_count)
        
        for i, row in enumerate(reader, start=1):
            # Skip completely empty rows
            if not any(row.values()):
                continue

            #Validation 
            student_id = row.get('student_id', '').strip()
            name = row.get('name', '').strip()
            # Needs to be adjusted for full name and last name

            # Store errors for invalid lines 
            if not student_id.isdigit() or len(student_id) != 8:
                errors.append(f"Row {i}: student_id must be exactly 8 digits.")
                continue 

            # Foreign Key Validation for Major
            major_name = row.get('major', '').strip()
            major_obj = None 
            if major_name: 
                try: 
                    major_obj = Major.objects.get(name=major_name)
                except Major.DoesNotExist:
                    errors.append(f"Row {i}: Major '{major_name}' does not exist.")
                    continue

            # Optional fields
            cwa = row.get('cwa')
            
            try:
                cwa = float(cwa) if cwa and cwa.strip() else None
                
                if cwa is not None and (cwa < 0 or cwa > 100):
                    errors.append(f"Row {i}: CWA must be between 0 and 100")
                    continue

            except ValueError:
                errors.append(f"Row {i}: CWA must be a number.")

            email = row.get('email')
            notes = row.get('notes')

            if Student.objects.filter(student_id=student_id.strip()).exists():
                student = Student.objects.get(student_id=student_id)
                # Update this student
                if name: 
                    student.name = name
                if cwa is not None: 
                    student.cwa = cwa 
                if major_obj is not None: 
                    student.major = major_obj
                if email:
                    student.email = email
                if notes: 
                    student.notes = notes 
                student.save()

                updated_count += 1
                continue

            # Create Student
            Student.objects.create(
                student_id=student_id,
                name=name,
                cwa=cwa if cwa else None,
                major=major_obj if major_obj else None, 
                email=email if email else None, 
                notes=notes if notes else None
            )
            created_count += 1 

        skipped_count = len(errors)
        return self._handle_response(errors, created_count, updated_count, skipped_count)
    
    def form_invalid(self, form):
        # Handle invalid form (no file, wrong type, etc.)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return super().form_invalid(form)
    
    # "Helper for consistent AJAX vs normal responses"
    def _handle_response(self, errors, created_count, updated_count, skipped_count=0):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": created_count + updated_count > 0,
                "errors": errors,
                "created_count": created_count,
                "skipped_count": skipped_count,
                "updated_count": updated_count
            })
        
        if errors:
            return self.render_to_response(self.get_context_data(
                form=self.get_form(),
                errors=errors,
                created_count=created_count,
                skipped_count=skipped_count,
                updated_count=updated_count
            ))
        
        messages.success(self.request, f"{created_count} students imported successfully!")
        return super().form_valid(self.get_form())
    
@login_required
@require_POST
def update_student_notes(request):
    student_id = request.POST.get('student_id')
    notes = request.POST.get('notes', '')

    if not student_id:
        return JsonResponse({"success": False, "error": "Missing student ID."})
    
    try: 
        student = Student.objects.get(student_id=student_id)
        student.notes = notes 
        student.save() #update student
        return JsonResponse({"success": True})
    except Student.DoesNotExist:
        return JsonResponse({"success": False, "error": "Student not found"})
    
# Partial Render (AJAX)
# Renders student table to a string when submitting or resetting filters
@method_decorator(never_cache, name='dispatch')
class StudentTableAjaxView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "student_table.html"
    context_object_name = "students"

    def get_queryset(self):
        filter_object = StudentFilter(self.request.GET)
        return filter_object.get_filtered_queryset()
    
    def render_to_response(self, context, **response_kwargs):
        html = render_to_string(self.template_name, context, self.request)
        return JsonResponse({"table_html": html})


TEMPLATE_MAP = {
    "round_closed": "emails/round_closed.txt",
    "application_success": "emails/application_success.txt",
    "allocation_released": "emails/allocation_released.txt",
    "generic_notice": "emails/generic_notice.txt",
}
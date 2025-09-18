from admin_app.models import Major
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from admin_app.forms.student_forms import addStudentForm, importStudentForm

@login_required 
def student_page(request):
    degree_major_pairs = {}
    for major in Major.objects.all():
        degree_major_pairs.setdefault(major.degree.name, []).append((major.id, major.name))


    selected_majors = request.GET.getlist("major")

    return render(request, "students/student_view.html",
        {
            "add_form": addStudentForm(),
            "import_form": importStudentForm(),
            "filter_target_url": request.path, 
            "degree_major_pairs": degree_major_pairs,
            "selected_majors": selected_majors,
        })
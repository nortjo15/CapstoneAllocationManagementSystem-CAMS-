from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import management
from admin_app.models import FinalGroup, SuggestedGroup
import json
from django.http import HttpResponse
#from django.contrib.admin.views.decorators import staff_member_required
from io import StringIO
import datetime
from admin_app.models import Project

#Email notification view, needs to be updated to use the API
@login_required
@user_passes_test(lambda u: u.is_staff)  # only staff/admins can access
def email_page(request):
    """
    Renders the admin email notification page.
    Filters projects to show only those with at least one internal round.
    """
    # Step 1: Get all projects that have at least one internal round
    internal_projects = Project.objects.filter(rounds__is_internal=True).distinct()

    # Step 2: Render the template with filtered projects
    return render(request, "admin_email.html", {"projects": internal_projects})

@login_required
def settings_view(request):
    return render(request, 'settings.html')

@login_required
def download_db(request):
    out = StringIO()
    management.call_command('dumpdata', '--indent', '2', stdout=out)
    data = out.getvalue()

    filename = f"db_backup_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def download_final_groups(request):
    #Build data
    data = []
    for group in FinalGroup.objects.prefetch_related('members__student').all():
        data.append({
            'group_name': group.name or f"FinalGroup {group.finalgroup_id}",
            'project_title': group.project.title,
            'students': [
                {'name': m.student.name, 'email': getattr(m.student, 'email', '')} 
                for m in group.members.all()
            ]
        })

    json_data = json.dumps(data, indent=2)

    filename = f"final_groups_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def download_suggested_groups(request):
    # Build data
    data = []
    for group in SuggestedGroup.objects.prefetch_related('members__student').all():
        project_title = group.project.title if group.project else None  # <-- safe check
        data.append({
            'group_name': group.name or f"SuggestedGroup {group.suggestedgroup_id}",
            'project_title': project_title,
            'students': [
                {'name': m.student.name, 'email': getattr(m.student, 'email', '')} 
                for m in group.members.all()
            ]
        })

    json_data = json.dumps(data, indent=2)

    filename = f"suggested_groups_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
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

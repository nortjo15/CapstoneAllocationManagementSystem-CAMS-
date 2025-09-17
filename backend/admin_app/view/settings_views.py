from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..models import AdminLog

#Settings view - user needs to be logged in
@login_required
def settings_view(request):
    # Get all admin logs, ordered by most recent first          
    admin_logs = AdminLog.objects.all().order_by('-timestamp')              
    
    context = {
        'admin_logs': admin_logs,
    }
    return render(request, 'settings.html', context)
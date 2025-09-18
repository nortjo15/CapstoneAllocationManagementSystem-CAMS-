from django.contrib.auth.decorators import login_required
from admin_app.models import AdminLog
from django.shortcuts import render, redirect
from rest_framework import viewsets
from admin_app.serializers import AdminLogSerializer

class AdminLogViewSet(viewsets.ModelViewSet):
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer

#Settings view - user needs to be logged in
@login_required
def settings_view(request):
    # Get all admin logs, ordered by most recent first          
    admin_logs = AdminLog.objects.all().order_by('-timestamp')
    
    context = {
        'admin_logs': admin_logs,
    }
    return render(request, 'settings.html', context)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

#Settings view - user needs to be logged in
@login_required
def settings_view(request):
    return render(request, 'settings.html')
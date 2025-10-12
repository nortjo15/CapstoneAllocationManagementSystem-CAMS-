from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def degree_view(request):
    return render(request, "degree_dashboard.html")



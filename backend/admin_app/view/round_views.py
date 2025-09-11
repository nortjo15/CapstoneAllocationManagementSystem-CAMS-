from django.shortcuts import render, get_object_or_404
from admin_app.models import *
from django.contrib.auth.decorators import login_required

#@login_required
def round_view(request):
   return render(request, "rounds.html")
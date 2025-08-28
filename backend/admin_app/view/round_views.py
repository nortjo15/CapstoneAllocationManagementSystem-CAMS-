from django.shortcuts import render
from django.contrib.auth.decorators import login_required

<<<<<<< HEAD
# @login_required
=======
@login_required
>>>>>>> merge-resolver/sprint-2
def round_view(request):
   return render(request, "rounds.html")
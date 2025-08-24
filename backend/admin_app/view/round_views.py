from django.shortcuts import render

@login_required
def round_view(request):
   return render(request, "rounds.html")
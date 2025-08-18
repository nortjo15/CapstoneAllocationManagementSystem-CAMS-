from django.shortcuts import render

def round_view(request):
   return render(request, "rounds.html")
from django.shortcuts import render, get_object_or_404
from admin_app.models import *
from django.contrib.auth.decorators import login_required

#@login_required
def round2_view(request):
   rounds = Round.objects.all()
   return render(request,
               "rounds2.html",
               {"rounds" : rounds})

def round2_detail_view(request, pk):
   rounds = Round.objects.all()
   round_obj = get_object_or_404(Round, pk=pk)
   return render(request,
                "rounds2.html",
                {"rounds" : rounds,
                "selected_round" : round_obj})

from django.shortcuts import render, get_object_or_404
from admin_app.models import Round
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from admin_app.api.serializers import *

class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer
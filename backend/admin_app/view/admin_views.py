from rest_framework import generics
from admin_app.models import AdminLog
from admin_app.serializers import AdminLogSerializer
from django.shortcuts import render

class AdminLogListCreateView(generics.ListCreateAPIView):
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer

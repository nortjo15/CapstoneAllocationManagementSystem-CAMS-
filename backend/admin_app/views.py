from rest_framework import generics
from .models import AdminLog
from .serializers import AdminLogSerializer

class AdminLogListCreateView(generics.ListCreateAPIView):
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer

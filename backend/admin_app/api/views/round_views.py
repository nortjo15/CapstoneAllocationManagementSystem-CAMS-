from admin_app.models import Round
from rest_framework import viewsets
from admin_app.api.serializers import RoundSerializer

class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer
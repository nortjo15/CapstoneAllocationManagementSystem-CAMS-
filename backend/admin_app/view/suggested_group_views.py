from rest_framework import generics
from admin_app.models import SuggestedGroup
from admin_app.serializers import SuggestedGroupSerializer

class SuggestedGroupListView(generics.ListAPIView):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer

class SuggestedGroupDetailView(generics.RetrieveAPIView):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer
    lookup_field  = 'suggestedgroup_id'


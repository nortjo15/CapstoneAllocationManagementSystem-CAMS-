from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from admin_app.models import *
from admin_app.serializers import *
from rest_framework import generics  
from rest_framework.views import APIView
from admin_app.group_utils import generate_suggestions_from_likes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404

# Webpage
class GroupListView(LoginRequiredMixin, ListView):
    model = SuggestedGroup
    template_name = "students/suggested_groups_view.html"  
    context_object_name = "suggested_groups"

# List + create suggested groups
class SuggestedGroupListCreateView(generics.ListCreateAPIView):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer

# Retrieve one suggested group by ID
class SuggestedGroupDetailView(generics.RetrieveAPIView):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer
    lookup_field = 'suggestedgroup_id'

# GroupMember 
class SuggestedGroupMemberListCreateView(generics.ListCreateAPIView):
    queryset = SuggestedGroupMember.objects.all()
    serializer_class = SuggestedGroupMemberSerializer

# GenerateSuggestions View
class GenerateSuggestionsView(APIView):
    def post(self, request, *args, **kwargs):
        # Run generator
        suggestions = generate_suggestions_from_likes()

        return Response(suggestions, status=status.HTTP_201_CREATED)
    
@api_view(["POST"])
def remove_student_from_group(request, pk):
    group = get_object_or_404(SuggestedGroup, pk=pk)
    student_id = request.data.get("student_id")
    SuggestedGroupMember.objects.filter(
        suggested_group=group,
        student__student_id=student_id
    ).delete()
    return Response({"status": "removed"})
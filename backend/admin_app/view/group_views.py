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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Build degree -> majors dict
        degree_major_pairs = {}
        for major in Major.objects.all():
            degree_major_pairs.setdefault(major.degree.name, []).append((major.id, major.name))

        context["degree_major_pairs"] = degree_major_pairs
        context["selected_majors"] = self.request.GET.getlist("major")
        context["filter_target_url"] = self.request.path
        context["groups_page"] = True #Used to filter the table

        return context

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
    
# SuggestedGroupUpdate View
class SuggestedGroupUpdateView(generics.UpdateAPIView):
    queryset = SuggestedGroup.objects.all()
    serializer_class = SuggestedGroupSerializer
    lookup_field = "suggestedgroup_id"
    
@api_view(["POST"])
def remove_student_from_group(request, pk):
    group = get_object_or_404(SuggestedGroup, pk=pk)
    student_id = request.data.get("student_id")
    SuggestedGroupMember.objects.filter(
        suggested_group=group,
        student__student_id=student_id
    ).delete()

    serializer = SuggestedGroupSerializer(group)
    return Response(serializer.data)

@api_view(["POST"])
def add_student_to_group(request, pk):
    group = get_object_or_404(SuggestedGroup, pk=pk)
    student_id = request.data.get("student_id")

    if not student_id:
        return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST) 
    
    # Look up student
    student = get_object_or_404(Student, student_id=student_id)

    # Prevent duplicates
    if SuggestedGroupMember.objects.filter(suggested_group=group, student=student).exists():
        serializer = SuggestedGroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    SuggestedGroupMember.objects.create(suggested_group=group, student=student)
    serializer = SuggestedGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
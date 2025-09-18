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
    queryset = SuggestedGroup.objects.select_related("project").prefetch_related("members__student__major")
    serializer_class = SuggestedGroupSerializer

class SuggestedGroupLiteListView(generics.ListAPIView):
    serializer_class = SuggestedGroupLiteSerializer

    def get_queryset(self):
        return (
            SuggestedGroup.objects
            .select_related("project")
            .prefetch_related("members__student__major")
            .filter(is_manual=False)   # only auto groups
        )

# Retrieve one suggested group by ID
class SuggestedGroupDetailView(generics.RetrieveAPIView):
    serializer_class = SuggestedGroupSerializer
    lookup_field = 'suggestedgroup_id'

    def get_queryset(self):
        return (
            SuggestedGroup.objects
            .select_related("project")
            .prefetch_related(
                "members__student__major",
                "members__student__preferences__project",
                "members__student__given_preferences__target_student",
                "members__student__received_preferences__student",
            )
        )


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

# ManualGroups View
class ManualGroupListView(generics.ListAPIView):
    serializer_class = SuggestedGroupLiteSerializer

    def get_queryset(self):
        return SuggestedGroup.objects.select_related("project").prefetch_related("members__student__major").filter(is_manual=True)
    
@api_view(["POST"])
def remove_student_from_group(request, suggestedgroup_id):
    group = get_object_or_404(SuggestedGroup, suggestedgroup_id=suggestedgroup_id)
    student_id = request.data.get("student_id")
    SuggestedGroupMember.objects.filter(
        suggested_group=group,
        student__student_id=student_id
    ).delete()

    group = (
        SuggestedGroup.objects
        .select_related("project")
        .prefetch_related("members__student__major")
        .get(pk=group.pk)
    )

    serializer = SuggestedGroupLiteSerializer(group)
    return Response(serializer.data)

@api_view(["POST"])
def add_student_to_group(request, suggestedgroup_id):
    group = get_object_or_404(SuggestedGroup, suggestedgroup_id=suggestedgroup_id)
    student_id = request.data.get("student_id")

    if not student_id:
        return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST) 
    
    # Look up student
    student = get_object_or_404(Student, student_id=student_id)

    group = (
        SuggestedGroup.objects
        .select_related("project")
        .prefetch_related("members__student__major")
        .get(pk=group.pk)
    )

    # Prevent duplicates
    if SuggestedGroupMember.objects.filter(suggested_group=group, student=student).exists():
        serializer = SuggestedGroupLiteSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    SuggestedGroupMember.objects.create(suggested_group=group, student=student)
    group.refresh_from_db()
    serializer = SuggestedGroupLiteSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def create_manual_group(request):
    existing = (
        SuggestedGroup.objects.filter(name__startswith="Manual Group")
        .values_list("name", flat=True)
    )
    
    # Extract numbers
    numbers = []
    for n in existing: 
        parts = n.split(" ")
        if len(parts) == 3 and parts[2].isdigit():
            numbers.append(int(parts[2]))

    next_num = max(numbers) + 1 if numbers else 1

    group = SuggestedGroup.objects.create(
        name=f"Manual Group {next_num}",
        project=None,
        is_manual=True
    )
    return Response(SuggestedGroupLiteSerializer(group).data)

@api_view(["DELETE"])
def delete_manual_group(request, suggestedgroup_id):
    group = get_object_or_404(SuggestedGroup, suggestedgroup_id=suggestedgroup_id, is_manual=True)
    group.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# FinalGroup Create View
class FinalGroupCreateView(generics.CreateAPIView):
    queryset = FinalGroup.objects.all()
    serializer_class = FinalGroupCreateSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
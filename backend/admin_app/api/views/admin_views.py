from rest_framework import generics, viewsets
from admin_app.api.serializers import AdminLogSerializer
from admin_app import email_service
from admin_app.models import AdminLog, Project, Round, FinalGroup
from student_app.models import Student
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.core.mail import send_mail
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.pagination import PageNumberPagination
from admin_app.api.serializers import AdminLogSerializer
from rest_framework.decorators import action

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

class AdminLogViewSet(viewsets.ModelViewSet):
    queryset = AdminLog.objects.all().order_by('-timestamp')
    serializer_class = AdminLogSerializer
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=['delete'], permission_classes=[IsAdminUser])
    def clear(self, request):
        """Delete all AdminLog entries and return the count deleted."""
        deleted, _ = AdminLog.objects.all().delete()
        return Response({"deleted": deleted})

class SendRoundStartView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, round_id):
        try:
            round_obj = Round.objects.get(pk=round_id)
        except Round.DoesNotExist:
            return Response({"error": "Round not found"}, status=404)

        sent = email_service.send_round_start(round_obj)
        return Response({"ok": True, "sent": sent})


class SendRoundClosedView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, round_id):
        try:
            round_obj = Round.objects.get(pk=round_id)
        except Round.DoesNotExist:
            return Response({"error": "Round not found"}, status=404)

        sent = email_service.send_round_closed(round_obj)
        return Response({"ok": True, "sent": sent})


class SendApplicationSuccessView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, student_id):
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        sent = email_service.send_application_success(student)
        return Response({"ok": True, "sent": sent})


class SendAllocationReleasedView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, final_group_id):
        sent = email_service.send_allocation_released(final_group_id)
        return Response({"ok": True, "sent": sent})

from rest_framework import generics
from admin_app.models import AdminLog
from admin_app.serializers import AdminLogSerializer
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from rest_framework.response import Response
from admin_app.models import Round, FinalGroup
from student_app.models import Student
from admin_app import email_service
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from admin_app.models import Project



class AdminLogListCreateView(generics.ListCreateAPIView):
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer



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
    


@login_required
@user_passes_test(lambda u: u.is_staff)  # only staff/admins can access
def email_page(request):
    """Render the Email Notifications page with projects for industry emails"""
    projects = Project.objects.all()
    return render(request, "admin_email.html", {"projects": projects})
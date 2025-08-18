from rest_framework import generics
from admin_app.models import AdminLog
from admin_app.serializers import AdminLogSerializer
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail


class AdminLogListCreateView(generics.ListCreateAPIView):
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer

class SendNotificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        """
        POST JSON:
        {
            "subject": "Your Subject Here",
            "template_key": "round_closed",
            "audience": "students" | "hosts" | "final_group" | "custom",
            "round_name": "Round 1",
            "project_name": "Project X",
            "final_group_id": 5,
            "emails": ["test@example.com"],
            "message_body": "Optional extra message"
        }
        """
        data = request.data
        subject = data.get("subject")
        template_key = data.get("template_key")
        audience = data.get("audience")

        if not subject or not template_key or not audience:
            return Response({"error": "Missing required fields"}, status=400)

        template_path = TEMPLATE_MAP.get(template_key)
        if not template_path:
            return Response({"error": f"Unknown template_key '{template_key}'"}, status=400)

        context = {
            "round_name": data.get("round_name", ""),
            "project_name": data.get("project_name", ""),
            "message_body": data.get("message_body", ""),
        }

        recipients = []
        if audience == "students":
            recipients = list(
                Student.objects.exclude(email__isnull=True).exclude(email="").values_list("email", flat=True)
            )
        elif audience == "hosts":
            recipients = list(
                Project.objects.exclude(host_email__isnull=True).exclude(host_email="").values_list("host_email", flat=True)
            )
        elif audience == "final_group":
            if not data.get("final_group_id"):
                return Response({"error": "final_group_id required for audience=final_group"}, status=400)
            members = FinalGroupMember.objects.filter(final_group_id=data["final_group_id"]).select_related("student")
            recipients = [m.student.email for m in members if m.student.email]
        elif audience == "custom":
            recipients = data.get("emails", [])
        else:
            return Response({"error": "Invalid audience"}, status=400)

        if not recipients:
            return Response({"error": "No recipients found"}, status=400)

        message = render_to_string(template_path, context)
        sent = 0
        for email in recipients:
            sent += send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

        return Response({"ok": True, "sent": sent})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from admin_app.email_service import generate_mailto_link

class MailtoLinkView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        subject = request.data.get("subject")
        body = request.data.get("body")
        audience = request.data.get("audience")
        final_group_id = request.data.get("final_group_id")

        if not subject or not body or not audience:
            return Response({"error": "Missing fields"}, status=400)

        link = generate_mailto_link(subject, body, audience, final_group_id)
        return Response({"mailto_link": link})
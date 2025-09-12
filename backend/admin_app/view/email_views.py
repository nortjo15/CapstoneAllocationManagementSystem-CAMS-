# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from admin_app.email_service import generate_mailto_link


NOTIFICATION_TEMPLATES = {
    "round_start": {
        "subject": "Round {round_num} Started",
        "body": "Dear Students,\n\nRound {round_num} has started.\n\nRegards,\nAdmin",
        "audience": "students",
    },
    "round_end": {
        "subject": "Round {round_num} Closed",
        "body": "Dear Students,\n\nRound {round_num} has been closed.\n\nRegards,\nAdmin",
        "audience": "students",
    },
    "post_round_finish_industry": {
        "subject": "Candidate CVs",
        "body": "Dear Industry Partner,\n\nPlease find attached batches of relevant CVs/Resumes.\n\nRegards,\nAdmin",
        "audience": "industry",
    },
    "post_round_finish_students": {
        "subject": "Round Outcome",
        "body": "Dear Student,\n\nWe are pleased to inform you of your outcome. Please check the portal for details.\n\nRegards,\nAdmin",
        "audience": "students",
    },
    "post_round_finish_finalised_groups": {
        "subject": "Final Allocation Notification",
        "body": "Dear Group,\n\nYour allocation has been finalised. Please review the details on the portal.\n\nRegards,\nAdmin",
        "audience": "finalised_groups",
    },
}


class MailtoLinkView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        notification_type = request.data.get("notification_type")
        final_group_id = request.data.get("final_group_id")
        round_num = request.data.get("round_num")

        if notification_type not in NOTIFICATION_TEMPLATES:
            return Response({"error": "Invalid notification type"}, status=400)

        tpl = NOTIFICATION_TEMPLATES[notification_type]

        subject = tpl["subject"]
        body = tpl["body"]

        # inject round number only for round_start / round_end
        if notification_type in ["round_start", "round_end"]:
            if not round_num:
                return Response({"error": "round_num is required"}, status=400)
            subject = subject.format(round_num=round_num)
            body = body.format(round_num=round_num)

        link = generate_mailto_link(
            subject, body, tpl["audience"], final_group_id
        )
        return Response({"mailto_link": link})

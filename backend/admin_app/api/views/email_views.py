# --- Notification templates ---
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
        "body": "Dear Student,\n\nYour allocation has been finalised. Please review the details on the portal.\n\nRegards,\nAdmin",
        "audience": "finalised_groups",
    },
}


















class MailtoLinkView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        notification_type = request.data.get("notification_type")
        round_num = request.data.get("round_num")
        project_id = request.data.get("project_id")

        if notification_type not in NOTIFICATION_TEMPLATES:
            return Response({"error": "Invalid notification type"}, status=400)

        tpl = NOTIFICATION_TEMPLATES[notification_type]
        subject, body = tpl["subject"], tpl["body"]

        if notification_type in ["round_start", "round_end"]:
            if not round_num:
                return Response({"error": "round_num is required"}, status=400)
            subject = subject.format(round_num=round_num)
            body = body.format(round_num=round_num)

        if notification_type == "post_round_finish_industry":
            if not project_id:
                return Response({"error": "project_id is required"}, status=400)

            # Ensure project is linked to an internal round
            valid_project = Project.objects.filter(pk=project_id, rounds__is_internal=True).distinct()
            if not valid_project.exists():
                return Response({"error": "Invalid project (not internal)"}, status=400)

        link = generate_mailto_link(subject, body, audience=tpl["audience"], project_id=project_id)
        if not link:
            return Response({"error": "Could not generate mailto link"}, status=400)

        return Response({"mailto_link": link})


class ProjectResumesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=404)

        members = FinalGroupMember.objects.filter(final_group__project=project).select_related("student")
        resumes = []
        for member in members:
            student = member.student
            if student and student.resume:
                resumes.append({
                    "student_id": student.student_id,
                    "name": student.name,
                    "resume_url": request.build_absolute_uri(student.resume.url),
                })

        return Response({"project": project.title, "resumes": resumes})


class ProjectResumesZipView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return HttpResponse("Project not found", status=404)

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            members = FinalGroupMember.objects.filter(final_group__project=project).select_related("student")
            for member in members:
                student = member.student
                if student and student.resume:
                    file_path = student.resume.name
                    file_name = f"{student.student_id}_resume.pdf"
                    try:
                        with default_storage.open(file_path, "rb") as f:
                            zip_file.writestr(file_name, f.read())
                    except Exception:
                        continue

        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="project_{project_id}_resumes.zip"'
        return response


# --- Email Service ---
def generate_mailto_link(subject, body, audience="students", project_id=None):
    recipients = []

    if audience == "students":
        # Only students in final groups of projects with at least one internal round
        members = FinalGroupMember.objects.select_related("final_group__project", "student")
        recipients = [
            m.student.email
            for m in members
            if m.student and m.student.email and m.final_group.project.rounds.filter(is_internal=True).exists()
        ]
        if not recipients:
            return None

    elif audience == "hosts":
        recipients = list(Project.objects.exclude(host_email__isnull=True).exclude(host_email="").values_list("host_email", flat=True))
    elif audience == "finalised_groups":
        members = FinalGroupMember.objects.select_related("student")
        recipients = [m.student.email for m in members if m.student and m.student.email]
        if not recipients:
            return None
    elif audience == "industry" and project_id:
        try:
            project = Project.objects.get(pk=project_id, rounds__is_internal=True)
        except Project.DoesNotExist:
            return None

        recipients = [project.host_email] if project.host_email else []

        final_groups = project.final_groups.all().prefetch_related("members__student")
        resume_links = []
        for group in final_groups:
            for member in group.members.all():
                if member.student.resume:
                    resume_links.append(f"{settings.MEDIA_URL}{member.student.resume}")

        if resume_links:
            body += "\n\nAttached CVs/Resumes (please download from links):\n" + "\n".join(resume_links)
        else:
            body += "\n\n(No resumes found for this project)"

    if not recipients:
        return None

    to_emails = ";".join(recipients)
    query = urllib.parse.urlencode({"subject": subject, "body": body}, quote_via=urllib.parse.quote)
    return f"mailto:{to_emails}?{query}"


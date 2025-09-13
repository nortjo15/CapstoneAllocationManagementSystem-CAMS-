import urllib.parse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from student_app.models import Student
from .models import Project, FinalGroupMember, Round

def generate_mailto_link(subject, body, audience="students", final_group_id=None):
    if audience == "students":
        recipients = list(
            Student.objects.exclude(email__isnull=True).exclude(email="").values_list("email", flat=True)
        )
    elif audience == "hosts":
        recipients = list(
            Project.objects.exclude(host_email__isnull=True).exclude(host_email="").values_list("host_email", flat=True)
        )
    elif audience == "finalised_groups":
        # get all students part of any final group
        members = FinalGroupMember.objects.select_related("student")
        recipients = [m.student.email for m in members if m.student.email]
    else:
        recipients = []

    to_emails = ";".join(recipients)

    import urllib.parse
    params = {"subject": subject, "body": body}
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

    return f"mailto:{to_emails}?{query}"
















# def _send_bulk_email(recipients, subject, template_path, context):
 #   """Helper to render template and send emails to multiple recipients"""
  #  if not recipients:
   #     return 0
#
 #   message = render_to_string(template_path, context)
  #  sent = 0
   # for email in recipients:
    ##    sent += send_mail(
      #      subject=subject,
       #     message=message,
        #    from_email=settings.DEFAULT_FROM_EMAIL,
         #   recipient_list=[email],
          #  fail_silently=False,
        #)
    #return sent


#def send_round_start(round_obj: Round):
 #   """Notify students + hosts when a round opens"""
  #  recipients = list(Student.objects.exclude(email__isnull=True).exclude(email="").values_list("email", flat=True))
   # host_emails = list(Project.objects.exclude(host_email__isnull=True).exclude(host_email="").values_list("host_email", flat=True))
    #recipients.extend(host_emails)

    #return _send_bulk_email(
     #   recipients,
      #  subject=f"{round_obj.round_name} Started",
       # template_path="emails/round_start.txt",
        #context={"round_name": round_obj.round_name}
   # )


#def send_round_closed(round_obj: Round):
 #   """Notify students when a round closes"""
  #  recipients = list(Student.objects.exclude(email__isnull=True).exclude(email="").values_list("email", flat=True))
#
 #   return _send_bulk_email(
  #      recipients,
   #     subject=f"{round_obj.round_name} Closed",
    #    template_path="emails/round_closed.txt",
     #   context={"round_name": round_obj.round_name}
    #)


#def send_application_success(student: Student):
 #   """Notify one student after successful application"""
  ##  if not student.email:
    #    return 0

    #return _send_bulk_email(
     #   [student.email],
      #  subject="Application Submitted Successfully",
       # template_path="emails/application_success.txt",
        #context={"student_name": student.name}
    #)


#def send_allocation_released(final_group_id: int):
 #   """Notify all students in a final group when allocation is released"""
  #  members = FinalGroupMember.objects.filter(final_group_id=final_group_id).select_related("student")
#    recipients = [m.student.email for m in members if m.student.email]
#
 #   return _send_bulk_email(
  #      recipients,
   #     subject="Group Allocation Released",
    ##    template_path="emails/allocation_released.txt",
      #  context={"group_id": final_group_id}
    #)

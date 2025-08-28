from django.core.management.base import BaseCommand
from django.utils import timezone
from admin_app.models import CapstoneInformationContent

#This command archives expired announcements by setting their status to 'archived'.
#This should eb run periodically via a container task.
class Command(BaseCommand):
    help = "Archive expired announcements (status → 'archived')."

    def handle(self, *args, **opts):
        now = timezone.now()
        qs = CapstoneInformationContent.objects.filter(expires_at__lte=now, status__in=["draft", "published"])
        n = qs.update(status="archived")
        self.stdout.write(self.style.SUCCESS(f"Archived {n} announcements."))

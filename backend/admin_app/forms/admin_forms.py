from django import forms
from django.utils import timezone
from admin_app.models import CapstoneInformationContent

class AnnouncementForm(forms.ModelForm):
    published_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = CapstoneInformationContent
        fields = [
            "title", "section_id", "body",
            "status", "priority", "pinned",
            "published_at", "expires_at",
            "author",
        ]
        widgets = {"body": forms.Textarea(attrs={"rows": 8})}

    def clean(self):
        data = super().clean()
        pub = data.get("published_at")
        exp = data.get("expires_at")
        if pub is None:
            data["published_at"] = timezone.now()
        if pub and exp and exp <= pub:
            self.add_error("expires_at", "Expiry must be after Published time.")
        return data

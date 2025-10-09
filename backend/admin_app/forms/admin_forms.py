from django import forms
from admin_app.models import CapstoneInformationContent, CapstoneInformationSection

class InformationForm(forms.ModelForm):
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = CapstoneInformationContent
        fields = [
            "title", "section_id", "body",
            "status", "priority", "pinned",
            "expires_at",
            "author",
        ]
        widgets = {"body": forms.Textarea(attrs={"rows": 8})}

    def clean(self):
        data = super().clean()
        # Keep expiry optional. No hard validation needed.
        return data

class SectionForm(forms.ModelForm):
    class Meta:
        model = CapstoneInformationSection
        fields = ["name", "parent_section", "order"]

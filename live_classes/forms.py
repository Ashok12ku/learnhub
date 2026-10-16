from django import forms
from .models import LiveClass


class LiveClassForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ["title", "platform", "meeting_link", "scheduled_at", "duration_minutes", "notes"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Week 3 Live Doubt Session"}),
            "platform": forms.Select(attrs={"class": "form-select"}),
            "meeting_link": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://zoom.us/j/... or https://meet.google.com/..."}),
            "scheduled_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Optional agenda/notes"}),
        }

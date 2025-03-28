from django import forms
from .models import Event, EventOption
from datetime import datetime, timedelta


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "image", "deadline", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "deadline": forms.DateTimeInput(attrs={
                "class": "input",
                "type": "datetime-local"
            }),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default deadline to tomorrow at 12:00
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_noon = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
        self.fields['deadline'].initial = tomorrow_noon

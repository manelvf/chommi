from django import forms
from .models import Event, EventOption


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "image", "deadline", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "deadline": forms.DateTimeInput(attrs={"class": "form-control"}),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

from django import forms
from .models import Event, EventOption
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory


IMAGE_SIZE_LIMIT = 2 * 1024 * 1024


class EventOptionForm(forms.ModelForm):
    class Meta:
        model = EventOption
        fields = ['title', 'initial_odds']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'initial_odds': forms.NumberInput(attrs={'class': 'input', 'step': '0.01', 'min': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the form's position in the formset
        if 'prefix' in kwargs:
            form_number = int(kwargs['prefix'].split('-')[-1]) + 1
            self.fields['title'].label = f'Opción {form_number}'

    def clean_initial_odds(self):
        odds = self.cleaned_data.get('initial_odds')
        if odds <= 0:
            raise ValidationError('Las cuotas deben ser mayores a 0')
        return odds


EventOptionFormSet = inlineformset_factory(
    Event,
    EventOption,
    form=EventOptionForm,
    extra=1,
    can_delete=True,
    min_num=2,
    max_num=7,
    validate_min=True,
    validate_max=True
)


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

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > IMAGE_SIZE_LIMIT:  # 2MB in bytes
                raise ValidationError('La imagen no puede ser mayor a 2MB.')
        return image

from django import forms
from .models import Event, EventOption
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from django.core.files import File
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import imghdr
import os
import json


IMAGE_SIZE_LIMIT = 4 * 1024 * 1024
IMAGE_DIMENSIONS = (300, 300)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}


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
            self.fields['title'].label = _('Opción %(number)d') % {'number': form_number}
            # Make fields required
            self.fields['title'].required = True
            self.fields['initial_odds'].required = True

    def clean_initial_odds(self):
        odds = self.cleaned_data.get('initial_odds')
        if odds <= 0:
            raise ValidationError(_('Las cuotas deben ser mayores a 0'))
        return odds


class CustomEventOptionFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not self.is_valid():
            return

        # Count non-deleted forms with data
        non_deleted_forms = [form for form in self.forms if not form.cleaned_data.get('DELETE', False)]
        valid_forms = [form for form in non_deleted_forms if form.cleaned_data.get('title') and form.cleaned_data.get('initial_odds')]

        if len(valid_forms) < 2:
            raise ValidationError(_('Debes proporcionar al menos 2 opciones válidas para el evento.'))

    def save(self, commit=True):
        instances = super().save(commit=False)
        for instance in instances:
            if not instance.pk:  # Only for new instances
                instance.current_odds = instance.initial_odds
        if commit:
            self.save_m2m()
            for instance in instances:
                instance.save()
        return instances


EventOptionFormSet = inlineformset_factory(
    Event,
    EventOption,
    form=EventOptionForm,
    formset=CustomEventOptionFormSet,
    extra=1,
    can_delete=True,
    min_num=2,
    max_num=7,
    validate_min=True,
    validate_max=True
)


class ImageUploadForm(forms.ModelForm):
    debug_info = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Event
        fields = ["title", "description", "image", "deadline", "is_public", "creator"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "deadline": forms.DateTimeInput(attrs={
                "class": "input",
                "type": "datetime-local"
            }),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "creator": forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)
        
        # Set default deadline only for new events
        if not self.instance.pk:
            tomorrow = timezone.now() + timedelta(days=1)
            tomorrow_noon = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
            self.fields['deadline'].initial = tomorrow_noon

        # Add debug info if DEBUG is enabled
        if settings.DEBUG:
            self.fields['debug_info'].widget = forms.Textarea(attrs={
                'class': 'debug-info',
                'readonly': True,
                'style': 'display: none;'
            })

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        now = timezone.now()
        
        # For existing events, allow the current deadline
        if self.instance.pk and deadline == self.instance.deadline:
            return deadline
        
        # Check if deadline is in the past
        if deadline <= now:
            raise ValidationError(_('La fecha límite debe ser en el futuro.'))
        
        # Check if deadline is too far in the future (e.g., 1 year)
        max_future = now + timedelta(days=365)
        if deadline > max_future:
            raise ValidationError(_('La fecha límite no puede ser más de un año en el futuro.'))
        
        return deadline

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            # If no new image is provided and we're editing, return the existing image
            if self.instance.pk and self.instance.image:
                return self.instance.image
            return image

        # Check file size
        if image.size > IMAGE_SIZE_LIMIT:
            raise ValidationError(_('La imagen no puede ser mayor a 2MB.'))

        # Check file extension
        extension = image.name.split('.')[-1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValidationError(_('Solo se permiten archivos de imagen (PNG, JPG, JPEG, GIF).'))

        # Check content type
        if image.content_type not in ALLOWED_MIME_TYPES:
            raise ValidationError(_('El archivo debe ser una imagen válida (PNG, JPG, JPEG, GIF).'))

        try:
            # Try to open and verify the image
            img = Image.open(image)
            img.verify()  # Verify it's a valid image
            image.seek(0)  # Reset file pointer after verify
            
            # Reopen the image for processing
            img = Image.open(image)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Resize the image
            img.thumbnail(IMAGE_DIMENSIONS, Image.Resampling.LANCZOS)
            
            # Save the resized image
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            # Create a new file with the resized image
            # Use a new name to avoid overwriting the original
            new_name = f"resized_{os.path.splitext(image.name)[0]}.jpg"
            image.file = File(output, name=new_name)
            
        except UnidentifiedImageError:
            raise ValidationError(_('El archivo no es una imagen válida.'))
        except Exception as e:
            raise ValidationError(_('Error al procesar la imagen: %(error)s') % {'error': str(e)})
        
        return image

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:  # Only set user for new instances
            instance.creator = self.creator
        if commit:
            instance.save()
        return instance

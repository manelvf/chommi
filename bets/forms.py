from django import forms
from .models import Event, EventOption
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from django.core.files import File
import imghdr
import os


IMAGE_SIZE_LIMIT = 2 * 1024 * 1024
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
        if not image:
            return image

        # Check file size
        if image.size > IMAGE_SIZE_LIMIT:
            raise ValidationError('La imagen no puede ser mayor a 2MB.')

        # Check file extension
        extension = image.name.split('.')[-1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValidationError('Solo se permiten archivos de imagen (PNG, JPG, JPEG, GIF).')

        # Check content type
        if image.content_type not in ALLOWED_MIME_TYPES:
            raise ValidationError('El archivo debe ser una imagen válida (PNG, JPG, JPEG, GIF).')

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
            raise ValidationError('El archivo no es una imagen válida.')
        except Exception as e:
            raise ValidationError(f'Error al procesar la imagen: {str(e)}')
        
        return image

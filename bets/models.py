from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
from io import BytesIO

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.files import File
from PIL import Image

MONTHS_IN_ADVANCE = 3
IMAGE_DIMENSIONS = (300, 300)


STATUS_CHOICES = (
    ("AC", _("Active")),
    ("DI", _("Disabled")),
    ("EX", _("Expired")),
)


def get_default_subscription_date():
    return datetime.now().date() + relativedelta(months=MONTHS_IN_ADVANCE)


class Gambler(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    date_of_birth = models.DateField(null=True, blank=True)
    status = models.TextField(max_length=3, choices=STATUS_CHOICES, default="AC")
    
    subscription_date = models.DateField(null=True, blank=True, default=get_default_subscription_date)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Event(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to="events/%Y/%m/", null=True, blank=True)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    winner = models.ForeignKey(
        "EventOption",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_events",
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image:
            self._process_image()
        super().save(*args, **kwargs)

    def _process_image(self):
        """Process and resize the uploaded image"""
        try:
            # Open and verify the image
            img = Image.open(self.image)
            
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
            original_name = os.path.splitext(self.image.name)[0]
            new_name = f"resized_{os.path.basename(original_name)}.jpg"
            self.image.file = File(output, name=new_name)
            
        except Exception:
            # If image processing fails, keep the original image
            pass


class EventOption(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='options')
    title = models.CharField(max_length=255)
    initial_odds = models.DecimalField(max_digits=5, decimal_places=2)
    current_odds = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Bet(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bets')
    option = models.ForeignKey(EventOption, on_delete=models.CASCADE, related_name='bets')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    odds = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.option}: {self.odds}"


NotificationKinds = (
    ("RE", "Registration"),
    ("SU", "Subscription"),
    ("DI", "Disabled"),
    ("DE", "DeletedAccount"),
    ("BA", "Balance"),
    ("WI", "Win"),
    ("LO", "Lose"),
)


class EmailNotifications(models.Model):
    """
    Parameters field should be a serialized JSON object, pased a keyword arguments
    to the notification class.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kind = models.TextField(max_length=3, choices=NotificationKinds) 
    parameters = models.TextField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.kind}"

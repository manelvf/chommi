from django.db import models
from django.contrib.auth.models import User


class Gambler(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    date_of_birth = models.DateField(null=True, blank=True)
    subscription_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Event(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to="events/", null=True, blank=True)
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


class EventOption(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
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
    eventOption = models.ForeignKey(EventOption, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.IntegerField()
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.eventOption}: {self.price} x {self.amount}"

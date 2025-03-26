from django.contrib import admin
from bets.models import Bet, Event, EventOption, Gambler

# Register your models here.
#

admin.site.register(Bet)
admin.site.register(Event)
admin.site.register(EventOption)
admin.site.register(Gambler)

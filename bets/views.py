from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.conf.urls.static import static
from django.conf import settings
from django.forms.models import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import ImageUploadForm, EventOptionForm, CustomUserCreationForm, LoginForm, CustomEventOptionFormSet, UserRegistrationForm
from .models import Event, EventOption, Gambler, Bet
from django.db.models import Count
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import timedelta


def home(request):
    """Home page view showing popular events"""
    # Get events with the most bets in the last 7 days
    recent_date = timezone.now() - timedelta(days=7)
    events = Event.objects.filter(
        Q(is_public=True),
    )    

    # Paginate events
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'title': _('Popular Events'),
        'show_bet_count': True,
        'show_event_count': False,
    }
    return render(request, 'event_list.html', context)


def about(request):
    return render(request, "about.html")


def create_event(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create an event.")
        return redirect('login')

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES, label_suffix="", creator=request.user)
        formset = EventOptionFormSet(request.POST, instance=form.instance if form.is_valid() else None)

        if form.is_valid() and formset.is_valid():
            event = form.save()
            formset.instance = event
            formset.save()
            messages.success(request, "Event created successfully!")
            return redirect("home")
        else:
            messages.error(request, "Error creating event. Please check the form.")
            return render(request, "create_event.html", {
                "form": form, 
                "formset": formset,
                "debug": settings.DEBUG
            })
    else:
        form = ImageUploadForm(label_suffix="", creator=request.user)
        formset = EventOptionFormSet(instance=form.instance)

    return render(request, "create_event.html", {
        "form": form, 
        "formset": formset,
        "debug": settings.DEBUG
    })


def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES, instance=event, label_suffix="")
        formset = EventOptionFormSet(request.POST, instance=event)
        
        if form.is_valid() and formset.is_valid():
            event = form.save()
            formset.save()
            messages.success(request, "Event updated successfully!")
            return redirect("home")
        else:
            messages.error(request, "Error updating event. Please check the form.")
            return render(request, "create_event.html", {
                "form": form, 
                "formset": formset,
                "debug": settings.DEBUG,
                "is_edit": True
            })
    else:
        form = ImageUploadForm(instance=event, label_suffix="")
        formset = EventOptionFormSet(instance=event)

    return render(request, "create_event.html", {
        "form": form, 
        "formset": formset,
        "debug": settings.DEBUG,
        "is_edit": True
    })


def service2(request):
    return render(request, "bets/service2.html")


def all_services(request):
    return render(request, "bets/all_services.html")


@login_required
def profile(request):
    user = request.user
    created_events = Event.objects.filter(creator=user).order_by('-created_at')
    user_bets = Bet.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'created_events': created_events,
        'user_bets': user_bets,
        'total_events': created_events.count(),
        'total_bets': user_bets.count(),
        'winning_bets': user_bets.filter(eventOption__is_winner=True).count(),
    }
    
    return render(request, 'profile.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, _('You have been successfully logged out.'))
    return redirect('home')


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Successfully logged in!'))
        return response


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated Gambler profile
            Gambler.objects.create(user=user)
            login(request, user)
            messages.success(request, _('Account created successfully!'))
            return redirect('home')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


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


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    options = event.options.all()
    user_bet = None
    if request.user.is_authenticated:
        user_bet = Bet.objects.filter(event=event, user=request.user).first()
    
    context = {
        'event': event,
        'options': options,
        'user_bet': user_bet,
        'can_bet': event.deadline > timezone.now(),
        'is_creator': event.creator == request.user,
    }
    return render(request, 'event_detail.html', context)


@login_required
@require_POST
def place_bet(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    option_id = request.POST.get('option')
    
    # Validate event is still open for betting
    if event.deadline <= timezone.now():
        messages.error(request, _("This event has ended. No more bets can be placed."))
        return redirect('event_detail', event_id=event_id)
    
    # Validate option exists and belongs to this event
    try:
        option = EventOption.objects.get(id=option_id, event=event)
    except EventOption.DoesNotExist:
        messages.error(request, _("Invalid betting option selected."))
        return redirect('event_detail', event_id=event_id)
    
    # Check if user has already placed a bet
    if Bet.objects.filter(event=event, user=request.user).exists():
        messages.error(request, _("You have already placed a bet on this event."))
        return redirect('event_detail', event_id=event_id)
    
    try:
        with transaction.atomic():
            # Create the bet
            bet = Bet.objects.create(
                event=event,
                option=option,
                user=request.user,
                odds=option.current_odds
            )
            
            # Update the odds for all options
            total_bets = Bet.objects.filter(event=event).count()
            for opt in event.options.all():
                opt_bets = opt.bets.count()
                if total_bets > 0:
                    opt.current_odds = total_bets / opt_bets if opt_bets > 0 else 1.0
                    opt.save()
            
            messages.success(request, _("Your bet has been placed successfully!"))
            return redirect('event_detail', event_id=event_id)
            
    except Exception as e:
        messages.error(request, _("An error occurred while placing your bet. Please try again."))
        if settings.DEBUG:
            messages.error(request, str(e))
        return redirect('event_detail', event_id=event_id)


@login_required
def my_bets(request):
    # Get all bets for the current user, ordered by most recent first
    bets = Bet.objects.filter(user=request.user).select_related(
        'event', 'option'
    ).order_by('-created_at')
    
    # Group bets by event status
    active_bets = []
    past_bets = []
    
    for bet in bets:
        if bet.event.deadline > timezone.now():
            active_bets.append(bet)
        else:
            past_bets.append(bet)
    
    context = {
        'active_bets': active_bets,
        'past_bets': past_bets,
        'total_active_bets': len(active_bets),
        'total_past_bets': len(past_bets),
    }
    
    return render(request, 'my_bets.html', context)


def latest_events(request):
    """View for displaying the latest events"""
    events = Event.objects.filter(
        Q(is_public=True) | Q(user=request.user)
    ).order_by('-created_at')
    
    # Paginate events
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'title': _('Latest Events'),
        'show_bet_count': False,
        'show_event_count': True,
    }
    return render(request, 'event_list.html', context)


def popular_events(request):
    """View for displaying the most popular events"""
    # Get events with the most bets in the last 7 days
    recent_date = timezone.now() - timedelta(days=7)
    events = Event.objects.filter(
        Q(is_public=True) | Q(user=request.user),
        bets__created_at__gte=recent_date
    ).annotate(
        bet_count=Count('bets')
    ).order_by('-bet_count')
    
    # Paginate events
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'title': _('Popular Events'),
        'show_bet_count': True,
    }
    return render(request, 'event_list.html', context)


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                # Create associated Gambler profile with date of birth
                Gambler.objects.create(
                    user=user,
                    date_of_birth=form.cleaned_data['date_of_birth']
                )
                login(request, user)
                messages.success(request, _("Registration successful!"))
                return redirect("home")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        # For now, we'll just show a success message
        messages.success(request, _('Thank you for your message! We will get back to you soon.'))
        return redirect('contact')
        
    return render(request, 'contact.html')

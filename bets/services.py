"""Betting service layer for business logic."""

import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _
from .models import Event, EventOption, Bet

logger = logging.getLogger('bets')


class BettingError(Exception):
    """Base exception for betting operations."""
    pass


class EventClosedError(BettingError):
    """Raised when trying to bet on a closed event."""
    pass


class InvalidOptionError(BettingError):
    """Raised when trying to bet on an invalid option."""
    pass


class DuplicateBetError(BettingError):
    """Raised when user tries to place multiple bets on same event."""
    pass


def place_new_bet(user, event, option_id):
    """
    Place a new bet for a user on an event option.
    
    Args:
        user: The user placing the bet
        event: The Event instance
        option_id: ID of the EventOption to bet on
        
    Returns:
        Bet: The created bet instance
        
    Raises:
        EventClosedError: If the event has ended
        InvalidOptionError: If the option doesn't exist or doesn't belong to event
        DuplicateBetError: If user already has a bet on this event
        ValidationError: For other validation errors
    """
    # Validate event is still open for betting
    if event.deadline <= timezone.now():
        raise EventClosedError(_("This event has ended. No more bets can be placed."))
    
    # Validate option exists and belongs to this event
    try:
        option = EventOption.objects.get(id=option_id, event=event)
    except EventOption.DoesNotExist:
        raise InvalidOptionError(_("Invalid betting option selected."))
    
    # Check if user has already placed a bet on this event
    if Bet.objects.filter(event=event, user=user).exists():
        raise DuplicateBetError(_("You have already placed a bet on this event."))
    
    try:
        with transaction.atomic():
            # Create the bet - using field names as expected by current model
            bet = Bet.objects.create(
                event=event,
                option=option,
                user=user,
                odds=option.current_odds
            )

            # Update the odds for all options
            _update_event_odds(event)

            return bet

    except ValidationError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        # Log unexpected errors with full context
        logger.error(f"Unexpected error placing bet for user {user.id} on event {event.id}: {str(e)}", exc_info=True)
        raise ValidationError(_("An error occurred while placing your bet. Please try again."))


def _update_event_odds(event):
    """
    Update odds for all options in an event based on current bet distribution.

    The odds are calculated inversely proportional to the number of bets.
    More bets = lower odds (lower payout), fewer bets = higher odds (higher payout).

    Args:
        event: The Event instance to update odds for
    """
    total_bets = Bet.objects.filter(event=event).count()

    if total_bets == 0:
        # No bets yet, keep initial odds
        return

    for option in event.options.all():
        option_bets = option.bets.count()

        if option_bets > 0:
            # Calculate odds based on bet distribution
            # Odds increase when fewer people bet on this option
            option.current_odds = total_bets / option_bets
        else:
            # No bets on this option yet - use maximum odds based on total bets
            # or keep initial odds, whichever is higher
            option.current_odds = max(float(option.initial_odds), total_bets * 2.0)

        option.save()
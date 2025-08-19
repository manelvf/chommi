from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Gambler, Event, EventOption, Bet, get_default_subscription_date, MONTHS_IN_ADVANCE


class GamblerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_gambler_creation_with_defaults(self):
        """Test that a Gambler is created with correct default values"""
        gambler = Gambler.objects.create(user=self.user)
        
        self.assertEqual(gambler.user, self.user)
        self.assertEqual(gambler.points, 0)
        self.assertEqual(gambler.status, "AC")
        self.assertIsNone(gambler.date_of_birth)
        self.assertIsNotNone(gambler.subscription_date)
        self.assertIsNotNone(gambler.created_at)
        self.assertIsNotNone(gambler.updated_at)

    def test_default_subscription_date_calculation(self):
        """Test that subscription_date defaults to 3 months in advance"""
        expected_date = datetime.now().date() + relativedelta(months=MONTHS_IN_ADVANCE)
        
        gambler = Gambler.objects.create(user=self.user)
        
        # Allow for small time differences during test execution
        self.assertEqual(gambler.subscription_date, expected_date)

    def test_get_default_subscription_date_function(self):
        """Test the get_default_subscription_date utility function"""
        expected_date = datetime.now().date() + relativedelta(months=MONTHS_IN_ADVANCE)
        actual_date = get_default_subscription_date()
        
        self.assertEqual(actual_date, expected_date)

    def test_gambler_str_representation(self):
        """Test the string representation of Gambler"""
        gambler = Gambler.objects.create(user=self.user)
        self.assertEqual(str(gambler), 'testuser')

    def test_gambler_custom_values(self):
        """Test creating a Gambler with custom values"""
        custom_date = datetime(2024, 6, 15).date()
        custom_subscription = datetime(2025, 1, 1).date()
        
        gambler = Gambler.objects.create(
            user=self.user,
            points=100,
            date_of_birth=custom_date,
            status="DI",
            subscription_date=custom_subscription
        )
        
        self.assertEqual(gambler.points, 100)
        self.assertEqual(gambler.date_of_birth, custom_date)
        self.assertEqual(gambler.status, "DI")
        self.assertEqual(gambler.subscription_date, custom_subscription)

    def test_gambler_user_relationship(self):
        """Test OneToOneField relationship with User"""
        gambler = Gambler.objects.create(user=self.user)
        
        # Test forward relationship
        self.assertEqual(gambler.user, self.user)
        
        # Test reverse relationship
        self.assertEqual(self.user.gambler, gambler)


class EventModelTest(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )

    def test_event_creation_with_required_fields(self):
        """Test Event creation with required fields"""
        deadline = timezone.now() + timedelta(days=7)
        
        event = Event.objects.create(
            title='Test Event',
            description='Test event description',
            deadline=deadline,
            creator=self.creator
        )
        
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.description, 'Test event description')
        self.assertEqual(event.deadline, deadline)
        self.assertEqual(event.creator, self.creator)
        self.assertTrue(event.is_public)  # Default value
        self.assertIsNone(event.subtitle)  # Optional field
        self.assertIsNone(event.image)  # Optional field
        self.assertIsNone(event.winner)  # Optional field
        self.assertIsNotNone(event.created_at)
        self.assertIsNotNone(event.updated_at)

    def test_event_creation_with_all_fields(self):
        """Test Event creation with all fields including optional ones"""
        deadline = timezone.now() + timedelta(days=7)
        
        event = Event.objects.create(
            title='Complete Event',
            subtitle='Event Subtitle',
            description='Complete event description',
            deadline=deadline,
            creator=self.creator,
            is_public=False
        )
        
        self.assertEqual(event.title, 'Complete Event')
        self.assertEqual(event.subtitle, 'Event Subtitle')
        self.assertEqual(event.description, 'Complete event description')
        self.assertEqual(event.deadline, deadline)
        self.assertEqual(event.creator, self.creator)
        self.assertFalse(event.is_public)

    def test_event_str_representation(self):
        """Test the string representation of Event"""
        event = Event.objects.create(
            title='Test Event',
            description='Test description',
            deadline=timezone.now() + timedelta(days=7),
            creator=self.creator
        )
        
        self.assertEqual(str(event), 'Test Event')

    def test_event_creator_relationship(self):
        """Test ForeignKey relationship with creator (User)"""
        event = Event.objects.create(
            title='Test Event',
            description='Test description',
            deadline=timezone.now() + timedelta(days=7),
            creator=self.creator
        )
        
        # Test forward relationship
        self.assertEqual(event.creator, self.creator)
        
        # Test reverse relationship
        self.assertIn(event, self.creator.created_events.all())

    def test_event_winner_relationship(self):
        """Test ForeignKey relationship with winner (EventOption)"""
        event = Event.objects.create(
            title='Test Event',
            description='Test description',
            deadline=timezone.now() + timedelta(days=7),
            creator=self.creator
        )
        
        # Create an EventOption
        option = EventOption.objects.create(
            event=event,
            title='Option 1',
            initial_odds=Decimal('2.00'),
            current_odds=Decimal('2.00'),
            description='Test option'
        )
        
        # Set as winner
        event.winner = option
        event.save()
        
        # Test relationships
        self.assertEqual(event.winner, option)
        self.assertIn(event, option.won_events.all())


class EventOptionModelTest(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test event description',
            deadline=timezone.now() + timedelta(days=7),
            creator=self.creator
        )

    def test_event_option_creation(self):
        """Test EventOption creation with all fields"""
        option = EventOption.objects.create(
            event=self.event,
            title='Test Option',
            initial_odds=Decimal('1.50'),
            current_odds=Decimal('1.75'),
            description='Test option description'
        )
        
        self.assertEqual(option.event, self.event)
        self.assertEqual(option.title, 'Test Option')
        self.assertEqual(option.initial_odds, Decimal('1.50'))
        self.assertEqual(option.current_odds, Decimal('1.75'))
        self.assertEqual(option.description, 'Test option description')
        self.assertTrue(option.is_active)  # Default value
        self.assertFalse(option.is_winner)  # Default value
        self.assertIsNotNone(option.created_at)
        self.assertIsNotNone(option.updated_at)

    def test_event_option_str_representation(self):
        """Test the string representation of EventOption"""
        option = EventOption.objects.create(
            event=self.event,
            title='Test Option',
            initial_odds=Decimal('2.00'),
            current_odds=Decimal('2.00'),
            description='Test option'
        )
        
        self.assertEqual(str(option), 'Test Option')

    def test_event_option_relationship_with_event(self):
        """Test ForeignKey relationship with Event"""
        option = EventOption.objects.create(
            event=self.event,
            title='Test Option',
            initial_odds=Decimal('2.00'),
            current_odds=Decimal('2.00'),
            description='Test option'
        )
        
        # Test forward relationship
        self.assertEqual(option.event, self.event)
        
        # Test reverse relationship
        self.assertIn(option, self.event.eventoption_set.all())


class BetModelTest(TestCase):
    def setUp(self):
        # Create users
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        
        self.bettor = User.objects.create_user(
            username='bettor',
            email='bettor@example.com',
            password='testpass123'
        )
        
        # Create event
        self.event = Event.objects.create(
            title='Test Event',
            description='Test event description',
            deadline=timezone.now() + timedelta(days=7),
            creator=self.creator
        )
        
        # Create event option
        self.event_option = EventOption.objects.create(
            event=self.event,
            title='Test Option',
            initial_odds=Decimal('2.00'),
            current_odds=Decimal('2.00'),
            description='Test option'
        )

    def test_bet_creation(self):
        """Test Bet creation with all required fields"""
        bet = Bet.objects.create(
            eventOption=self.event_option,
            user=self.bettor,
            price=200,
            amount=50
        )
        
        self.assertEqual(bet.eventOption, self.event_option)
        self.assertEqual(bet.user, self.bettor)
        self.assertEqual(bet.price, 200)
        self.assertEqual(bet.amount, 50)
        self.assertIsNotNone(bet.created_at)

    def test_bet_str_representation(self):
        """Test the string representation of Bet"""
        bet = Bet.objects.create(
            eventOption=self.event_option,
            user=self.bettor,
            price=200,
            amount=50
        )
        
        expected_str = f"{self.bettor} - {self.event_option}: 200 x 50"
        self.assertEqual(str(bet), expected_str)

    def test_bet_user_relationship(self):
        """Test ForeignKey relationship with User"""
        bet = Bet.objects.create(
            eventOption=self.event_option,
            user=self.bettor,
            price=200,
            amount=50
        )
        
        # Test forward relationship
        self.assertEqual(bet.user, self.bettor)
        
        # Test reverse relationship
        self.assertIn(bet, self.bettor.bet_set.all())

    def test_bet_event_option_relationship(self):
        """Test ForeignKey relationship with EventOption"""
        bet = Bet.objects.create(
            eventOption=self.event_option,
            user=self.bettor,
            price=200,
            amount=50
        )
        
        # Test forward relationship
        self.assertEqual(bet.eventOption, self.event_option)
        
        # Test reverse relationship
        self.assertIn(bet, self.event_option.bet_set.all())

    def test_bet_links_user_to_event_option(self):
        """Test that Bet correctly links a user to an EventOption"""
        bet = Bet.objects.create(
            eventOption=self.event_option,
            user=self.bettor,
            price=200,
            amount=50
        )
        
        # Verify the bet connects the user to the event option
        self.assertEqual(bet.user, self.bettor)
        self.assertEqual(bet.eventOption, self.event_option)
        
        # Verify we can navigate from user to event through bet
        user_bets = Bet.objects.filter(user=self.bettor)
        self.assertIn(bet, user_bets)
        
        # Verify we can navigate from event option to users through bet
        option_bets = Bet.objects.filter(eventOption=self.event_option)
        self.assertIn(bet, option_bets)

    def test_multiple_bets_same_user_different_options(self):
        """Test that a user can place multiple bets on different options"""
        # Create another event option
        option2 = EventOption.objects.create(
            event=self.event,
            title='Option 2',
            initial_odds=Decimal('3.00'),
            current_odds=Decimal('3.00'),
            description='Second option'
        )
        
        # Create bets on different options
        bet1 = Bet.objects.create(
            eventOption=self.event_option,
            user=self.bettor,
            price=200,
            amount=50
        )
        
        bet2 = Bet.objects.create(
            eventOption=option2,
            user=self.bettor,
            price=300,
            amount=25
        )
        
        # Verify both bets exist for the user
        user_bets = Bet.objects.filter(user=self.bettor)
        self.assertEqual(user_bets.count(), 2)
        self.assertIn(bet1, user_bets)
        self.assertIn(bet2, user_bets)

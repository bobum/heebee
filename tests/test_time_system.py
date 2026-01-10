"""
Tests for the Time System in Heebee.

Tests cover:
- Time advancement (hours, days)
- Day/night cycles
- Scheduled events triggering
- Deadlines and expiration
- Energy/fatigue systems
"""
import pytest


class TestTimeManager:
    """Tests for the TimeManager class."""

    def test_initial_state(self, load_system):
        """Test TimeManager initializes with correct default values."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        assert tm.day == 1
        assert tm.hour == 8
        assert tm.weekday == 0  # Monday
        assert tm.energy == 100
        assert tm.fatigue == 0
        assert tm.is_exhausted is False

    def test_custom_initialization(self, load_system):
        """Test TimeManager can be initialized with custom values."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=5, start_hour=14, start_weekday=3)

        assert tm.day == 5
        assert tm.hour == 14
        assert tm.weekday == 3  # Thursday


class TestTimeAdvancement:
    """Tests for time advancement functionality."""

    def test_advance_single_hour(self, load_system):
        """Test advancing time by one hour."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=10)

        tm.advance_hour(1)

        assert tm.hour == 11
        assert tm.day == 1

    def test_advance_multiple_hours(self, load_system):
        """Test advancing time by multiple hours."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=10)

        tm.advance_hour(5)

        assert tm.hour == 15
        assert tm.day == 1

    def test_advance_hour_day_rollover(self, load_system):
        """Test hour advancement rolls over to next day."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=22)

        tm.advance_hour(5)

        assert tm.hour == 3
        assert tm.day == 2

    def test_advance_hour_weekday_rollover(self, load_system):
        """Test weekday advances correctly with day rollover."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=23, start_weekday=6)  # Sunday night

        tm.advance_hour(2)

        assert tm.weekday == 0  # Monday

    def test_advance_single_day(self, load_system):
        """Test advancing time by one day."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=10)

        tm.advance_day(1)

        assert tm.day == 2
        assert tm.hour == 10  # Hour maintained

    def test_advance_multiple_days(self, load_system):
        """Test advancing time by multiple days."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_weekday=0)

        tm.advance_day(3)

        assert tm.day == 4
        assert tm.weekday == 3  # Thursday

    def test_advance_day_full_week(self, load_system):
        """Test advancing a full week cycles weekday correctly."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_weekday=2)  # Wednesday

        tm.advance_day(7)

        assert tm.weekday == 2  # Still Wednesday

    def test_set_time(self, load_system):
        """Test setting specific time values."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.set_time(day=10, hour=15)

        assert tm.day == 10
        assert tm.hour == 15

    def test_set_time_partial(self, load_system):
        """Test setting only day or hour."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=5, start_hour=10)

        tm.set_time(hour=20)

        assert tm.day == 5
        assert tm.hour == 20

    def test_set_time_clamps_hour(self, load_system):
        """Test that set_time clamps hour to valid range."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.set_time(hour=30)
        assert tm.hour == 23

        tm.set_time(hour=-5)
        assert tm.hour == 0

    def test_skip_to_hour_same_day(self, load_system):
        """Test skipping to later hour on same day."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=8)

        hours_skipped = tm.skip_to_hour(14)

        assert tm.hour == 14
        assert tm.day == 1
        assert hours_skipped == 6

    def test_skip_to_hour_next_day(self, load_system):
        """Test skipping to hour that requires going to next day."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=20)

        hours_skipped = tm.skip_to_hour(8)

        assert tm.hour == 8
        assert tm.day == 2
        assert hours_skipped == 12

    def test_skip_to_same_hour(self, load_system):
        """Test skipping to current hour goes to next day."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=10)

        hours_skipped = tm.skip_to_hour(10)

        assert tm.hour == 10
        assert tm.day == 2
        assert hours_skipped == 24


class TestDayNightCycle:
    """Tests for day/night cycle functionality."""

    def test_time_of_day_dawn(self, load_system):
        """Test dawn detection (5-7)."""
        ns = load_system("time_system")
        TimeOfDay = ns["TimeOfDay"]

        tm = ns["TimeManager"](start_hour=6)
        assert tm.get_time_of_day() == TimeOfDay.DAWN

        tm.set_time(hour=5)
        assert tm.get_time_of_day() == TimeOfDay.DAWN

    def test_time_of_day_morning(self, load_system):
        """Test morning detection (7-12)."""
        ns = load_system("time_system")
        TimeOfDay = ns["TimeOfDay"]

        tm = ns["TimeManager"](start_hour=10)
        assert tm.get_time_of_day() == TimeOfDay.MORNING

        tm.set_time(hour=7)
        assert tm.get_time_of_day() == TimeOfDay.MORNING

    def test_time_of_day_afternoon(self, load_system):
        """Test afternoon detection (12-17)."""
        ns = load_system("time_system")
        TimeOfDay = ns["TimeOfDay"]

        tm = ns["TimeManager"](start_hour=14)
        assert tm.get_time_of_day() == TimeOfDay.AFTERNOON

        tm.set_time(hour=12)
        assert tm.get_time_of_day() == TimeOfDay.AFTERNOON

    def test_time_of_day_evening(self, load_system):
        """Test evening detection (17-20)."""
        ns = load_system("time_system")
        TimeOfDay = ns["TimeOfDay"]

        tm = ns["TimeManager"](start_hour=18)
        assert tm.get_time_of_day() == TimeOfDay.EVENING

        tm.set_time(hour=17)
        assert tm.get_time_of_day() == TimeOfDay.EVENING

    def test_time_of_day_night(self, load_system):
        """Test night detection (20-24)."""
        ns = load_system("time_system")
        TimeOfDay = ns["TimeOfDay"]

        tm = ns["TimeManager"](start_hour=22)
        assert tm.get_time_of_day() == TimeOfDay.NIGHT

        tm.set_time(hour=20)
        assert tm.get_time_of_day() == TimeOfDay.NIGHT

    def test_time_of_day_late_night(self, load_system):
        """Test late night detection (0-5)."""
        ns = load_system("time_system")
        TimeOfDay = ns["TimeOfDay"]

        tm = ns["TimeManager"](start_hour=2)
        assert tm.get_time_of_day() == TimeOfDay.LATE_NIGHT

        tm.set_time(hour=0)
        assert tm.get_time_of_day() == TimeOfDay.LATE_NIGHT

    def test_is_daytime(self, load_system):
        """Test daytime detection (7am-8pm)."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.set_time(hour=12)
        assert tm.is_daytime() is True

        tm.set_time(hour=7)
        assert tm.is_daytime() is True

        tm.set_time(hour=19)
        assert tm.is_daytime() is True

        tm.set_time(hour=6)
        assert tm.is_daytime() is False

        tm.set_time(hour=20)
        assert tm.is_daytime() is False

    def test_is_nighttime(self, load_system):
        """Test nighttime detection (8pm-7am)."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.set_time(hour=22)
        assert tm.is_nighttime() is True

        tm.set_time(hour=3)
        assert tm.is_nighttime() is True

        tm.set_time(hour=12)
        assert tm.is_nighttime() is False

    def test_get_weekday_name(self, load_system):
        """Test weekday name retrieval."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.weekday = 0
        assert tm.get_weekday_name() == "Monday"

        tm.weekday = 4
        assert tm.get_weekday_name() == "Friday"

        tm.weekday = 6
        assert tm.get_weekday_name() == "Sunday"

    def test_is_weekend(self, load_system):
        """Test weekend detection."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.weekday = 5  # Saturday
        assert tm.is_weekend() is True

        tm.weekday = 6  # Sunday
        assert tm.is_weekend() is True

        tm.weekday = 4  # Friday
        assert tm.is_weekend() is False

    def test_get_formatted_time(self, load_system):
        """Test formatted time string."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.set_time(hour=0)
        assert tm.get_formatted_time() == "12:00 AM"

        tm.set_time(hour=9)
        assert tm.get_formatted_time() == "9:00 AM"

        tm.set_time(hour=12)
        assert tm.get_formatted_time() == "12:00 PM"

        tm.set_time(hour=15)
        assert tm.get_formatted_time() == "3:00 PM"

    def test_get_date_string(self, load_system):
        """Test date string format."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=5, start_weekday=2)

        assert "Day 5" in tm.get_date_string()
        assert "Wednesday" in tm.get_date_string()


class TestScheduledEvents:
    """Tests for scheduled events functionality."""

    def test_schedule_event(self, load_system):
        """Test scheduling a new event."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        event = tm.schedule_event(
            event_id="test_event",
            name="Test Event",
            trigger_day=5,
            trigger_hour=10
        )

        assert event.event_id == "test_event"
        assert "test_event" in tm.scheduled_events
        assert event.active is True

    def test_get_event(self, load_system):
        """Test retrieving a scheduled event."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.schedule_event("my_event", "My Event", trigger_day=1, trigger_hour=12)
        event = tm.get_event("my_event")

        assert event is not None
        assert event.name == "My Event"

    def test_event_triggers_at_correct_time(self, load_system):
        """Test that events trigger at the correct day/hour."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=9)

        tm.schedule_event(
            event_id="trigger_test",
            name="Trigger Test",
            trigger_day=1,
            trigger_hour=10,
            callback="test_label"
        )

        # Advance to trigger time
        events = tm.advance_hour(1)

        assert len(events) == 1
        assert events[0]['event_id'] == "trigger_test"
        assert events[0]['callback'] == "test_label"

    def test_event_does_not_trigger_before_time(self, load_system):
        """Test that events don't trigger before their scheduled time."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=8)

        tm.schedule_event(
            event_id="future_event",
            name="Future Event",
            trigger_day=2,
            trigger_hour=10
        )

        # Advance but not to trigger time
        events = tm.advance_hour(1)

        assert len(events) == 0

    def test_one_time_event_expires_after_trigger(self, load_system):
        """Test that one-time events expire after triggering."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=9)

        tm.schedule_event(
            event_id="one_time",
            name="One Time Event",
            trigger_day=1,
            trigger_hour=10,
            recurring=False
        )

        tm.advance_hour(1)  # Triggers
        event = tm.get_event("one_time")

        assert event.expired is True
        assert event.times_triggered == 1

        # Advance to same time next day - should not trigger again
        tm.advance_day(1)
        tm.set_time(hour=9)
        events = tm.advance_hour(1)

        assert len([e for e in events if e['event_id'] == 'one_time']) == 0

    def test_recurring_daily_event(self, load_system):
        """Test that recurring daily events trigger every day."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=9)

        tm.schedule_event(
            event_id="daily_event",
            name="Daily Event",
            trigger_hour=10,
            recurring=True
        )

        # Trigger on day 1
        events = tm.advance_hour(1)
        assert len(events) == 1

        # Advance to next day and trigger again
        tm.advance_day(1)
        tm.set_time(hour=9)
        events = tm.advance_hour(1)
        assert len(events) == 1
        assert events[0]['event_id'] == "daily_event"

    def test_recurring_weekly_event(self, load_system):
        """Test weekly recurring events on specific days."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=9, start_weekday=0)  # Monday

        tm.schedule_event(
            event_id="weekly_meeting",
            name="Weekly Meeting",
            trigger_hour=10,
            recurring=True,
            days_of_week=[0, 3]  # Monday and Thursday
        )

        # Should trigger on Monday
        events = tm.advance_hour(1)
        assert len(events) == 1

        # Advance to Tuesday - should not trigger
        tm.advance_day(1)
        tm.set_time(hour=9)
        events = tm.advance_hour(1)
        assert len(events) == 0

        # Advance to Thursday - should trigger
        tm.advance_day(2)
        tm.set_time(hour=9)
        events = tm.advance_hour(1)
        assert len(events) == 1

    def test_cancel_event(self, load_system):
        """Test canceling a scheduled event."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=9)

        tm.schedule_event(
            event_id="cancelable",
            name="Cancelable Event",
            trigger_day=1,
            trigger_hour=10
        )

        result = tm.cancel_event("cancelable")
        assert result is True

        events = tm.advance_hour(1)
        assert len(events) == 0

    def test_cancel_nonexistent_event(self, load_system):
        """Test canceling an event that doesn't exist."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        result = tm.cancel_event("nonexistent")
        assert result is False

    def test_get_upcoming_events(self, load_system):
        """Test getting events within a time window."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=8, start_weekday=0)

        tm.schedule_event("event1", "Event 1", trigger_day=1, trigger_hour=10)
        tm.schedule_event("event2", "Event 2", trigger_day=1, trigger_hour=20)
        tm.schedule_event("event3", "Event 3", trigger_day=2, trigger_hour=10)

        # Within 12 hours - should get event1 and event2
        upcoming = tm.get_upcoming_events(hours_ahead=12)
        event_ids = [e.event_id for e in upcoming]
        assert "event1" in event_ids
        assert "event2" in event_ids
        assert "event3" not in event_ids


class TestDeadlines:
    """Tests for deadline functionality."""

    def test_add_deadline(self, load_system):
        """Test adding a new deadline."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        deadline = tm.add_deadline(
            deadline_id="quest1",
            name="Complete Quest",
            description="Finish the main quest",
            due_day=5,
            due_hour=18
        )

        assert deadline.deadline_id == "quest1"
        assert "quest1" in tm.deadlines
        assert deadline.completed is False
        assert deadline.expired is False

    def test_get_deadline(self, load_system):
        """Test retrieving a deadline."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.add_deadline("test_dl", "Test Deadline", "Description", due_day=3)
        deadline = tm.get_deadline("test_dl")

        assert deadline is not None
        assert deadline.name == "Test Deadline"

    def test_complete_deadline(self, load_system):
        """Test completing a deadline."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.add_deadline(
            "complete_test",
            "Completable",
            "Test",
            due_day=5,
            on_complete="reward_label"
        )

        callback = tm.complete_deadline("complete_test")
        deadline = tm.get_deadline("complete_test")

        assert deadline.completed is True
        assert callback == "reward_label"

    def test_deadline_expires(self, load_system):
        """Test that deadlines expire when due time passes."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=10)

        tm.add_deadline(
            "expiring",
            "Expiring Deadline",
            "Will expire",
            due_day=1,
            due_hour=12
        )

        # Advance past deadline
        tm.advance_hour(3)
        deadline = tm.get_deadline("expiring")

        assert deadline.expired is True

    def test_deadline_expires_on_day_change(self, load_system):
        """Test deadline expiration when day advances past due date."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1)

        tm.add_deadline("day_expire", "Day Expire", "Test", due_day=2)

        tm.advance_day(2)
        deadline = tm.get_deadline("day_expire")

        assert deadline.expired is True

    def test_complete_expired_deadline_fails(self, load_system):
        """Test that completing an expired deadline returns None."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=5)

        tm.add_deadline(
            "past_due",
            "Past Due",
            "Already expired",
            due_day=3,
            on_complete="should_not_get_this"
        )

        # Force expiration check
        tm.get_deadline("past_due").check_expiration(tm.day, tm.hour)

        callback = tm.complete_deadline("past_due")
        assert callback is None

    def test_time_remaining(self, load_system):
        """Test calculating time remaining on deadline."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=10)

        tm.add_deadline("timing_test", "Timing", "Test", due_day=3, due_hour=15)
        deadline = tm.get_deadline("timing_test")

        days, hours = deadline.time_remaining(tm.day, tm.hour)

        # Day 1 hour 10 to Day 3 hour 15 = 2 days + 5 hours
        assert days == 2
        assert hours == 5

    def test_time_remaining_same_day(self, load_system):
        """Test time remaining when deadline is same day."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=10)

        tm.add_deadline("today", "Today", "Test", due_day=1, due_hour=18)
        deadline = tm.get_deadline("today")

        days, hours = deadline.time_remaining(tm.day, tm.hour)

        assert days == 0
        assert hours == 8

    def test_get_active_deadlines(self, load_system):
        """Test getting all active deadlines."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1)

        tm.add_deadline("active1", "Active 1", "Test", due_day=5)
        tm.add_deadline("active2", "Active 2", "Test", due_day=6)
        tm.add_deadline("completed", "Completed", "Test", due_day=7)

        tm.complete_deadline("completed")

        active = tm.get_active_deadlines()
        active_ids = [d.deadline_id for d in active]

        assert "active1" in active_ids
        assert "active2" in active_ids
        assert "completed" not in active_ids

    def test_get_urgent_deadlines(self, load_system):
        """Test getting deadlines due within threshold."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_day=1, start_hour=10)

        tm.add_deadline("urgent", "Urgent", "Due soon", due_day=1, due_hour=20)
        tm.add_deadline("not_urgent", "Not Urgent", "Due later", due_day=5)

        urgent = tm.get_urgent_deadlines(hours_threshold=24)
        urgent_ids = [d.deadline_id for d in urgent]

        assert "urgent" in urgent_ids
        assert "not_urgent" not in urgent_ids


class TestEnergyFatigue:
    """Tests for energy and fatigue system."""

    def test_initial_energy(self, load_system):
        """Test initial energy values."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        assert tm.energy == 100
        assert tm.max_energy == 100
        assert tm.fatigue == 0

    def test_modify_energy(self, load_system):
        """Test modifying energy."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        change = tm.modify_energy(-20)

        assert tm.energy == 80
        assert change == -20

    def test_energy_cannot_exceed_max(self, load_system):
        """Test that energy cannot exceed maximum."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.modify_energy(50)

        assert tm.energy == 100

    def test_energy_cannot_go_negative(self, load_system):
        """Test that energy cannot go below zero."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.modify_energy(-150)

        assert tm.energy == 0

    def test_modify_fatigue(self, load_system):
        """Test modifying fatigue."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.modify_fatigue(30)

        assert tm.fatigue == 30

    def test_fatigue_clamped(self, load_system):
        """Test that fatigue is clamped between 0 and 100."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.modify_fatigue(150)
        assert tm.fatigue == 100

        tm.modify_fatigue(-200)
        assert tm.fatigue == 0

    def test_exhaustion_triggered(self, load_system):
        """Test exhaustion is triggered when energy is low."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.modify_energy(-85)  # Energy now at 15

        assert tm.is_exhausted is True

    def test_exhaustion_recovery(self, load_system):
        """Test recovering from exhaustion."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.energy = 10
        tm.is_exhausted = True

        # Recover past threshold + buffer
        tm.modify_energy(30)

        assert tm.is_exhausted is False

    def test_energy_drain_from_time(self, load_system):
        """Test that advancing time drains energy."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=10)

        initial_energy = tm.energy
        tm.advance_hour(2)

        assert tm.energy < initial_energy

    def test_high_fatigue_increases_energy_drain(self, load_system):
        """Test that high fatigue increases energy consumption."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=10)

        # Normal drain
        tm.energy = 100
        tm.fatigue = 0
        tm.advance_hour(1)
        normal_drain = 100 - tm.energy

        # High fatigue drain
        tm.energy = 100
        tm.fatigue = 60
        tm.advance_hour(1)
        fatigue_drain = 100 - tm.energy

        assert fatigue_drain > normal_drain

    def test_rest_overnight_restores_energy(self, load_system):
        """Test that overnight rest restores energy."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.energy = 30
        tm.fatigue = 50

        tm._rest_overnight()

        assert tm.energy == tm.max_energy
        assert tm.fatigue < 50

    def test_advance_day_includes_rest(self, load_system):
        """Test that advancing day includes overnight rest."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.energy = 20
        tm.advance_day(1)

        assert tm.energy == tm.max_energy

    def test_can_perform_action(self, load_system):
        """Test checking if action can be performed."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.energy = 50
        assert tm.can_perform_action(10) is True

        tm.energy = 5
        assert tm.can_perform_action(10) is False

    def test_cannot_perform_action_when_exhausted(self, load_system):
        """Test that exhausted state prevents actions."""
        ns = load_system("time_system")
        tm = ns["TimeManager"]()

        tm.energy = 50
        tm.is_exhausted = True

        assert tm.can_perform_action(10) is False

    def test_perform_action(self, load_system):
        """Test performing an action consumes energy and time."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=10)

        initial_energy = tm.energy
        result = tm.perform_action(energy_cost=15, hours=2)

        assert result is True
        assert tm.energy == initial_energy - 15
        assert tm.hour == 12

    def test_perform_action_fails_without_energy(self, load_system):
        """Test that action fails when not enough energy."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=10)

        tm.energy = 5
        result = tm.perform_action(energy_cost=20, hours=1)

        assert result is False
        assert tm.hour == 10  # Time not advanced

    def test_rest_recovers_energy(self, load_system):
        """Test that rest recovers energy over time."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=10)

        tm.energy = 50
        initial_energy = tm.energy

        tm.rest(2)

        assert tm.energy > initial_energy

    def test_rest_at_night_more_effective(self, load_system):
        """Test that resting at night recovers more energy."""
        ns = load_system("time_system")
        tm = ns["TimeManager"](start_hour=10)  # Daytime

        tm.energy = 50
        tm.rest(1)
        day_recovery = tm.energy - 50

        tm = ns["TimeManager"](start_hour=22)  # Nighttime
        tm.energy = 50
        tm.rest(1)
        night_recovery = tm.energy - 50

        assert night_recovery > day_recovery


class TestScheduledEventClass:
    """Tests for the ScheduledEvent class directly."""

    def test_should_trigger_one_time(self, load_system):
        """Test one-time event trigger detection."""
        ns = load_system("time_system")
        ScheduledEvent = ns["ScheduledEvent"]

        event = ScheduledEvent(
            event_id="test",
            name="Test",
            trigger_day=5,
            trigger_hour=10
        )

        assert event.should_trigger(5, 10, 0) is True
        assert event.should_trigger(5, 11, 0) is False
        assert event.should_trigger(4, 10, 0) is False

    def test_should_trigger_recurring_daily(self, load_system):
        """Test recurring daily event trigger detection."""
        ns = load_system("time_system")
        ScheduledEvent = ns["ScheduledEvent"]

        event = ScheduledEvent(
            event_id="daily",
            name="Daily",
            trigger_hour=12,
            recurring=True
        )

        assert event.should_trigger(1, 12, 0) is True
        assert event.should_trigger(100, 12, 3) is True
        assert event.should_trigger(5, 11, 0) is False

    def test_should_trigger_recurring_weekly(self, load_system):
        """Test recurring weekly event trigger detection."""
        ns = load_system("time_system")
        ScheduledEvent = ns["ScheduledEvent"]

        event = ScheduledEvent(
            event_id="weekly",
            name="Weekly",
            trigger_hour=9,
            recurring=True,
            days_of_week=[1, 4]  # Tuesday and Friday
        )

        assert event.should_trigger(1, 9, 1) is True  # Tuesday
        assert event.should_trigger(1, 9, 4) is True  # Friday
        assert event.should_trigger(1, 9, 0) is False  # Monday
        assert event.should_trigger(1, 9, 6) is False  # Sunday

    def test_trigger_method(self, load_system):
        """Test the trigger method marks event correctly."""
        ns = load_system("time_system")
        ScheduledEvent = ns["ScheduledEvent"]

        event = ScheduledEvent(
            event_id="test",
            name="Test",
            trigger_day=1,
            trigger_hour=10,
            callback="my_callback",
            recurring=False
        )

        callback = event.trigger()

        assert callback == "my_callback"
        assert event.times_triggered == 1
        assert event.expired is True

    def test_trigger_recurring_not_expired(self, load_system):
        """Test recurring events don't expire after trigger."""
        ns = load_system("time_system")
        ScheduledEvent = ns["ScheduledEvent"]

        event = ScheduledEvent(
            event_id="recurring",
            name="Recurring",
            trigger_hour=10,
            recurring=True
        )

        event.trigger()

        assert event.expired is False
        assert event.times_triggered == 1

    def test_cancel_event(self, load_system):
        """Test canceling an event."""
        ns = load_system("time_system")
        ScheduledEvent = ns["ScheduledEvent"]

        event = ScheduledEvent("test", "Test", trigger_day=5, trigger_hour=10)
        event.cancel()

        assert event.active is False
        assert event.should_trigger(5, 10, 0) is False


class TestDeadlineClass:
    """Tests for the Deadline class directly."""

    def test_check_expiration_not_expired(self, load_system):
        """Test expiration check when not expired."""
        ns = load_system("time_system")
        Deadline = ns["Deadline"]

        deadline = Deadline("test", "Test", "Desc", due_day=5, due_hour=12)

        result = deadline.check_expiration(3, 10)

        assert result is False
        assert deadline.expired is False

    def test_check_expiration_expired_by_day(self, load_system):
        """Test expiration check when day has passed."""
        ns = load_system("time_system")
        Deadline = ns["Deadline"]

        deadline = Deadline("test", "Test", "Desc", due_day=5, due_hour=12)

        result = deadline.check_expiration(6, 10)

        assert result is True
        assert deadline.expired is True

    def test_check_expiration_expired_by_hour(self, load_system):
        """Test expiration check when hour has passed on due day."""
        ns = load_system("time_system")
        Deadline = ns["Deadline"]

        deadline = Deadline("test", "Test", "Desc", due_day=5, due_hour=12)

        result = deadline.check_expiration(5, 12)

        assert result is True
        assert deadline.expired is True

    def test_complete_before_expiration(self, load_system):
        """Test completing deadline before expiration."""
        ns = load_system("time_system")
        Deadline = ns["Deadline"]

        deadline = Deadline(
            "test", "Test", "Desc",
            due_day=5,
            on_complete="complete_callback"
        )

        callback = deadline.complete()

        assert deadline.completed is True
        assert callback == "complete_callback"

    def test_complete_after_expiration(self, load_system):
        """Test completing deadline after expiration fails."""
        ns = load_system("time_system")
        Deadline = ns["Deadline"]

        deadline = Deadline("test", "Test", "Desc", due_day=5)
        deadline.expired = True

        callback = deadline.complete()

        assert deadline.completed is False
        assert callback is None

    def test_time_remaining_calculation(self, load_system):
        """Test time remaining calculation."""
        ns = load_system("time_system")
        Deadline = ns["Deadline"]

        deadline = Deadline("test", "Test", "Desc", due_day=10, due_hour=15)

        # Current: day 5, hour 10
        # Due: day 10, hour 15
        # Remaining: 5 days + 5 hours = 125 hours total
        days, hours = deadline.time_remaining(5, 10)

        assert days == 5
        assert hours == 5

    def test_time_remaining_when_completed(self, load_system):
        """Test time remaining returns zero when completed."""
        ns = load_system("time_system")
        Deadline = ns["Deadline"]

        deadline = Deadline("test", "Test", "Desc", due_day=10)
        deadline.completed = True

        days, hours = deadline.time_remaining(5, 10)

        assert days == 0
        assert hours == 0

    def test_time_remaining_when_expired(self, load_system):
        """Test time remaining returns zero when expired."""
        ns = load_system("time_system")
        Deadline = ns["Deadline"]

        deadline = Deadline("test", "Test", "Desc", due_day=10)
        deadline.expired = True

        days, hours = deadline.time_remaining(5, 10)

        assert days == 0
        assert hours == 0

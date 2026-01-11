"""
Tests for the Time System module.

Tests cover:
- TimeManager core functionality (day/time tracking)
- Energy management
- Scheduled events
- Deadlines
- NPC schedules
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from conftest import load_rpy_classes


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def time_classes(load_system):
    """Load time system classes."""
    return load_system("time_system")


@pytest.fixture
def TimeManager(time_classes):
    """Get the TimeManager class."""
    return time_classes["TimeManager"]


@pytest.fixture
def ScheduledEvent(time_classes):
    """Get the ScheduledEvent class."""
    return time_classes["ScheduledEvent"]


@pytest.fixture
def Deadline(time_classes):
    """Get the Deadline class."""
    return time_classes["Deadline"]


@pytest.fixture
def NPCSchedule(time_classes):
    """Get the NPCSchedule class."""
    return time_classes["NPCSchedule"]


@pytest.fixture
def time_manager(TimeManager):
    """Create a fresh TimeManager for testing."""
    return TimeManager()


# =============================================================================
# TIME MANAGER BASIC TESTS
# =============================================================================

class TestTimeManagerBasics:
    """Test basic TimeManager functionality."""

    def test_initial_state(self, TimeManager):
        """Test default initial state."""
        tm = TimeManager()
        assert tm.current_day == 1
        assert tm.current_time_period == 0
        assert tm.time_period_name == "Morning"

    def test_custom_start_day(self, TimeManager):
        """Test starting on a custom day."""
        tm = TimeManager(start_day=5)
        assert tm.current_day == 5

    def test_custom_start_time_period(self, TimeManager):
        """Test starting at a custom time period."""
        tm = TimeManager(start_time_period=2)
        assert tm.current_time_period == 2
        assert tm.time_period_name == "Evening"

    def test_day_of_week_calculation(self, TimeManager):
        """Test day of week calculation."""
        # Start on Monday (week_day=0)
        tm = TimeManager(start_week_day=0)
        assert tm.day_of_week == "Monday"

        # After 3 days should be Thursday
        tm.advance_day(3)
        assert tm.day_of_week == "Thursday"

    def test_is_weekend(self, TimeManager):
        """Test weekend detection."""
        # Start on Friday (week_day=4)
        tm = TimeManager(start_week_day=4)
        assert not tm.is_weekend

        # Advance to Saturday
        tm.advance_day(1)
        assert tm.is_weekend

        # Sunday is also weekend
        tm.advance_day(1)
        assert tm.is_weekend

        # Monday is not
        tm.advance_day(1)
        assert not tm.is_weekend

    def test_week_number(self, TimeManager):
        """Test week number calculation."""
        tm = TimeManager()
        assert tm.week_number == 1

        tm.advance_day(7)
        assert tm.week_number == 2

    def test_get_formatted_date(self, TimeManager):
        """Test formatted date string."""
        tm = TimeManager(start_day=3, start_time_period=1, start_week_day=2)
        formatted = tm.get_formatted_date()
        assert "Day 3" in formatted
        assert "Afternoon" in formatted


# =============================================================================
# TIME ADVANCEMENT TESTS
# =============================================================================

class TestTimeAdvancement:
    """Test time advancement functionality."""

    def test_advance_time_single_period(self, time_manager):
        """Test advancing by one time period."""
        time_manager.advance_time(1)
        assert time_manager.current_time_period == 1
        assert time_manager.time_period_name == "Afternoon"

    def test_advance_time_multiple_periods(self, time_manager):
        """Test advancing by multiple periods."""
        time_manager.advance_time(3)
        assert time_manager.current_time_period == 3
        assert time_manager.time_period_name == "Night"

    def test_advance_time_wraps_to_next_day(self, time_manager):
        """Test that advancing past Night goes to next day Morning."""
        time_manager.advance_time(4)  # Morning -> Afternoon -> Evening -> Night -> next Morning
        assert time_manager.current_day == 2
        assert time_manager.current_time_period == 0
        assert time_manager.time_period_name == "Morning"

    def test_advance_day(self, time_manager):
        """Test advancing full days."""
        time_manager.advance_day(3)
        assert time_manager.current_day == 4
        assert time_manager.current_time_period == 0

    def test_skip_to_time(self, TimeManager):
        """Test skipping to a specific time period."""
        tm = TimeManager(start_time_period=0)  # Start at Morning
        tm.skip_to_time("Evening")
        assert tm.time_period_name == "Evening"
        assert tm.current_day == 1

    def test_skip_to_time_next_day(self, TimeManager):
        """Test skipping to earlier time goes to next day."""
        tm = TimeManager(start_time_period=2)  # Start at Evening
        tm.skip_to_time("Morning", allow_day_advance=True)
        assert tm.time_period_name == "Morning"
        assert tm.current_day == 2

    def test_skip_to_day(self, TimeManager):
        """Test skipping to a specific day."""
        tm = TimeManager(start_day=1)
        tm.skip_to_day(5)
        assert tm.current_day == 5


# =============================================================================
# ENERGY SYSTEM TESTS
# =============================================================================

class TestEnergySystem:
    """Test energy management functionality."""

    def test_initial_energy(self, time_manager):
        """Test initial energy is max."""
        assert time_manager.energy == time_manager.max_energy
        assert time_manager.energy == 100

    def test_energy_costs_on_time_advance(self, time_manager):
        """Test energy is consumed when advancing time."""
        initial_energy = time_manager.energy
        time_manager.advance_time(1)
        # Morning has 0 cost, so advancing from Morning consumes 0
        # But the cost is applied for the period we're leaving
        # From the code: energy_costs shows cost for each period
        assert time_manager.energy <= initial_energy

    def test_use_energy(self, time_manager):
        """Test using energy for an action."""
        assert time_manager.use_energy(30)
        assert time_manager.energy == 70

    def test_use_energy_insufficient(self, time_manager):
        """Test using more energy than available fails."""
        time_manager.energy = 20
        assert not time_manager.use_energy(30)
        assert time_manager.energy == 20  # Energy unchanged

    def test_restore_energy(self, time_manager):
        """Test restoring energy."""
        time_manager.energy = 50
        time_manager.restore_energy(30)
        assert time_manager.energy == 80

    def test_restore_energy_caps_at_max(self, time_manager):
        """Test energy doesn't exceed max."""
        time_manager.energy = 90
        time_manager.restore_energy(50)
        assert time_manager.energy == time_manager.max_energy

    def test_is_exhausted(self, time_manager):
        """Test exhaustion detection."""
        assert not time_manager.is_exhausted

        time_manager.energy = 10
        assert time_manager.is_exhausted

    def test_rest_restores_energy(self, time_manager):
        """Test rest action restores energy."""
        time_manager.energy = 50
        time_manager.rest()
        assert time_manager.energy == 80  # 50 + 30

    def test_rest_advances_time(self, time_manager):
        """Test rest advances time by one period."""
        time_manager.rest()
        assert time_manager.current_time_period == 1

    def test_energy_restored_on_new_day(self, time_manager):
        """Test energy restoration when advancing to new day."""
        time_manager.energy = 20
        time_manager.advance_day(1)
        assert time_manager.energy == time_manager.max_energy


# =============================================================================
# SCHEDULED EVENT TESTS
# =============================================================================

class TestScheduledEvent:
    """Test ScheduledEvent class."""

    def test_create_event(self, ScheduledEvent):
        """Test creating a scheduled event."""
        event = ScheduledEvent(
            event_id="test_event",
            name="Test Event",
            day=5,
            time_period="Evening"
        )
        assert event.event_id == "test_event"
        assert event.name == "Test Event"
        assert event.day == 5
        assert event.time_period == "Evening"

    def test_event_matches_day_and_time(self, ScheduledEvent):
        """Test event matching logic."""
        event = ScheduledEvent(
            event_id="test",
            name="Test",
            day=5,
            time_period="Evening"
        )
        assert event.matches(5, "Evening", "Monday")
        assert not event.matches(5, "Morning", "Monday")
        assert not event.matches(4, "Evening", "Monday")

    def test_event_matches_day_of_week(self, ScheduledEvent):
        """Test matching by day of week."""
        event = ScheduledEvent(
            event_id="weekly",
            name="Weekly Event",
            day_of_week="Monday",
            time_period="Morning"
        )
        assert event.matches(1, "Morning", "Monday")
        assert event.matches(8, "Morning", "Monday")  # Next Monday
        assert not event.matches(1, "Morning", "Tuesday")

    def test_repeating_event(self, ScheduledEvent):
        """Test repeating events can trigger multiple times."""
        event = ScheduledEvent(
            event_id="repeat",
            name="Repeating",
            time_period="Morning",
            repeating=True
        )
        assert event.matches(1, "Morning", "Monday")
        event.trigger()
        # Repeating events can still match after triggering
        assert event.matches(2, "Morning", "Monday")

    def test_one_time_event(self, ScheduledEvent):
        """Test one-time events don't repeat."""
        event = ScheduledEvent(
            event_id="once",
            name="Once Only",
            day=5,
            time_period="Evening",
            repeating=False
        )
        assert event.matches(5, "Evening", "Monday")
        event.trigger()
        assert not event.matches(5, "Evening", "Monday")

    def test_disabled_event(self, ScheduledEvent):
        """Test disabled events don't match."""
        event = ScheduledEvent(
            event_id="disabled",
            name="Disabled",
            time_period="Morning"
        )
        event.enabled = False
        assert not event.matches(1, "Morning", "Monday")


class TestTimeManagerEvents:
    """Test TimeManager event management."""

    def test_add_event(self, time_manager, ScheduledEvent):
        """Test adding an event."""
        event = ScheduledEvent(
            event_id="test",
            name="Test Event",
            day=2,
            time_period="Afternoon"
        )
        time_manager.add_event(event)
        assert time_manager.get_event("test") is event

    def test_remove_event(self, time_manager, ScheduledEvent):
        """Test removing an event."""
        event = ScheduledEvent(event_id="test", name="Test")
        time_manager.add_event(event)
        time_manager.remove_event("test")
        assert time_manager.get_event("test") is None

    def test_event_triggers_on_time_advance(self, TimeManager, ScheduledEvent):
        """Test events trigger when reaching their time."""
        tm = TimeManager(start_day=1, start_time_period=0)
        event = ScheduledEvent(
            event_id="afternoon_event",
            name="Afternoon Event",
            day=1,
            time_period="Afternoon",
            label="test_label"
        )
        tm.add_event(event)

        # Advance to afternoon
        triggered = tm.advance_time(1)
        assert len(triggered) == 1
        assert triggered[0]["event"].event_id == "afternoon_event"

    def test_events_sorted_by_priority(self, time_manager, ScheduledEvent):
        """Test events are sorted by priority."""
        low = ScheduledEvent(event_id="low", name="Low", priority=1)
        high = ScheduledEvent(event_id="high", name="High", priority=10)
        time_manager.add_event(low)
        time_manager.add_event(high)

        # High priority should be first
        assert time_manager.scheduled_events[0].event_id == "high"


# =============================================================================
# DEADLINE TESTS
# =============================================================================

class TestDeadline:
    """Test Deadline class."""

    def test_create_deadline(self, Deadline):
        """Test creating a deadline."""
        deadline = Deadline(
            deadline_id="quest1",
            name="Complete Quest",
            days_limit=5,
            start_day=1
        )
        assert deadline.deadline_id == "quest1"
        assert deadline.days_limit == 5
        assert deadline.start_day == 1

    def test_days_remaining(self, Deadline):
        """Test days remaining calculation."""
        deadline = Deadline(
            deadline_id="test",
            name="Test",
            days_limit=5,
            start_day=1
        )
        assert deadline.days_remaining(1) == 5
        assert deadline.days_remaining(3) == 3
        assert deadline.days_remaining(6) == 0

    def test_is_expired(self, Deadline):
        """Test expiration detection."""
        deadline = Deadline(
            deadline_id="test",
            name="Test",
            days_limit=3,
            start_day=1
        )
        assert not deadline.is_expired(2)
        assert not deadline.is_expired(3)
        assert deadline.is_expired(4)
        assert deadline.is_expired(5)

    def test_should_warn(self, Deadline):
        """Test warning detection."""
        deadline = Deadline(
            deadline_id="test",
            name="Test",
            days_limit=5,
            start_day=1,
            warning_days=2
        )
        assert not deadline.should_warn(2)  # 4 days left
        assert deadline.should_warn(4)      # 2 days left
        assert deadline.should_warn(5)      # 1 day left

    def test_complete_deadline(self, Deadline):
        """Test completing a deadline."""
        deadline = Deadline(deadline_id="test", name="Test", days_limit=5, start_day=1)
        assert not deadline.completed
        deadline.complete()
        assert deadline.completed

    def test_completed_deadline_no_warning(self, Deadline):
        """Test completed deadlines don't show warnings."""
        deadline = Deadline(
            deadline_id="test",
            name="Test",
            days_limit=3,
            start_day=1,
            warning_days=1
        )
        deadline.complete()
        assert not deadline.should_warn(3)


class TestTimeManagerDeadlines:
    """Test TimeManager deadline management."""

    def test_add_deadline(self, time_manager, Deadline):
        """Test adding a deadline."""
        deadline = Deadline(
            deadline_id="quest",
            name="Quest",
            days_limit=5,
            start_day=1
        )
        time_manager.add_deadline(deadline)
        assert time_manager.get_deadline("quest") is deadline

    def test_remove_deadline(self, time_manager, Deadline):
        """Test removing a deadline."""
        deadline = Deadline(deadline_id="quest", name="Quest", days_limit=5, start_day=1)
        time_manager.add_deadline(deadline)
        time_manager.remove_deadline("quest")
        assert time_manager.get_deadline("quest") is None

    def test_complete_deadline(self, time_manager, Deadline):
        """Test completing a deadline through manager."""
        deadline = Deadline(deadline_id="quest", name="Quest", days_limit=5, start_day=1)
        time_manager.add_deadline(deadline)
        assert time_manager.complete_deadline("quest")
        assert deadline.completed

    def test_get_active_deadlines(self, time_manager, Deadline):
        """Test getting active deadlines."""
        d1 = Deadline(deadline_id="d1", name="D1", days_limit=5, start_day=1)
        d2 = Deadline(deadline_id="d2", name="D2", days_limit=5, start_day=1)
        d2.completed = True
        time_manager.add_deadline(d1)
        time_manager.add_deadline(d2)

        active = time_manager.get_active_deadlines()
        assert len(active) == 1
        assert active[0].deadline_id == "d1"

    def test_deadline_expires_on_day_advance(self, TimeManager, Deadline):
        """Test deadline expiration when advancing days."""
        tm = TimeManager(start_day=1)
        deadline = Deadline(
            deadline_id="urgent",
            name="Urgent",
            days_limit=2,
            start_day=1
        )
        tm.add_deadline(deadline)

        tm.advance_day(2)
        assert deadline.expired

    def test_get_warning_deadlines(self, time_manager, Deadline):
        """Test getting deadlines that should warn."""
        deadline = Deadline(
            deadline_id="soon",
            name="Soon",
            days_limit=2,
            start_day=1,
            warning_days=1
        )
        time_manager.add_deadline(deadline)

        # On day 1, 2 days left - no warning (warning_days=1)
        warnings = time_manager.get_warning_deadlines()
        assert len(warnings) == 0

        # Advance to day 2, 1 day left - should warn
        time_manager.advance_day(1)
        warnings = time_manager.get_warning_deadlines()
        assert len(warnings) == 1


# =============================================================================
# NPC SCHEDULE TESTS
# =============================================================================

class TestNPCSchedule:
    """Test NPCSchedule class."""

    def test_create_npc_schedule(self, NPCSchedule):
        """Test creating an NPC schedule."""
        npc = NPCSchedule(npc_id="sarah", name="Sarah")
        assert npc.npc_id == "sarah"
        assert npc.name == "Sarah"

    def test_set_regular_schedule(self, NPCSchedule):
        """Test setting regular weekly schedule."""
        npc = NPCSchedule(npc_id="sarah", name="Sarah")
        npc.set_regular_schedule("Monday", "Morning", "cafe")
        assert npc.get_location(1, "Morning", "Monday") == "cafe"

    def test_set_special_schedule(self, NPCSchedule):
        """Test special schedule overrides regular."""
        npc = NPCSchedule(npc_id="sarah", name="Sarah")
        npc.set_regular_schedule("Monday", "Morning", "cafe")
        npc.set_special_schedule(1, "Morning", "library")  # Special for day 1

        # Special schedule takes priority
        assert npc.get_location(1, "Morning", "Monday") == "library"
        # Day 8 (also Monday) uses regular schedule
        assert npc.get_location(8, "Morning", "Monday") == "cafe"

    def test_is_available_at(self, NPCSchedule):
        """Test checking NPC availability at location."""
        npc = NPCSchedule(npc_id="sarah", name="Sarah")
        npc.set_regular_schedule("Monday", "Morning", "cafe")

        assert npc.is_available_at("cafe", 1, "Morning", "Monday")
        assert not npc.is_available_at("library", 1, "Morning", "Monday")

    def test_get_location_when_unavailable(self, NPCSchedule):
        """Test getting location returns None when unavailable."""
        npc = NPCSchedule(npc_id="sarah", name="Sarah")
        assert npc.get_location(1, "Morning", "Monday") is None


class TestTimeManagerNPCSchedules:
    """Test TimeManager NPC schedule integration."""

    def test_add_npc_schedule(self, time_manager, NPCSchedule):
        """Test adding NPC schedules."""
        npc = NPCSchedule(npc_id="sarah", name="Sarah")
        npc.set_regular_schedule("Monday", "Morning", "cafe")
        time_manager.add_npc_schedule(npc)

        assert time_manager.get_npc_location("sarah") == "cafe"

    def test_get_npc_location_unknown(self, time_manager):
        """Test getting location for unknown NPC."""
        assert time_manager.get_npc_location("unknown") is None

    def test_is_npc_at(self, time_manager, NPCSchedule):
        """Test checking if NPC is at location."""
        npc = NPCSchedule(npc_id="sarah", name="Sarah")
        npc.set_regular_schedule("Monday", "Morning", "cafe")
        time_manager.add_npc_schedule(npc)

        assert time_manager.is_npc_at("sarah", "cafe")
        assert not time_manager.is_npc_at("sarah", "library")

    def test_get_npcs_at_location(self, time_manager, NPCSchedule):
        """Test getting all NPCs at a location."""
        sarah = NPCSchedule(npc_id="sarah", name="Sarah")
        sarah.set_regular_schedule("Monday", "Morning", "cafe")

        mike = NPCSchedule(npc_id="mike", name="Mike")
        mike.set_regular_schedule("Monday", "Morning", "cafe")

        time_manager.add_npc_schedule(sarah)
        time_manager.add_npc_schedule(mike)

        npcs_at_cafe = time_manager.get_npcs_at("cafe")
        assert len(npcs_at_cafe) == 2
        assert "sarah" in npcs_at_cafe
        assert "mike" in npcs_at_cafe


# =============================================================================
# CALENDAR TESTS
# =============================================================================

class TestCalendar:
    """Test calendar event functionality."""

    def test_add_calendar_event(self, time_manager):
        """Test adding calendar events."""
        time_manager.add_calendar_event(5, "Party", "Fun party")
        events = time_manager.get_events_on_day(5)
        assert len(events) == 1
        assert events[0][1] == "Party"

    def test_get_upcoming_events(self, time_manager):
        """Test getting upcoming calendar events."""
        time_manager.add_calendar_event(3, "Event 1")
        time_manager.add_calendar_event(5, "Event 2")
        time_manager.add_calendar_event(10, "Event 3")  # Outside 7 day window

        upcoming = time_manager.get_upcoming_events(7)
        assert len(upcoming) == 2

    def test_calendar_events_sorted(self, time_manager):
        """Test calendar events are sorted by day."""
        time_manager.add_calendar_event(5, "Later")
        time_manager.add_calendar_event(2, "Earlier")

        assert time_manager.calendar_events[0][0] == 2
        assert time_manager.calendar_events[1][0] == 5


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestTimeSystemIntegration:
    """Integration tests for the time system."""

    def test_full_day_cycle(self, TimeManager):
        """Test a full day cycle with all features."""
        tm = TimeManager(start_day=1, start_time_period=0, start_week_day=0)

        # Start fresh morning
        assert tm.time_period_name == "Morning"
        assert tm.energy == 100

        # Use some energy and advance
        tm.use_energy(20)
        tm.advance_time(1)  # Afternoon
        assert tm.time_period_name == "Afternoon"

        tm.advance_time(1)  # Evening
        assert tm.time_period_name == "Evening"

        tm.advance_time(1)  # Night
        assert tm.time_period_name == "Night"

        # Advance to next day
        tm.advance_time(1)
        assert tm.current_day == 2
        assert tm.time_period_name == "Morning"
        # Energy should be restored after sleep
        assert tm.energy > 80

    def test_event_and_deadline_interaction(self, TimeManager, ScheduledEvent, Deadline):
        """Test events and deadlines working together."""
        tm = TimeManager(start_day=1)

        # Add a deadline for day 3
        deadline = Deadline(
            deadline_id="quest",
            name="Main Quest",
            days_limit=2,
            start_day=1,
            warning_days=1
        )
        tm.add_deadline(deadline)

        # Add an event for day 2 afternoon
        event = ScheduledEvent(
            event_id="meeting",
            name="Meeting",
            day=2,
            time_period="Afternoon"
        )
        tm.add_event(event)

        # Advance to day 2 afternoon
        tm.skip_to_day(2, 1)  # Day 2, Afternoon

        # Check deadline warning
        warnings = tm.get_warning_deadlines()
        assert len(warnings) == 1

    def test_npc_schedule_with_time_advance(self, TimeManager, NPCSchedule):
        """Test NPC schedules update with time advancement."""
        tm = TimeManager(start_day=1, start_time_period=0, start_week_day=0)  # Monday Morning

        sarah = NPCSchedule(npc_id="sarah", name="Sarah")
        sarah.set_regular_schedule("Monday", "Morning", "cafe")
        sarah.set_regular_schedule("Monday", "Afternoon", "library")
        tm.add_npc_schedule(sarah)

        assert tm.get_npc_location("sarah") == "cafe"

        tm.advance_time(1)  # Afternoon
        assert tm.get_npc_location("sarah") == "library"

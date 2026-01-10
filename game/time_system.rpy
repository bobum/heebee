# Time System for Ren'Py Visual Novel
# Provides day/time tracking, scheduled events, deadlines, and energy management

init python:
    import datetime

    # Time period definitions
    TIME_PERIODS = ["Morning", "Afternoon", "Evening", "Night"]
    DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    class ScheduledEvent:
        """Represents an event that triggers at a specific time/day."""
        def __init__(self, event_id, name, day=None, time_period=None, day_of_week=None,
                     label=None, callback=None, repeating=False, priority=0):
            self.event_id = event_id
            self.name = name
            self.day = day  # Specific day number (1, 2, 3, etc.) or None for any day
            self.time_period = time_period  # "Morning", "Afternoon", etc. or None for any
            self.day_of_week = day_of_week  # "Monday", etc. or None for any
            self.label = label  # Ren'Py label to jump to
            self.callback = callback  # Python function to call
            self.repeating = repeating  # Whether event repeats
            self.priority = priority  # Higher priority events trigger first
            self.triggered = False  # Has this event been triggered?
            self.enabled = True  # Is this event active?

        def matches(self, day, time_period, day_of_week):
            """Check if this event should trigger at the given time."""
            if not self.enabled:
                return False
            if not self.repeating and self.triggered:
                return False

            day_match = self.day is None or self.day == day
            time_match = self.time_period is None or self.time_period == time_period
            dow_match = self.day_of_week is None or self.day_of_week == day_of_week

            return day_match and time_match and dow_match

        def trigger(self):
            """Mark event as triggered and return the label/callback."""
            self.triggered = True
            return (self.label, self.callback)

    class Deadline:
        """Represents a quest or task with a day limit."""
        def __init__(self, deadline_id, name, days_limit, start_day, description="",
                     warning_days=1, on_expire_label=None, on_complete_label=None):
            self.deadline_id = deadline_id
            self.name = name
            self.days_limit = days_limit
            self.start_day = start_day
            self.description = description
            self.warning_days = warning_days  # Days before deadline to show warning
            self.on_expire_label = on_expire_label
            self.on_complete_label = on_complete_label
            self.completed = False
            self.expired = False

        def days_remaining(self, current_day):
            """Calculate days remaining until deadline."""
            elapsed = current_day - self.start_day
            return max(0, self.days_limit - elapsed)

        def is_expired(self, current_day):
            """Check if deadline has passed."""
            return self.days_remaining(current_day) <= 0

        def should_warn(self, current_day):
            """Check if we should show a warning."""
            remaining = self.days_remaining(current_day)
            return remaining <= self.warning_days and remaining > 0 and not self.completed

        def complete(self):
            """Mark the deadline as completed."""
            self.completed = True

        def expire(self):
            """Mark the deadline as expired."""
            self.expired = True

    class NPCSchedule:
        """Defines when an NPC is available at a location."""
        def __init__(self, npc_id, name):
            self.npc_id = npc_id
            self.name = name
            self.schedule = {}  # {day_of_week: {time_period: location}}
            self.special_schedule = {}  # {day_number: {time_period: location}}

        def set_regular_schedule(self, day_of_week, time_period, location):
            """Set regular weekly schedule."""
            if day_of_week not in self.schedule:
                self.schedule[day_of_week] = {}
            self.schedule[day_of_week][time_period] = location

        def set_special_schedule(self, day_number, time_period, location):
            """Set special schedule for a specific day."""
            if day_number not in self.special_schedule:
                self.special_schedule[day_number] = {}
            self.special_schedule[day_number][time_period] = location

        def get_location(self, day_number, time_period, day_of_week):
            """Get NPC location at a given time. Returns None if unavailable."""
            # Check special schedule first
            if day_number in self.special_schedule:
                if time_period in self.special_schedule[day_number]:
                    return self.special_schedule[day_number][time_period]

            # Fall back to regular schedule
            if day_of_week in self.schedule:
                if time_period in self.schedule[day_of_week]:
                    return self.schedule[day_of_week][time_period]

            return None

        def is_available_at(self, location, day_number, time_period, day_of_week):
            """Check if NPC is at a specific location at the given time."""
            return self.get_location(day_number, time_period, day_of_week) == location

    class TimeManager:
        """Main class for managing game time, events, and energy."""
        def __init__(self, start_day=1, start_time_period=0, start_week_day=0):
            # Core time tracking
            self.current_day = start_day
            self.current_time_period = start_time_period  # Index into TIME_PERIODS
            self.total_days = start_day
            self.start_week_day = start_week_day  # Which day of week we started on

            # Energy/fatigue system
            self.max_energy = 100
            self.energy = self.max_energy
            self.energy_costs = {
                "Morning": 0,  # Energy restored after sleep
                "Afternoon": 10,
                "Evening": 15,
                "Night": 20
            }
            self.energy_restore_on_sleep = 80
            self.fatigue_threshold = 20  # Below this, player is exhausted

            # Event tracking
            self.scheduled_events = []
            self.deadlines = []
            self.npc_schedules = {}

            # Calendar events (for display)
            self.calendar_events = []  # List of (day, name, description) tuples

        @property
        def time_period_name(self):
            """Get current time period as string."""
            return TIME_PERIODS[self.current_time_period]

        @property
        def day_of_week(self):
            """Get current day of week as string."""
            # Calculate based on start day and current day
            day_index = (self.start_week_day + self.current_day - 1) % 7
            return DAYS_OF_WEEK[day_index]

        @property
        def day_of_week_index(self):
            """Get current day of week as index (0-6)."""
            return (self.start_week_day + self.current_day - 1) % 7

        @property
        def week_number(self):
            """Get current week number."""
            return ((self.current_day - 1) // 7) + 1

        @property
        def is_weekend(self):
            """Check if it's a weekend."""
            return self.day_of_week in ["Saturday", "Sunday"]

        @property
        def is_exhausted(self):
            """Check if player is exhausted."""
            return self.energy < self.fatigue_threshold

        def get_formatted_date(self):
            """Get a formatted date string."""
            return "Day {} ({}) - {}".format(
                self.current_day,
                self.day_of_week,
                self.time_period_name
            )

        def advance_time(self, periods=1):
            """Advance time by the specified number of periods."""
            triggered_events = []

            for _ in range(periods):
                # Apply energy cost for current period
                period_name = TIME_PERIODS[self.current_time_period]
                self.energy -= self.energy_costs.get(period_name, 0)
                self.energy = max(0, self.energy)

                # Move to next period
                self.current_time_period += 1

                # Check if we moved to a new day
                if self.current_time_period >= len(TIME_PERIODS):
                    self.current_time_period = 0
                    self.current_day += 1
                    self.total_days += 1

                    # Restore energy on new day (sleeping)
                    self.energy = min(self.max_energy, self.energy + self.energy_restore_on_sleep)

                    # Check deadlines
                    self._check_deadlines()

                # Check for triggered events
                events = self._check_events()
                triggered_events.extend(events)

            return triggered_events

        def advance_day(self, days=1):
            """Advance to morning of the next day (or multiple days)."""
            triggered_events = []

            for _ in range(days):
                self.current_time_period = 0  # Reset to morning
                self.current_day += 1
                self.total_days += 1

                # Full energy restore after rest
                self.energy = self.max_energy

                # Check deadlines
                self._check_deadlines()

                # Check for morning events
                events = self._check_events()
                triggered_events.extend(events)

            return triggered_events

        def skip_to_time(self, target_period, allow_day_advance=True):
            """Skip to a specific time period."""
            triggered_events = []
            target_index = TIME_PERIODS.index(target_period) if isinstance(target_period, str) else target_period

            if target_index == self.current_time_period:
                return triggered_events

            if target_index < self.current_time_period:
                if allow_day_advance:
                    # Need to advance to next day
                    periods_remaining = len(TIME_PERIODS) - self.current_time_period
                    periods_to_skip = periods_remaining + target_index
                    return self.advance_time(periods_to_skip)
                else:
                    return triggered_events
            else:
                periods_to_skip = target_index - self.current_time_period
                return self.advance_time(periods_to_skip)

        def skip_to_day(self, target_day, target_period=0):
            """Skip to a specific day and time period."""
            if target_day <= self.current_day:
                return []

            days_to_advance = target_day - self.current_day
            events = self.advance_day(days_to_advance)

            if target_period > 0:
                events.extend(self.advance_time(target_period))

            return events

        # Energy management
        def use_energy(self, amount):
            """Use energy for an action. Returns True if enough energy."""
            if self.energy >= amount:
                self.energy -= amount
                return True
            return False

        def restore_energy(self, amount):
            """Restore energy."""
            self.energy = min(self.max_energy, self.energy + amount)

        def rest(self):
            """Take a rest, advancing time and restoring some energy."""
            self.energy = min(self.max_energy, self.energy + 30)
            return self.advance_time(1)

        # Event management
        def add_event(self, event):
            """Add a scheduled event."""
            self.scheduled_events.append(event)
            # Sort by priority (higher first)
            self.scheduled_events.sort(key=lambda e: e.priority, reverse=True)

        def remove_event(self, event_id):
            """Remove an event by ID."""
            self.scheduled_events = [e for e in self.scheduled_events if e.event_id != event_id]

        def get_event(self, event_id):
            """Get an event by ID."""
            for event in self.scheduled_events:
                if event.event_id == event_id:
                    return event
            return None

        def _check_events(self):
            """Check for and return triggered events."""
            triggered = []
            for event in self.scheduled_events:
                if event.matches(self.current_day, self.time_period_name, self.day_of_week):
                    label, callback = event.trigger()
                    triggered.append({
                        "event": event,
                        "label": label,
                        "callback": callback
                    })
            return triggered

        # Deadline management
        def add_deadline(self, deadline):
            """Add a deadline."""
            self.deadlines.append(deadline)

        def remove_deadline(self, deadline_id):
            """Remove a deadline by ID."""
            self.deadlines = [d for d in self.deadlines if d.deadline_id != deadline_id]

        def get_deadline(self, deadline_id):
            """Get a deadline by ID."""
            for deadline in self.deadlines:
                if deadline.deadline_id == deadline_id:
                    return deadline
            return None

        def complete_deadline(self, deadline_id):
            """Mark a deadline as completed."""
            deadline = self.get_deadline(deadline_id)
            if deadline:
                deadline.complete()
                return True
            return False

        def _check_deadlines(self):
            """Check for expired deadlines."""
            for deadline in self.deadlines:
                if not deadline.completed and not deadline.expired:
                    if deadline.is_expired(self.current_day):
                        deadline.expire()

        def get_active_deadlines(self):
            """Get all active (not completed, not expired) deadlines."""
            return [d for d in self.deadlines if not d.completed and not d.expired]

        def get_warning_deadlines(self):
            """Get deadlines that should show warnings."""
            return [d for d in self.deadlines if d.should_warn(self.current_day)]

        # NPC schedule management
        def add_npc_schedule(self, npc_schedule):
            """Add an NPC schedule."""
            self.npc_schedules[npc_schedule.npc_id] = npc_schedule

        def get_npc_location(self, npc_id):
            """Get current location of an NPC."""
            if npc_id in self.npc_schedules:
                return self.npc_schedules[npc_id].get_location(
                    self.current_day,
                    self.time_period_name,
                    self.day_of_week
                )
            return None

        def is_npc_at(self, npc_id, location):
            """Check if an NPC is at a specific location now."""
            return self.get_npc_location(npc_id) == location

        def get_npcs_at(self, location):
            """Get all NPCs currently at a location."""
            npcs = []
            for npc_id, schedule in self.npc_schedules.items():
                if schedule.is_available_at(location, self.current_day,
                                           self.time_period_name, self.day_of_week):
                    npcs.append(npc_id)
            return npcs

        # Calendar management
        def add_calendar_event(self, day, name, description=""):
            """Add an event to the calendar for display."""
            self.calendar_events.append((day, name, description))
            self.calendar_events.sort(key=lambda x: x[0])

        def get_upcoming_events(self, days_ahead=7):
            """Get calendar events in the next N days."""
            max_day = self.current_day + days_ahead
            return [(d, n, desc) for d, n, desc in self.calendar_events
                    if self.current_day <= d <= max_day]

        def get_events_on_day(self, day):
            """Get all calendar events on a specific day."""
            return [(d, n, desc) for d, n, desc in self.calendar_events if d == day]

# Initialize the global time manager
default time_manager = TimeManager()

# Convenience variables for easy access in Ren'Py script
default current_day = 1
default current_time = "Morning"
default current_day_of_week = "Monday"
default player_energy = 100

# Update convenience variables
init python:
    def update_time_display():
        """Update the convenience display variables."""
        global current_day, current_time, current_day_of_week, player_energy
        store.current_day = time_manager.current_day
        store.current_time = time_manager.time_period_name
        store.current_day_of_week = time_manager.day_of_week
        store.player_energy = time_manager.energy

# Example scheduled events setup
init python:
    def setup_example_events():
        """Set up example scheduled events."""
        # Weekly meeting every Monday morning
        meeting_event = ScheduledEvent(
            event_id="weekly_meeting",
            name="Weekly Team Meeting",
            day_of_week="Monday",
            time_period="Morning",
            label="weekly_meeting_scene",
            repeating=True,
            priority=10
        )
        time_manager.add_event(meeting_event)

        # Special event on day 5 evening
        special_event = ScheduledEvent(
            event_id="special_party",
            name="Special Party",
            day=5,
            time_period="Evening",
            label="party_scene",
            repeating=False,
            priority=20
        )
        time_manager.add_event(special_event)

        # Add to calendar
        time_manager.add_calendar_event(5, "Party Night", "Don't forget the party!")

        # Weekend relaxation event (Saturday afternoon)
        weekend_event = ScheduledEvent(
            event_id="weekend_rest",
            name="Weekend Relaxation",
            day_of_week="Saturday",
            time_period="Afternoon",
            label="weekend_scene",
            repeating=True,
            priority=5
        )
        time_manager.add_event(weekend_event)

    def setup_example_npc_schedules():
        """Set up example NPC schedules."""
        # Example NPC: Sarah
        sarah = NPCSchedule("sarah", "Sarah")

        # Weekday schedule
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            sarah.set_regular_schedule(day, "Morning", "cafe")
            sarah.set_regular_schedule(day, "Afternoon", "library")
            sarah.set_regular_schedule(day, "Evening", "park")
            sarah.set_regular_schedule(day, "Night", "home")

        # Weekend schedule
        for day in ["Saturday", "Sunday"]:
            sarah.set_regular_schedule(day, "Morning", "home")
            sarah.set_regular_schedule(day, "Afternoon", "mall")
            sarah.set_regular_schedule(day, "Evening", "restaurant")
            sarah.set_regular_schedule(day, "Night", "home")

        time_manager.add_npc_schedule(sarah)

        # Example NPC: Mike
        mike = NPCSchedule("mike", "Mike")

        # Mike works night shifts on weekdays
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            mike.set_regular_schedule(day, "Morning", "home")
            mike.set_regular_schedule(day, "Afternoon", "gym")
            mike.set_regular_schedule(day, "Evening", "work")
            mike.set_regular_schedule(day, "Night", "work")

        # Weekends free
        for day in ["Saturday", "Sunday"]:
            mike.set_regular_schedule(day, "Morning", "home")
            mike.set_regular_schedule(day, "Afternoon", "park")
            mike.set_regular_schedule(day, "Evening", "bar")
            mike.set_regular_schedule(day, "Night", "bar")

        time_manager.add_npc_schedule(mike)

    def setup_example_deadline():
        """Set up an example deadline."""
        quest_deadline = Deadline(
            deadline_id="main_quest",
            name="Complete Main Investigation",
            days_limit=7,
            start_day=1,
            description="You must complete the investigation within a week!",
            warning_days=2,
            on_expire_label="quest_failed"
        )
        time_manager.add_deadline(quest_deadline)
        time_manager.add_calendar_event(8, "Investigation Deadline", "Last day to complete investigation!")

# Screens for the time system

screen time_display():
    """Display current time in corner of screen."""
    frame:
        xalign 1.0
        yalign 0.0
        xpadding 20
        ypadding 10
        background "#00000080"

        vbox:
            spacing 5

            text "Day [time_manager.current_day] - [time_manager.day_of_week]":
                size 20
                color "#FFFFFF"

            text "[time_manager.time_period_name]":
                size 24
                color "#FFD700"

            text "Week [time_manager.week_number]":
                size 16
                color "#AAAAAA"

screen energy_bar():
    """Display player energy bar."""
    frame:
        xalign 0.0
        yalign 0.0
        xpadding 20
        ypadding 10
        background "#00000080"

        vbox:
            spacing 5

            text "Energy":
                size 16
                color "#FFFFFF"

            bar:
                value time_manager.energy
                range time_manager.max_energy
                xsize 150
                ysize 20
                left_bar "#00FF00" if time_manager.energy > time_manager.fatigue_threshold else "#FF0000"
                right_bar "#333333"

            text "[time_manager.energy]/[time_manager.max_energy]":
                size 14
                color "#FFFFFF"
                xalign 0.5

screen calendar_screen():
    """Calendar screen showing current date and upcoming events."""
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 700
        ysize 500

        vbox:
            spacing 20
            xfill True

            # Header
            hbox:
                xfill True

                text "Calendar":
                    size 32
                    color "#FFD700"

                textbutton "X":
                    xalign 1.0
                    action Hide("calendar_screen")

            # Current date display
            frame:
                xfill True
                ysize 80
                background "#333366"

                vbox:
                    xalign 0.5
                    yalign 0.5

                    text "Current Date":
                        size 16
                        color "#AAAAAA"
                        xalign 0.5

                    text "[time_manager.get_formatted_date()]":
                        size 24
                        color "#FFFFFF"
                        xalign 0.5

            # Week display
            text "This Week":
                size 20
                color "#FFFFFF"

            hbox:
                spacing 10
                xalign 0.5

                for i, day_name in enumerate(DAYS_OF_WEEK):
                    $ is_today = (i == time_manager.day_of_week_index)

                    frame:
                        xsize 80
                        ysize 60
                        background "#FFD700" if is_today else "#444444"

                        vbox:
                            xalign 0.5
                            yalign 0.5

                            text day_name[:3]:
                                size 14
                                color "#000000" if is_today else "#FFFFFF"
                                xalign 0.5

            # Upcoming events
            text "Upcoming Events (Next 7 Days)":
                size 20
                color "#FFFFFF"

            viewport:
                ysize 150
                scrollbars "vertical"
                mousewheel True

                vbox:
                    spacing 5

                    $ upcoming = time_manager.get_upcoming_events(7)

                    if upcoming:
                        for event_day, event_name, event_desc in upcoming:
                            frame:
                                xfill True
                                background "#333333"
                                xpadding 10
                                ypadding 5

                                hbox:
                                    text "Day [event_day]:":
                                        size 14
                                        color "#FFD700"
                                        xsize 80

                                    text "[event_name]":
                                        size 14
                                        color "#FFFFFF"
                    else:
                        text "No upcoming events.":
                            size 14
                            color "#888888"

            # Active deadlines
            text "Active Deadlines":
                size 20
                color "#FFFFFF"

            viewport:
                ysize 100
                scrollbars "vertical"
                mousewheel True

                vbox:
                    spacing 5

                    $ active_deadlines = time_manager.get_active_deadlines()

                    if active_deadlines:
                        for deadline in active_deadlines:
                            $ days_left = deadline.days_remaining(time_manager.current_day)
                            $ is_warning = deadline.should_warn(time_manager.current_day)

                            frame:
                                xfill True
                                background "#660000" if is_warning else "#333333"
                                xpadding 10
                                ypadding 5

                                hbox:
                                    text "[deadline.name]":
                                        size 14
                                        color "#FFFFFF"
                                        xsize 300

                                    text "[days_left] days left":
                                        size 14
                                        color "#FF0000" if is_warning else "#00FF00"
                    else:
                        text "No active deadlines.":
                            size 14
                            color "#888888"

screen time_actions():
    """Screen with time-related actions."""
    frame:
        xalign 0.5
        yalign 1.0
        yoffset -50

        hbox:
            spacing 20

            textbutton "Wait (1 Period)":
                action [Function(time_manager.advance_time, 1), Function(update_time_display)]

            textbutton "Rest":
                action [Function(time_manager.rest), Function(update_time_display)]

            textbutton "Sleep (Next Day)":
                action [Function(time_manager.advance_day, 1), Function(update_time_display)]

            textbutton "Calendar":
                action Show("calendar_screen")

# Labels for time-based story events

label advance_time_with_events:
    # Call this to advance time and handle any triggered events
    python:
        triggered = time_manager.advance_time(1)
        update_time_display()

    if triggered:
        python:
            for event_data in triggered:
                if event_data["label"]:
                    renpy.call(event_data["label"])
                if event_data["callback"]:
                    event_data["callback"]()

    return

label check_deadline_warnings:
    # Call this to check for deadline warnings
    python:
        warnings = time_manager.get_warning_deadlines()

    if warnings:
        $ warning_deadline = warnings[0]
        $ days_left = warning_deadline.days_remaining(time_manager.current_day)

        "Warning! [warning_deadline.name] - Only [days_left] days remaining!"

    return

# Example scene labels that would be triggered by scheduled events

label weekly_meeting_scene:
    "It's time for the weekly team meeting."
    return

label party_scene:
    "The party has begun!"
    return

label weekend_scene:
    "Time to relax on this beautiful Saturday afternoon."
    return

label quest_failed:
    "You ran out of time to complete the investigation..."
    return

# Initialization label to set up the time system
label setup_time_system:
    python:
        setup_example_events()
        setup_example_npc_schedules()
        setup_example_deadline()
        update_time_display()
    return

# Example of using the time system in game
label time_system_demo:
    call setup_time_system

    show screen time_display
    show screen energy_bar

    "Welcome to the Time System Demo!"
    "Current time: [time_manager.get_formatted_date()]"
    "Your energy: [time_manager.energy]/[time_manager.max_energy]"

    menu:
        "What would you like to do?"

        "Advance Time (1 period)":
            python:
                events = time_manager.advance_time(1)
                update_time_display()
            "Time advanced to [time_manager.time_period_name]."
            if events:
                "An event was triggered!"

        "Sleep (next day)":
            python:
                events = time_manager.advance_day(1)
                update_time_display()
            "You slept. It's now Day [time_manager.current_day], [time_manager.time_period_name]."

        "Check NPC Locations":
            $ sarah_loc = time_manager.get_npc_location("sarah")
            $ mike_loc = time_manager.get_npc_location("mike")
            "Sarah is at: [sarah_loc]"
            "Mike is at: [mike_loc]"

        "Open Calendar":
            call screen calendar_screen

        "End Demo":
            hide screen time_display
            hide screen energy_bar
            return

    jump time_system_demo

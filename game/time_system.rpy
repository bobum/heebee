# Time System for Heebee
# Manages in-game time, day/night cycles, scheduled events, deadlines, and energy/fatigue

init python:
    from enum import Enum

    class TimeOfDay(Enum):
        """Represents different periods of the day."""
        DAWN = "dawn"           # 5-7
        MORNING = "morning"     # 7-12
        AFTERNOON = "afternoon" # 12-17
        EVENING = "evening"     # 17-20
        NIGHT = "night"         # 20-24
        LATE_NIGHT = "late_night"  # 0-5

    class ScheduledEvent:
        """
        Represents an event scheduled to occur at a specific time.

        Attributes:
            event_id: Unique identifier for the event
            name: Display name of the event
            trigger_day: Day number when event triggers (None for recurring)
            trigger_hour: Hour when event triggers (0-23)
            callback: Label or function to call when triggered
            recurring: Whether event repeats daily
            days_of_week: List of weekday indices (0=Monday) for weekly events
            active: Whether the event is currently active
            expired: Whether the event has expired (one-time events)
        """

        def __init__(self, event_id, name, trigger_day=None, trigger_hour=8,
                     callback=None, recurring=False, days_of_week=None):
            self.event_id = event_id
            self.name = name
            self.trigger_day = trigger_day
            self.trigger_hour = trigger_hour
            self.callback = callback
            self.recurring = recurring
            self.days_of_week = days_of_week if days_of_week else []
            self.active = True
            self.expired = False
            self.times_triggered = 0

        def should_trigger(self, current_day, current_hour, current_weekday):
            """Check if this event should trigger at the given time."""
            if not self.active or self.expired:
                return False

            # Check hour match
            if current_hour != self.trigger_hour:
                return False

            # For recurring weekly events
            if self.recurring and self.days_of_week:
                return current_weekday in self.days_of_week

            # For recurring daily events
            if self.recurring and not self.days_of_week:
                return True

            # For one-time events
            if self.trigger_day is not None:
                return current_day == self.trigger_day

            return False

        def trigger(self):
            """Mark the event as triggered."""
            self.times_triggered += 1
            if not self.recurring:
                self.expired = True
            return self.callback

        def cancel(self):
            """Cancel the event."""
            self.active = False

        def __repr__(self):
            return f"ScheduledEvent({self.event_id}, day={self.trigger_day}, hour={self.trigger_hour})"


    class Deadline:
        """
        Represents a deadline that must be met before expiration.

        Attributes:
            deadline_id: Unique identifier
            name: Display name
            description: What needs to be done
            due_day: Day number when deadline expires
            due_hour: Hour when deadline expires
            completed: Whether deadline was met
            expired: Whether deadline has passed
            on_complete: Callback when completed
            on_expire: Callback when expired
        """

        def __init__(self, deadline_id, name, description, due_day, due_hour=23,
                     on_complete=None, on_expire=None):
            self.deadline_id = deadline_id
            self.name = name
            self.description = description
            self.due_day = due_day
            self.due_hour = due_hour
            self.completed = False
            self.expired = False
            self.on_complete = on_complete
            self.on_expire = on_expire

        def check_expiration(self, current_day, current_hour):
            """Check if deadline has expired."""
            if self.completed or self.expired:
                return False

            if current_day > self.due_day:
                self.expired = True
                return True
            elif current_day == self.due_day and current_hour >= self.due_hour:
                self.expired = True
                return True
            return False

        def complete(self):
            """Mark deadline as completed."""
            if not self.expired:
                self.completed = True
                return self.on_complete
            return None

        def time_remaining(self, current_day, current_hour):
            """Get remaining time as (days, hours) tuple."""
            if self.completed or self.expired:
                return (0, 0)

            total_hours_left = (self.due_day - current_day) * 24 + (self.due_hour - current_hour)
            if total_hours_left < 0:
                return (0, 0)

            days = total_hours_left // 24
            hours = total_hours_left % 24
            return (days, hours)

        def __repr__(self):
            return f"Deadline({self.deadline_id}, due=day {self.due_day} hour {self.due_hour})"


    class TimeManager:
        """
        Manages all time-related functionality in the game.

        Time System:
            - 24-hour days
            - 7-day weeks (0=Monday through 6=Sunday)
            - Tracks total days elapsed

        Features:
            - Time advancement (hours, days)
            - Day/night cycle detection
            - Scheduled events
            - Deadlines with expiration
            - Energy/fatigue system
        """

        WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        def __init__(self, start_day=1, start_hour=8, start_weekday=0):
            # Core time tracking
            self.day = start_day
            self.hour = start_hour
            self.weekday = start_weekday  # 0=Monday, 6=Sunday

            # Events and deadlines
            self.scheduled_events = {}
            self.deadlines = {}
            self.triggered_events = []  # Events triggered this update

            # Energy/fatigue system
            self.max_energy = 100
            self.energy = 100
            self.fatigue = 0
            self.is_exhausted = False

            # Configuration
            self.hours_per_action = 1
            self.energy_per_hour = 5
            self.fatigue_recovery_rate = 20  # Per night's rest
            self.exhaustion_threshold = 20  # Energy below this = exhausted

        # ===================================================================
        # TIME ADVANCEMENT
        # ===================================================================

        def advance_hour(self, hours=1):
            """
            Advance time by the specified number of hours.
            Returns list of events triggered during advancement.
            """
            self.triggered_events = []

            for _ in range(hours):
                self.hour += 1

                # Handle day rollover
                if self.hour >= 24:
                    self.hour = 0
                    self._advance_day()

                # Check for triggered events
                self._check_events()

                # Update energy
                self._update_energy(1)

            return self.triggered_events

        def advance_day(self, days=1):
            """
            Advance time by the specified number of days.
            Maintains current hour. Returns list of events triggered.
            """
            self.triggered_events = []

            for _ in range(days):
                self._advance_day()

                # Rest overnight restores energy
                self._rest_overnight()

                # Check events at current hour on new day
                self._check_events()

            return self.triggered_events

        def _advance_day(self):
            """Internal method to advance one day."""
            self.day += 1
            self.weekday = (self.weekday + 1) % 7

            # Check deadline expirations
            self._check_deadlines()

        def set_time(self, day=None, hour=None):
            """Set specific time values."""
            if day is not None:
                self.day = day
            if hour is not None:
                self.hour = max(0, min(23, hour))

        def skip_to_hour(self, target_hour):
            """
            Skip forward to a specific hour (today or tomorrow if past).
            Returns hours skipped.
            """
            target_hour = max(0, min(23, target_hour))

            if target_hour <= self.hour:
                # Skip to tomorrow
                hours_to_skip = (24 - self.hour) + target_hour
            else:
                hours_to_skip = target_hour - self.hour

            self.advance_hour(hours_to_skip)
            return hours_to_skip

        # ===================================================================
        # TIME OF DAY / DAY-NIGHT CYCLE
        # ===================================================================

        def get_time_of_day(self):
            """Get the current time of day period."""
            if 5 <= self.hour < 7:
                return TimeOfDay.DAWN
            elif 7 <= self.hour < 12:
                return TimeOfDay.MORNING
            elif 12 <= self.hour < 17:
                return TimeOfDay.AFTERNOON
            elif 17 <= self.hour < 20:
                return TimeOfDay.EVENING
            elif 20 <= self.hour < 24:
                return TimeOfDay.NIGHT
            else:  # 0-5
                return TimeOfDay.LATE_NIGHT

        def is_daytime(self):
            """Check if it's currently daytime (7am - 8pm)."""
            return 7 <= self.hour < 20

        def is_nighttime(self):
            """Check if it's currently nighttime (8pm - 7am)."""
            return self.hour >= 20 or self.hour < 7

        def get_weekday_name(self):
            """Get the name of the current weekday."""
            return self.WEEKDAY_NAMES[self.weekday]

        def is_weekend(self):
            """Check if it's currently a weekend (Saturday/Sunday)."""
            return self.weekday >= 5

        def get_formatted_time(self):
            """Get formatted time string (e.g., '2:30 PM')."""
            if self.hour == 0:
                return "12:00 AM"
            elif self.hour < 12:
                return f"{self.hour}:00 AM"
            elif self.hour == 12:
                return "12:00 PM"
            else:
                return f"{self.hour - 12}:00 PM"

        def get_date_string(self):
            """Get formatted date string."""
            return f"Day {self.day} ({self.get_weekday_name()})"

        # ===================================================================
        # SCHEDULED EVENTS
        # ===================================================================

        def schedule_event(self, event_id, name, trigger_day=None, trigger_hour=8,
                          callback=None, recurring=False, days_of_week=None):
            """Schedule a new event."""
            event = ScheduledEvent(
                event_id=event_id,
                name=name,
                trigger_day=trigger_day,
                trigger_hour=trigger_hour,
                callback=callback,
                recurring=recurring,
                days_of_week=days_of_week
            )
            self.scheduled_events[event_id] = event
            return event

        def cancel_event(self, event_id):
            """Cancel a scheduled event."""
            if event_id in self.scheduled_events:
                self.scheduled_events[event_id].cancel()
                return True
            return False

        def get_event(self, event_id):
            """Get a scheduled event by ID."""
            return self.scheduled_events.get(event_id)

        def get_upcoming_events(self, hours_ahead=24):
            """Get events scheduled within the next N hours."""
            upcoming = []
            check_day = self.day
            check_hour = self.hour
            check_weekday = self.weekday

            for _ in range(hours_ahead):
                for event in self.scheduled_events.values():
                    if event.should_trigger(check_day, check_hour, check_weekday):
                        if event not in upcoming:
                            upcoming.append(event)

                check_hour += 1
                if check_hour >= 24:
                    check_hour = 0
                    check_day += 1
                    check_weekday = (check_weekday + 1) % 7

            return upcoming

        def _check_events(self):
            """Check and trigger any events at current time."""
            for event in self.scheduled_events.values():
                if event.should_trigger(self.day, self.hour, self.weekday):
                    callback = event.trigger()
                    self.triggered_events.append({
                        'event_id': event.event_id,
                        'name': event.name,
                        'callback': callback
                    })

        # ===================================================================
        # DEADLINES
        # ===================================================================

        def add_deadline(self, deadline_id, name, description, due_day, due_hour=23,
                        on_complete=None, on_expire=None):
            """Add a new deadline."""
            deadline = Deadline(
                deadline_id=deadline_id,
                name=name,
                description=description,
                due_day=due_day,
                due_hour=due_hour,
                on_complete=on_complete,
                on_expire=on_expire
            )
            self.deadlines[deadline_id] = deadline
            return deadline

        def complete_deadline(self, deadline_id):
            """Mark a deadline as completed."""
            if deadline_id in self.deadlines:
                return self.deadlines[deadline_id].complete()
            return None

        def get_deadline(self, deadline_id):
            """Get a deadline by ID."""
            return self.deadlines.get(deadline_id)

        def get_active_deadlines(self):
            """Get all active (not completed or expired) deadlines."""
            return [d for d in self.deadlines.values()
                    if not d.completed and not d.expired]

        def get_urgent_deadlines(self, hours_threshold=24):
            """Get deadlines due within the threshold hours."""
            urgent = []
            for deadline in self.get_active_deadlines():
                days, hours = deadline.time_remaining(self.day, self.hour)
                total_hours = days * 24 + hours
                if total_hours <= hours_threshold:
                    urgent.append(deadline)
            return urgent

        def _check_deadlines(self):
            """Check for expired deadlines."""
            expired = []
            for deadline in self.deadlines.values():
                if deadline.check_expiration(self.day, self.hour):
                    expired.append({
                        'deadline_id': deadline.deadline_id,
                        'name': deadline.name,
                        'callback': deadline.on_expire
                    })
            return expired

        # ===================================================================
        # ENERGY / FATIGUE SYSTEM
        # ===================================================================

        def get_energy(self):
            """Get current energy level."""
            return self.energy

        def get_fatigue(self):
            """Get current fatigue level."""
            return self.fatigue

        def modify_energy(self, amount):
            """Modify energy by amount (positive or negative)."""
            old_energy = self.energy
            self.energy = max(0, min(self.max_energy, self.energy + amount))

            # Check exhaustion
            if self.energy <= self.exhaustion_threshold:
                self.is_exhausted = True
            elif self.energy > self.exhaustion_threshold + 10:
                self.is_exhausted = False

            return self.energy - old_energy

        def modify_fatigue(self, amount):
            """Modify fatigue by amount."""
            self.fatigue = max(0, min(100, self.fatigue + amount))

        def _update_energy(self, hours):
            """Update energy based on time passed."""
            energy_cost = hours * self.energy_per_hour

            # Fatigue increases energy drain
            if self.fatigue > 50:
                energy_cost = int(energy_cost * 1.5)

            self.modify_energy(-energy_cost)

            # Accumulate fatigue when active
            if not self.is_nighttime():
                self.modify_fatigue(hours * 2)

        def _rest_overnight(self):
            """Restore energy from overnight rest."""
            # Full rest only if sleeping at night
            self.energy = self.max_energy
            self.fatigue = max(0, self.fatigue - self.fatigue_recovery_rate)
            self.is_exhausted = False

        def rest(self, hours):
            """Rest for a number of hours, recovering energy."""
            recovery_per_hour = 15
            if self.is_nighttime():
                recovery_per_hour = 25  # Better recovery at night

            for _ in range(hours):
                self.modify_energy(recovery_per_hour)
                self.modify_fatigue(-5)
                self.advance_hour(1)

        def can_perform_action(self, energy_cost=None):
            """Check if player has enough energy for an action."""
            if energy_cost is None:
                energy_cost = self.energy_per_hour
            return self.energy >= energy_cost and not self.is_exhausted

        def perform_action(self, energy_cost=None, hours=1):
            """Perform an action that costs energy and time."""
            if energy_cost is None:
                energy_cost = self.energy_per_hour * hours

            if not self.can_perform_action(energy_cost):
                return False

            self.modify_energy(-energy_cost)
            self.advance_hour(hours)
            return True


# Initialize time system
default time_manager = TimeManager()


# ============================================================================
# TIME DISPLAY SCREEN
# ============================================================================

screen time_display():
    frame:
        xalign 1.0
        yalign 0.0
        padding (15, 10)
        background "#00000099"

        vbox:
            spacing 5

            text "[time_manager.get_date_string()]" size 16 color "#ffffff"
            text "[time_manager.get_formatted_time()]" size 14 color "#aaaaaa"

            hbox:
                spacing 5
                text "Energy:" size 12 color "#88ff88"
                bar value time_manager.energy range time_manager.max_energy xmaximum 100

            if time_manager.is_exhausted:
                text "EXHAUSTED" size 12 color "#ff4444"


screen deadline_warning(deadline):
    timer 3.0 action Hide("deadline_warning")

    frame:
        xalign 0.5
        yalign 0.1
        padding (20, 15)
        background "#ff000099"

        vbox:
            text "Deadline Approaching!" size 18 color "#ffffff" bold True
            text deadline.name size 14 color "#ffcccc"
            python:
                days, hours = deadline.time_remaining(time_manager.day, time_manager.hour)
            text "Time remaining: [days] days, [hours] hours" size 12 color "#ffffff"


# ============================================================================
# HELPER LABELS
# ============================================================================

label advance_time(hours=1):
    python:
        events = time_manager.advance_hour(hours)
        for event_data in events:
            if event_data.get('callback'):
                renpy.call(event_data['callback'])
    return

label sleep_until_morning:
    python:
        time_manager.skip_to_hour(7)
        time_manager._rest_overnight()
    "You sleep through the night and wake up refreshed."
    return

label check_energy:
    if time_manager.is_exhausted:
        "You're too exhausted to continue. You need to rest."
        return
    return

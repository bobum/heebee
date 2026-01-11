# Morality/Karma System for Ren'Py Visual Novel
# This module provides a comprehensive karma tracking system with
# alignment calculation, karma-gated content, and optional decay.

init python:
    import time

    # =========================================================================
    # ALIGNMENT THRESHOLDS - Define karma ranges for each alignment
    # =========================================================================

    ALIGNMENT_THRESHOLDS = {
        "evil": {"min": -100, "max": -31, "label": "Evil", "color": "#ff3333"},
        "neutral": {"min": -30, "max": 30, "label": "Neutral", "color": "#888888"},
        "good": {"min": 31, "max": 100, "label": "Good", "color": "#33ff33"}
    }

    # =========================================================================
    # KARMA CHANGE REASONS - Predefined reason categories
    # =========================================================================

    KARMA_REASONS = {
        "help": "Helped someone in need",
        "steal": "Stole from someone",
        "lie": "Told a lie",
        "truth": "Told the truth",
        "mercy": "Showed mercy",
        "violence": "Committed unnecessary violence",
        "charity": "Gave to those in need",
        "greed": "Acted out of greed",
        "sacrifice": "Made a personal sacrifice",
        "betrayal": "Betrayed someone's trust"
    }

    # =========================================================================
    # KARMA GATED CONTENT - Content unlocked at specific karma levels
    # =========================================================================

    KARMA_UNLOCKS = {
        -80: "dark_ritual",          # Very evil - dark magic available
        -50: "villain_alliance",      # Evil - can join villains
        -30: "intimidation_option",   # Slight evil - can intimidate NPCs
        30: "trusted_helper",         # Slight good - NPCs trust you more
        50: "hero_recognition",       # Good - recognized as a hero
        80: "saintly_blessing"        # Very good - receive divine blessing
    }

    # =========================================================================
    # KARMA ENTRY CLASS - Represents a single karma change
    # =========================================================================

    class KarmaEntry:
        """
        Represents a single karma modification entry.

        Attributes:
            amount (int): The karma change amount (positive or negative)
            reason (str): The reason for the karma change
            timestamp (float): When the change occurred
            resulting_karma (int): Karma value after this change
        """

        def __init__(self, amount, reason, resulting_karma, timestamp=None):
            self.amount = amount
            self.reason = reason
            self.resulting_karma = resulting_karma
            self.timestamp = timestamp if timestamp is not None else time.time()

        def __repr__(self):
            direction = "+" if self.amount >= 0 else ""
            return f"KarmaEntry({direction}{self.amount}, '{self.reason}', karma={self.resulting_karma})"

    # =========================================================================
    # MORALITY MANAGER CLASS - Central manager for karma system
    # =========================================================================

    class MoralityManager:
        """
        Central manager for tracking player karma and moral alignment.

        This class provides methods to modify karma, query alignment status,
        check karma-gated content availability, and optionally apply karma decay.

        Attributes:
            _karma (int): Current karma value (-100 to 100)
            karma_history (list): List of KarmaEntry objects tracking changes
            decay_enabled (bool): Whether karma decay is active
            decay_rate (float): Amount of karma decay per tick
            decay_interval (float): Seconds between decay ticks
            last_decay_time (float): Timestamp of last decay application
        """

        MIN_KARMA = -100
        MAX_KARMA = 100

        def __init__(self, initial_karma=0, decay_enabled=False, decay_rate=1, decay_interval=300):
            """
            Initialize the MoralityManager.

            Args:
                initial_karma (int): Starting karma value (default 0)
                decay_enabled (bool): Enable karma decay over time (default False)
                decay_rate (float): Amount karma decays toward 0 per tick (default 1)
                decay_interval (float): Seconds between decay applications (default 300)
            """
            self._karma = max(self.MIN_KARMA, min(self.MAX_KARMA, initial_karma))
            self.karma_history = []
            self.decay_enabled = decay_enabled
            self.decay_rate = decay_rate
            self.decay_interval = decay_interval
            self.last_decay_time = time.time()
            self._unlocked_content = set()
            self._pending_notifications = []

        # ---------------------------------------------------------------------
        # Karma Property
        # ---------------------------------------------------------------------

        @property
        def karma(self):
            """Get the current karma value."""
            return self._karma

        @karma.setter
        def karma(self, value):
            """Set karma value with bounds checking."""
            self._karma = max(self.MIN_KARMA, min(self.MAX_KARMA, value))

        # ---------------------------------------------------------------------
        # Alignment Property
        # ---------------------------------------------------------------------

        @property
        def alignment(self):
            """Get the current alignment based on karma value."""
            return self.get_alignment()

        # ---------------------------------------------------------------------
        # Core Methods
        # ---------------------------------------------------------------------

        def modify_karma(self, amount, reason=""):
            """
            Modify karma by the given amount with an optional reason.

            Args:
                amount (int): Amount to change karma (positive or negative)
                reason (str): Reason for the karma change

            Returns:
                tuple: (new_karma, unlocked_content_list)
            """
            old_karma = self._karma
            self._karma = max(self.MIN_KARMA, min(self.MAX_KARMA, self._karma + amount))

            # Record in history
            entry = KarmaEntry(amount, reason, self._karma)
            self.karma_history.append(entry)

            # Check for newly unlocked content
            newly_unlocked = self._check_unlocks()

            # Queue notification
            if amount != 0:
                self._pending_notifications.append({
                    "amount": amount,
                    "reason": reason,
                    "old_karma": old_karma,
                    "new_karma": self._karma
                })

            return self._karma, newly_unlocked

        def get_alignment(self):
            """
            Get the current alignment based on karma thresholds.

            Returns:
                tuple: (alignment_id, alignment_label, color)
            """
            for align_id, align_data in ALIGNMENT_THRESHOLDS.items():
                if align_data["min"] <= self._karma <= align_data["max"]:
                    return (align_id, align_data["label"], align_data["color"])
            return ("neutral", "Neutral", "#888888")

        def get_alignment_id(self):
            """Get just the alignment ID (evil, neutral, good)."""
            return self.get_alignment()[0]

        def get_alignment_label(self):
            """Get the displayable alignment label."""
            return self.get_alignment()[1]

        def get_alignment_color(self):
            """Get the color associated with current alignment."""
            return self.get_alignment()[2]

        # ---------------------------------------------------------------------
        # Karma History Methods
        # ---------------------------------------------------------------------

        def get_karma_history(self, limit=None):
            """
            Get karma change history.

            Args:
                limit (int): Maximum number of entries to return (None for all)

            Returns:
                list: List of KarmaEntry objects, newest first
            """
            history = list(reversed(self.karma_history))
            if limit is not None:
                return history[:limit]
            return history

        def get_total_positive_karma(self):
            """Get total positive karma earned."""
            return sum(e.amount for e in self.karma_history if e.amount > 0)

        def get_total_negative_karma(self):
            """Get total negative karma earned (as positive number)."""
            return abs(sum(e.amount for e in self.karma_history if e.amount < 0))

        def clear_history(self):
            """Clear karma history but keep current karma value."""
            self.karma_history = []

        # ---------------------------------------------------------------------
        # Karma-Gated Content Methods
        # ---------------------------------------------------------------------

        def _check_unlocks(self):
            """Check and unlock content based on current karma."""
            newly_unlocked = []
            for threshold, content_id in KARMA_UNLOCKS.items():
                if content_id in self._unlocked_content:
                    continue

                # Check if karma crosses the threshold
                if threshold < 0 and self._karma <= threshold:
                    self._unlocked_content.add(content_id)
                    newly_unlocked.append(content_id)
                elif threshold > 0 and self._karma >= threshold:
                    self._unlocked_content.add(content_id)
                    newly_unlocked.append(content_id)

            return newly_unlocked

        def is_content_available(self, content_id):
            """
            Check if karma-gated content is available.

            Args:
                content_id (str): The content identifier to check

            Returns:
                bool: True if content is unlocked
            """
            return content_id in self._unlocked_content

        def check_karma_requirement(self, min_karma=None, max_karma=None, alignment=None):
            """
            Check if current karma meets specified requirements.

            Args:
                min_karma (int): Minimum karma required (optional)
                max_karma (int): Maximum karma required (optional)
                alignment (str): Required alignment ID (optional)

            Returns:
                bool: True if all requirements are met
            """
            if min_karma is not None and self._karma < min_karma:
                return False
            if max_karma is not None and self._karma > max_karma:
                return False
            if alignment is not None and self.get_alignment_id() != alignment:
                return False
            return True

        def get_available_content(self):
            """Get list of all unlocked content IDs."""
            return list(self._unlocked_content)

        # ---------------------------------------------------------------------
        # Karma Decay Methods
        # ---------------------------------------------------------------------

        def enable_decay(self, rate=1, interval=300):
            """
            Enable karma decay toward neutral.

            Args:
                rate (float): Amount to decay per tick
                interval (float): Seconds between decay ticks
            """
            self.decay_enabled = True
            self.decay_rate = rate
            self.decay_interval = interval
            self.last_decay_time = time.time()

        def disable_decay(self):
            """Disable karma decay."""
            self.decay_enabled = False

        def apply_decay(self):
            """
            Apply karma decay if enabled and enough time has passed.

            Karma decays toward 0 (neutral). Positive karma decreases,
            negative karma increases.

            Returns:
                int: Amount of decay applied (0 if no decay occurred)
            """
            if not self.decay_enabled:
                return 0

            current_time = time.time()
            elapsed = current_time - self.last_decay_time

            if elapsed < self.decay_interval:
                return 0

            # Calculate number of decay ticks
            ticks = int(elapsed / self.decay_interval)
            if ticks == 0:
                return 0

            self.last_decay_time = current_time

            # Apply decay toward neutral (0)
            decay_amount = 0
            if self._karma > 0:
                decay_amount = min(self._karma, self.decay_rate * ticks)
                self._karma -= int(decay_amount)
            elif self._karma < 0:
                decay_amount = min(abs(self._karma), self.decay_rate * ticks)
                self._karma += int(decay_amount)

            if decay_amount > 0:
                entry = KarmaEntry(
                    -int(decay_amount) if self._karma >= 0 else int(decay_amount),
                    "karma_decay",
                    self._karma
                )
                self.karma_history.append(entry)

            return int(decay_amount)

        # ---------------------------------------------------------------------
        # Notification Methods
        # ---------------------------------------------------------------------

        def get_pending_notification(self):
            """
            Get and clear the next pending notification.

            Returns:
                dict or None: Notification data or None if no notifications
            """
            if self._pending_notifications:
                return self._pending_notifications.pop(0)
            return None

        def has_pending_notifications(self):
            """Check if there are pending notifications."""
            return len(self._pending_notifications) > 0

        def clear_notifications(self):
            """Clear all pending notifications."""
            self._pending_notifications = []

        # ---------------------------------------------------------------------
        # Utility Methods
        # ---------------------------------------------------------------------

        def reset(self, karma=0):
            """
            Reset the morality system to a clean state.

            Args:
                karma (int): New karma value (default 0)
            """
            self._karma = max(self.MIN_KARMA, min(self.MAX_KARMA, karma))
            self.karma_history = []
            self._unlocked_content = set()
            self._pending_notifications = []
            self.last_decay_time = time.time()

        def get_karma_percentage(self):
            """
            Get karma as a percentage for UI display.

            Returns:
                float: Karma as 0-100 percentage (50 = neutral)
            """
            return ((self._karma + 100) / 200) * 100

        def get_status_summary(self):
            """
            Get a summary of current morality status.

            Returns:
                dict: Summary including karma, alignment, and stats
            """
            return {
                "karma": self._karma,
                "alignment": self.get_alignment_label(),
                "alignment_id": self.get_alignment_id(),
                "color": self.get_alignment_color(),
                "total_positive": self.get_total_positive_karma(),
                "total_negative": self.get_total_negative_karma(),
                "changes_count": len(self.karma_history),
                "unlocked_content": list(self._unlocked_content)
            }

# =============================================================================
# GLOBAL MORALITY MANAGER INSTANCE
# =============================================================================

default morality_manager = MoralityManager()

# =============================================================================
# KARMA INDICATOR SCREEN - Shows karma in corner during gameplay
# =============================================================================

screen karma_indicator():
    zorder 50

    # Get current alignment for styling
    $ align_id, align_label, align_color = morality_manager.get_alignment()
    $ karma_value = morality_manager.karma

    frame:
        xalign 1.0
        yalign 0.0
        xoffset -10
        yoffset 10
        padding (15, 10, 15, 10)
        background Solid("#00000099")

        hbox:
            spacing 10

            # Alignment icon based on karma
            frame:
                xysize (30, 30)
                background align_color

                # Simple text icon
                if align_id == "evil":
                    text "E" align (0.5, 0.5) size 18 color "#000000"
                elif align_id == "good":
                    text "G" align (0.5, 0.5) size 18 color "#000000"
                else:
                    text "N" align (0.5, 0.5) size 18 color "#ffffff"

            vbox:
                spacing 2

                # Alignment label
                text align_label size 14 color align_color

                # Karma bar
                hbox:
                    spacing 5

                    # Karma bar showing -100 to 100 centered at 0
                    frame:
                        xsize 80
                        ysize 8
                        background "#333333"

                        # Calculate bar fill
                        $ bar_percent = (karma_value + 100) / 200.0
                        $ bar_width = int(80 * bar_percent)

                        # Left half (negative) or right half (positive)
                        if karma_value < 0:
                            # Red bar from karma position to center
                            frame:
                                pos (bar_width, 0)
                                xsize 40 - bar_width
                                ysize 8
                                background "#ff3333"
                        elif karma_value > 0:
                            # Green bar from center to karma position
                            frame:
                                pos (40, 0)
                                xsize bar_width - 40
                                ysize 8
                                background "#33ff33"

                        # Center marker
                        frame:
                            pos (39, 0)
                            xsize 2
                            ysize 8
                            background "#ffffff"

                    text "[karma_value]" size 12 color "#aaaaaa"

# =============================================================================
# KARMA NOTIFICATION TOAST - Shows when karma changes
# =============================================================================

screen karma_notification(amount, reason=""):
    zorder 200
    modal False

    $ is_positive = amount > 0
    $ color = "#33ff33" if is_positive else "#ff3333"
    $ prefix = "+" if is_positive else ""

    frame:
        xalign 0.5
        yalign 0.0
        yoffset 60
        padding (20, 12, 20, 12)
        background Solid("#000000cc")

        hbox:
            spacing 15

            # Karma icon
            frame:
                xysize (24, 24)
                background color

                if is_positive:
                    text "+" align (0.5, 0.5) size 16 color "#000000"
                else:
                    text "-" align (0.5, 0.5) size 16 color "#000000"

            vbox:
                spacing 2

                text "Karma [prefix][amount]" size 18 color color

                if reason:
                    text reason size 12 color "#aaaaaa"

    timer 2.5 action Hide("karma_notification")

# =============================================================================
# KARMA SCREEN - Full karma status display
# =============================================================================

screen karma_screen():
    tag menu

    frame:
        xfill True
        yfill True
        background "#1a1a1a"
        padding (40, 40)

        vbox:
            spacing 20
            xfill True
            yfill True

            # Title bar with close button
            hbox:
                xfill True
                text _("Karma") size 36 color "#ffffff"
                textbutton _("Return") action Return() align (1.0, 0.5)

            style_prefix "karma"

            $ align_id, align_label, align_color = morality_manager.get_alignment()
            $ karma_value = morality_manager.karma
            $ summary = morality_manager.get_status_summary()

            viewport:
                scrollbars "vertical"
                mousewheel True
                xfill True
                yfill True

                vbox:
                    spacing 20

                    # Header with alignment
                    hbox:
                        spacing 20

                        # Large alignment indicator
                        frame:
                            xysize (100, 100)
                            background align_color

                            vbox:
                                align (0.5, 0.5)
                                spacing 5

                                if align_id == "evil":
                                    text "EVIL" align (0.5, 0.5) size 24 color "#000000"
                                elif align_id == "good":
                                    text "GOOD" align (0.5, 0.5) size 24 color "#000000"
                                else:
                                    text "NEUTRAL" align (0.5, 0.5) size 18 color "#ffffff"

                        vbox:
                            spacing 10

                            text "Moral Alignment" size 32 color "#ffffff"
                            text "Your actions shape who you are" size 16 color "#888888"

                            # Large karma value display
                            hbox:
                                spacing 10
                                text "Karma:" size 24 color "#aaaaaa"
                                text "[karma_value]" size 28 color align_color

                    null height 10

                    # Full karma bar
                    frame:
                        xfill True
                        padding (20, 15)
                        background "#333333"

                        vbox:
                            spacing 10

                            text "Karma Scale" size 20 color "#ffffff"

                            hbox:
                                spacing 10

                                text "Evil" size 14 color "#ff3333" min_width 50
                                text "-100" size 12 color "#666666"

                                frame:
                                    xsize 400
                                    ysize 24
                                    background "#222222"

                                    # Gradient-like appearance with sections
                                    hbox:
                                        spacing 0

                                        # Evil section
                                        frame:
                                            xsize 140
                                            ysize 24
                                            background "#661111"

                                        # Neutral section
                                        frame:
                                            xsize 120
                                            ysize 24
                                            background "#444444"

                                        # Good section
                                        frame:
                                            xsize 140
                                            ysize 24
                                            background "#116611"

                                    # Karma position marker
                                    $ marker_x = int(((karma_value + 100) / 200.0) * 400)
                                    frame:
                                        pos (marker_x - 3, 0)
                                        xsize 6
                                        ysize 24
                                        background "#ffffff"

                                text "+100" size 12 color "#666666"
                                text "Good" size 14 color "#33ff33" min_width 50

                    # Statistics section
                    frame:
                        xfill True
                        padding (20, 15)
                        background "#333333"

                        vbox:
                            spacing 10

                            text "Karma Statistics" size 20 color "#ffffff"

                            hbox:
                                spacing 40

                                vbox:
                                    spacing 5
                                    text "Total Good Deeds" size 14 color "#888888"
                                    text "+[summary['total_positive']]" size 20 color "#33ff33"

                                vbox:
                                    spacing 5
                                    text "Total Bad Deeds" size 14 color "#888888"
                                    text "-[summary['total_negative']]" size 20 color "#ff3333"

                                vbox:
                                    spacing 5
                                    text "Total Actions" size 14 color "#888888"
                                    text "[summary['changes_count']]" size 20 color "#ffffff"

                    # Recent karma history
                    frame:
                        xfill True
                        padding (20, 15)
                        background "#333333"

                        vbox:
                            spacing 10

                            text "Recent Actions" size 20 color "#ffffff"

                            $ history = morality_manager.get_karma_history(limit=5)

                            if history:
                                for entry in history:
                                    $ entry_color = "#33ff33" if entry.amount > 0 else "#ff3333"
                                    $ entry_prefix = "+" if entry.amount > 0 else ""

                                    hbox:
                                        spacing 10
                                        text "[entry_prefix][entry.amount]" size 16 color entry_color min_width 50
                                        text entry.reason size 14 color "#aaaaaa"
                            else:
                                text "No karma changes recorded yet." size 14 color "#666666"

                    # Unlocked content section
                    $ unlocked = morality_manager.get_available_content()
                    if unlocked:
                        frame:
                            xfill True
                            padding (20, 15)
                            background "#333333"

                            vbox:
                                spacing 10

                                text "Unlocked Content" size 20 color "#ffffff"

                                for content_id in unlocked:
                                    hbox:
                                        spacing 10
                                        text "[*]" size 14 color align_color
                                        text content_id.replace("_", " ").title() size 14 color "#cccccc"

# =============================================================================
# STYLES FOR KARMA SCREEN
# =============================================================================

style karma_vbox:
    xfill True
    spacing 10

style karma_frame:
    background "#2a2a2a"
    padding (20, 20)

style karma_text:
    color "#ffffff"

# =============================================================================
# HELPER LABELS FOR EASY KARMA CHANGES
# =============================================================================

# Change karma with notification
label change_karma(amount, reason="", notify=True):
    $ new_karma, unlocks = morality_manager.modify_karma(amount, reason)
    if notify and amount != 0:
        call screen karma_notification(amount, reason)

    # Notify about unlocked content
    python:
        for content_id in unlocks:
            renpy.notify("Unlocked: " + content_id)
    return

# Quick karma helpers
label good_deed(amount=5, reason="Did a good deed"):
    call change_karma(amount, reason)
    return

label bad_deed(amount=-5, reason="Did something wrong"):
    call change_karma(amount, reason)
    return

# Check karma for gated content
label check_karma_gate(content_id):
    if morality_manager.is_content_available(content_id):
        return True
    return False

# Apply karma decay (call periodically if decay is enabled)
label apply_karma_decay():
    $ decay = morality_manager.apply_decay()
    if decay > 0:
        $ renpy.notify("Karma decayed by [decay]")
    return

# Reset karma system
label reset_karma(karma=0):
    $ morality_manager.reset(karma)
    return

# =============================================================================
# SCREEN TOGGLE HELPERS
# =============================================================================

init python:
    def show_karma_indicator():
        """Show the karma indicator on screen."""
        renpy.show_screen("karma_indicator")

    def hide_karma_indicator():
        """Hide the karma indicator."""
        renpy.hide_screen("karma_indicator")

    def show_karma_notification(amount, reason=""):
        """Show a karma change notification."""
        renpy.show_screen("karma_notification", amount=amount, reason=reason)

# =============================================================================
# EXAMPLE USAGE IN GAME SCRIPT
# =============================================================================

# Example label showing karma system usage:
#
# label example_moral_choice:
#     "You see a merchant drop their coin purse."
#
#     menu:
#         "Return the purse":
#             call change_karma(10, "Returned lost money")
#             "The merchant thanks you profusely."
#
#         "Keep the money":
#             call change_karma(-15, "Stole lost money")
#             "You pocket the coins and walk away."
#
#         "Ignore it":
#             "You continue on your way."
#
#     # Check alignment for different dialogue
#     if morality_manager.get_alignment_id() == "evil":
#         "People eye you with suspicion."
#     elif morality_manager.get_alignment_id() == "good":
#         "People smile warmly at you."
#
#     return
#
# To show karma indicator during gameplay:
#     $ show_karma_indicator()
#
# To open the full karma screen:
#     call screen karma_screen
#
# To check karma requirements:
#     if morality_manager.check_karma_requirement(min_karma=50):
#         "The guards let you pass without question."
#
# To enable karma decay:
#     $ morality_manager.enable_decay(rate=1, interval=300)

# Achievement System for Ren'Py Visual Novel
# This module provides a comprehensive achievement tracking system with
# unlock notifications, progress tracking, and a gallery UI.

init python:
    import datetime as dt

    # =========================================================================
    # ACHIEVEMENT CATEGORIES - Organize achievements by type
    # =========================================================================

    ACHIEVEMENT_CATEGORIES = {
        "story": {"label": "Story", "description": "Story progression achievements"},
        "exploration": {"label": "Exploration", "description": "Discover secrets and hidden content"},
        "social": {"label": "Social", "description": "Relationship and friendship achievements"},
        "completion": {"label": "Completion", "description": "Complete various collections and tasks"},
        "challenge": {"label": "Challenge", "description": "Overcome difficult challenges"},
        "secret": {"label": "Secret", "description": "Hidden achievements"}
    }

    # =========================================================================
    # ACHIEVEMENT CLASS - Base class for all achievements
    # =========================================================================

    class Achievement:
        """
        Represents a single achievement in the game.

        Attributes:
            id (str): Unique identifier for the achievement
            name (str): Display name of the achievement
            description (str): Description of how to unlock
            icon (str): Path to achievement icon image
            points (int): Point value of the achievement
            hidden (bool): Whether achievement is hidden until unlocked
            unlocked (bool): Whether achievement has been unlocked
            unlock_date (datetime): When the achievement was unlocked
            category (str): Category for organization
        """

        def __init__(self, id, name, description, icon=None, points=10,
                     hidden=False, category="story"):
            self.id = id
            self.name = name
            self.description = description
            self.icon = icon
            self.points = points
            self.hidden = hidden
            self.unlocked = False
            self.unlock_date = None
            self.category = category

        def unlock(self):
            """
            Unlock this achievement.

            Returns:
                bool: True if newly unlocked, False if already unlocked
            """
            if not self.unlocked:
                self.unlocked = True
                self.unlock_date = dt.datetime.now()
                return True
            return False

        def get_display_name(self):
            """Get name for display (respects hidden flag)."""
            if self.hidden and not self.unlocked:
                return "???"
            return self.name

        def get_display_description(self):
            """Get description for display (respects hidden flag)."""
            if self.hidden and not self.unlocked:
                return "This achievement is hidden."
            return self.description

        def get_display_icon(self):
            """Get icon for display (returns locked icon if hidden/locked)."""
            if not self.unlocked:
                return "gui/achievements/locked.png"
            return self.icon or "gui/achievements/default.png"

        def to_dict(self):
            """Serialize achievement to dictionary for saving."""
            return {
                "id": self.id,
                "unlocked": self.unlocked,
                "unlock_date": self.unlock_date.isoformat() if self.unlock_date else None
            }

        def from_dict(self, data):
            """Restore achievement state from dictionary."""
            self.unlocked = data.get("unlocked", False)
            unlock_date_str = data.get("unlock_date")
            if unlock_date_str:
                self.unlock_date = dt.datetime.fromisoformat(unlock_date_str)

    # =========================================================================
    # PROGRESS ACHIEVEMENT CLASS - For achievements with progress tracking
    # =========================================================================

    class ProgressAchievement(Achievement):
        """
        Achievement that tracks progress toward a goal.

        Extends Achievement with current/target progress tracking.

        Attributes:
            current (int): Current progress value
            target (int): Target value to unlock
        """

        def __init__(self, id, name, description, target, icon=None, points=10,
                     hidden=False, category="story"):
            super().__init__(id, name, description, icon, points, hidden, category)
            self.current = 0
            self.target = target

        def add_progress(self, amount=1):
            """
            Add progress toward the achievement.

            Args:
                amount (int): Amount to add to progress

            Returns:
                bool: True if this caused the achievement to unlock
            """
            if self.unlocked:
                return False

            self.current = min(self.current + amount, self.target)

            if self.current >= self.target:
                return self.unlock()
            return False

        def set_progress(self, value):
            """
            Set progress to a specific value.

            Args:
                value (int): Value to set progress to

            Returns:
                bool: True if this caused the achievement to unlock
            """
            if self.unlocked:
                return False

            self.current = min(max(0, value), self.target)

            if self.current >= self.target:
                return self.unlock()
            return False

        def get_progress_percent(self):
            """Get progress as a percentage (0-100)."""
            if self.target == 0:
                return 100
            return int((self.current / self.target) * 100)

        def get_progress_text(self):
            """Get progress as displayable text."""
            return f"{self.current}/{self.target}"

        def get_display_description(self):
            """Get description with progress info."""
            base = super().get_display_description()
            if not self.hidden or self.unlocked:
                return f"{base} ({self.get_progress_text()})"
            return base

        def to_dict(self):
            """Serialize progress achievement to dictionary."""
            data = super().to_dict()
            data["current"] = self.current
            return data

        def from_dict(self, data):
            """Restore progress achievement state from dictionary."""
            super().from_dict(data)
            self.current = data.get("current", 0)

    # =========================================================================
    # ACHIEVEMENT MANAGER - Central manager for all achievements
    # =========================================================================

    class AchievementManager:
        """
        Central manager for tracking and managing all game achievements.

        Handles registration, unlocking, progress tracking, and notifications.
        """

        def __init__(self):
            self.achievements = {}
            self.notification_queue = []
            self.notification_duration = 3.0  # seconds

        # ---------------------------------------------------------------------
        # Achievement Registration
        # ---------------------------------------------------------------------

        def register(self, achievement):
            """
            Register an achievement with the manager.

            Args:
                achievement (Achievement): Achievement to register

            Returns:
                Achievement: The registered achievement
            """
            self.achievements[achievement.id] = achievement
            return achievement

        def register_achievement(self, id, name, description, icon=None, points=10,
                                  hidden=False, category="story"):
            """
            Create and register a new achievement.

            Args:
                id (str): Unique identifier
                name (str): Display name
                description (str): Description text
                icon (str): Path to icon image
                points (int): Point value
                hidden (bool): Whether hidden until unlocked
                category (str): Category for organization

            Returns:
                Achievement: The created and registered achievement
            """
            achievement = Achievement(
                id=id,
                name=name,
                description=description,
                icon=icon,
                points=points,
                hidden=hidden,
                category=category
            )
            return self.register(achievement)

        def register_progress_achievement(self, id, name, description, target,
                                           icon=None, points=10, hidden=False,
                                           category="story"):
            """
            Create and register a new progress achievement.

            Args:
                id (str): Unique identifier
                name (str): Display name
                description (str): Description text
                target (int): Target value to unlock
                icon (str): Path to icon image
                points (int): Point value
                hidden (bool): Whether hidden until unlocked
                category (str): Category for organization

            Returns:
                ProgressAchievement: The created and registered achievement
            """
            achievement = ProgressAchievement(
                id=id,
                name=name,
                description=description,
                target=target,
                icon=icon,
                points=points,
                hidden=hidden,
                category=category
            )
            return self.register(achievement)

        # ---------------------------------------------------------------------
        # Achievement Unlocking
        # ---------------------------------------------------------------------

        def unlock(self, achievement_id, notify=True):
            """
            Unlock an achievement by ID.

            Args:
                achievement_id (str): ID of achievement to unlock
                notify (bool): Whether to show unlock notification

            Returns:
                bool: True if newly unlocked, False otherwise
            """
            achievement = self.achievements.get(achievement_id)
            if achievement is None:
                return False

            if achievement.unlock():
                if notify:
                    self._queue_notification(achievement)
                return True
            return False

        def add_progress(self, achievement_id, amount=1, notify=True):
            """
            Add progress to a progress achievement.

            Args:
                achievement_id (str): ID of achievement
                amount (int): Amount to add
                notify (bool): Whether to show notification on unlock

            Returns:
                bool: True if this caused an unlock
            """
            achievement = self.achievements.get(achievement_id)
            if achievement is None:
                return False

            if not isinstance(achievement, ProgressAchievement):
                return False

            if achievement.add_progress(amount):
                if notify:
                    self._queue_notification(achievement)
                return True
            return False

        def set_progress(self, achievement_id, value, notify=True):
            """
            Set progress for a progress achievement.

            Args:
                achievement_id (str): ID of achievement
                value (int): Value to set
                notify (bool): Whether to show notification on unlock

            Returns:
                bool: True if this caused an unlock
            """
            achievement = self.achievements.get(achievement_id)
            if achievement is None:
                return False

            if not isinstance(achievement, ProgressAchievement):
                return False

            if achievement.set_progress(value):
                if notify:
                    self._queue_notification(achievement)
                return True
            return False

        # ---------------------------------------------------------------------
        # Notification System
        # ---------------------------------------------------------------------

        def _queue_notification(self, achievement):
            """Add achievement to notification queue."""
            self.notification_queue.append(achievement)

        def get_pending_notification(self):
            """
            Get the next pending notification.

            Returns:
                Achievement or None: Next achievement to show, or None
            """
            if self.notification_queue:
                return self.notification_queue.pop(0)
            return None

        def has_pending_notifications(self):
            """Check if there are pending notifications."""
            return len(self.notification_queue) > 0

        def show_notification(self, achievement):
            """Show achievement unlock notification screen."""
            renpy.show_screen("achievement_notification", achievement=achievement)

        # ---------------------------------------------------------------------
        # Query Methods
        # ---------------------------------------------------------------------

        def get(self, achievement_id):
            """Get an achievement by ID."""
            return self.achievements.get(achievement_id)

        def get_all(self):
            """Get all registered achievements."""
            return list(self.achievements.values())

        def get_unlocked(self):
            """Get all unlocked achievements."""
            return [a for a in self.achievements.values() if a.unlocked]

        def get_locked(self):
            """Get all locked achievements."""
            return [a for a in self.achievements.values() if not a.unlocked]

        def get_by_category(self, category):
            """Get all achievements in a category."""
            return [a for a in self.achievements.values()
                    if a.category == category]

        def get_unlocked_by_category(self, category):
            """Get unlocked achievements in a category."""
            return [a for a in self.achievements.values()
                    if a.category == category and a.unlocked]

        def get_visible(self):
            """Get all achievements that should be visible (not hidden or unlocked)."""
            return [a for a in self.achievements.values()
                    if not a.hidden or a.unlocked]

        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        def get_total_points(self):
            """Get total points from unlocked achievements."""
            return sum(a.points for a in self.achievements.values() if a.unlocked)

        def get_max_points(self):
            """Get maximum possible points."""
            return sum(a.points for a in self.achievements.values())

        def get_unlock_count(self):
            """Get number of unlocked achievements."""
            return len(self.get_unlocked())

        def get_total_count(self):
            """Get total number of achievements."""
            return len(self.achievements)

        def get_completion_percent(self):
            """Get completion percentage."""
            total = self.get_total_count()
            if total == 0:
                return 100
            return int((self.get_unlock_count() / total) * 100)

        # ---------------------------------------------------------------------
        # Persistence
        # ---------------------------------------------------------------------

        def save_to_persistent(self):
            """Save achievement states to persistent storage."""
            data = {}
            for achievement_id, achievement in self.achievements.items():
                data[achievement_id] = achievement.to_dict()
            persistent.achievements_data = data

        def load_from_persistent(self):
            """Load achievement states from persistent storage."""
            data = getattr(persistent, 'achievements_data', None)
            if data is None:
                return

            for achievement_id, achievement_data in data.items():
                achievement = self.achievements.get(achievement_id)
                if achievement:
                    achievement.from_dict(achievement_data)

# =============================================================================
# GLOBAL ACHIEVEMENT MANAGER INSTANCE
# =============================================================================

default achievement_manager = AchievementManager()

# =============================================================================
# EXAMPLE ACHIEVEMENT DEFINITIONS
# =============================================================================

init python:
    def setup_achievements():
        """Initialize example achievements for the game."""

        # Story achievements
        achievement_manager.register_achievement(
            id="first_steps",
            name="First Steps",
            description="Begin your adventure",
            points=10,
            category="story"
        )

        achievement_manager.register_achievement(
            id="chapter_1_complete",
            name="Chapter Complete",
            description="Complete Chapter 1",
            points=25,
            category="story"
        )

        achievement_manager.register_achievement(
            id="true_ending",
            name="True Ending",
            description="Discover the true ending",
            points=100,
            hidden=True,
            category="story"
        )

        # Social achievements
        achievement_manager.register_achievement(
            id="first_friend",
            name="First Friend",
            description="Reach Friend status with any character",
            points=15,
            category="social"
        )

        achievement_manager.register_achievement(
            id="true_love",
            name="True Love",
            description="Reach maximum romance with a character",
            points=50,
            hidden=True,
            category="social"
        )

        # Progress achievements
        achievement_manager.register_progress_achievement(
            id="explorer",
            name="Explorer",
            description="Visit all locations",
            target=10,
            points=30,
            category="exploration"
        )

        achievement_manager.register_progress_achievement(
            id="social_butterfly",
            name="Social Butterfly",
            description="Have 50 conversations",
            target=50,
            points=25,
            category="social"
        )

        achievement_manager.register_progress_achievement(
            id="completionist",
            name="Completionist",
            description="Unlock all other achievements",
            target=6,
            points=100,
            category="completion"
        )

        # Challenge achievements
        achievement_manager.register_achievement(
            id="speed_runner",
            name="Speed Runner",
            description="Complete the game in under 30 minutes",
            points=50,
            hidden=True,
            category="challenge"
        )

        # Secret achievements
        achievement_manager.register_achievement(
            id="easter_egg",
            name="Easter Egg Hunter",
            description="Find the hidden easter egg",
            points=25,
            hidden=True,
            category="secret"
        )

# =============================================================================
# ACHIEVEMENT NOTIFICATION SCREEN (Toast-style)
# =============================================================================

screen achievement_notification(achievement):
#    Toast-style notification that appears when an achievement is unlocked.

    zorder 200
    modal False

    frame:
        style "achievement_toast"
        at achievement_toast_transform

        hbox:
            spacing 15

            # Achievement icon
            frame:
                style "achievement_toast_icon_frame"
                if achievement.icon:
                    add achievement.icon fit "contain"
                else:
                    text "!" style "achievement_toast_icon_text"

            vbox:
                spacing 5

                text "Achievement Unlocked!" style "achievement_toast_title"
                text achievement.name style "achievement_toast_name"
                text "+[achievement.points] points" style "achievement_toast_points"

    timer 3.0 action Hide("achievement_notification")

transform achievement_toast_transform:
    xalign 0.5
    yalign 0.0
    yoffset -100
    alpha 0.0

    # Slide in from top
    ease 0.5 yoffset 20 alpha 1.0

    # Hold
    pause 2.0

    # Fade out
    ease 0.5 alpha 0.0

# =============================================================================
# ACHIEVEMENT GALLERY SCREEN
# =============================================================================

screen achievement_gallery():
    # Full achievement gallery with categories and progress.

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
                text _("Achievements") size 36 color "#ffffff"
                textbutton _("Return") action Return() align (1.0, 0.5)

            style_prefix "achievement"

            viewport:
                scrollbars "vertical"
                mousewheel True
                xfill True
                yfill True

                vbox:
                    spacing 20

                    # Overall stats header
                    frame:
                        style "achievement_stats_frame"

                        hbox:
                            xfill True
                            spacing 30

                            vbox:
                                text "Total Progress" size 20
                                text "[achievement_manager.get_unlock_count()]/[achievement_manager.get_total_count()]" size 32

                            vbox:
                                text "Points" size 20
                                text "[achievement_manager.get_total_points()]/[achievement_manager.get_max_points()]" size 32

                            vbox:
                                text "Completion" size 20
                                text "[achievement_manager.get_completion_percent()]%" size 32

                    # Category tabs and achievements
                    for cat_id, cat_data in ACHIEVEMENT_CATEGORIES.items():
                        $ cat_achievements = achievement_manager.get_by_category(cat_id)
                        $ cat_unlocked = achievement_manager.get_unlocked_by_category(cat_id)

                        if cat_achievements:
                            frame:
                                style "achievement_category_frame"

                                vbox:
                                    spacing 10

                                    # Category header
                                    hbox:
                                        text cat_data["label"] size 28 color "#ffffff"
                                        null width 20
                                        text "([len(cat_unlocked)]/[len(cat_achievements)])" size 20 color "#888888"

                                    # Category achievements
                                    for ach in cat_achievements:
                                        if not ach.hidden or ach.unlocked:
                                            use achievement_entry(ach)

                                    # Show count of hidden achievements
                                    $ hidden_count = len([a for a in cat_achievements if a.hidden and not a.unlocked])
                                    if hidden_count > 0:
                                        text "+ [hidden_count] hidden achievement(s)" size 16 color "#666666" italic True

screen achievement_entry(achievement):
    # Single achievement entry in the gallery.

    $ entry_bg = "#333333" if achievement.unlocked else "#222222"
    $ name_color = "#ffffff" if achievement.unlocked else "#888888"
    $ points_color = "#ffcc00" if achievement.unlocked else "#555555"
    $ desc_color = "#aaaaaa" if achievement.unlocked else "#666666"

    frame:
        style "achievement_entry_frame"
        background entry_bg

        hbox:
            spacing 15

            # Achievement icon
            frame:
                xysize (60, 60)
                background "#444444"

                if achievement.unlocked and achievement.icon:
                    add achievement.icon fit "contain"
                elif achievement.unlocked:
                    text "!" align (0.5, 0.5) size 30 color "#ffcc00"
                else:
                    text "?" align (0.5, 0.5) size 30 color "#666666"

            vbox:
                spacing 5
                xfill True

                # Name and points
                hbox:
                    text achievement.get_display_name() size 20 color name_color
                    null width 15
                    text "[achievement.points] pts" size 16 color points_color

                # Description
                text achievement.get_display_description() size 14 color desc_color

                # Progress bar for progress achievements
                if isinstance(achievement, ProgressAchievement) and not achievement.unlocked:
                    hbox:
                        spacing 10
                        bar:
                            value achievement.current
                            range achievement.target
                            xsize 200
                            ysize 10
                            left_bar "#4488ff"
                            right_bar "#333333"
                        text achievement.get_progress_text() size 12 color "#888888"

                # Unlock date
                if achievement.unlocked and achievement.unlock_date:
                    $ date_str = achievement.unlock_date.strftime("%Y-%m-%d %H:%M")
                    text "Unlocked: [date_str]" size 12 color "#666666"

# =============================================================================
# STYLES FOR ACHIEVEMENT SCREENS
# =============================================================================

style achievement_toast:
    background "#1a1a2e"
    padding (20, 15)
    xminimum 300

style achievement_toast_icon_frame:
    xysize (50, 50)
    background "#2a2a4e"

style achievement_toast_icon_text:
    align (0.5, 0.5)
    size 30
    color "#ffcc00"

style achievement_toast_title:
    size 14
    color "#888888"

style achievement_toast_name:
    size 20
    color "#ffffff"

style achievement_toast_points:
    size 14
    color "#ffcc00"

style achievement_stats_frame:
    background "#2a2a2a"
    padding (25, 20)
    xfill True

style achievement_category_frame:
    background "#1a1a1a"
    padding (20, 15)
    xfill True

style achievement_entry_frame:
    xfill True
    padding (15, 12)

style achievement_vbox:
    xfill True
    spacing 10

# =============================================================================
# HELPER LABELS FOR ACHIEVEMENT OPERATIONS
# =============================================================================

# Unlock an achievement with notification
label unlock_achievement(achievement_id, notify=True):
    $ achievement_manager.unlock(achievement_id, notify)
    return

# Add progress to a progress achievement
label add_achievement_progress(achievement_id, amount=1, notify=True):
    $ achievement_manager.add_progress(achievement_id, amount, notify)
    return

# Set progress for a progress achievement
label set_achievement_progress(achievement_id, value, notify=True):
    $ achievement_manager.set_progress(achievement_id, value, notify)
    return

# Process pending notifications
label process_achievement_notifications:
    while achievement_manager.has_pending_notifications():
        $ ach = achievement_manager.get_pending_notification()
        if ach:
            show screen achievement_notification(achievement=ach)
            pause 3.5
    return

# Save achievements to persistent
label save_achievements:
    $ achievement_manager.save_to_persistent()
    return

# Load achievements from persistent
label load_achievements:
    $ achievement_manager.load_from_persistent()
    return

# =============================================================================
# INITIALIZATION
# =============================================================================

# Initialize achievements when game starts
label after_load:
    $ setup_achievements()
    $ achievement_manager.load_from_persistent()
    return

label splashscreen:
    $ setup_achievements()
    return

# =============================================================================
# EXAMPLE USAGE IN GAME SCRIPT
# =============================================================================

# Example label showing achievement system usage:
#
# label start:
#     # Unlock a simple achievement
#     call unlock_achievement("first_steps")
#
#     # Add progress to a progress achievement
#     call add_achievement_progress("explorer", 1)
#
#     # Check if an achievement is unlocked
#     $ ach = achievement_manager.get("chapter_1_complete")
#     if ach and ach.unlocked:
#         "You've already completed chapter 1!"
#
#     # Open the achievement gallery
#     call screen achievement_gallery
#
#     return

# Multiple Endings Tracker System for Ren'Py Visual Novel
# This module provides a comprehensive system for tracking, unlocking, and displaying
# multiple game endings with persistent storage, hidden endings support, and completion statistics.

init python:
    import datetime as dt

    # =========================================================================
    # ENDING CLASS - Represents a single game ending
    # =========================================================================

    class Ending:
        """
        Represents a single game ending with tracking capabilities.

        Attributes:
            id (str): Unique identifier for the ending
            name (str): Display name of the ending
            description (str): Description shown when ending is unlocked
            unlocked (bool): Whether the ending has been achieved
            unlock_date (str): ISO format date when ending was unlocked
            hidden (bool): Whether ending is hidden until unlocked
            requirements_hint (str): Hint text for how to unlock this ending
            category (str): Optional category for grouping endings
            image (str): Optional path to ending image/thumbnail
            priority (int): Display order priority (lower = first)
        """

        def __init__(self, id, name, description="", hidden=False,
                     requirements_hint="", category="main", image=None, priority=100):
            self.id = id
            self.name = name
            self.description = description
            self.unlocked = False
            self.unlock_date = None
            self.hidden = hidden
            self.requirements_hint = requirements_hint
            self.category = category
            self.image = image
            self.priority = priority

        def unlock(self):
            """
            Unlock this ending and record the unlock date.

            Returns:
                bool: True if newly unlocked, False if already unlocked
            """
            if not self.unlocked:
                self.unlocked = True
                self.unlock_date = dt.datetime.now().isoformat()
                return True
            return False

        def lock(self):
            """
            Lock this ending (mainly for testing/debugging).

            Returns:
                bool: True if was unlocked and is now locked
            """
            if self.unlocked:
                self.unlocked = False
                self.unlock_date = None
                return True
            return False

        def get_display_name(self):
            """
            Get the display name, respecting hidden status.

            Returns:
                str: The name if unlocked or not hidden, otherwise "???"
            """
            if self.unlocked or not self.hidden:
                return self.name
            return "???"

        def get_display_description(self):
            """
            Get the display description, respecting hidden/locked status.

            Returns:
                str: Full description if unlocked, hint if locked, "???" if hidden
            """
            if self.unlocked:
                return self.description
            elif self.hidden:
                return "???"
            else:
                return self.requirements_hint if self.requirements_hint else "Ending not yet unlocked."

        def to_dict(self):
            """
            Serialize ending state for persistent storage.

            Returns:
                dict: Serializable representation of ending state
            """
            return {
                "id": self.id,
                "unlocked": self.unlocked,
                "unlock_date": self.unlock_date
            }

        def from_dict(self, data):
            """
            Restore ending state from persistent storage.

            Args:
                data (dict): Previously serialized ending data
            """
            if data and data.get("id") == self.id:
                self.unlocked = data.get("unlocked", False)
                self.unlock_date = data.get("unlock_date", None)

        def __repr__(self):
            status = "Unlocked" if self.unlocked else "Locked"
            hidden_str = " (Hidden)" if self.hidden else ""
            return f"Ending({self.id}, '{self.name}', {status}{hidden_str})"

    # =========================================================================
    # ENDINGS MANAGER CLASS - Central manager for all endings
    # =========================================================================

    class EndingsManager:
        """
        Central manager for tracking and managing all game endings.

        This class provides methods to register endings, track unlock status,
        calculate completion statistics, and manage persistent storage.
        """

        def __init__(self):
            self.endings = {}
            self.categories = {}
            self._requirements_callbacks = {}

        # ---------------------------------------------------------------------
        # Ending Registration
        # ---------------------------------------------------------------------

        def register_ending(self, ending):
            """
            Register an ending with the manager.

            Args:
                ending (Ending): The ending to register

            Returns:
                Ending: The registered ending
            """
            self.endings[ending.id] = ending

            # Track categories
            if ending.category not in self.categories:
                self.categories[ending.category] = []
            if ending.id not in self.categories[ending.category]:
                self.categories[ending.category].append(ending.id)

            return ending

        def create_ending(self, id, name, description="", hidden=False,
                         requirements_hint="", category="main", image=None, priority=100):
            """
            Create and register a new ending in one step.

            Args:
                id (str): Unique identifier
                name (str): Display name
                description (str): Description when unlocked
                hidden (bool): Whether ending is hidden until unlocked
                requirements_hint (str): Hint for unlocking
                category (str): Category for grouping
                image (str): Path to ending image
                priority (int): Display order priority

            Returns:
                Ending: The newly created and registered ending
            """
            ending = Ending(
                id=id,
                name=name,
                description=description,
                hidden=hidden,
                requirements_hint=requirements_hint,
                category=category,
                image=image,
                priority=priority
            )
            return self.register_ending(ending)

        def get_ending(self, ending_id):
            """
            Get an ending by ID.

            Args:
                ending_id (str): The ending identifier

            Returns:
                Ending: The ending or None if not found
            """
            return self.endings.get(ending_id, None)

        def remove_ending(self, ending_id):
            """
            Remove an ending from the manager.

            Args:
                ending_id (str): The ending identifier

            Returns:
                bool: True if removed, False if not found
            """
            if ending_id in self.endings:
                ending = self.endings[ending_id]
                if ending.category in self.categories:
                    if ending_id in self.categories[ending.category]:
                        self.categories[ending.category].remove(ending_id)
                del self.endings[ending_id]
                return True
            return False

        # ---------------------------------------------------------------------
        # Unlock Management
        # ---------------------------------------------------------------------

        def unlock_ending(self, ending_id):
            """
            Unlock an ending by ID.

            Args:
                ending_id (str): The ending identifier

            Returns:
                bool: True if newly unlocked, False if already unlocked or not found
            """
            ending = self.get_ending(ending_id)
            if ending:
                result = ending.unlock()
                if result:
                    self._save_to_persistent()
                return result
            return False

        def lock_ending(self, ending_id):
            """
            Lock an ending (for testing/debugging).

            Args:
                ending_id (str): The ending identifier

            Returns:
                bool: True if was unlocked, False otherwise
            """
            ending = self.get_ending(ending_id)
            if ending:
                result = ending.lock()
                if result:
                    self._save_to_persistent()
                return result
            return False

        def is_ending_unlocked(self, ending_id):
            """
            Check if an ending is unlocked.

            Args:
                ending_id (str): The ending identifier

            Returns:
                bool: True if unlocked, False otherwise
            """
            ending = self.get_ending(ending_id)
            return ending.unlocked if ending else False

        # ---------------------------------------------------------------------
        # Requirements Checking
        # ---------------------------------------------------------------------

        def register_requirements(self, ending_id, callback):
            """
            Register a callback function to check ending requirements.

            The callback should return True if requirements are met.

            Args:
                ending_id (str): The ending identifier
                callback (callable): Function that returns bool
            """
            self._requirements_callbacks[ending_id] = callback

        def check_requirements(self, ending_id):
            """
            Check if requirements for an ending are met.

            Args:
                ending_id (str): The ending identifier

            Returns:
                bool: True if requirements met or no callback registered
            """
            if ending_id in self._requirements_callbacks:
                try:
                    return self._requirements_callbacks[ending_id]()
                except Exception:
                    return False
            return True

        def get_available_endings(self):
            """
            Get list of endings whose requirements are currently met but not unlocked.

            Returns:
                list: List of Ending objects available to unlock
            """
            available = []
            for ending in self.endings.values():
                if not ending.unlocked and self.check_requirements(ending.id):
                    available.append(ending)
            return available

        # ---------------------------------------------------------------------
        # Listing and Filtering
        # ---------------------------------------------------------------------

        def get_all_endings(self):
            """
            Get all registered endings sorted by priority.

            Returns:
                list: List of all Ending objects
            """
            return sorted(self.endings.values(), key=lambda e: (e.priority, e.name))

        def get_unlocked_endings(self):
            """
            Get all unlocked endings.

            Returns:
                list: List of unlocked Ending objects
            """
            return sorted(
                [e for e in self.endings.values() if e.unlocked],
                key=lambda e: (e.priority, e.name)
            )

        def get_locked_endings(self):
            """
            Get all locked endings.

            Returns:
                list: List of locked Ending objects
            """
            return sorted(
                [e for e in self.endings.values() if not e.unlocked],
                key=lambda e: (e.priority, e.name)
            )

        def get_visible_endings(self):
            """
            Get all endings that should be visible in the gallery.
            Hidden endings only show if unlocked.

            Returns:
                list: List of visible Ending objects
            """
            visible = []
            for ending in self.endings.values():
                if ending.unlocked or not ending.hidden:
                    visible.append(ending)
            return sorted(visible, key=lambda e: (e.priority, e.name))

        def get_hidden_endings(self):
            """
            Get all hidden endings (regardless of unlock status).

            Returns:
                list: List of hidden Ending objects
            """
            return sorted(
                [e for e in self.endings.values() if e.hidden],
                key=lambda e: (e.priority, e.name)
            )

        def get_endings_by_category(self, category):
            """
            Get all endings in a specific category.

            Args:
                category (str): The category name

            Returns:
                list: List of Ending objects in that category
            """
            if category not in self.categories:
                return []
            ending_ids = self.categories[category]
            endings = [self.endings[eid] for eid in ending_ids if eid in self.endings]
            return sorted(endings, key=lambda e: (e.priority, e.name))

        def get_categories(self):
            """
            Get list of all categories that have endings.

            Returns:
                list: List of category names
            """
            return list(self.categories.keys())

        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        def get_completion_percentage(self):
            """
            Calculate completion percentage across all endings.

            Returns:
                float: Percentage (0.0 to 100.0) of endings unlocked
            """
            total = len(self.endings)
            if total == 0:
                return 0.0
            unlocked = len(self.get_unlocked_endings())
            return (unlocked / total) * 100.0

        def get_category_completion(self, category):
            """
            Calculate completion percentage for a specific category.

            Args:
                category (str): The category name

            Returns:
                float: Percentage (0.0 to 100.0) of category endings unlocked
            """
            endings = self.get_endings_by_category(category)
            if not endings:
                return 0.0
            unlocked = sum(1 for e in endings if e.unlocked)
            return (unlocked / len(endings)) * 100.0

        def get_stats(self):
            """
            Get comprehensive statistics about endings.

            Returns:
                dict: Statistics including counts and percentages
            """
            total = len(self.endings)
            unlocked = len(self.get_unlocked_endings())
            hidden_total = len(self.get_hidden_endings())
            hidden_unlocked = sum(1 for e in self.get_hidden_endings() if e.unlocked)

            return {
                "total": total,
                "unlocked": unlocked,
                "locked": total - unlocked,
                "completion_percentage": self.get_completion_percentage(),
                "hidden_total": hidden_total,
                "hidden_unlocked": hidden_unlocked,
                "categories": {
                    cat: {
                        "total": len(self.get_endings_by_category(cat)),
                        "unlocked": sum(1 for e in self.get_endings_by_category(cat) if e.unlocked),
                        "percentage": self.get_category_completion(cat)
                    }
                    for cat in self.categories
                }
            }

        # ---------------------------------------------------------------------
        # Persistence
        # ---------------------------------------------------------------------

        def _save_to_persistent(self):
            """Save ending states to Ren'Py persistent storage."""
            try:
                data = {}
                for ending_id, ending in self.endings.items():
                    data[ending_id] = ending.to_dict()
                persistent.endings_data = data
            except Exception:
                # Outside of Ren'Py context (e.g., testing)
                pass

        def _load_from_persistent(self):
            """Load ending states from Ren'Py persistent storage."""
            try:
                data = persistent.endings_data
                if data:
                    for ending_id, ending in self.endings.items():
                        if ending_id in data:
                            ending.from_dict(data[ending_id])
            except Exception:
                # Outside of Ren'Py context (e.g., testing)
                pass

        def save_state(self):
            """
            Manually trigger a save to persistent storage.
            """
            self._save_to_persistent()

        def load_state(self):
            """
            Manually trigger a load from persistent storage.
            """
            self._load_from_persistent()

        def reset_all(self):
            """
            Reset all endings to locked state (for testing/new game+).

            Returns:
                int: Number of endings that were reset
            """
            count = 0
            for ending in self.endings.values():
                if ending.unlocked:
                    ending.lock()
                    count += 1
            self._save_to_persistent()
            return count

        def export_state(self):
            """
            Export all ending states for backup/transfer.

            Returns:
                dict: All ending states
            """
            return {eid: e.to_dict() for eid, e in self.endings.items()}

        def import_state(self, data):
            """
            Import ending states from backup/transfer.

            Args:
                data (dict): Previously exported ending states

            Returns:
                int: Number of endings updated
            """
            count = 0
            for ending_id, ending_data in data.items():
                if ending_id in self.endings:
                    self.endings[ending_id].from_dict(ending_data)
                    count += 1
            self._save_to_persistent()
            return count


# =============================================================================
# GLOBAL ENDINGS MANAGER INSTANCE
# =============================================================================

default endings_manager = EndingsManager()

# =============================================================================
# INITIALIZE PERSISTENT STORAGE
# =============================================================================

default persistent.endings_data = None

# =============================================================================
# EXAMPLE ENDINGS SETUP
# =============================================================================

init python:
    def setup_example_endings():
        """Initialize example endings for the system."""

        # Main story endings
        endings_manager.create_ending(
            id="true_ending",
            name="The True Path",
            description="You discovered the truth behind everything and achieved the perfect outcome.",
            hidden=False,
            requirements_hint="Uncover all secrets and make the right choices.",
            category="main",
            priority=1
        )

        endings_manager.create_ending(
            id="good_ending",
            name="A Bright Future",
            description="Though not perfect, you found happiness with those you care about.",
            hidden=False,
            requirements_hint="Maintain high relationships with key characters.",
            category="main",
            priority=2
        )

        endings_manager.create_ending(
            id="neutral_ending",
            name="Life Goes On",
            description="Neither triumph nor tragedy - simply the next chapter of your story.",
            hidden=False,
            requirements_hint="Complete the main story.",
            category="main",
            priority=3
        )

        endings_manager.create_ending(
            id="bad_ending",
            name="Bitter Conclusion",
            description="Your choices led to a difficult outcome. Perhaps another path exists...",
            hidden=False,
            requirements_hint="Sometimes failure teaches us the most.",
            category="main",
            priority=4
        )

        # Romance endings
        endings_manager.create_ending(
            id="elena_romance",
            name="Elena's Heart",
            description="You and Elena confessed your feelings and began a beautiful journey together.",
            hidden=False,
            requirements_hint="Build a strong bond with Elena and choose the romance path.",
            category="romance",
            priority=10
        )

        endings_manager.create_ending(
            id="marcus_romance",
            name="Merchant's Love",
            description="Marcus proved that his heart was worth more than all his gold.",
            hidden=False,
            requirements_hint="Earn Marcus's trust and support his dreams.",
            category="romance",
            priority=11
        )

        endings_manager.create_ending(
            id="victoria_romance",
            name="Noble Heart",
            description="Lady Victoria defied tradition for love, and you stood by her side.",
            hidden=False,
            requirements_hint="Prove yourself worthy to the noble house.",
            category="romance",
            priority=12
        )

        # Secret/Hidden endings
        endings_manager.create_ending(
            id="secret_ending",
            name="The Hidden Truth",
            description="You discovered what no one was meant to find...",
            hidden=True,
            requirements_hint="",  # No hint for hidden endings
            category="secret",
            priority=50
        )

        endings_manager.create_ending(
            id="joke_ending",
            name="Wait, What?",
            description="How did you even get here? This shouldn't be possible!",
            hidden=True,
            requirements_hint="",
            category="secret",
            priority=51
        )

        # Load any previously saved state
        endings_manager.load_state()


# =============================================================================
# UI SCREENS FOR ENDINGS GALLERY
# =============================================================================

screen endings_gallery():
    # Main endings gallery screen showing all endings and completion status.

    tag menu
    modal True

    default selected_ending = None
    default selected_category = "all"

    frame:
        xfill True
        yfill True
        background "#1a1a2e"
        padding (40, 40)

        vbox:
            spacing 15

            # Header with title and close button
            hbox:
                xfill True
                text "Endings Gallery" size 36 color "#aaaaff"
                textbutton "Return" action Return() xalign 1.0

            style_prefix "endings"

            vbox:
                spacing 15

                # Completion Statistics Header
                frame:
                    xfill True
                    padding (20, 15)
                    background "#2a2a4a"

                    hbox:
                        spacing 30
                        xalign 0.5

                        vbox:
                            xalign 0.5
                            spacing 5

                            text "Overall Completion" size 18 color "#aaaaff" xalign 0.5

                            $ completion = endings_manager.get_completion_percentage()
                            $ stats = endings_manager.get_stats()

                            hbox:
                                spacing 10
                                xalign 0.5

                                text "{:.1f}%".format(completion) size 32 color "#ffffff" bold True

                            text "{}/{} Endings Unlocked".format(stats["unlocked"], stats["total"]) size 14 color "#888899" xalign 0.5

                            # Completion bar
                            bar:
                                value completion
                                range 100.0
                                xsize 250
                                ysize 12
                                left_bar "#66ff66"
                                right_bar "#333344"
                                xalign 0.5

                # Category Filter Buttons
                hbox:
                    spacing 10
                    xalign 0.5

                    textbutton "All" action SetScreenVariable("selected_category", "all"):
                        style "endings_category_button"
                        selected selected_category == "all"

                    for category in endings_manager.get_categories():
                        $ cat_label = category.replace("_", " ").title()
                        textbutton cat_label action SetScreenVariable("selected_category", category):
                            style "endings_category_button"
                            selected selected_category == category

                null height 10

                # Endings Grid
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    ysize 400

                    vbox:
                        spacing 10
                        xfill True

                        if selected_category == "all":
                            $ display_endings = endings_manager.get_visible_endings()
                        else:
                            $ display_endings = [e for e in endings_manager.get_endings_by_category(selected_category) if e.unlocked or not e.hidden]

                        for ending in display_endings:
                            button:
                                action SetScreenVariable("selected_ending", ending)
                                xfill True
                                padding (15, 12)

                                if ending.unlocked:
                                    background "#3a4a3a"
                                    hover_background "#4a5a4a"
                                else:
                                    background "#3a3a4a"
                                    hover_background "#4a4a5a"

                                hbox:
                                    spacing 15

                                    # Unlock status icon
                                    frame:
                                        xysize (50, 50)
                                        background "#222233"

                                        if ending.unlocked:
                                            text "{color=#66ff66}[check]{/color}" align (0.5, 0.5) size 28
                                        elif ending.hidden:
                                            text "{color=#666666}?{/color}" align (0.5, 0.5) size 28
                                        else:
                                            text "{color=#ff6666}[lock]{/color}" align (0.5, 0.5) size 28

                                    vbox:
                                        spacing 4

                                        # Ending name
                                        $ name_color = "#ffffff" if ending.unlocked else "#888888"
                                        text ending.get_display_name() size 20 color name_color

                                        # Category and status
                                        hbox:
                                            spacing 15

                                            $ cat_display = ending.category.replace("_", " ").title()
                                            text cat_display size 12 color "#666688"

                                            if ending.unlocked and ending.unlock_date:
                                                $ date_display = ending.unlock_date[:10] if ending.unlock_date else ""
                                                text "Unlocked: [date_display]" size 12 color "#668866"

                                        # Brief description/hint
                                        $ brief = ending.get_display_description()
                                        if len(brief) > 80:
                                            $ brief = brief[:77] + "..."
                                        $ brief_color = "#aaaaaa" if ending.unlocked else "#666666"
                                        text brief size 14 color brief_color

                # Show hidden endings count if any exist
                $ hidden_count = len([e for e in endings_manager.get_hidden_endings() if not e.unlocked])
                if hidden_count > 0:
                    text "... and [hidden_count] hidden ending(s) to discover" size 14 color "#666666" xalign 0.5

    # Ending Detail Popup
    if selected_ending:
        use ending_detail_popup(selected_ending)


screen ending_detail_popup(ending):
    # Popup screen showing detailed information about a selected ending.

    modal True

    frame:
        align (0.5, 0.5)
        xysize (600, 450)
        padding (30, 25)
        background "#1a1a2a"

        vbox:
            spacing 20

            # Header with close button
            hbox:
                xfill True

                $ header_color = "#ffffff" if ending.unlocked else "#888888"
                text ending.get_display_name() size 28 color header_color

                textbutton "X":
                    action SetScreenVariable("selected_ending", None)
                    xalign 1.0
                    text_size 24
                    text_color "#ff6666"
                    text_hover_color "#ff9999"

            # Status and category
            hbox:
                spacing 20

                if ending.unlocked:
                    text "{color=#66ff66}UNLOCKED{/color}" size 16 bold True
                else:
                    text "{color=#ff6666}LOCKED{/color}" size 16 bold True

                $ cat_display = ending.category.replace("_", " ").title()
                text "Category: [cat_display]" size 16 color "#8888aa"

            # Unlock date if applicable
            if ending.unlocked and ending.unlock_date:
                text "Unlocked on: [ending.unlock_date[:10]]" size 14 color "#668866"

            null height 10

            # Ending image if available
            if ending.image and ending.unlocked:
                frame:
                    xalign 0.5
                    xysize (300, 150)
                    background "#222233"
                    add ending.image fit "contain" align (0.5, 0.5)
            elif ending.image and not ending.unlocked:
                frame:
                    xalign 0.5
                    xysize (300, 150)
                    background "#222233"
                    text "?" align (0.5, 0.5) size 48 color "#444455"

            null height 10

            # Description or hint
            viewport:
                ysize 120
                scrollbars "vertical"
                mousewheel True

                $ desc_color = "#cccccc" if ending.unlocked else "#888888"
                text ending.get_display_description() size 18 color desc_color

            # Close button
            textbutton "Close":
                action SetScreenVariable("selected_ending", None)
                xalign 0.5
                text_size 18
                text_color "#aaaaff"
                text_hover_color "#ccccff"


screen endings_completion_badge():
    # Small completion badge that can be shown on the main menu.

    $ stats = endings_manager.get_stats()
    $ completion = stats["completion_percentage"]

    frame:
        padding (10, 8)
        background "#2a2a4a"

        hbox:
            spacing 8

            text "Endings:" size 14 color "#aaaaaa"
            text "{}/{} ({:.0f}%)".format(stats["unlocked"], stats["total"], completion) size 14 color "#ffffff"


# =============================================================================
# STYLES FOR ENDINGS SCREENS
# =============================================================================

style endings_vbox:
    xfill True
    spacing 10

style endings_category_button:
    padding (15, 8)

style endings_category_button_text:
    size 16
    color "#888899"
    hover_color "#aaaaff"
    selected_color "#ffffff"


# =============================================================================
# HELPER LABELS FOR EASY ENDING MANAGEMENT
# =============================================================================

# Unlock an ending with notification
label unlock_ending(ending_id, notify=True):
    $ result = endings_manager.unlock_ending(ending_id)
    if result and notify:
        $ ending = endings_manager.get_ending(ending_id)
        if ending:
            $ renpy.notify("Ending Unlocked: " + ending.name)
    return

# Show the endings gallery
label show_endings_gallery:
    call screen endings_gallery
    return

# Check and potentially unlock endings based on requirements
label check_ending_requirements:
    $ available = endings_manager.get_available_endings()
    python:
        for ending in available:
            renpy.call("unlock_ending", ending.id, True)
    return


# =============================================================================
# INITIALIZATION
# =============================================================================

# Initialize endings when game starts
# Note: Call setup_example_endings() from your main after_load or splashscreen label
label endings_init:
    $ setup_example_endings()
    return


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

# Example of how to use the endings system in your game:
#
# At the end of a route:
#   call unlock_ending("good_ending")
#
# To show the gallery from a menu:
#   call screen endings_gallery
#
# To check completion in dialogue:
#   $ completion = endings_manager.get_completion_percentage()
#   if completion >= 100:
#       "Congratulations! You've seen all endings!"
#
# To register custom requirements:
#   init python:
#       def true_ending_requirements():
#           return (relationship_manager.get_character("elena").affection >= 100 and
#                   some_other_flag == True)
#       endings_manager.register_requirements("true_ending", true_ending_requirements)

# Flashback/Memory System for Ren'Py Visual Novel
# This module provides a comprehensive flashback and memory collection system with
# memory tracking, flashback sequences, memory gallery, and visual effects.

init python:
    # =========================================================================
    # MEMORY CATEGORIES - Define types of memories
    # =========================================================================

    MEMORY_CATEGORIES = {
        "story": {"label": "Story Memories", "description": "Key moments from the main narrative"},
        "character": {"label": "Character Memories", "description": "Important moments with characters"},
        "discovery": {"label": "Discoveries", "description": "Secrets and hidden revelations"},
        "achievement": {"label": "Achievements", "description": "Special accomplishments and milestones"}
    }

    # =========================================================================
    # MEMORY CLASS - Represents a single flashback memory
    # =========================================================================

    class Memory:
        """
        Represents a single flashback memory that can be collected and replayed.

        Attributes:
            id (str): Unique identifier for the memory
            name (str): Display name of the memory
            description (str): Description shown in the gallery
            label_name (str): Ren'Py label to call for flashback sequence
            unlocked (bool): Whether the memory has been unlocked
            category (str): Category for organization (story, character, discovery, achievement)
            thumbnail (str): Optional path to thumbnail image
            unlock_date (str): When the memory was unlocked (for sorting)
        """

        def __init__(self, id, name, description, label_name, unlocked=False,
                     category="story", thumbnail=None):
            self.id = id
            self.name = name
            self.description = description
            self.label_name = label_name
            self.unlocked = unlocked
            self.category = category
            self.thumbnail = thumbnail
            self.unlock_date = None

        def unlock(self):
            """Unlock this memory and record the unlock time."""
            if not self.unlocked:
                self.unlocked = True
                import time
                self.unlock_date = time.strftime("%Y-%m-%d %H:%M:%S")
                return True
            return False

        def to_dict(self):
            """Convert memory to dictionary for persistent storage."""
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "label_name": self.label_name,
                "unlocked": self.unlocked,
                "category": self.category,
                "thumbnail": self.thumbnail,
                "unlock_date": self.unlock_date
            }

        @classmethod
        def from_dict(cls, data):
            """Create a Memory instance from dictionary data."""
            memory = cls(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                label_name=data["label_name"],
                unlocked=data.get("unlocked", False),
                category=data.get("category", "story"),
                thumbnail=data.get("thumbnail")
            )
            memory.unlock_date = data.get("unlock_date")
            return memory

    # =========================================================================
    # FLASHBACK MANAGER CLASS - Central manager for all memories
    # =========================================================================

    class FlashbackManager:
        """
        Central manager for tracking all memories and flashback sequences.

        This class provides methods to register memories, unlock them,
        query by category, and manage the overall memory collection system.

        Attributes:
            memories (dict): Dictionary of Memory objects keyed by id
            _pending_unlock_notification (Memory): Memory awaiting notification display
        """

        def __init__(self):
            self.memories = {}
            self._pending_unlock_notification = None

        # ---------------------------------------------------------------------
        # Memory Registration
        # ---------------------------------------------------------------------

        def register_memory(self, memory):
            """
            Register a memory with the system.

            Args:
                memory (Memory): The Memory object to register

            Returns:
                Memory: The registered memory
            """
            self.memories[memory.id] = memory
            return memory

        def register(self, id, name, description, label_name, category="story", thumbnail=None):
            """
            Convenience method to create and register a memory in one step.

            Args:
                id (str): Unique identifier for the memory
                name (str): Display name of the memory
                description (str): Description shown in the gallery
                label_name (str): Ren'Py label to call for flashback sequence
                category (str): Category for organization
                thumbnail (str): Optional path to thumbnail image

            Returns:
                Memory: The created and registered memory
            """
            memory = Memory(
                id=id,
                name=name,
                description=description,
                label_name=label_name,
                category=category,
                thumbnail=thumbnail
            )
            return self.register_memory(memory)

        def unregister_memory(self, memory_id):
            """
            Remove a memory from the system.

            Args:
                memory_id (str): The id of the memory to remove

            Returns:
                bool: True if removed, False if not found
            """
            if memory_id in self.memories:
                del self.memories[memory_id]
                return True
            return False

        # ---------------------------------------------------------------------
        # Memory Unlocking
        # ---------------------------------------------------------------------

        def unlock_memory(self, memory_id, show_notification=True):
            """
            Unlock a specific memory.

            Args:
                memory_id (str): The id of the memory to unlock
                show_notification (bool): Whether to show unlock notification

            Returns:
                bool: True if newly unlocked, False if already unlocked or not found
            """
            memory = self.get_memory(memory_id)
            if memory:
                newly_unlocked = memory.unlock()
                if newly_unlocked:
                    # Save to persistent storage
                    self._save_to_persistent()
                    if show_notification:
                        self._pending_unlock_notification = memory
                        renpy.show_screen("memory_unlock_notification", memory=memory)
                return newly_unlocked
            return False

        def is_memory_unlocked(self, memory_id):
            """
            Check if a specific memory is unlocked.

            Args:
                memory_id (str): The id of the memory to check

            Returns:
                bool: True if unlocked, False otherwise
            """
            memory = self.get_memory(memory_id)
            if memory:
                return memory.unlocked
            return False

        # ---------------------------------------------------------------------
        # Query Methods
        # ---------------------------------------------------------------------

        def get_memory(self, memory_id):
            """
            Get a memory by its id.

            Args:
                memory_id (str): The id of the memory

            Returns:
                Memory: The memory object or None if not found
            """
            return self.memories.get(memory_id)

        def get_all_memories(self):
            """
            Get all registered memories.

            Returns:
                list: List of all Memory objects
            """
            return list(self.memories.values())

        def get_unlocked_memories(self):
            """
            Get all unlocked memories.

            Returns:
                list: List of unlocked Memory objects
            """
            return [m for m in self.memories.values() if m.unlocked]

        def get_locked_memories(self):
            """
            Get all locked memories.

            Returns:
                list: List of locked Memory objects
            """
            return [m for m in self.memories.values() if not m.unlocked]

        def get_memories_by_category(self, category):
            """
            Get all memories in a specific category.

            Args:
                category (str): The category to filter by

            Returns:
                list: List of Memory objects in the category
            """
            return [m for m in self.memories.values() if m.category == category]

        def get_unlocked_memories_by_category(self, category):
            """
            Get all unlocked memories in a specific category.

            Args:
                category (str): The category to filter by

            Returns:
                list: List of unlocked Memory objects in the category
            """
            return [m for m in self.memories.values()
                    if m.category == category and m.unlocked]

        def get_memory_count(self):
            """
            Get total and unlocked memory counts.

            Returns:
                tuple: (total_count, unlocked_count)
            """
            total = len(self.memories)
            unlocked = len(self.get_unlocked_memories())
            return total, unlocked

        def get_category_progress(self, category):
            """
            Get progress for a specific category.

            Args:
                category (str): The category to check

            Returns:
                tuple: (total_in_category, unlocked_in_category)
            """
            category_memories = self.get_memories_by_category(category)
            unlocked = [m for m in category_memories if m.unlocked]
            return len(category_memories), len(unlocked)

        def get_categories_with_counts(self):
            """
            Get all categories with their memory counts.

            Returns:
                dict: Dictionary with category info including counts
            """
            result = {}
            for cat_id, cat_info in MEMORY_CATEGORIES.items():
                total, unlocked = self.get_category_progress(cat_id)
                result[cat_id] = {
                    "label": cat_info["label"],
                    "description": cat_info["description"],
                    "total": total,
                    "unlocked": unlocked
                }
            return result

        # ---------------------------------------------------------------------
        # Flashback Playback
        # ---------------------------------------------------------------------

        def play_flashback(self, memory_id):
            """
            Play a flashback sequence for a memory.

            Args:
                memory_id (str): The id of the memory to play

            Returns:
                bool: True if flashback started, False if memory not found or locked
            """
            memory = self.get_memory(memory_id)
            if memory and memory.unlocked:
                renpy.call_in_new_context(memory.label_name)
                return True
            return False

        # ---------------------------------------------------------------------
        # Persistent Storage
        # ---------------------------------------------------------------------

        def _save_to_persistent(self):
            """Save unlocked memory states to persistent storage."""
            if persistent.unlocked_memories is None:
                persistent.unlocked_memories = {}

            for memory_id, memory in self.memories.items():
                if memory.unlocked:
                    persistent.unlocked_memories[memory_id] = {
                        "unlocked": True,
                        "unlock_date": memory.unlock_date
                    }

        def load_from_persistent(self):
            """Load unlocked memory states from persistent storage."""
            if persistent.unlocked_memories:
                for memory_id, data in persistent.unlocked_memories.items():
                    memory = self.get_memory(memory_id)
                    if memory and data.get("unlocked"):
                        memory.unlocked = True
                        memory.unlock_date = data.get("unlock_date")

        def reset_all_memories(self):
            """Reset all memories to locked state (useful for testing)."""
            for memory in self.memories.values():
                memory.unlocked = False
                memory.unlock_date = None
            persistent.unlocked_memories = {}

# =============================================================================
# GLOBAL FLASHBACK MANAGER INSTANCE
# =============================================================================

default flashback_manager = FlashbackManager()

# =============================================================================
# FLASHBACK VISUAL EFFECTS - Transforms and Transitions
# =============================================================================

# Sepia tint matrix for flashback effect
transform sepia_tint:
    matrixcolor TintMatrix("#d4a574")

# Alternative sepia using saturation adjustment
transform flashback_sepia:
    matrixcolor SaturationMatrix(0.0) * TintMatrix("#e8d4b8")

# Vignette effect overlay (requires vignette image)
transform vignette_overlay:
    alpha 0.7

# Flashback transform combining effects
transform flashback_effect:
    matrixcolor SaturationMatrix(0.3) * TintMatrix("#d4a574")
    blur 1

# Dreamy/hazy flashback effect
transform dreamy_flashback:
    matrixcolor SaturationMatrix(0.2) * TintMatrix("#c9b896")
    blur 2
    alpha 0.95

# Memory fade in effect
transform memory_fade_in:
    alpha 0.0 blur 5
    linear 1.0 alpha 1.0 blur 0

# Memory fade out effect
transform memory_fade_out:
    alpha 1.0 blur 0
    linear 0.8 alpha 0.0 blur 5

# =============================================================================
# FLASHBACK TRANSITIONS
# =============================================================================

# Standard flashback transition (dissolve with effects)
define flashback_transition = Dissolve(1.5)

# Ripple-style memory transition (if supported)
define memory_ripple = Dissolve(2.0)

# Quick flash for sudden memories
define memory_flash = Fade(0.1, 0.3, 0.5, color="#ffffff")

# Slow fade for contemplative memories
define memory_slow_fade = Fade(0.5, 0.5, 1.0, color="#000000")

# Flashback enter transition
define flashback_enter = Fade(0.3, 0.8, 0.5, color="#d4a574")

# Flashback exit transition
define flashback_exit = Fade(0.3, 0.5, 0.5, color="#d4a574")

# =============================================================================
# FLASHBACK SCREENS
# =============================================================================

# Memory unlock notification popup
screen memory_unlock_notification(memory):
    zorder 200
    modal False

    frame:
        xalign 0.5
        yalign 0.1
        padding (30, 20, 30, 20)
        background "#2a2a4eee"

        vbox:
            spacing 10
            xalign 0.5

            text "Memory Unlocked" size 28 color "#ffcc00" xalign 0.5
            text memory.name size 22 color "#ffffff" xalign 0.5
            text memory.description size 16 color "#aaaaaa" xalign 0.5

            # Category indicator
            $ cat_info = MEMORY_CATEGORIES.get(memory.category, {"label": "Unknown"})
            text "[" + cat_info["label"] + "]" size 14 color "#66aaff" xalign 0.5

    timer 3.0 action Hide("memory_unlock_notification")

# Memory Gallery Screen
screen memory_gallery():
    tag menu

    # Background
    add Solid("#1a1a2e")

    # Header
    frame:
        xalign 0.5
        ypos 20
        padding (40, 15)
        background "#2a2a4e"

        hbox:
            spacing 30
            text "Memory Gallery" size 36 color "#ffffff"

            # Progress display
            $ total, unlocked = flashback_manager.get_memory_count()
            text "Memories: [unlocked]/[total]" size 24 color "#aaaaaa" yalign 0.5

    # Category tabs
    frame:
        xalign 0.5
        ypos 90
        padding (20, 10)
        background None

        hbox:
            spacing 15

            # All memories tab
            textbutton "All" action SetScreenVariable("selected_category", None):
                style "gallery_tab_button"
                selected selected_category is None

            # Category tabs
            for cat_id, cat_info in MEMORY_CATEGORIES.items():
                $ cat_total, cat_unlocked = flashback_manager.get_category_progress(cat_id)
                textbutton "[cat_info[label]] ([cat_unlocked]/[cat_total])" action SetScreenVariable("selected_category", cat_id):
                    style "gallery_tab_button"
                    selected selected_category == cat_id

    # Memory grid
    default selected_category = None

    viewport:
        xpos 50
        ypos 150
        xsize config.screen_width - 100
        ysize config.screen_height - 250
        scrollbars "vertical"
        mousewheel True

        vbox:
            spacing 15

            # Filter memories based on selected category
            if selected_category:
                $ display_memories = flashback_manager.get_memories_by_category(selected_category)
            else:
                $ display_memories = flashback_manager.get_all_memories()

            # Sort by unlock date (unlocked first, then by date)
            $ sorted_memories = sorted(display_memories, key=lambda m: (not m.unlocked, m.unlock_date or ""))

            # Display in grid
            grid 3 (len(sorted_memories) // 3 + (1 if len(sorted_memories) % 3 else 0)):
                spacing 20
                xalign 0.5

                for memory in sorted_memories:
                    frame:
                        xysize (250, 200)
                        padding (15, 15)

                        if memory.unlocked:
                            background "#3a3a5e"
                            action Function(flashback_manager.play_flashback, memory.id)

                            vbox:
                                spacing 8

                                # Thumbnail area
                                frame:
                                    xysize (220, 100)
                                    background "#4a4a6e"
                                    if memory.thumbnail:
                                        add memory.thumbnail fit "contain" align (0.5, 0.5)
                                    else:
                                        text memory.name[0:3].upper() align (0.5, 0.5) size 30 color "#888888"

                                # Memory info
                                text memory.name size 16 color "#ffffff"
                                text memory.description size 12 color "#aaaaaa"

                        else:
                            background "#2a2a3e"

                            vbox:
                                spacing 8

                                # Locked thumbnail
                                frame:
                                    xysize (220, 100)
                                    background "#333344"
                                    text "?" align (0.5, 0.5) size 40 color "#555555"

                                # Locked indicator
                                text "???" size 16 color "#666666"
                                text "Locked" size 12 color "#555555"

                # Pad grid if needed
                for i in range((3 - len(sorted_memories) % 3) % 3):
                    null

    # Back button
    textbutton "Back" action Return():
        xalign 0.5
        yalign 0.95
        style "gallery_back_button"

# =============================================================================
# GALLERY SCREEN STYLES
# =============================================================================

style gallery_tab_button:
    background "#333355"
    hover_background "#4444aa"
    selected_background "#5555cc"
    padding (15, 8, 15, 8)

style gallery_tab_button_text:
    color "#aaaaaa"
    hover_color "#ffffff"
    selected_color "#ffffff"
    size 18

style gallery_back_button:
    background "#333355"
    hover_background "#4444aa"
    padding (30, 10, 30, 10)

style gallery_back_button_text:
    color "#ffffff"
    size 20

# =============================================================================
# FLASHBACK SEQUENCE WRAPPER SCREEN
# =============================================================================

# Overlay screen that applies flashback visual effects
screen flashback_overlay():
    zorder 50

    # Vignette effect frame
    frame:
        xfill True
        yfill True
        background Solid("#00000000")

        # Corner vignettes using gradients
        add Solid("#00000088"):
            xsize 200
            ysize 200
            pos (0, 0)

        add Solid("#00000088"):
            xsize 200
            ysize 200
            xpos config.screen_width - 200
            ypos 0

        add Solid("#00000088"):
            xsize 200
            ysize 200
            xpos 0
            ypos config.screen_height - 200

        add Solid("#00000088"):
            xsize 200
            ysize 200
            xpos config.screen_width - 200
            ypos config.screen_height - 200

    # Flashback indicator
    frame:
        xalign 1.0
        yalign 0.0
        xoffset -20
        yoffset 20
        padding (15, 8)
        background "#d4a57488"

        text "Memory" size 18 color "#ffffff"

# =============================================================================
# HELPER LABELS FOR FLASHBACK CONTROL
# =============================================================================

# Start a flashback sequence with visual effects
label start_flashback(memory_id=None):
    # Apply transition
    with flashback_enter

    # Show flashback overlay
    show screen flashback_overlay

    # Apply sepia effect to scene
    scene expression Solid("#d4a574") at flashback_effect

    if memory_id:
        $ flashback_manager.unlock_memory(memory_id, show_notification=False)

    return

# End a flashback sequence
label end_flashback:
    # Hide overlay
    hide screen flashback_overlay

    # Transition back
    with flashback_exit

    return

# Trigger a specific memory flashback from normal gameplay
label trigger_flashback(memory_id):
    # Get the memory
    $ memory = flashback_manager.get_memory(memory_id)

    if memory:
        # Unlock if not already
        $ flashback_manager.unlock_memory(memory_id, show_notification=True)

        # Wait for notification to show
        pause 2.0

        # Hide notification
        hide screen memory_unlock_notification

        # Play the flashback
        call start_flashback
        call expression memory.label_name from _call_flashback_label
        call end_flashback
    else:
        "Memory not found: [memory_id]"

    return

# Quick unlock without playing (for story progression)
label unlock_memory(memory_id, show_notification=True):
    $ flashback_manager.unlock_memory(memory_id, show_notification)
    if show_notification:
        pause 2.5
        hide screen memory_unlock_notification
    return

# Replay a memory from the gallery (plays in new context)
label replay_memory(memory_id):
    $ flashback_manager.play_flashback(memory_id)
    return

# =============================================================================
# EXAMPLE MEMORY DEFINITIONS
# =============================================================================

init python:
    def setup_example_memories():
        """Initialize example memories for the flashback system."""

        # Story memories
        flashback_manager.register(
            id="first_meeting",
            name="The First Encounter",
            description="The day everything changed...",
            label_name="flashback_first_meeting",
            category="story"
        )

        flashback_manager.register(
            id="hidden_truth",
            name="Hidden Truth",
            description="The secret was finally revealed.",
            label_name="flashback_hidden_truth",
            category="story"
        )

        # Character memories
        flashback_manager.register(
            id="elena_childhood",
            name="Elena's Childhood",
            description="A glimpse into Elena's past.",
            label_name="flashback_elena_childhood",
            category="character"
        )

        flashback_manager.register(
            id="marcus_secret",
            name="Marcus's Burden",
            description="The weight he's been carrying.",
            label_name="flashback_marcus_secret",
            category="character"
        )

        # Discovery memories
        flashback_manager.register(
            id="ancient_ruins",
            name="Ancient Ruins",
            description="What lies beneath the old temple.",
            label_name="flashback_ancient_ruins",
            category="discovery"
        )

        # Achievement memories
        flashback_manager.register(
            id="hero_moment",
            name="A Hero's Choice",
            description="When you proved your worth.",
            label_name="flashback_hero_moment",
            category="achievement"
        )

        # Load persistent data
        flashback_manager.load_from_persistent()

# Initialize memories when game starts
label setup_memories:
    $ setup_example_memories()
    return

# =============================================================================
# EXAMPLE FLASHBACK SEQUENCES
# =============================================================================

label flashback_first_meeting:
    scene bg forest at flashback_effect
    with flashback_transition

    "The forest was dense that day..."
    "Little did I know what awaited me beyond those trees."
    "A chance encounter that would change everything."

    return

label flashback_hidden_truth:
    scene bg study at flashback_effect
    with flashback_transition

    "The documents lay scattered across the desk..."
    "Each one revealing a piece of the puzzle."
    "The truth had been hidden in plain sight all along."

    return

label flashback_elena_childhood:
    scene bg village at flashback_effect
    with flashback_transition

    "The village was smaller back then..."
    "Elena ran through the cobblestone streets, carefree."
    "Before the weight of responsibility found her."

    return

label flashback_marcus_secret:
    scene bg night_sky at flashback_effect
    with flashback_transition

    "He stood alone under the stars..."
    "The burden of his family's legacy pressing down."
    "Some secrets are too heavy to share."

    return

label flashback_ancient_ruins:
    scene bg ruins at flashback_effect
    with flashback_transition

    "The ruins had been forgotten by time..."
    "But the inscriptions on the walls told stories."
    "Stories of power, betrayal, and ancient magic."

    return

label flashback_hero_moment:
    scene bg battlefield at flashback_effect
    with flashback_transition

    "The moment of truth had arrived..."
    "Everyone was counting on your choice."
    "And you rose to the occasion."

    return

# =============================================================================
# INTEGRATION WITH MAIN MENU (Optional)
# =============================================================================

# Add to main menu or extras menu to access memory gallery
# Example:
#     textbutton _("Memories") action ShowMenu("memory_gallery")

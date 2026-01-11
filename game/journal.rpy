# journal.rpy
# Journal/Codex System for tracking lore, characters, locations, items, and clues
# Provides persistent unlock tracking, notifications, and search functionality

# ============================================================================
# DATA CLASSES AND MANAGER
# ============================================================================

init python:
    from datetime import datetime
    from typing import Optional, List, Dict, Any

    class JournalCategory:
        """Enumeration of journal entry categories."""
        LORE = "Lore"
        CHARACTERS = "Characters"
        LOCATIONS = "Locations"
        ITEMS = "Items"
        CLUES = "Clues"

        @classmethod
        def all(cls) -> List[str]:
            """Return all category names."""
            return [cls.LORE, cls.CHARACTERS, cls.LOCATIONS, cls.ITEMS, cls.CLUES]


    class JournalEntry:
        """
        Represents a single journal entry.

        Attributes:
            id: Unique identifier for the entry
            title: Display title
            content: Full text content of the entry
            category: One of the JournalCategory values
            unlocked: Whether the entry has been discovered
            read: Whether the entry has been viewed after unlocking
            unlock_date: When the entry was unlocked (None if locked)
        """

        def __init__(
            self,
            id: str,
            title: str,
            content: str,
            category: str,
            unlocked: bool = False,
            read: bool = False,
            unlock_date: Optional[str] = None
        ):
            self.id = id
            self.title = title
            self.content = content
            self.category = category
            self.unlocked = unlocked
            self.read = read
            self.unlock_date = unlock_date

            # Validate category
            if category not in JournalCategory.all():
                raise ValueError(f"Invalid category: {category}. Must be one of {JournalCategory.all()}")

        def unlock(self) -> bool:
            """
            Unlock this entry if not already unlocked.

            Returns:
                True if entry was newly unlocked, False if already unlocked
            """
            if self.unlocked:
                return False
            self.unlocked = True
            self.unlock_date = datetime.now().isoformat()
            return True

        def mark_read(self) -> bool:
            """
            Mark this entry as read.

            Returns:
                True if status changed, False if already read or not unlocked
            """
            if not self.unlocked or self.read:
                return False
            self.read = True
            return True

        def to_dict(self) -> Dict[str, Any]:
            """Convert entry to dictionary for serialization."""
            return {
                "id": self.id,
                "title": self.title,
                "content": self.content,
                "category": self.category,
                "unlocked": self.unlocked,
                "read": self.read,
                "unlock_date": self.unlock_date
            }

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "JournalEntry":
            """Create entry from dictionary."""
            return cls(
                id=data["id"],
                title=data["title"],
                content=data["content"],
                category=data["category"],
                unlocked=data.get("unlocked", False),
                read=data.get("read", False),
                unlock_date=data.get("unlock_date")
            )

        def __repr__(self) -> str:
            status = "unlocked" if self.unlocked else "locked"
            read_status = ", read" if self.read else ", unread" if self.unlocked else ""
            return f"JournalEntry({self.id!r}, {self.title!r}, {self.category}, {status}{read_status})"


    class JournalManager:
        """
        Manages all journal entries.

        Provides registration, unlock tracking, filtering, and search functionality.
        Uses persistent storage for unlock/read states across game sessions.
        """

        def __init__(self):
            self._entries: Dict[str, JournalEntry] = {}
            self._pending_notifications: List[str] = []
            self._load_persistent_state()

        def _load_persistent_state(self) -> None:
            """Load unlock/read states from persistent storage."""
            if persistent.journal_states is None:
                persistent.journal_states = {}

        def _save_entry_state(self, entry: JournalEntry) -> None:
            """Save an entry's unlock/read state to persistent storage."""
            persistent.journal_states[entry.id] = {
                "unlocked": entry.unlocked,
                "read": entry.read,
                "unlock_date": entry.unlock_date
            }

        def _apply_persistent_state(self, entry: JournalEntry) -> None:
            """Apply saved state to an entry if it exists."""
            if persistent.journal_states and entry.id in persistent.journal_states:
                state = persistent.journal_states[entry.id]
                entry.unlocked = state.get("unlocked", False)
                entry.read = state.get("read", False)
                entry.unlock_date = state.get("unlock_date")

        def register_entry(
            self,
            id: str,
            title: str,
            content: str,
            category: str,
            unlocked: bool = False
        ) -> JournalEntry:
            """
            Register a new journal entry.

            Args:
                id: Unique identifier
                title: Display title
                content: Entry content
                category: One of JournalCategory values
                unlocked: Initial unlock state (default False)

            Returns:
                The created JournalEntry

            Raises:
                ValueError: If id already exists or category is invalid
            """
            if id in self._entries:
                raise ValueError(f"Entry with id '{id}' already registered")

            entry = JournalEntry(
                id=id,
                title=title,
                content=content,
                category=category,
                unlocked=unlocked
            )

            # Apply any saved persistent state
            self._apply_persistent_state(entry)

            self._entries[id] = entry
            return entry

        def get_entry(self, id: str) -> Optional[JournalEntry]:
            """Get an entry by ID."""
            return self._entries.get(id)

        def unlock_entry(self, id: str, show_notification: bool = True) -> bool:
            """
            Unlock an entry by ID.

            Args:
                id: The entry ID to unlock
                show_notification: Whether to queue a notification

            Returns:
                True if entry was newly unlocked, False if already unlocked or not found
            """
            entry = self._entries.get(id)
            if entry is None:
                return False

            newly_unlocked = entry.unlock()
            if newly_unlocked:
                self._save_entry_state(entry)
                if show_notification:
                    self._pending_notifications.append(id)

            return newly_unlocked

        def mark_read(self, id: str) -> bool:
            """
            Mark an entry as read.

            Args:
                id: The entry ID to mark as read

            Returns:
                True if status changed, False otherwise
            """
            entry = self._entries.get(id)
            if entry is None:
                return False

            changed = entry.mark_read()
            if changed:
                self._save_entry_state(entry)

            return changed

        def get_entries_by_category(
            self,
            category: str,
            unlocked_only: bool = True
        ) -> List[JournalEntry]:
            """
            Get all entries in a category.

            Args:
                category: Category to filter by
                unlocked_only: If True, only return unlocked entries

            Returns:
                List of matching entries, sorted by title
            """
            entries = [
                e for e in self._entries.values()
                if e.category == category and (not unlocked_only or e.unlocked)
            ]
            return sorted(entries, key=lambda e: e.title)

        def get_all_entries(self, unlocked_only: bool = True) -> List[JournalEntry]:
            """
            Get all entries.

            Args:
                unlocked_only: If True, only return unlocked entries

            Returns:
                List of entries, sorted by category then title
            """
            entries = [
                e for e in self._entries.values()
                if not unlocked_only or e.unlocked
            ]
            return sorted(entries, key=lambda e: (e.category, e.title))

        def get_unread_count(self, category: Optional[str] = None) -> int:
            """
            Get count of unread (but unlocked) entries.

            Args:
                category: If provided, only count entries in this category

            Returns:
                Number of unread entries
            """
            entries = self._entries.values()
            if category:
                entries = [e for e in entries if e.category == category]
            return sum(1 for e in entries if e.unlocked and not e.read)

        def get_unlocked_count(self, category: Optional[str] = None) -> int:
            """
            Get count of unlocked entries.

            Args:
                category: If provided, only count entries in this category

            Returns:
                Number of unlocked entries
            """
            entries = self._entries.values()
            if category:
                entries = [e for e in entries if e.category == category]
            return sum(1 for e in entries if e.unlocked)

        def get_total_count(self, category: Optional[str] = None) -> int:
            """
            Get total count of entries.

            Args:
                category: If provided, only count entries in this category

            Returns:
                Total number of entries
            """
            if category:
                return sum(1 for e in self._entries.values() if e.category == category)
            return len(self._entries)

        def search(
            self,
            query: str,
            unlocked_only: bool = True,
            search_content: bool = True
        ) -> List[JournalEntry]:
            """
            Search entries by title and optionally content.

            Args:
                query: Search string (case-insensitive)
                unlocked_only: If True, only search unlocked entries
                search_content: If True, also search entry content

            Returns:
                List of matching entries, sorted by title
            """
            query_lower = query.lower()
            results = []

            for entry in self._entries.values():
                if unlocked_only and not entry.unlocked:
                    continue

                title_match = query_lower in entry.title.lower()
                content_match = search_content and query_lower in entry.content.lower()

                if title_match or content_match:
                    results.append(entry)

            return sorted(results, key=lambda e: e.title)

        def has_pending_notifications(self) -> bool:
            """Check if there are pending new entry notifications."""
            return len(self._pending_notifications) > 0

        def get_pending_notifications(self) -> List[JournalEntry]:
            """Get entries with pending notifications."""
            return [
                self._entries[id]
                for id in self._pending_notifications
                if id in self._entries
            ]

        def clear_notifications(self) -> None:
            """Clear all pending notifications."""
            self._pending_notifications.clear()

        def pop_notification(self) -> Optional[JournalEntry]:
            """
            Pop and return the oldest pending notification.

            Returns:
                The entry with the notification, or None if no notifications
            """
            if not self._pending_notifications:
                return None

            entry_id = self._pending_notifications.pop(0)
            return self._entries.get(entry_id)

        def reset_all(self) -> None:
            """Reset all entries to locked/unread state (for testing/new game)."""
            for entry in self._entries.values():
                entry.unlocked = False
                entry.read = False
                entry.unlock_date = None
            persistent.journal_states = {}
            self._pending_notifications.clear()


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

default journal_manager = JournalManager()

# Track current viewing state for UI
default journal_current_category = "Lore"
default journal_current_entry = None
default journal_search_query = ""


# ============================================================================
# UI SCREENS
# ============================================================================

# Style definitions for journal UI
style journal_frame:
    background Solid("#1a1a2eee")
    padding (20, 20, 20, 20)

style journal_title:
    color "#ffcc66"
    size 36
    xalign 0.5

style journal_category_button:
    background Solid("#2a2a4e")
    hover_background Solid("#3a3a6e")
    selected_background Solid("#4a4a8e")
    padding (15, 8, 15, 8)
    xsize 140

style journal_category_button_text:
    color "#aaaacc"
    hover_color "#ffffff"
    selected_color "#ffcc66"
    size 16
    xalign 0.5

style journal_entry_button:
    background Solid("#252545")
    hover_background Solid("#353565")
    padding (15, 10, 15, 10)
    xfill True

style journal_entry_button_text:
    color "#ccccee"
    hover_color "#ffffff"
    size 18

style journal_content_text:
    color "#ddddee"
    size 18
    line_spacing 6

style journal_unread_indicator:
    color "#66ff66"
    size 14

style journal_search_input:
    color "#ffffff"
    size 18


# Main Journal Screen
screen journal_screen():
    tag menu
    modal True

    add Solid("#000000cc")

    frame:
        style "journal_frame"
        xalign 0.5
        yalign 0.5
        xsize 1000
        ysize 700

        vbox:
            spacing 15

            # Header
            hbox:
                xfill True

                text "Journal" style "journal_title"

                textbutton "X":
                    xalign 1.0
                    action Hide("journal_screen")
                    text_color "#ff6666"
                    text_hover_color "#ff9999"
                    text_size 24

            # Search bar
            hbox:
                spacing 10
                xalign 0.5

                text "Search:" color "#aaaacc" yalign 0.5 size 16

                input:
                    value VariableInputValue("journal_search_query")
                    style "journal_search_input"
                    pixel_width 300
                    length 50

                if journal_search_query:
                    textbutton "Clear":
                        action SetVariable("journal_search_query", "")
                        text_color "#ff9966"
                        text_hover_color "#ffcc99"
                        text_size 14

            # Category tabs
            hbox:
                spacing 5
                xalign 0.5

                for category in ["Lore", "Characters", "Locations", "Items", "Clues"]:
                    python:
                        unread = journal_manager.get_unread_count(category)
                        unlocked = journal_manager.get_unlocked_count(category)
                        total = journal_manager.get_total_count(category)

                    textbutton "{} ({}/{})".format(category, unlocked, total):
                        style "journal_category_button"
                        action [
                            SetVariable("journal_current_category", category),
                            SetVariable("journal_current_entry", None)
                        ]
                        selected (journal_current_category == category)

                        # Show unread indicator
                        if unread > 0:
                            foreground Text(" [{}]".format(unread), color="#66ff66", size=12, xalign=1.0, yalign=0.0)

            null height 10

            # Content area
            hbox:
                spacing 15
                xfill True
                yfill True

                # Entry list
                frame:
                    background Solid("#15152a")
                    xsize 300
                    yfill True
                    padding (10, 10, 10, 10)

                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        draggable True

                        vbox:
                            spacing 5

                            python:
                                if journal_search_query:
                                    display_entries = journal_manager.search(journal_search_query)
                                else:
                                    display_entries = journal_manager.get_entries_by_category(journal_current_category)

                            if not display_entries:
                                if journal_search_query:
                                    text "No entries found." color "#888888" italic True
                                else:
                                    text "No entries discovered yet." color "#888888" italic True

                            for entry in display_entries:
                                hbox:
                                    spacing 5
                                    xfill True

                                    # Unread indicator
                                    if not entry.read:
                                        text "*" style "journal_unread_indicator" yalign 0.5
                                    else:
                                        text " " size 14 yalign 0.5

                                    textbutton entry.title:
                                        style "journal_entry_button"
                                        action [
                                            SetVariable("journal_current_entry", entry.id),
                                            Function(journal_manager.mark_read, entry.id)
                                        ]
                                        selected (journal_current_entry == entry.id)

                # Entry detail
                frame:
                    background Solid("#15152a")
                    xfill True
                    yfill True
                    padding (20, 15, 20, 15)

                    if journal_current_entry:
                        python:
                            current = journal_manager.get_entry(journal_current_entry)

                        if current:
                            vbox:
                                spacing 15

                                text current.title color "#ffcc66" size 24

                                hbox:
                                    spacing 20
                                    text "Category: [current.category]" color "#888899" size 14
                                    if current.unlock_date:
                                        text "Discovered: [current.unlock_date[:10]]" color "#888899" size 14

                                null height 5

                                viewport:
                                    scrollbars "vertical"
                                    mousewheel True
                                    draggable True
                                    yfill True

                                    text current.content style "journal_content_text"
                    else:
                        text "Select an entry to view details." color "#666677" italic True xalign 0.5 yalign 0.5


# New Entry Notification Screen
screen journal_notification(entry):
    zorder 200
    modal False

    frame:
        xalign 1.0
        yalign 0.0
        xoffset -20
        yoffset 20
        background Solid("#2a4a2acc")
        padding (20, 15, 20, 15)

        hbox:
            spacing 15

            vbox:
                text "New Journal Entry!" color "#88ff88" size 16
                text entry.title color "#ffffff" size 20
                text "Category: [entry.category]" color "#aaccaa" size 14

            textbutton "View":
                action [
                    Hide("journal_notification"),
                    SetVariable("journal_current_category", entry.category),
                    SetVariable("journal_current_entry", entry.id),
                    Function(journal_manager.mark_read, entry.id),
                    Show("journal_screen")
                ]
                text_color "#88ff88"
                text_hover_color "#aaffaa"

            textbutton "X":
                action Hide("journal_notification")
                text_color "#ff8888"
                text_hover_color "#ffaaaa"

    # Auto-hide after 5 seconds
    timer 5.0 action Hide("journal_notification")


# Compact notification for multiple entries
screen journal_notification_badge():
    zorder 150

    python:
        unread_total = journal_manager.get_unread_count()

    if unread_total > 0:
        frame:
            xalign 1.0
            yalign 0.0
            xoffset -10
            yoffset 10
            background Solid("#4a2a4acc")
            padding (10, 5, 10, 5)

            textbutton "Journal ([unread_total] new)":
                action Show("journal_screen")
                text_color "#ffcc66"
                text_hover_color "#ffee88"
                text_size 14


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

init python:
    def show_journal_notification(entry_id: str) -> None:
        """
        Show a notification for a newly unlocked entry.

        Call this after unlocking an entry to display the popup.
        """
        entry = journal_manager.get_entry(entry_id)
        if entry and entry.unlocked:
            renpy.show_screen("journal_notification", entry=entry)

    def unlock_journal_entry(entry_id: str, notify: bool = True) -> bool:
        """
        Unlock a journal entry and optionally show notification.

        Args:
            entry_id: The entry ID to unlock
            notify: Whether to show the notification popup

        Returns:
            True if entry was newly unlocked
        """
        newly_unlocked = journal_manager.unlock_entry(entry_id, show_notification=notify)
        if newly_unlocked and notify:
            show_journal_notification(entry_id)
        return newly_unlocked


# ============================================================================
# EXAMPLE ENTRIES (for demonstration/testing)
# ============================================================================

init python:
    # Register some example entries - these would normally be defined elsewhere
    # and unlocked during gameplay

    def setup_example_journal_entries():
        """Set up example journal entries for demonstration."""

        # Lore entries
        journal_manager.register_entry(
            id="lore_world_history",
            title="World History",
            content="The world was created long ago by ancient beings. Their influence can still be felt in the magical artifacts scattered across the land.\n\nLegends speak of a great cataclysm that reshaped the continents and gave rise to the current age of humanity.",
            category="Lore"
        )

        journal_manager.register_entry(
            id="lore_magic_system",
            title="The Art of Magic",
            content="Magic flows through all living things, though few can harness its power. Practitioners must train for years to master even basic spells.\n\nThere are five schools of magic: Fire, Water, Earth, Air, and Spirit. Each has its own strengths and weaknesses.",
            category="Lore"
        )

        # Character entries
        journal_manager.register_entry(
            id="char_protagonist",
            title="The Protagonist",
            content="A young adventurer seeking answers about their mysterious past. They possess an unusual affinity for magic that has drawn the attention of powerful forces.",
            category="Characters"
        )

        journal_manager.register_entry(
            id="char_mentor",
            title="The Mentor",
            content="An elderly sage who guides the protagonist on their journey. They seem to know more about the protagonist's origins than they let on.",
            category="Characters"
        )

        # Location entries
        journal_manager.register_entry(
            id="loc_starting_village",
            title="Willowbrook Village",
            content="A peaceful farming village nestled in a verdant valley. The protagonist grew up here, though they always felt like they didn't quite belong.\n\nNotable locations:\n- The Old Mill\n- Elder's House\n- The Wandering Merchant's Shop",
            category="Locations"
        )

        journal_manager.register_entry(
            id="loc_ancient_ruins",
            title="The Ancient Ruins",
            content="Crumbling remnants of a civilization long forgotten. Strange symbols cover the walls, and an eerie energy permeates the air.\n\nDanger Level: High\nRecommended: Bring torches and protective charms.",
            category="Locations"
        )

        # Item entries
        journal_manager.register_entry(
            id="item_mysterious_amulet",
            title="Mysterious Amulet",
            content="A strange amulet found in the protagonist's belongings since childhood. Its origin is unknown, but it occasionally glows with an inner light.\n\nProperties:\n- Unknown magical properties\n- Resistant to damage\n- Warm to the touch",
            category="Items"
        )

        journal_manager.register_entry(
            id="item_ancient_map",
            title="Ancient Map",
            content="A weathered map showing locations that don't match any modern geography. Some symbols seem to indicate hidden treasures or dangers.",
            category="Items"
        )

        # Clue entries
        journal_manager.register_entry(
            id="clue_strange_dreams",
            title="Strange Dreams",
            content="The protagonist has been having recurring dreams of a vast library filled with glowing books. A hooded figure always appears, beckoning them deeper.",
            category="Clues"
        )

        journal_manager.register_entry(
            id="clue_missing_villagers",
            title="Missing Villagers",
            content="Several villagers have gone missing in recent weeks. All disappearances occurred on moonless nights, and strange tracks were found near the forest edge.",
            category="Clues"
        )


# ============================================================================
# GAME INTEGRATION
# ============================================================================

# Add journal button to quick menu
screen journal_quick_button():
    zorder 100

    python:
        unread = journal_manager.get_unread_count()

    frame:
        xalign 1.0
        yalign 1.0
        xoffset -10
        yoffset -50
        background Solid("#2a2a4ecc")
        padding (10, 5, 10, 5)

        hbox:
            spacing 5

            textbutton "Journal":
                action Show("journal_screen")
                text_color "#aaaacc"
                text_hover_color "#ffffff"
                text_size 16

            if unread > 0:
                text "([unread])" color "#66ff66" size 14 yalign 0.5

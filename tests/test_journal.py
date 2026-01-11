"""
Tests for the Journal/Codex system.

Tests cover:
- JournalCategory enumeration
- JournalEntry class functionality
- JournalManager operations including:
  - Entry registration
  - Unlock/read tracking
  - Category filtering
  - Search functionality
  - Notification system
  - Persistent state management
"""
import pytest
from pathlib import Path


@pytest.fixture
def journal_classes(load_system):
    """Load journal system classes."""
    return load_system("journal")


@pytest.fixture
def JournalCategory(journal_classes):
    """Get JournalCategory class."""
    return journal_classes["JournalCategory"]


@pytest.fixture
def JournalEntry(journal_classes):
    """Get JournalEntry class."""
    return journal_classes["JournalEntry"]


@pytest.fixture
def JournalManager(journal_classes):
    """Get JournalManager class."""
    return journal_classes["JournalManager"]


@pytest.fixture
def manager(JournalManager):
    """Create a fresh JournalManager instance."""
    return JournalManager()


# ============================================================================
# JournalCategory Tests
# ============================================================================

class TestJournalCategory:
    """Tests for JournalCategory enumeration."""

    def test_category_values(self, JournalCategory):
        """Test that all expected categories are defined."""
        assert JournalCategory.LORE == "Lore"
        assert JournalCategory.CHARACTERS == "Characters"
        assert JournalCategory.LOCATIONS == "Locations"
        assert JournalCategory.ITEMS == "Items"
        assert JournalCategory.CLUES == "Clues"

    def test_all_categories(self, JournalCategory):
        """Test that all() returns all category names."""
        all_categories = JournalCategory.all()
        assert len(all_categories) == 5
        assert "Lore" in all_categories
        assert "Characters" in all_categories
        assert "Locations" in all_categories
        assert "Items" in all_categories
        assert "Clues" in all_categories


# ============================================================================
# JournalEntry Tests
# ============================================================================

class TestJournalEntry:
    """Tests for JournalEntry class."""

    def test_entry_creation(self, JournalEntry):
        """Test basic entry creation."""
        entry = JournalEntry(
            id="test_entry",
            title="Test Title",
            content="Test content here.",
            category="Lore"
        )

        assert entry.id == "test_entry"
        assert entry.title == "Test Title"
        assert entry.content == "Test content here."
        assert entry.category == "Lore"
        assert entry.unlocked is False
        assert entry.read is False
        assert entry.unlock_date is None

    def test_entry_creation_unlocked(self, JournalEntry):
        """Test entry creation with unlocked state."""
        entry = JournalEntry(
            id="test_entry",
            title="Test",
            content="Content",
            category="Characters",
            unlocked=True
        )

        assert entry.unlocked is True
        assert entry.read is False

    def test_entry_invalid_category(self, JournalEntry):
        """Test that invalid category raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            JournalEntry(
                id="test",
                title="Test",
                content="Content",
                category="InvalidCategory"
            )

        assert "Invalid category" in str(exc_info.value)

    def test_entry_unlock(self, JournalEntry):
        """Test unlocking an entry."""
        entry = JournalEntry(
            id="test",
            title="Test",
            content="Content",
            category="Items"
        )

        assert entry.unlocked is False
        result = entry.unlock()

        assert result is True
        assert entry.unlocked is True
        assert entry.unlock_date is not None

    def test_entry_unlock_already_unlocked(self, JournalEntry):
        """Test that unlocking an already unlocked entry returns False."""
        entry = JournalEntry(
            id="test",
            title="Test",
            content="Content",
            category="Items",
            unlocked=True
        )

        result = entry.unlock()
        assert result is False

    def test_entry_mark_read(self, JournalEntry):
        """Test marking an entry as read."""
        entry = JournalEntry(
            id="test",
            title="Test",
            content="Content",
            category="Clues",
            unlocked=True
        )

        assert entry.read is False
        result = entry.mark_read()

        assert result is True
        assert entry.read is True

    def test_entry_mark_read_locked(self, JournalEntry):
        """Test that marking a locked entry as read returns False."""
        entry = JournalEntry(
            id="test",
            title="Test",
            content="Content",
            category="Clues"
        )

        result = entry.mark_read()
        assert result is False
        assert entry.read is False

    def test_entry_mark_read_already_read(self, JournalEntry):
        """Test that marking an already read entry returns False."""
        entry = JournalEntry(
            id="test",
            title="Test",
            content="Content",
            category="Clues",
            unlocked=True,
            read=True
        )

        result = entry.mark_read()
        assert result is False

    def test_entry_to_dict(self, JournalEntry):
        """Test serialization to dictionary."""
        entry = JournalEntry(
            id="test",
            title="Test Title",
            content="Test Content",
            category="Lore",
            unlocked=True,
            read=True,
            unlock_date="2024-01-15T10:30:00"
        )

        data = entry.to_dict()

        assert data["id"] == "test"
        assert data["title"] == "Test Title"
        assert data["content"] == "Test Content"
        assert data["category"] == "Lore"
        assert data["unlocked"] is True
        assert data["read"] is True
        assert data["unlock_date"] == "2024-01-15T10:30:00"

    def test_entry_from_dict(self, JournalEntry):
        """Test deserialization from dictionary."""
        data = {
            "id": "test",
            "title": "Test Title",
            "content": "Test Content",
            "category": "Locations",
            "unlocked": True,
            "read": False,
            "unlock_date": "2024-01-15T10:30:00"
        }

        entry = JournalEntry.from_dict(data)

        assert entry.id == "test"
        assert entry.title == "Test Title"
        assert entry.content == "Test Content"
        assert entry.category == "Locations"
        assert entry.unlocked is True
        assert entry.read is False
        assert entry.unlock_date == "2024-01-15T10:30:00"

    def test_entry_repr(self, JournalEntry):
        """Test string representation."""
        entry = JournalEntry(
            id="test",
            title="Test",
            content="Content",
            category="Items"
        )

        repr_str = repr(entry)
        assert "test" in repr_str
        assert "Test" in repr_str
        assert "Items" in repr_str
        assert "locked" in repr_str

    def test_entry_repr_unlocked_unread(self, JournalEntry):
        """Test string representation for unlocked but unread entry."""
        entry = JournalEntry(
            id="test",
            title="Test",
            content="Content",
            category="Items",
            unlocked=True
        )

        repr_str = repr(entry)
        assert "unlocked" in repr_str
        assert "unread" in repr_str

    def test_entry_repr_read(self, JournalEntry):
        """Test string representation for read entry."""
        entry = JournalEntry(
            id="test",
            title="Test",
            content="Content",
            category="Items",
            unlocked=True,
            read=True
        )

        repr_str = repr(entry)
        assert "unlocked" in repr_str
        assert ", read" in repr_str


# ============================================================================
# JournalManager Registration Tests
# ============================================================================

class TestJournalManagerRegistration:
    """Tests for JournalManager entry registration."""

    def test_register_entry(self, manager):
        """Test basic entry registration."""
        entry = manager.register_entry(
            id="test_entry",
            title="Test Title",
            content="Test content",
            category="Lore"
        )

        assert entry is not None
        assert entry.id == "test_entry"
        assert entry.title == "Test Title"
        assert entry.unlocked is False

    def test_register_entry_unlocked(self, manager):
        """Test registering an already unlocked entry."""
        entry = manager.register_entry(
            id="test_entry",
            title="Test",
            content="Content",
            category="Characters",
            unlocked=True
        )

        assert entry.unlocked is True

    def test_register_duplicate_id(self, manager):
        """Test that registering duplicate ID raises ValueError."""
        manager.register_entry(
            id="test_entry",
            title="Test",
            content="Content",
            category="Items"
        )

        with pytest.raises(ValueError) as exc_info:
            manager.register_entry(
                id="test_entry",
                title="Test 2",
                content="Content 2",
                category="Items"
            )

        assert "already registered" in str(exc_info.value)

    def test_register_invalid_category(self, manager):
        """Test that invalid category raises ValueError."""
        with pytest.raises(ValueError):
            manager.register_entry(
                id="test",
                title="Test",
                content="Content",
                category="InvalidCategory"
            )

    def test_get_entry(self, manager):
        """Test getting an entry by ID."""
        manager.register_entry(
            id="test_entry",
            title="Test",
            content="Content",
            category="Lore"
        )

        entry = manager.get_entry("test_entry")
        assert entry is not None
        assert entry.id == "test_entry"

    def test_get_entry_not_found(self, manager):
        """Test getting a non-existent entry returns None."""
        entry = manager.get_entry("nonexistent")
        assert entry is None


# ============================================================================
# JournalManager Unlock/Read Tests
# ============================================================================

class TestJournalManagerUnlockRead:
    """Tests for unlock and read functionality."""

    def test_unlock_entry(self, manager):
        """Test unlocking an entry."""
        manager.register_entry(
            id="test_entry",
            title="Test",
            content="Content",
            category="Clues"
        )

        result = manager.unlock_entry("test_entry")

        assert result is True
        entry = manager.get_entry("test_entry")
        assert entry.unlocked is True

    def test_unlock_entry_already_unlocked(self, manager):
        """Test unlocking an already unlocked entry."""
        manager.register_entry(
            id="test_entry",
            title="Test",
            content="Content",
            category="Clues",
            unlocked=True
        )

        result = manager.unlock_entry("test_entry")
        assert result is False

    def test_unlock_entry_not_found(self, manager):
        """Test unlocking a non-existent entry."""
        result = manager.unlock_entry("nonexistent")
        assert result is False

    def test_mark_read(self, manager):
        """Test marking an entry as read."""
        manager.register_entry(
            id="test_entry",
            title="Test",
            content="Content",
            category="Items",
            unlocked=True
        )

        result = manager.mark_read("test_entry")

        assert result is True
        entry = manager.get_entry("test_entry")
        assert entry.read is True

    def test_mark_read_locked(self, manager):
        """Test marking a locked entry as read."""
        manager.register_entry(
            id="test_entry",
            title="Test",
            content="Content",
            category="Items"
        )

        result = manager.mark_read("test_entry")
        assert result is False

    def test_mark_read_not_found(self, manager):
        """Test marking a non-existent entry as read."""
        result = manager.mark_read("nonexistent")
        assert result is False


# ============================================================================
# JournalManager Category Filtering Tests
# ============================================================================

class TestJournalManagerCategoryFiltering:
    """Tests for category filtering functionality."""

    @pytest.fixture
    def populated_manager(self, manager):
        """Create a manager with multiple entries."""
        # Lore entries
        manager.register_entry("lore1", "Lore 1", "Content", "Lore", unlocked=True)
        manager.register_entry("lore2", "Lore 2", "Content", "Lore", unlocked=True)
        manager.register_entry("lore3", "Lore 3", "Content", "Lore")  # locked

        # Character entries
        manager.register_entry("char1", "Character 1", "Content", "Characters", unlocked=True)
        manager.register_entry("char2", "Character 2", "Content", "Characters")

        # Location entries
        manager.register_entry("loc1", "Location 1", "Content", "Locations", unlocked=True)

        # Item entries
        manager.register_entry("item1", "Item 1", "Content", "Items", unlocked=True)
        manager.register_entry("item2", "Item 2", "Content", "Items", unlocked=True)

        # Clue entries
        manager.register_entry("clue1", "Clue 1", "Content", "Clues")

        return manager

    def test_get_entries_by_category_unlocked_only(self, populated_manager):
        """Test getting entries by category (unlocked only)."""
        entries = populated_manager.get_entries_by_category("Lore")

        assert len(entries) == 2
        assert all(e.category == "Lore" for e in entries)
        assert all(e.unlocked for e in entries)

    def test_get_entries_by_category_all(self, populated_manager):
        """Test getting all entries by category including locked."""
        entries = populated_manager.get_entries_by_category("Lore", unlocked_only=False)

        assert len(entries) == 3
        assert all(e.category == "Lore" for e in entries)

    def test_get_entries_by_category_sorted(self, populated_manager):
        """Test that entries are sorted by title."""
        entries = populated_manager.get_entries_by_category("Items")

        assert len(entries) == 2
        assert entries[0].title == "Item 1"
        assert entries[1].title == "Item 2"

    def test_get_entries_by_category_empty(self, populated_manager):
        """Test getting entries from category with no unlocked entries."""
        entries = populated_manager.get_entries_by_category("Clues")
        assert len(entries) == 0

    def test_get_all_entries_unlocked_only(self, populated_manager):
        """Test getting all unlocked entries."""
        entries = populated_manager.get_all_entries()

        assert len(entries) == 6  # 2 lore + 1 char + 1 loc + 2 items
        assert all(e.unlocked for e in entries)

    def test_get_all_entries_including_locked(self, populated_manager):
        """Test getting all entries including locked."""
        entries = populated_manager.get_all_entries(unlocked_only=False)

        assert len(entries) == 9  # All entries

    def test_get_all_entries_sorted(self, populated_manager):
        """Test that all entries are sorted by category then title."""
        entries = populated_manager.get_all_entries()

        # Should be sorted by category first
        categories = [e.category for e in entries]
        assert categories == sorted(categories)


# ============================================================================
# JournalManager Count Tests
# ============================================================================

class TestJournalManagerCounts:
    """Tests for count functionality."""

    @pytest.fixture
    def counted_manager(self, manager):
        """Create a manager with entries for count testing."""
        # Lore: 2 unlocked (1 read, 1 unread), 1 locked
        manager.register_entry("lore1", "Lore 1", "Content", "Lore", unlocked=True)
        manager.mark_read("lore1")
        manager.register_entry("lore2", "Lore 2", "Content", "Lore", unlocked=True)
        manager.register_entry("lore3", "Lore 3", "Content", "Lore")

        # Characters: 1 unlocked unread
        manager.register_entry("char1", "Char 1", "Content", "Characters", unlocked=True)

        return manager

    def test_get_unread_count_all(self, counted_manager):
        """Test getting total unread count."""
        count = counted_manager.get_unread_count()
        assert count == 2  # lore2 and char1

    def test_get_unread_count_by_category(self, counted_manager):
        """Test getting unread count by category."""
        lore_count = counted_manager.get_unread_count("Lore")
        assert lore_count == 1

        char_count = counted_manager.get_unread_count("Characters")
        assert char_count == 1

    def test_get_unlocked_count_all(self, counted_manager):
        """Test getting total unlocked count."""
        count = counted_manager.get_unlocked_count()
        assert count == 3  # lore1, lore2, char1

    def test_get_unlocked_count_by_category(self, counted_manager):
        """Test getting unlocked count by category."""
        lore_count = counted_manager.get_unlocked_count("Lore")
        assert lore_count == 2

        char_count = counted_manager.get_unlocked_count("Characters")
        assert char_count == 1

    def test_get_total_count_all(self, counted_manager):
        """Test getting total entry count."""
        count = counted_manager.get_total_count()
        assert count == 4  # All entries

    def test_get_total_count_by_category(self, counted_manager):
        """Test getting total count by category."""
        lore_count = counted_manager.get_total_count("Lore")
        assert lore_count == 3

        char_count = counted_manager.get_total_count("Characters")
        assert char_count == 1


# ============================================================================
# JournalManager Search Tests
# ============================================================================

class TestJournalManagerSearch:
    """Tests for search functionality."""

    @pytest.fixture
    def searchable_manager(self, manager):
        """Create a manager with searchable entries."""
        manager.register_entry(
            "entry1",
            "Ancient History",
            "The world was created by the Old Gods.",
            "Lore",
            unlocked=True
        )
        manager.register_entry(
            "entry2",
            "Modern Times",
            "The current age began after the ancient cataclysm.",
            "Lore",
            unlocked=True
        )
        manager.register_entry(
            "entry3",
            "Secret Knowledge",
            "Hidden information about the ancient ones.",
            "Lore"  # locked
        )
        manager.register_entry(
            "entry4",
            "The Hero",
            "A brave warrior who saved the world.",
            "Characters",
            unlocked=True
        )

        return manager

    def test_search_by_title(self, searchable_manager):
        """Test searching by title."""
        results = searchable_manager.search("History")

        assert len(results) == 1
        assert results[0].id == "entry1"

    def test_search_by_content(self, searchable_manager):
        """Test searching by content."""
        results = searchable_manager.search("cataclysm")

        assert len(results) == 1
        assert results[0].id == "entry2"

    def test_search_case_insensitive(self, searchable_manager):
        """Test that search is case-insensitive."""
        results = searchable_manager.search("HISTORY")

        assert len(results) == 1
        assert results[0].id == "entry1"

    def test_search_multiple_results(self, searchable_manager):
        """Test search returning multiple results."""
        results = searchable_manager.search("world")

        assert len(results) == 2  # entry1 (content) and entry4 (content)

    def test_search_unlocked_only_default(self, searchable_manager):
        """Test that search excludes locked entries by default."""
        results = searchable_manager.search("ancient")

        # entry1 (title) and entry2 (content) but NOT entry3 (locked)
        assert len(results) == 2
        assert all(e.unlocked for e in results)

    def test_search_including_locked(self, searchable_manager):
        """Test search including locked entries."""
        results = searchable_manager.search("ancient", unlocked_only=False)

        assert len(results) == 3  # entry1, entry2, entry3

    def test_search_title_only(self, searchable_manager):
        """Test search only in titles."""
        results = searchable_manager.search("ancient", search_content=False)

        assert len(results) == 1
        assert results[0].id == "entry1"

    def test_search_no_results(self, searchable_manager):
        """Test search with no matching results."""
        results = searchable_manager.search("xyznonexistent")

        assert len(results) == 0

    def test_search_sorted_by_title(self, searchable_manager):
        """Test that search results are sorted by title."""
        results = searchable_manager.search("the")

        titles = [r.title for r in results]
        assert titles == sorted(titles)


# ============================================================================
# JournalManager Notification Tests
# ============================================================================

class TestJournalManagerNotifications:
    """Tests for notification functionality."""

    def test_no_pending_notifications_initially(self, manager):
        """Test that there are no notifications initially."""
        assert manager.has_pending_notifications() is False

    def test_unlock_creates_notification(self, manager):
        """Test that unlocking an entry creates a notification."""
        manager.register_entry("test", "Test", "Content", "Lore")
        manager.unlock_entry("test")

        assert manager.has_pending_notifications() is True

    def test_unlock_no_notification_when_disabled(self, manager):
        """Test that notifications can be disabled."""
        manager.register_entry("test", "Test", "Content", "Lore")
        manager.unlock_entry("test", show_notification=False)

        assert manager.has_pending_notifications() is False

    def test_get_pending_notifications(self, manager):
        """Test getting pending notifications."""
        manager.register_entry("test1", "Test 1", "Content", "Lore")
        manager.register_entry("test2", "Test 2", "Content", "Characters")

        manager.unlock_entry("test1")
        manager.unlock_entry("test2")

        notifications = manager.get_pending_notifications()

        assert len(notifications) == 2
        assert notifications[0].id == "test1"
        assert notifications[1].id == "test2"

    def test_clear_notifications(self, manager):
        """Test clearing all notifications."""
        manager.register_entry("test", "Test", "Content", "Lore")
        manager.unlock_entry("test")

        manager.clear_notifications()

        assert manager.has_pending_notifications() is False

    def test_pop_notification(self, manager):
        """Test popping a single notification."""
        manager.register_entry("test1", "Test 1", "Content", "Lore")
        manager.register_entry("test2", "Test 2", "Content", "Characters")

        manager.unlock_entry("test1")
        manager.unlock_entry("test2")

        entry = manager.pop_notification()

        assert entry is not None
        assert entry.id == "test1"
        assert manager.has_pending_notifications() is True

        entry2 = manager.pop_notification()
        assert entry2.id == "test2"
        assert manager.has_pending_notifications() is False

    def test_pop_notification_empty(self, manager):
        """Test popping when no notifications."""
        entry = manager.pop_notification()
        assert entry is None


# ============================================================================
# JournalManager Reset Tests
# ============================================================================

class TestJournalManagerReset:
    """Tests for reset functionality."""

    def test_reset_all(self, manager, journal_classes):
        """Test resetting all entries."""
        # Set up persistent mock
        persistent = journal_classes["persistent"]

        manager.register_entry("test1", "Test 1", "Content", "Lore", unlocked=True)
        manager.register_entry("test2", "Test 2", "Content", "Characters")
        manager.unlock_entry("test2")
        manager.mark_read("test1")

        manager.reset_all()

        # All entries should be locked and unread
        entry1 = manager.get_entry("test1")
        entry2 = manager.get_entry("test2")

        assert entry1.unlocked is False
        assert entry1.read is False
        assert entry2.unlocked is False
        assert entry2.read is False

        # Notifications should be cleared
        assert manager.has_pending_notifications() is False


# ============================================================================
# Integration Tests
# ============================================================================

class TestJournalIntegration:
    """Integration tests for the journal system."""

    def test_full_workflow(self, manager):
        """Test complete journal workflow."""
        # Register entries
        manager.register_entry(
            "mystery_clue",
            "Strange Symbol",
            "A mysterious symbol found at the crime scene.",
            "Clues"
        )
        manager.register_entry(
            "suspect_info",
            "The Butler",
            "Information about the suspicious butler.",
            "Characters"
        )

        # Initially no unlocked entries
        assert manager.get_unlocked_count() == 0

        # Discover a clue
        manager.unlock_entry("mystery_clue")
        assert manager.get_unlocked_count() == 1
        assert manager.get_unread_count() == 1

        # Read the clue
        manager.mark_read("mystery_clue")
        assert manager.get_unread_count() == 0

        # Search for clues
        results = manager.search("symbol")
        assert len(results) == 1
        assert results[0].id == "mystery_clue"

        # Later discover character info
        manager.unlock_entry("suspect_info")
        assert manager.get_unlocked_count() == 2
        assert manager.get_unread_count() == 1

        # Filter by category
        characters = manager.get_entries_by_category("Characters")
        assert len(characters) == 1

        clues = manager.get_entries_by_category("Clues")
        assert len(clues) == 1

    def test_all_categories_workflow(self, manager):
        """Test entries across all categories."""
        categories = ["Lore", "Characters", "Locations", "Items", "Clues"]

        for i, category in enumerate(categories):
            manager.register_entry(
                f"entry_{category.lower()}",
                f"{category} Entry",
                f"Content for {category}",
                category
            )
            manager.unlock_entry(f"entry_{category.lower()}")

        # Should have one entry in each category
        for category in categories:
            entries = manager.get_entries_by_category(category)
            assert len(entries) == 1
            assert entries[0].category == category

        # Total counts
        assert manager.get_unlocked_count() == 5
        assert manager.get_unread_count() == 5
        assert manager.get_total_count() == 5

    def test_persistent_state_simulation(self, JournalManager, journal_classes):
        """Test that persistent state works across manager instances."""
        persistent = journal_classes["persistent"]

        # First manager instance
        manager1 = JournalManager()
        manager1.register_entry("test", "Test", "Content", "Lore")
        manager1.unlock_entry("test")
        manager1.mark_read("test")

        # Simulate save (already done via _save_entry_state)

        # Second manager instance (simulating game reload)
        manager2 = JournalManager()
        manager2.register_entry("test", "Test", "Content", "Lore")

        # Entry should have persistent state applied
        entry = manager2.get_entry("test")
        assert entry.unlocked is True
        assert entry.read is True

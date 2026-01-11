"""
Tests for the Flashback/Memory System.

This module tests the Memory class, FlashbackManager class, and their
functionality for memory collection, unlocking, and category organization.
"""
import pytest
from pathlib import Path
import sys

# Add tests directory to path so conftest utilities can be imported
TESTS_DIR = Path(__file__).parent
GAME_DIR = TESTS_DIR.parent / "game"
sys.path.insert(0, str(TESTS_DIR))

from conftest import load_rpy_classes


@pytest.fixture
def flashback_module():
    """Load the flashback module and return its namespace."""
    rpy_path = GAME_DIR / "flashback.rpy"
    if not rpy_path.exists():
        pytest.skip("flashback.rpy not found")
    return load_rpy_classes(rpy_path)


@pytest.fixture
def Memory(flashback_module):
    """Get the Memory class from the flashback module."""
    return flashback_module["Memory"]


@pytest.fixture
def FlashbackManager(flashback_module):
    """Get the FlashbackManager class from the flashback module."""
    return flashback_module["FlashbackManager"]


@pytest.fixture
def MEMORY_CATEGORIES(flashback_module):
    """Get the MEMORY_CATEGORIES dict from the flashback module."""
    return flashback_module["MEMORY_CATEGORIES"]


# =============================================================================
# Memory Class Tests
# =============================================================================

class TestMemoryClass:
    """Tests for the Memory class."""

    def test_memory_creation_basic(self, Memory):
        """Test creating a Memory with required parameters."""
        memory = Memory(
            id="test_memory",
            name="Test Memory",
            description="A test memory description",
            label_name="flashback_test"
        )

        assert memory.id == "test_memory"
        assert memory.name == "Test Memory"
        assert memory.description == "A test memory description"
        assert memory.label_name == "flashback_test"
        assert memory.unlocked is False
        assert memory.category == "story"  # default
        assert memory.thumbnail is None
        assert memory.unlock_date is None

    def test_memory_creation_with_all_params(self, Memory):
        """Test creating a Memory with all parameters."""
        memory = Memory(
            id="full_memory",
            name="Full Memory",
            description="Complete memory with all params",
            label_name="flashback_full",
            unlocked=True,
            category="character",
            thumbnail="images/memory_thumb.png"
        )

        assert memory.id == "full_memory"
        assert memory.name == "Full Memory"
        assert memory.description == "Complete memory with all params"
        assert memory.label_name == "flashback_full"
        assert memory.unlocked is True
        assert memory.category == "character"
        assert memory.thumbnail == "images/memory_thumb.png"

    def test_memory_unlock(self, Memory):
        """Test unlocking a memory."""
        memory = Memory(
            id="unlock_test",
            name="Unlock Test",
            description="Test unlock functionality",
            label_name="flashback_unlock"
        )

        assert memory.unlocked is False
        assert memory.unlock_date is None

        # Unlock the memory
        result = memory.unlock()

        assert result is True
        assert memory.unlocked is True
        assert memory.unlock_date is not None
        assert len(memory.unlock_date) > 0

    def test_memory_unlock_already_unlocked(self, Memory):
        """Test unlocking an already unlocked memory returns False."""
        memory = Memory(
            id="already_unlocked",
            name="Already Unlocked",
            description="Test double unlock",
            label_name="flashback_double"
        )

        # First unlock
        first_result = memory.unlock()
        first_date = memory.unlock_date

        # Second unlock attempt
        second_result = memory.unlock()

        assert first_result is True
        assert second_result is False
        # Date should not change
        assert memory.unlock_date == first_date

    def test_memory_to_dict(self, Memory):
        """Test converting a memory to dictionary."""
        memory = Memory(
            id="dict_test",
            name="Dict Test",
            description="Test dictionary conversion",
            label_name="flashback_dict",
            category="discovery",
            thumbnail="images/test.png"
        )
        memory.unlock()

        data = memory.to_dict()

        assert data["id"] == "dict_test"
        assert data["name"] == "Dict Test"
        assert data["description"] == "Test dictionary conversion"
        assert data["label_name"] == "flashback_dict"
        assert data["unlocked"] is True
        assert data["category"] == "discovery"
        assert data["thumbnail"] == "images/test.png"
        assert data["unlock_date"] is not None

    def test_memory_from_dict(self, Memory):
        """Test creating a memory from dictionary data."""
        data = {
            "id": "from_dict",
            "name": "From Dict",
            "description": "Created from dictionary",
            "label_name": "flashback_from_dict",
            "unlocked": True,
            "category": "achievement",
            "thumbnail": "images/thumb.png",
            "unlock_date": "2024-01-01 12:00:00"
        }

        memory = Memory.from_dict(data)

        assert memory.id == "from_dict"
        assert memory.name == "From Dict"
        assert memory.description == "Created from dictionary"
        assert memory.label_name == "flashback_from_dict"
        assert memory.unlocked is True
        assert memory.category == "achievement"
        assert memory.thumbnail == "images/thumb.png"
        assert memory.unlock_date == "2024-01-01 12:00:00"

    def test_memory_from_dict_minimal(self, Memory):
        """Test creating a memory from minimal dictionary data."""
        data = {
            "id": "minimal",
            "name": "Minimal",
            "description": "Minimal data",
            "label_name": "flashback_minimal"
        }

        memory = Memory.from_dict(data)

        assert memory.id == "minimal"
        assert memory.unlocked is False
        assert memory.category == "story"  # default
        assert memory.thumbnail is None
        assert memory.unlock_date is None


# =============================================================================
# FlashbackManager Class Tests
# =============================================================================

class TestFlashbackManagerClass:
    """Tests for the FlashbackManager class."""

    def test_manager_creation(self, FlashbackManager):
        """Test creating a FlashbackManager."""
        manager = FlashbackManager()

        assert manager.memories == {}
        assert manager._pending_unlock_notification is None

    def test_register_memory_object(self, FlashbackManager, Memory):
        """Test registering a Memory object."""
        manager = FlashbackManager()
        memory = Memory(
            id="registered",
            name="Registered",
            description="Test registration",
            label_name="flashback_registered"
        )

        result = manager.register_memory(memory)

        assert result is memory
        assert "registered" in manager.memories
        assert manager.memories["registered"] is memory

    def test_register_convenience_method(self, FlashbackManager):
        """Test the register convenience method."""
        manager = FlashbackManager()

        memory = manager.register(
            id="convenient",
            name="Convenient",
            description="Created via register method",
            label_name="flashback_convenient",
            category="character",
            thumbnail="images/conv.png"
        )

        assert memory.id == "convenient"
        assert memory.name == "Convenient"
        assert memory.category == "character"
        assert memory.thumbnail == "images/conv.png"
        assert "convenient" in manager.memories

    def test_unregister_memory(self, FlashbackManager, Memory):
        """Test unregistering a memory."""
        manager = FlashbackManager()
        memory = Memory(
            id="to_unregister",
            name="To Unregister",
            description="Will be removed",
            label_name="flashback_unregister"
        )
        manager.register_memory(memory)

        # Unregister
        result = manager.unregister_memory("to_unregister")

        assert result is True
        assert "to_unregister" not in manager.memories

    def test_unregister_nonexistent_memory(self, FlashbackManager):
        """Test unregistering a memory that doesn't exist."""
        manager = FlashbackManager()

        result = manager.unregister_memory("nonexistent")

        assert result is False

    def test_get_memory(self, FlashbackManager, Memory):
        """Test getting a memory by ID."""
        manager = FlashbackManager()
        memory = Memory(
            id="gettable",
            name="Gettable",
            description="Can be retrieved",
            label_name="flashback_gettable"
        )
        manager.register_memory(memory)

        result = manager.get_memory("gettable")

        assert result is memory

    def test_get_nonexistent_memory(self, FlashbackManager):
        """Test getting a memory that doesn't exist returns None."""
        manager = FlashbackManager()

        result = manager.get_memory("nonexistent")

        assert result is None

    def test_unlock_memory(self, FlashbackManager, Memory):
        """Test unlocking a memory through the manager."""
        manager = FlashbackManager()
        memory = Memory(
            id="to_unlock",
            name="To Unlock",
            description="Will be unlocked",
            label_name="flashback_to_unlock"
        )
        manager.register_memory(memory)

        result = manager.unlock_memory("to_unlock", show_notification=False)

        assert result is True
        assert memory.unlocked is True
        assert memory.unlock_date is not None

    def test_unlock_already_unlocked_memory(self, FlashbackManager, Memory):
        """Test unlocking an already unlocked memory returns False."""
        manager = FlashbackManager()
        memory = Memory(
            id="already_unlocked",
            name="Already Unlocked",
            description="Already unlocked",
            label_name="flashback_already",
            unlocked=True
        )
        manager.register_memory(memory)

        result = manager.unlock_memory("already_unlocked", show_notification=False)

        assert result is False

    def test_unlock_nonexistent_memory(self, FlashbackManager):
        """Test unlocking a nonexistent memory returns False."""
        manager = FlashbackManager()

        result = manager.unlock_memory("nonexistent", show_notification=False)

        assert result is False

    def test_is_memory_unlocked_true(self, FlashbackManager, Memory):
        """Test is_memory_unlocked returns True for unlocked memory."""
        manager = FlashbackManager()
        memory = Memory(
            id="check_unlocked",
            name="Check Unlocked",
            description="For unlocked check",
            label_name="flashback_check",
            unlocked=True
        )
        manager.register_memory(memory)

        result = manager.is_memory_unlocked("check_unlocked")

        assert result is True

    def test_is_memory_unlocked_false(self, FlashbackManager, Memory):
        """Test is_memory_unlocked returns False for locked memory."""
        manager = FlashbackManager()
        memory = Memory(
            id="check_locked",
            name="Check Locked",
            description="For locked check",
            label_name="flashback_check_locked"
        )
        manager.register_memory(memory)

        result = manager.is_memory_unlocked("check_locked")

        assert result is False

    def test_is_memory_unlocked_nonexistent(self, FlashbackManager):
        """Test is_memory_unlocked returns False for nonexistent memory."""
        manager = FlashbackManager()

        result = manager.is_memory_unlocked("nonexistent")

        assert result is False


# =============================================================================
# FlashbackManager Query Methods Tests
# =============================================================================

class TestFlashbackManagerQueries:
    """Tests for FlashbackManager query methods."""

    @pytest.fixture
    def populated_manager(self, FlashbackManager):
        """Create a manager with several memories for testing queries."""
        manager = FlashbackManager()

        # Story memories
        manager.register(
            id="story1", name="Story 1", description="First story",
            label_name="fb_story1", category="story"
        )
        manager.register(
            id="story2", name="Story 2", description="Second story",
            label_name="fb_story2", category="story"
        )

        # Character memories
        manager.register(
            id="char1", name="Character 1", description="First character",
            label_name="fb_char1", category="character"
        )
        manager.register(
            id="char2", name="Character 2", description="Second character",
            label_name="fb_char2", category="character"
        )

        # Discovery memories
        manager.register(
            id="disc1", name="Discovery 1", description="First discovery",
            label_name="fb_disc1", category="discovery"
        )

        # Unlock some memories
        manager.unlock_memory("story1", show_notification=False)
        manager.unlock_memory("char1", show_notification=False)
        manager.unlock_memory("disc1", show_notification=False)

        return manager

    def test_get_all_memories(self, populated_manager):
        """Test getting all registered memories."""
        memories = populated_manager.get_all_memories()

        assert len(memories) == 5
        ids = [m.id for m in memories]
        assert "story1" in ids
        assert "story2" in ids
        assert "char1" in ids
        assert "char2" in ids
        assert "disc1" in ids

    def test_get_unlocked_memories(self, populated_manager):
        """Test getting only unlocked memories."""
        unlocked = populated_manager.get_unlocked_memories()

        assert len(unlocked) == 3
        ids = [m.id for m in unlocked]
        assert "story1" in ids
        assert "char1" in ids
        assert "disc1" in ids

    def test_get_locked_memories(self, populated_manager):
        """Test getting only locked memories."""
        locked = populated_manager.get_locked_memories()

        assert len(locked) == 2
        ids = [m.id for m in locked]
        assert "story2" in ids
        assert "char2" in ids

    def test_get_memories_by_category(self, populated_manager):
        """Test getting memories by category."""
        story_memories = populated_manager.get_memories_by_category("story")
        char_memories = populated_manager.get_memories_by_category("character")
        disc_memories = populated_manager.get_memories_by_category("discovery")

        assert len(story_memories) == 2
        assert len(char_memories) == 2
        assert len(disc_memories) == 1

    def test_get_unlocked_memories_by_category(self, populated_manager):
        """Test getting unlocked memories by category."""
        story_unlocked = populated_manager.get_unlocked_memories_by_category("story")
        char_unlocked = populated_manager.get_unlocked_memories_by_category("character")
        disc_unlocked = populated_manager.get_unlocked_memories_by_category("discovery")

        assert len(story_unlocked) == 1
        assert story_unlocked[0].id == "story1"

        assert len(char_unlocked) == 1
        assert char_unlocked[0].id == "char1"

        assert len(disc_unlocked) == 1
        assert disc_unlocked[0].id == "disc1"

    def test_get_memory_count(self, populated_manager):
        """Test getting total and unlocked memory counts."""
        total, unlocked = populated_manager.get_memory_count()

        assert total == 5
        assert unlocked == 3

    def test_get_category_progress(self, populated_manager):
        """Test getting progress for a specific category."""
        story_total, story_unlocked = populated_manager.get_category_progress("story")
        char_total, char_unlocked = populated_manager.get_category_progress("character")
        disc_total, disc_unlocked = populated_manager.get_category_progress("discovery")

        assert story_total == 2
        assert story_unlocked == 1

        assert char_total == 2
        assert char_unlocked == 1

        assert disc_total == 1
        assert disc_unlocked == 1

    def test_get_category_progress_empty(self, populated_manager):
        """Test getting progress for an empty category."""
        achievement_total, achievement_unlocked = populated_manager.get_category_progress("achievement")

        assert achievement_total == 0
        assert achievement_unlocked == 0

    def test_get_categories_with_counts(self, populated_manager, MEMORY_CATEGORIES):
        """Test getting all categories with their counts."""
        categories = populated_manager.get_categories_with_counts()

        # Should have all defined categories
        for cat_id in MEMORY_CATEGORIES:
            assert cat_id in categories
            assert "label" in categories[cat_id]
            assert "description" in categories[cat_id]
            assert "total" in categories[cat_id]
            assert "unlocked" in categories[cat_id]

        # Check specific counts
        assert categories["story"]["total"] == 2
        assert categories["story"]["unlocked"] == 1
        assert categories["character"]["total"] == 2
        assert categories["character"]["unlocked"] == 1
        assert categories["discovery"]["total"] == 1
        assert categories["discovery"]["unlocked"] == 1
        assert categories["achievement"]["total"] == 0
        assert categories["achievement"]["unlocked"] == 0


# =============================================================================
# Memory Categories Tests
# =============================================================================

class TestMemoryCategories:
    """Tests for memory category definitions."""

    def test_default_categories_exist(self, MEMORY_CATEGORIES):
        """Test that default categories are defined."""
        assert "story" in MEMORY_CATEGORIES
        assert "character" in MEMORY_CATEGORIES
        assert "discovery" in MEMORY_CATEGORIES
        assert "achievement" in MEMORY_CATEGORIES

    def test_categories_have_labels(self, MEMORY_CATEGORIES):
        """Test that all categories have labels."""
        for cat_id, cat_info in MEMORY_CATEGORIES.items():
            assert "label" in cat_info
            assert len(cat_info["label"]) > 0

    def test_categories_have_descriptions(self, MEMORY_CATEGORIES):
        """Test that all categories have descriptions."""
        for cat_id, cat_info in MEMORY_CATEGORIES.items():
            assert "description" in cat_info
            assert len(cat_info["description"]) > 0


# =============================================================================
# FlashbackManager Reset and Persistence Tests
# =============================================================================

class TestFlashbackManagerPersistence:
    """Tests for FlashbackManager persistence functionality."""

    def test_reset_all_memories(self, FlashbackManager):
        """Test resetting all memories to locked state."""
        manager = FlashbackManager()

        # Register and unlock memories
        manager.register(
            id="reset1", name="Reset 1", description="To reset",
            label_name="fb_reset1"
        )
        manager.register(
            id="reset2", name="Reset 2", description="To reset",
            label_name="fb_reset2"
        )

        manager.unlock_memory("reset1", show_notification=False)
        manager.unlock_memory("reset2", show_notification=False)

        # Verify they're unlocked
        assert manager.is_memory_unlocked("reset1")
        assert manager.is_memory_unlocked("reset2")

        # Reset all
        manager.reset_all_memories()

        # Verify they're locked again
        assert not manager.is_memory_unlocked("reset1")
        assert not manager.is_memory_unlocked("reset2")

        # Verify unlock dates are cleared
        assert manager.get_memory("reset1").unlock_date is None
        assert manager.get_memory("reset2").unlock_date is None


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_manager_queries(self, FlashbackManager):
        """Test queries on an empty manager."""
        manager = FlashbackManager()

        assert manager.get_all_memories() == []
        assert manager.get_unlocked_memories() == []
        assert manager.get_locked_memories() == []
        assert manager.get_memories_by_category("story") == []
        assert manager.get_unlocked_memories_by_category("story") == []
        assert manager.get_memory_count() == (0, 0)
        assert manager.get_category_progress("story") == (0, 0)

    def test_memory_with_empty_strings(self, Memory):
        """Test creating a memory with empty strings."""
        memory = Memory(
            id="",
            name="",
            description="",
            label_name=""
        )

        assert memory.id == ""
        assert memory.name == ""
        assert memory.description == ""
        assert memory.label_name == ""

    def test_memory_with_special_characters(self, Memory):
        """Test creating a memory with special characters."""
        memory = Memory(
            id="special_!@#$%",
            name="Memory with 'quotes' and \"double quotes\"",
            description="Description with\nnewlines\tand\ttabs",
            label_name="flashback_special"
        )

        assert memory.id == "special_!@#$%"
        assert "quotes" in memory.name
        assert "\n" in memory.description
        assert "\t" in memory.description

    def test_multiple_managers_independent(self, FlashbackManager):
        """Test that multiple managers are independent."""
        manager1 = FlashbackManager()
        manager2 = FlashbackManager()

        manager1.register(
            id="only_in_1", name="Only in 1", description="Unique",
            label_name="fb_only1"
        )

        assert manager1.get_memory("only_in_1") is not None
        assert manager2.get_memory("only_in_1") is None

    def test_register_same_id_overwrites(self, FlashbackManager):
        """Test that registering with same ID overwrites the previous memory."""
        manager = FlashbackManager()

        manager.register(
            id="duplicate", name="First", description="Original",
            label_name="fb_first"
        )
        manager.register(
            id="duplicate", name="Second", description="Replacement",
            label_name="fb_second"
        )

        memory = manager.get_memory("duplicate")
        assert memory.name == "Second"
        assert memory.description == "Replacement"
        assert memory.label_name == "fb_second"


# =============================================================================
# Memory Roundtrip Tests
# =============================================================================

class TestMemoryRoundtrip:
    """Tests for memory serialization roundtrip."""

    def test_memory_dict_roundtrip(self, Memory):
        """Test that a memory survives conversion to dict and back."""
        original = Memory(
            id="roundtrip",
            name="Roundtrip Test",
            description="Testing serialization",
            label_name="fb_roundtrip",
            category="discovery",
            thumbnail="images/roundtrip.png"
        )
        original.unlock()

        # Convert to dict and back
        data = original.to_dict()
        restored = Memory.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.label_name == original.label_name
        assert restored.unlocked == original.unlocked
        assert restored.category == original.category
        assert restored.thumbnail == original.thumbnail
        assert restored.unlock_date == original.unlock_date

    def test_locked_memory_dict_roundtrip(self, Memory):
        """Test that a locked memory survives roundtrip."""
        original = Memory(
            id="locked_roundtrip",
            name="Locked Roundtrip",
            description="Locked memory test",
            label_name="fb_locked_roundtrip"
        )

        data = original.to_dict()
        restored = Memory.from_dict(data)

        assert restored.unlocked is False
        assert restored.unlock_date is None


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for the full flashback system."""

    def test_full_workflow(self, FlashbackManager):
        """Test a complete workflow of registering, unlocking, and querying."""
        manager = FlashbackManager()

        # Register memories across categories
        manager.register(
            id="intro", name="Introduction", description="The beginning",
            label_name="fb_intro", category="story"
        )
        manager.register(
            id="meeting_alice", name="Meeting Alice", description="First meeting",
            label_name="fb_alice", category="character"
        )
        manager.register(
            id="secret_door", name="Secret Door", description="Hidden entrance",
            label_name="fb_door", category="discovery"
        )
        manager.register(
            id="victory", name="Victory", description="First triumph",
            label_name="fb_victory", category="achievement"
        )

        # Verify initial state
        total, unlocked = manager.get_memory_count()
        assert total == 4
        assert unlocked == 0

        # Unlock some memories
        manager.unlock_memory("intro", show_notification=False)
        manager.unlock_memory("meeting_alice", show_notification=False)

        # Verify unlock state
        total, unlocked = manager.get_memory_count()
        assert unlocked == 2

        # Check category queries
        story_unlocked = manager.get_unlocked_memories_by_category("story")
        assert len(story_unlocked) == 1
        assert story_unlocked[0].id == "intro"

        char_unlocked = manager.get_unlocked_memories_by_category("character")
        assert len(char_unlocked) == 1
        assert char_unlocked[0].id == "meeting_alice"

        # Check that other categories are still locked
        disc_unlocked = manager.get_unlocked_memories_by_category("discovery")
        assert len(disc_unlocked) == 0

        # Unlock remaining
        manager.unlock_memory("secret_door", show_notification=False)
        manager.unlock_memory("victory", show_notification=False)

        # Verify all unlocked
        total, unlocked = manager.get_memory_count()
        assert unlocked == 4

        # Reset and verify
        manager.reset_all_memories()
        total, unlocked = manager.get_memory_count()
        assert unlocked == 0

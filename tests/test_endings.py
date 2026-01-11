"""
Comprehensive tests for the Multiple Endings Tracker system.

Tests cover the Ending class, EndingsManager class, and all features including:
- Ending creation and registration
- Unlock/lock functionality
- Persistent storage
- Hidden endings support
- Requirements hints
- Completion statistics
- Category management
"""

import pytest
from pathlib import Path


class TestEnding:
    """Tests for the Ending class."""

    @pytest.fixture
    def endings_module(self, load_system):
        """Load the endings module."""
        return load_system("endings")

    @pytest.fixture
    def Ending(self, endings_module):
        """Get the Ending class."""
        return endings_module["Ending"]

    def test_ending_creation_basic(self, Ending):
        """Test basic ending creation with required parameters."""
        ending = Ending(id="test_ending", name="Test Ending")

        assert ending.id == "test_ending"
        assert ending.name == "Test Ending"
        assert ending.description == ""
        assert ending.unlocked is False
        assert ending.unlock_date is None
        assert ending.hidden is False
        assert ending.requirements_hint == ""
        assert ending.category == "main"
        assert ending.image is None
        assert ending.priority == 100

    def test_ending_creation_full(self, Ending):
        """Test ending creation with all parameters."""
        ending = Ending(
            id="full_ending",
            name="Full Ending",
            description="A complete ending description.",
            hidden=True,
            requirements_hint="Do something special.",
            category="secret",
            image="images/endings/secret.png",
            priority=50
        )

        assert ending.id == "full_ending"
        assert ending.name == "Full Ending"
        assert ending.description == "A complete ending description."
        assert ending.hidden is True
        assert ending.requirements_hint == "Do something special."
        assert ending.category == "secret"
        assert ending.image == "images/endings/secret.png"
        assert ending.priority == 50

    def test_ending_unlock(self, Ending):
        """Test unlocking an ending."""
        ending = Ending(id="test", name="Test")

        assert ending.unlocked is False
        assert ending.unlock_date is None

        result = ending.unlock()

        assert result is True
        assert ending.unlocked is True
        assert ending.unlock_date is not None
        # Check date format (ISO format)
        assert "T" in ending.unlock_date

    def test_ending_unlock_twice(self, Ending):
        """Test that unlocking twice returns False."""
        ending = Ending(id="test", name="Test")

        first_unlock = ending.unlock()
        second_unlock = ending.unlock()

        assert first_unlock is True
        assert second_unlock is False
        assert ending.unlocked is True

    def test_ending_lock(self, Ending):
        """Test locking an ending."""
        ending = Ending(id="test", name="Test")
        ending.unlock()

        result = ending.lock()

        assert result is True
        assert ending.unlocked is False
        assert ending.unlock_date is None

    def test_ending_lock_when_already_locked(self, Ending):
        """Test locking an already locked ending."""
        ending = Ending(id="test", name="Test")

        result = ending.lock()

        assert result is False
        assert ending.unlocked is False

    def test_get_display_name_unlocked(self, Ending):
        """Test display name when ending is unlocked."""
        ending = Ending(id="test", name="Secret Ending", hidden=True)
        ending.unlock()

        assert ending.get_display_name() == "Secret Ending"

    def test_get_display_name_locked_visible(self, Ending):
        """Test display name when ending is locked but not hidden."""
        ending = Ending(id="test", name="Normal Ending", hidden=False)

        assert ending.get_display_name() == "Normal Ending"

    def test_get_display_name_locked_hidden(self, Ending):
        """Test display name when ending is locked and hidden."""
        ending = Ending(id="test", name="Secret Ending", hidden=True)

        assert ending.get_display_name() == "???"

    def test_get_display_description_unlocked(self, Ending):
        """Test display description when ending is unlocked."""
        ending = Ending(
            id="test",
            name="Test",
            description="Full description here.",
            requirements_hint="Some hint."
        )
        ending.unlock()

        assert ending.get_display_description() == "Full description here."

    def test_get_display_description_locked_visible(self, Ending):
        """Test display description when locked but visible."""
        ending = Ending(
            id="test",
            name="Test",
            description="Full description here.",
            requirements_hint="Some hint.",
            hidden=False
        )

        assert ending.get_display_description() == "Some hint."

    def test_get_display_description_locked_no_hint(self, Ending):
        """Test display description when locked with no hint."""
        ending = Ending(
            id="test",
            name="Test",
            description="Full description here.",
            requirements_hint="",
            hidden=False
        )

        assert ending.get_display_description() == "Ending not yet unlocked."

    def test_get_display_description_hidden(self, Ending):
        """Test display description when hidden."""
        ending = Ending(
            id="test",
            name="Test",
            description="Full description here.",
            hidden=True
        )

        assert ending.get_display_description() == "???"

    def test_to_dict(self, Ending):
        """Test serialization to dictionary."""
        ending = Ending(id="test", name="Test")
        ending.unlock()

        data = ending.to_dict()

        assert data["id"] == "test"
        assert data["unlocked"] is True
        assert data["unlock_date"] is not None

    def test_from_dict(self, Ending):
        """Test deserialization from dictionary."""
        ending = Ending(id="test", name="Test")
        data = {
            "id": "test",
            "unlocked": True,
            "unlock_date": "2024-01-15T10:30:00"
        }

        ending.from_dict(data)

        assert ending.unlocked is True
        assert ending.unlock_date == "2024-01-15T10:30:00"

    def test_from_dict_wrong_id(self, Ending):
        """Test that from_dict ignores data with wrong ID."""
        ending = Ending(id="test", name="Test")
        data = {
            "id": "different",
            "unlocked": True,
            "unlock_date": "2024-01-15T10:30:00"
        }

        ending.from_dict(data)

        assert ending.unlocked is False
        assert ending.unlock_date is None

    def test_repr(self, Ending):
        """Test string representation."""
        ending = Ending(id="test", name="Test Ending", hidden=True)

        repr_str = repr(ending)

        assert "test" in repr_str
        assert "Test Ending" in repr_str
        assert "Locked" in repr_str
        assert "Hidden" in repr_str


class TestEndingsManager:
    """Tests for the EndingsManager class."""

    @pytest.fixture
    def endings_module(self, load_system):
        """Load the endings module."""
        return load_system("endings")

    @pytest.fixture
    def Ending(self, endings_module):
        """Get the Ending class."""
        return endings_module["Ending"]

    @pytest.fixture
    def EndingsManager(self, endings_module):
        """Get the EndingsManager class."""
        return endings_module["EndingsManager"]

    @pytest.fixture
    def manager(self, EndingsManager):
        """Create a fresh manager instance."""
        return EndingsManager()

    def test_manager_creation(self, manager):
        """Test manager initialization."""
        assert manager.endings == {}
        assert manager.categories == {}

    def test_register_ending(self, manager, Ending):
        """Test registering an ending."""
        ending = Ending(id="test", name="Test", category="main")

        result = manager.register_ending(ending)

        assert result == ending
        assert "test" in manager.endings
        assert manager.endings["test"] == ending
        assert "main" in manager.categories
        assert "test" in manager.categories["main"]

    def test_create_ending(self, manager):
        """Test create_ending convenience method."""
        ending = manager.create_ending(
            id="created",
            name="Created Ending",
            description="Description",
            hidden=True,
            category="secret"
        )

        assert ending.id == "created"
        assert ending.name == "Created Ending"
        assert "created" in manager.endings
        assert "secret" in manager.categories

    def test_get_ending(self, manager, Ending):
        """Test getting an ending by ID."""
        ending = Ending(id="test", name="Test")
        manager.register_ending(ending)

        result = manager.get_ending("test")
        not_found = manager.get_ending("nonexistent")

        assert result == ending
        assert not_found is None

    def test_remove_ending(self, manager, Ending):
        """Test removing an ending."""
        ending = Ending(id="test", name="Test", category="main")
        manager.register_ending(ending)

        result = manager.remove_ending("test")
        not_found = manager.remove_ending("nonexistent")

        assert result is True
        assert not_found is False
        assert "test" not in manager.endings
        assert "test" not in manager.categories.get("main", [])

    def test_unlock_ending(self, manager, Ending):
        """Test unlocking an ending through manager."""
        ending = Ending(id="test", name="Test")
        manager.register_ending(ending)

        result = manager.unlock_ending("test")
        not_found = manager.unlock_ending("nonexistent")

        assert result is True
        assert not_found is False
        assert ending.unlocked is True

    def test_lock_ending(self, manager, Ending):
        """Test locking an ending through manager."""
        ending = Ending(id="test", name="Test")
        manager.register_ending(ending)
        ending.unlock()

        result = manager.lock_ending("test")

        assert result is True
        assert ending.unlocked is False

    def test_is_ending_unlocked(self, manager, Ending):
        """Test checking if ending is unlocked."""
        ending = Ending(id="test", name="Test")
        manager.register_ending(ending)

        assert manager.is_ending_unlocked("test") is False
        assert manager.is_ending_unlocked("nonexistent") is False

        ending.unlock()

        assert manager.is_ending_unlocked("test") is True

    def test_get_all_endings(self, manager, Ending):
        """Test getting all endings."""
        e1 = Ending(id="a", name="A", priority=2)
        e2 = Ending(id="b", name="B", priority=1)
        e3 = Ending(id="c", name="C", priority=3)

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        all_endings = manager.get_all_endings()

        assert len(all_endings) == 3
        # Should be sorted by priority
        assert all_endings[0].id == "b"
        assert all_endings[1].id == "a"
        assert all_endings[2].id == "c"

    def test_get_unlocked_endings(self, manager, Ending):
        """Test getting only unlocked endings."""
        e1 = Ending(id="unlocked1", name="Unlocked 1")
        e2 = Ending(id="locked", name="Locked")
        e3 = Ending(id="unlocked2", name="Unlocked 2")

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        e1.unlock()
        e3.unlock()

        unlocked = manager.get_unlocked_endings()

        assert len(unlocked) == 2
        assert all(e.unlocked for e in unlocked)

    def test_get_locked_endings(self, manager, Ending):
        """Test getting only locked endings."""
        e1 = Ending(id="unlocked", name="Unlocked")
        e2 = Ending(id="locked1", name="Locked 1")
        e3 = Ending(id="locked2", name="Locked 2")

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        e1.unlock()

        locked = manager.get_locked_endings()

        assert len(locked) == 2
        assert all(not e.unlocked for e in locked)

    def test_get_visible_endings(self, manager, Ending):
        """Test getting visible endings (hides locked hidden endings)."""
        e1 = Ending(id="visible", name="Visible", hidden=False)
        e2 = Ending(id="hidden_locked", name="Hidden Locked", hidden=True)
        e3 = Ending(id="hidden_unlocked", name="Hidden Unlocked", hidden=True)

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        e3.unlock()

        visible = manager.get_visible_endings()

        assert len(visible) == 2
        visible_ids = [e.id for e in visible]
        assert "visible" in visible_ids
        assert "hidden_unlocked" in visible_ids
        assert "hidden_locked" not in visible_ids

    def test_get_hidden_endings(self, manager, Ending):
        """Test getting all hidden endings."""
        e1 = Ending(id="visible", name="Visible", hidden=False)
        e2 = Ending(id="hidden1", name="Hidden 1", hidden=True)
        e3 = Ending(id="hidden2", name="Hidden 2", hidden=True)

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        hidden = manager.get_hidden_endings()

        assert len(hidden) == 2
        assert all(e.hidden for e in hidden)

    def test_get_endings_by_category(self, manager, Ending):
        """Test getting endings by category."""
        e1 = Ending(id="main1", name="Main 1", category="main")
        e2 = Ending(id="secret1", name="Secret 1", category="secret")
        e3 = Ending(id="main2", name="Main 2", category="main")

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        main_endings = manager.get_endings_by_category("main")
        secret_endings = manager.get_endings_by_category("secret")
        empty = manager.get_endings_by_category("nonexistent")

        assert len(main_endings) == 2
        assert len(secret_endings) == 1
        assert len(empty) == 0

    def test_get_categories(self, manager, Ending):
        """Test getting list of categories."""
        e1 = Ending(id="e1", name="E1", category="main")
        e2 = Ending(id="e2", name="E2", category="secret")
        e3 = Ending(id="e3", name="E3", category="romance")

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        categories = manager.get_categories()

        assert "main" in categories
        assert "secret" in categories
        assert "romance" in categories

    def test_completion_percentage_empty(self, manager):
        """Test completion percentage with no endings."""
        assert manager.get_completion_percentage() == 0.0

    def test_completion_percentage_none_unlocked(self, manager, Ending):
        """Test completion percentage with no unlocked endings."""
        manager.register_ending(Ending(id="e1", name="E1"))
        manager.register_ending(Ending(id="e2", name="E2"))

        assert manager.get_completion_percentage() == 0.0

    def test_completion_percentage_partial(self, manager, Ending):
        """Test completion percentage with some unlocked."""
        e1 = Ending(id="e1", name="E1")
        e2 = Ending(id="e2", name="E2")
        e3 = Ending(id="e3", name="E3")
        e4 = Ending(id="e4", name="E4")

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)
        manager.register_ending(e4)

        e1.unlock()
        e3.unlock()

        assert manager.get_completion_percentage() == 50.0

    def test_completion_percentage_all_unlocked(self, manager, Ending):
        """Test completion percentage with all unlocked."""
        e1 = Ending(id="e1", name="E1")
        e2 = Ending(id="e2", name="E2")

        manager.register_ending(e1)
        manager.register_ending(e2)

        e1.unlock()
        e2.unlock()

        assert manager.get_completion_percentage() == 100.0

    def test_category_completion(self, manager, Ending):
        """Test category-specific completion percentage."""
        e1 = Ending(id="m1", name="M1", category="main")
        e2 = Ending(id="m2", name="M2", category="main")
        e3 = Ending(id="s1", name="S1", category="secret")

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        e1.unlock()

        main_completion = manager.get_category_completion("main")
        secret_completion = manager.get_category_completion("secret")
        empty_completion = manager.get_category_completion("nonexistent")

        assert main_completion == 50.0
        assert secret_completion == 0.0
        assert empty_completion == 0.0

    def test_get_stats(self, manager, Ending):
        """Test comprehensive statistics."""
        e1 = Ending(id="m1", name="M1", category="main")
        e2 = Ending(id="m2", name="M2", category="main", hidden=True)
        e3 = Ending(id="s1", name="S1", category="secret", hidden=True)

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        e1.unlock()
        e2.unlock()

        stats = manager.get_stats()

        assert stats["total"] == 3
        assert stats["unlocked"] == 2
        assert stats["locked"] == 1
        assert stats["completion_percentage"] == pytest.approx(66.67, rel=0.01)
        assert stats["hidden_total"] == 2
        assert stats["hidden_unlocked"] == 1
        assert "main" in stats["categories"]
        assert "secret" in stats["categories"]
        assert stats["categories"]["main"]["total"] == 2
        assert stats["categories"]["main"]["unlocked"] == 2

    def test_reset_all(self, manager, Ending):
        """Test resetting all endings."""
        e1 = Ending(id="e1", name="E1")
        e2 = Ending(id="e2", name="E2")
        e3 = Ending(id="e3", name="E3")

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        e1.unlock()
        e2.unlock()

        count = manager.reset_all()

        assert count == 2
        assert e1.unlocked is False
        assert e2.unlocked is False
        assert e3.unlocked is False

    def test_export_import_state(self, manager, Ending):
        """Test exporting and importing state."""
        e1 = Ending(id="e1", name="E1")
        e2 = Ending(id="e2", name="E2")

        manager.register_ending(e1)
        manager.register_ending(e2)

        e1.unlock()

        # Export
        exported = manager.export_state()

        # Reset
        manager.reset_all()
        assert e1.unlocked is False

        # Import
        count = manager.import_state(exported)

        assert count == 2
        assert e1.unlocked is True

    def test_register_requirements_callback(self, manager, Ending):
        """Test registering requirements callback."""
        ending = Ending(id="conditional", name="Conditional")
        manager.register_ending(ending)

        condition_met = False

        def check_condition():
            return condition_met

        manager.register_requirements("conditional", check_condition)

        assert manager.check_requirements("conditional") is False

        condition_met = True

        assert manager.check_requirements("conditional") is True

    def test_check_requirements_no_callback(self, manager, Ending):
        """Test checking requirements when no callback registered."""
        ending = Ending(id="no_callback", name="No Callback")
        manager.register_ending(ending)

        # Should return True if no callback
        assert manager.check_requirements("no_callback") is True

    def test_check_requirements_callback_error(self, manager, Ending):
        """Test that callback errors return False."""
        ending = Ending(id="error", name="Error")
        manager.register_ending(ending)

        def bad_callback():
            raise RuntimeError("Intentional error")

        manager.register_requirements("error", bad_callback)

        assert manager.check_requirements("error") is False

    def test_get_available_endings(self, manager, Ending):
        """Test getting endings with met requirements."""
        e1 = Ending(id="available", name="Available")
        e2 = Ending(id="not_available", name="Not Available")
        e3 = Ending(id="already_unlocked", name="Already Unlocked")

        manager.register_ending(e1)
        manager.register_ending(e2)
        manager.register_ending(e3)

        manager.register_requirements("available", lambda: True)
        manager.register_requirements("not_available", lambda: False)
        manager.register_requirements("already_unlocked", lambda: True)

        e3.unlock()

        available = manager.get_available_endings()

        assert len(available) == 1
        assert available[0].id == "available"


class TestEndingsIntegration:
    """Integration tests for the endings system."""

    @pytest.fixture
    def endings_module(self, load_system):
        """Load the endings module."""
        return load_system("endings")

    @pytest.fixture
    def Ending(self, endings_module):
        """Get the Ending class."""
        return endings_module["Ending"]

    @pytest.fixture
    def EndingsManager(self, endings_module):
        """Get the EndingsManager class."""
        return endings_module["EndingsManager"]

    def test_full_workflow(self, Ending, EndingsManager):
        """Test a complete workflow of using the endings system."""
        manager = EndingsManager()

        # Register various endings
        manager.create_ending("good", "Good Ending", "You did good!", category="main", priority=1)
        manager.create_ending("bad", "Bad Ending", "Things went wrong.", category="main", priority=2)
        manager.create_ending("secret", "Secret Ending", "You found it!",
                             hidden=True, category="secret", priority=10)
        manager.create_ending("romance", "Love Story", "A romantic conclusion.",
                             requirements_hint="Build max affection.", category="romance", priority=5)

        # Initial state
        assert manager.get_completion_percentage() == 0.0
        assert len(manager.get_visible_endings()) == 3  # secret is hidden

        # Unlock some endings
        manager.unlock_ending("good")
        manager.unlock_ending("romance")

        assert manager.get_completion_percentage() == 50.0
        assert len(manager.get_unlocked_endings()) == 2

        # Check category stats
        assert manager.get_category_completion("main") == 50.0
        assert manager.get_category_completion("romance") == 100.0
        assert manager.get_category_completion("secret") == 0.0

        # Unlock secret ending
        manager.unlock_ending("secret")

        # Secret ending should now be visible
        assert len(manager.get_visible_endings()) == 4

        # Full stats
        stats = manager.get_stats()
        assert stats["total"] == 4
        assert stats["unlocked"] == 3
        assert stats["hidden_unlocked"] == 1

    def test_persistent_simulation(self, Ending, EndingsManager):
        """Simulate persistent storage workflow."""
        # First session - unlock some endings
        manager1 = EndingsManager()
        manager1.create_ending("ending1", "Ending 1")
        manager1.create_ending("ending2", "Ending 2")
        manager1.create_ending("ending3", "Ending 3")

        manager1.unlock_ending("ending1")
        manager1.unlock_ending("ending2")

        # Export state (simulating save)
        saved_state = manager1.export_state()

        # Second session - restore state
        manager2 = EndingsManager()
        manager2.create_ending("ending1", "Ending 1")
        manager2.create_ending("ending2", "Ending 2")
        manager2.create_ending("ending3", "Ending 3")

        # Import saved state
        manager2.import_state(saved_state)

        # Verify state restored
        assert manager2.is_ending_unlocked("ending1") is True
        assert manager2.is_ending_unlocked("ending2") is True
        assert manager2.is_ending_unlocked("ending3") is False

    def test_requirements_workflow(self, Ending, EndingsManager):
        """Test requirements checking workflow."""
        manager = EndingsManager()

        manager.create_ending("true_end", "True Ending",
                             requirements_hint="Complete all objectives.")
        manager.create_ending("normal_end", "Normal Ending")

        # Simulated game state
        game_state = {"objectives_complete": 0, "total_objectives": 5}

        def true_ending_requirements():
            return game_state["objectives_complete"] >= game_state["total_objectives"]

        manager.register_requirements("true_end", true_ending_requirements)

        # Initially not available
        available = manager.get_available_endings()
        assert len(available) == 1  # Only normal_end
        assert available[0].id == "normal_end"

        # Complete objectives
        game_state["objectives_complete"] = 5

        # Now true ending is available
        available = manager.get_available_endings()
        assert len(available) == 2

    def test_hidden_endings_display_logic(self, Ending, EndingsManager):
        """Test display logic for hidden endings."""
        manager = EndingsManager()

        hidden_end = manager.create_ending(
            "hidden", "Super Secret",
            description="You found the ultimate secret!",
            hidden=True
        )

        # Before unlock - hidden
        assert hidden_end.get_display_name() == "???"
        assert hidden_end.get_display_description() == "???"

        visible = manager.get_visible_endings()
        assert len(visible) == 0

        # After unlock - revealed
        manager.unlock_ending("hidden")

        assert hidden_end.get_display_name() == "Super Secret"
        assert hidden_end.get_display_description() == "You found the ultimate secret!"

        visible = manager.get_visible_endings()
        assert len(visible) == 1


class TestEndingsEdgeCases:
    """Edge case tests for the endings system."""

    @pytest.fixture
    def endings_module(self, load_system):
        """Load the endings module."""
        return load_system("endings")

    @pytest.fixture
    def Ending(self, endings_module):
        """Get the Ending class."""
        return endings_module["Ending"]

    @pytest.fixture
    def EndingsManager(self, endings_module):
        """Get the EndingsManager class."""
        return endings_module["EndingsManager"]

    def test_empty_manager(self, EndingsManager):
        """Test operations on empty manager."""
        manager = EndingsManager()

        assert manager.get_all_endings() == []
        assert manager.get_unlocked_endings() == []
        assert manager.get_locked_endings() == []
        assert manager.get_completion_percentage() == 0.0
        assert manager.get_stats()["total"] == 0
        assert manager.unlock_ending("nonexistent") is False
        assert manager.lock_ending("nonexistent") is False
        assert manager.check_requirements("nonexistent") is True
        assert manager.get_available_endings() == []

    def test_duplicate_registration(self, EndingsManager, Ending):
        """Test registering same ending ID twice."""
        manager = EndingsManager()

        e1 = Ending(id="dup", name="First")
        e2 = Ending(id="dup", name="Second")

        manager.register_ending(e1)
        manager.register_ending(e2)

        # Second registration overwrites
        assert manager.get_ending("dup").name == "Second"
        assert len(manager.get_all_endings()) == 1

    def test_special_characters_in_id(self, EndingsManager):
        """Test endings with special characters in ID."""
        manager = EndingsManager()

        ending = manager.create_ending(
            id="ending-with_special.chars",
            name="Special Ending"
        )

        assert manager.get_ending("ending-with_special.chars") == ending
        assert manager.unlock_ending("ending-with_special.chars") is True

    def test_unicode_in_name_and_description(self, EndingsManager):
        """Test endings with unicode characters."""
        manager = EndingsManager()

        ending = manager.create_ending(
            id="unicode",
            name="Final Ending",
            description="You achieved everything!"
        )

        assert ending.name == "Final Ending"
        assert ending.get_display_name() == "Final Ending"

    def test_long_description(self, EndingsManager):
        """Test endings with very long descriptions."""
        manager = EndingsManager()

        long_desc = "A" * 10000

        ending = manager.create_ending(
            id="long",
            name="Long",
            description=long_desc
        )

        ending.unlock()
        assert len(ending.get_display_description()) == 10000

    def test_many_endings(self, EndingsManager):
        """Test manager with many endings."""
        manager = EndingsManager()

        for i in range(100):
            manager.create_ending(
                id=f"ending_{i}",
                name=f"Ending {i}",
                category=f"category_{i % 5}",
                priority=i
            )

        assert len(manager.get_all_endings()) == 100
        assert len(manager.get_categories()) == 5

        # Unlock half
        for i in range(0, 100, 2):
            manager.unlock_ending(f"ending_{i}")

        assert manager.get_completion_percentage() == 50.0

    def test_category_with_removed_ending(self, EndingsManager, Ending):
        """Test that removing ending updates category properly."""
        manager = EndingsManager()

        manager.create_ending("e1", "E1", category="test")
        manager.create_ending("e2", "E2", category="test")

        assert len(manager.get_endings_by_category("test")) == 2

        manager.remove_ending("e1")

        assert len(manager.get_endings_by_category("test")) == 1
        assert manager.get_endings_by_category("test")[0].id == "e2"

    def test_from_dict_with_none(self, Ending):
        """Test from_dict with None data."""
        ending = Ending(id="test", name="Test")
        ending.unlock()

        # Should not crash, should not change state
        ending.from_dict(None)

        assert ending.unlocked is True

    def test_from_dict_with_empty(self, Ending):
        """Test from_dict with empty dict."""
        ending = Ending(id="test", name="Test")
        ending.unlock()

        ending.from_dict({})

        assert ending.unlocked is True  # State unchanged

    def test_priority_sorting(self, EndingsManager, Ending):
        """Test that endings are sorted by priority then name."""
        manager = EndingsManager()

        manager.create_ending("c", "Charlie", priority=1)
        manager.create_ending("a", "Alpha", priority=1)
        manager.create_ending("b", "Bravo", priority=2)

        endings = manager.get_all_endings()

        # Same priority sorts by name
        assert endings[0].id == "a"  # Alpha, priority 1
        assert endings[1].id == "c"  # Charlie, priority 1
        assert endings[2].id == "b"  # Bravo, priority 2

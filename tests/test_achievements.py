"""
Comprehensive tests for the Achievement System.

Tests cover:
- Achievement class functionality
- ProgressAchievement subclass with progress tracking
- AchievementManager registration, unlocking, and queries
- Notification system
- Persistence (save/load)
- Points calculation
"""
import pytest
from datetime import datetime


class TestAchievement:
    """Tests for the base Achievement class."""

    @pytest.fixture
    def system(self, load_system):
        """Load the achievements system."""
        return load_system("achievements")

    @pytest.fixture
    def Achievement(self, system):
        """Get the Achievement class."""
        return system["Achievement"]

    def test_achievement_creation(self, Achievement):
        """Test creating an achievement with default values."""
        ach = Achievement(
            id="test_ach",
            name="Test Achievement",
            description="A test achievement"
        )

        assert ach.id == "test_ach"
        assert ach.name == "Test Achievement"
        assert ach.description == "A test achievement"
        assert ach.icon is None
        assert ach.points == 10  # default
        assert ach.hidden is False
        assert ach.unlocked is False
        assert ach.unlock_date is None
        assert ach.category == "story"

    def test_achievement_creation_with_options(self, Achievement):
        """Test creating an achievement with custom values."""
        ach = Achievement(
            id="custom_ach",
            name="Custom Achievement",
            description="A custom achievement",
            icon="icons/custom.png",
            points=50,
            hidden=True,
            category="challenge"
        )

        assert ach.id == "custom_ach"
        assert ach.icon == "icons/custom.png"
        assert ach.points == 50
        assert ach.hidden is True
        assert ach.category == "challenge"

    def test_achievement_unlock(self, Achievement):
        """Test unlocking an achievement."""
        ach = Achievement(
            id="test_ach",
            name="Test",
            description="Test"
        )

        assert ach.unlocked is False
        assert ach.unlock_date is None

        # Unlock should return True for first unlock
        result = ach.unlock()
        assert result is True
        assert ach.unlocked is True
        assert ach.unlock_date is not None
        assert isinstance(ach.unlock_date, datetime)

    def test_achievement_unlock_idempotent(self, Achievement):
        """Test that unlocking an already unlocked achievement returns False."""
        ach = Achievement(
            id="test_ach",
            name="Test",
            description="Test"
        )

        # First unlock
        result1 = ach.unlock()
        unlock_date1 = ach.unlock_date

        # Second unlock
        result2 = ach.unlock()

        assert result1 is True
        assert result2 is False
        # Date should not change
        assert ach.unlock_date == unlock_date1

    def test_hidden_achievement_display(self, Achievement):
        """Test that hidden achievements show ??? when locked."""
        ach = Achievement(
            id="hidden_ach",
            name="Secret Achievement",
            description="Find the secret",
            hidden=True
        )

        # When locked, should show ???
        assert ach.get_display_name() == "???"
        assert ach.get_display_description() == "This achievement is hidden."

        # After unlock, should show real values
        ach.unlock()
        assert ach.get_display_name() == "Secret Achievement"
        assert ach.get_display_description() == "Find the secret"

    def test_non_hidden_achievement_display(self, Achievement):
        """Test that non-hidden achievements always show real values."""
        ach = Achievement(
            id="visible_ach",
            name="Visible Achievement",
            description="Easy to see",
            hidden=False
        )

        # Should show real values even when locked
        assert ach.get_display_name() == "Visible Achievement"
        assert ach.get_display_description() == "Easy to see"

    def test_achievement_serialization(self, Achievement):
        """Test achievement to_dict serialization."""
        ach = Achievement(
            id="test_ach",
            name="Test",
            description="Test"
        )

        # Serialize before unlock
        data = ach.to_dict()
        assert data["id"] == "test_ach"
        assert data["unlocked"] is False
        assert data["unlock_date"] is None

        # Serialize after unlock
        ach.unlock()
        data = ach.to_dict()
        assert data["unlocked"] is True
        assert data["unlock_date"] is not None

    def test_achievement_deserialization(self, Achievement):
        """Test achievement from_dict deserialization."""
        ach = Achievement(
            id="test_ach",
            name="Test",
            description="Test"
        )

        # Restore unlocked state
        data = {
            "id": "test_ach",
            "unlocked": True,
            "unlock_date": "2024-01-15T10:30:00"
        }

        ach.from_dict(data)

        assert ach.unlocked is True
        assert ach.unlock_date is not None
        assert ach.unlock_date.year == 2024
        assert ach.unlock_date.month == 1
        assert ach.unlock_date.day == 15


class TestProgressAchievement:
    """Tests for the ProgressAchievement subclass."""

    @pytest.fixture
    def system(self, load_system):
        """Load the achievements system."""
        return load_system("achievements")

    @pytest.fixture
    def ProgressAchievement(self, system):
        """Get the ProgressAchievement class."""
        return system["ProgressAchievement"]

    def test_progress_achievement_creation(self, ProgressAchievement):
        """Test creating a progress achievement."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Progress Test",
            description="Complete 10 tasks",
            target=10
        )

        assert ach.id == "progress_ach"
        assert ach.current == 0
        assert ach.target == 10
        assert ach.unlocked is False

    def test_add_progress(self, ProgressAchievement):
        """Test adding progress to an achievement."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=5
        )

        # Add progress incrementally
        result = ach.add_progress(1)
        assert ach.current == 1
        assert result is False  # Not unlocked yet

        result = ach.add_progress(2)
        assert ach.current == 3
        assert result is False

        # This should unlock
        result = ach.add_progress(2)
        assert ach.current == 5
        assert result is True
        assert ach.unlocked is True

    def test_add_progress_with_default_amount(self, ProgressAchievement):
        """Test adding progress with default amount of 1."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=3
        )

        ach.add_progress()
        assert ach.current == 1

        ach.add_progress()
        assert ach.current == 2

    def test_add_progress_clamped_to_target(self, ProgressAchievement):
        """Test that progress cannot exceed target."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=5
        )

        ach.add_progress(10)
        assert ach.current == 5
        assert ach.unlocked is True

    def test_add_progress_after_unlock_does_nothing(self, ProgressAchievement):
        """Test that adding progress after unlock returns False."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=3
        )

        ach.add_progress(3)  # Unlock
        assert ach.unlocked is True

        result = ach.add_progress(1)
        assert result is False
        assert ach.current == 3  # Unchanged

    def test_set_progress(self, ProgressAchievement):
        """Test setting progress to a specific value."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=10
        )

        result = ach.set_progress(5)
        assert ach.current == 5
        assert result is False

        result = ach.set_progress(10)
        assert ach.current == 10
        assert result is True
        assert ach.unlocked is True

    def test_set_progress_clamped(self, ProgressAchievement):
        """Test that set_progress is clamped to valid range."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=10
        )

        ach.set_progress(-5)
        assert ach.current == 0

        ach.set_progress(100)
        assert ach.current == 10

    def test_progress_percent(self, ProgressAchievement):
        """Test progress percentage calculation."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=10
        )

        assert ach.get_progress_percent() == 0

        ach.set_progress(5)
        assert ach.get_progress_percent() == 50

        ach.set_progress(10)
        assert ach.get_progress_percent() == 100

    def test_progress_percent_zero_target(self, ProgressAchievement):
        """Test progress percentage with zero target (edge case)."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=0
        )

        # Should not divide by zero
        assert ach.get_progress_percent() == 100

    def test_progress_text(self, ProgressAchievement):
        """Test progress text formatting."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=10
        )

        assert ach.get_progress_text() == "0/10"

        ach.set_progress(7)
        assert ach.get_progress_text() == "7/10"

    def test_progress_achievement_display_description(self, ProgressAchievement):
        """Test that progress is shown in description."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Collect items",
            target=10
        )

        ach.set_progress(3)
        desc = ach.get_display_description()
        assert "3/10" in desc

    def test_progress_achievement_serialization(self, ProgressAchievement):
        """Test progress achievement serialization includes current."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=10
        )

        ach.set_progress(7)
        data = ach.to_dict()

        assert data["current"] == 7

    def test_progress_achievement_deserialization(self, ProgressAchievement):
        """Test progress achievement deserialization restores current."""
        ach = ProgressAchievement(
            id="progress_ach",
            name="Test",
            description="Test",
            target=10
        )

        data = {
            "id": "progress_ach",
            "unlocked": False,
            "unlock_date": None,
            "current": 5
        }

        ach.from_dict(data)
        assert ach.current == 5


class TestAchievementManager:
    """Tests for the AchievementManager class."""

    @pytest.fixture
    def system(self, load_system):
        """Load the achievements system."""
        return load_system("achievements")

    @pytest.fixture
    def AchievementManager(self, system):
        """Get the AchievementManager class."""
        return system["AchievementManager"]

    @pytest.fixture
    def Achievement(self, system):
        """Get the Achievement class."""
        return system["Achievement"]

    @pytest.fixture
    def ProgressAchievement(self, system):
        """Get the ProgressAchievement class."""
        return system["ProgressAchievement"]

    @pytest.fixture
    def manager(self, AchievementManager):
        """Create a fresh AchievementManager instance."""
        return AchievementManager()

    # -------------------------------------------------------------------------
    # Registration Tests
    # -------------------------------------------------------------------------

    def test_register_achievement(self, manager, Achievement):
        """Test registering an achievement."""
        ach = Achievement(
            id="test_ach",
            name="Test",
            description="Test"
        )

        result = manager.register(ach)

        assert result is ach
        assert "test_ach" in manager.achievements
        assert manager.get("test_ach") is ach

    def test_register_achievement_helper(self, manager):
        """Test the register_achievement helper method."""
        ach = manager.register_achievement(
            id="helper_ach",
            name="Helper Achievement",
            description="Created via helper",
            points=25,
            hidden=True,
            category="challenge"
        )

        assert ach.id == "helper_ach"
        assert ach.name == "Helper Achievement"
        assert ach.points == 25
        assert ach.hidden is True
        assert manager.get("helper_ach") is ach

    def test_register_progress_achievement_helper(self, manager):
        """Test the register_progress_achievement helper method."""
        ach = manager.register_progress_achievement(
            id="progress_helper",
            name="Progress Helper",
            description="Progress via helper",
            target=20,
            points=30
        )

        assert ach.id == "progress_helper"
        assert ach.target == 20
        assert ach.current == 0
        assert manager.get("progress_helper") is ach

    # -------------------------------------------------------------------------
    # Unlock Tests
    # -------------------------------------------------------------------------

    def test_unlock_achievement(self, manager):
        """Test unlocking an achievement through the manager."""
        manager.register_achievement(
            id="unlock_test",
            name="Test",
            description="Test"
        )

        result = manager.unlock("unlock_test", notify=False)

        assert result is True
        assert manager.get("unlock_test").unlocked is True

    def test_unlock_nonexistent_achievement(self, manager):
        """Test unlocking a non-existent achievement returns False."""
        result = manager.unlock("nonexistent", notify=False)
        assert result is False

    def test_unlock_already_unlocked(self, manager):
        """Test unlocking an already unlocked achievement returns False."""
        manager.register_achievement(
            id="unlock_test",
            name="Test",
            description="Test"
        )

        manager.unlock("unlock_test", notify=False)
        result = manager.unlock("unlock_test", notify=False)

        assert result is False

    def test_unlock_queues_notification(self, manager):
        """Test that unlock queues a notification by default."""
        manager.register_achievement(
            id="notify_test",
            name="Test",
            description="Test"
        )

        manager.unlock("notify_test", notify=True)

        assert manager.has_pending_notifications()
        assert len(manager.notification_queue) == 1

    def test_unlock_no_notification_when_disabled(self, manager):
        """Test that unlock does not queue notification when disabled."""
        manager.register_achievement(
            id="no_notify",
            name="Test",
            description="Test"
        )

        manager.unlock("no_notify", notify=False)

        assert not manager.has_pending_notifications()

    # -------------------------------------------------------------------------
    # Progress Tests
    # -------------------------------------------------------------------------

    def test_add_progress_through_manager(self, manager):
        """Test adding progress through the manager."""
        manager.register_progress_achievement(
            id="progress_test",
            name="Test",
            description="Test",
            target=5
        )

        result = manager.add_progress("progress_test", 3, notify=False)
        assert result is False
        assert manager.get("progress_test").current == 3

        result = manager.add_progress("progress_test", 2, notify=False)
        assert result is True  # Unlocked
        assert manager.get("progress_test").unlocked is True

    def test_add_progress_to_regular_achievement(self, manager):
        """Test that adding progress to non-progress achievement returns False."""
        manager.register_achievement(
            id="regular",
            name="Test",
            description="Test"
        )

        result = manager.add_progress("regular", 1, notify=False)
        assert result is False

    def test_add_progress_nonexistent(self, manager):
        """Test adding progress to non-existent achievement returns False."""
        result = manager.add_progress("nonexistent", 1, notify=False)
        assert result is False

    def test_set_progress_through_manager(self, manager):
        """Test setting progress through the manager."""
        manager.register_progress_achievement(
            id="set_progress_test",
            name="Test",
            description="Test",
            target=10
        )

        result = manager.set_progress("set_progress_test", 10, notify=False)
        assert result is True
        assert manager.get("set_progress_test").unlocked is True

    def test_set_progress_to_regular_achievement(self, manager):
        """Test that setting progress on non-progress achievement returns False."""
        manager.register_achievement(
            id="regular",
            name="Test",
            description="Test"
        )

        result = manager.set_progress("regular", 5, notify=False)
        assert result is False

    # -------------------------------------------------------------------------
    # Query Tests
    # -------------------------------------------------------------------------

    def test_get_all(self, manager):
        """Test getting all achievements."""
        manager.register_achievement("ach1", "Ach1", "Desc1")
        manager.register_achievement("ach2", "Ach2", "Desc2")
        manager.register_achievement("ach3", "Ach3", "Desc3")

        all_achs = manager.get_all()
        assert len(all_achs) == 3

    def test_get_unlocked(self, manager):
        """Test getting unlocked achievements."""
        manager.register_achievement("ach1", "Ach1", "Desc1")
        manager.register_achievement("ach2", "Ach2", "Desc2")
        manager.register_achievement("ach3", "Ach3", "Desc3")

        manager.unlock("ach1", notify=False)
        manager.unlock("ach3", notify=False)

        unlocked = manager.get_unlocked()
        assert len(unlocked) == 2
        assert all(a.unlocked for a in unlocked)

    def test_get_locked(self, manager):
        """Test getting locked achievements."""
        manager.register_achievement("ach1", "Ach1", "Desc1")
        manager.register_achievement("ach2", "Ach2", "Desc2")
        manager.register_achievement("ach3", "Ach3", "Desc3")

        manager.unlock("ach1", notify=False)

        locked = manager.get_locked()
        assert len(locked) == 2
        assert all(not a.unlocked for a in locked)

    def test_get_by_category(self, manager):
        """Test getting achievements by category."""
        manager.register_achievement("story1", "Story1", "Desc", category="story")
        manager.register_achievement("story2", "Story2", "Desc", category="story")
        manager.register_achievement("challenge1", "Challenge1", "Desc", category="challenge")

        story_achs = manager.get_by_category("story")
        challenge_achs = manager.get_by_category("challenge")

        assert len(story_achs) == 2
        assert len(challenge_achs) == 1

    def test_get_unlocked_by_category(self, manager):
        """Test getting unlocked achievements by category."""
        manager.register_achievement("story1", "Story1", "Desc", category="story")
        manager.register_achievement("story2", "Story2", "Desc", category="story")
        manager.register_achievement("challenge1", "Challenge1", "Desc", category="challenge")

        manager.unlock("story1", notify=False)
        manager.unlock("challenge1", notify=False)

        story_unlocked = manager.get_unlocked_by_category("story")
        challenge_unlocked = manager.get_unlocked_by_category("challenge")

        assert len(story_unlocked) == 1
        assert len(challenge_unlocked) == 1

    def test_get_visible(self, manager):
        """Test getting visible achievements (not hidden or unlocked)."""
        manager.register_achievement("visible1", "Visible1", "Desc", hidden=False)
        manager.register_achievement("hidden1", "Hidden1", "Desc", hidden=True)
        manager.register_achievement("hidden2", "Hidden2", "Desc", hidden=True)

        # Initially only visible1 is visible
        visible = manager.get_visible()
        assert len(visible) == 1

        # After unlocking hidden1, it becomes visible too
        manager.unlock("hidden1", notify=False)
        visible = manager.get_visible()
        assert len(visible) == 2

    # -------------------------------------------------------------------------
    # Statistics Tests
    # -------------------------------------------------------------------------

    def test_get_total_points(self, manager):
        """Test calculating total points from unlocked achievements."""
        manager.register_achievement("ach1", "Ach1", "Desc", points=10)
        manager.register_achievement("ach2", "Ach2", "Desc", points=25)
        manager.register_achievement("ach3", "Ach3", "Desc", points=50)

        manager.unlock("ach1", notify=False)
        manager.unlock("ach3", notify=False)

        assert manager.get_total_points() == 60

    def test_get_max_points(self, manager):
        """Test calculating maximum possible points."""
        manager.register_achievement("ach1", "Ach1", "Desc", points=10)
        manager.register_achievement("ach2", "Ach2", "Desc", points=25)
        manager.register_achievement("ach3", "Ach3", "Desc", points=50)

        assert manager.get_max_points() == 85

    def test_get_unlock_count(self, manager):
        """Test counting unlocked achievements."""
        manager.register_achievement("ach1", "Ach1", "Desc")
        manager.register_achievement("ach2", "Ach2", "Desc")
        manager.register_achievement("ach3", "Ach3", "Desc")

        assert manager.get_unlock_count() == 0

        manager.unlock("ach1", notify=False)
        manager.unlock("ach2", notify=False)

        assert manager.get_unlock_count() == 2

    def test_get_total_count(self, manager):
        """Test counting total achievements."""
        manager.register_achievement("ach1", "Ach1", "Desc")
        manager.register_achievement("ach2", "Ach2", "Desc")
        manager.register_achievement("ach3", "Ach3", "Desc")

        assert manager.get_total_count() == 3

    def test_get_completion_percent(self, manager):
        """Test calculating completion percentage."""
        manager.register_achievement("ach1", "Ach1", "Desc")
        manager.register_achievement("ach2", "Ach2", "Desc")
        manager.register_achievement("ach3", "Ach3", "Desc")
        manager.register_achievement("ach4", "Ach4", "Desc")

        assert manager.get_completion_percent() == 0

        manager.unlock("ach1", notify=False)
        manager.unlock("ach2", notify=False)

        assert manager.get_completion_percent() == 50

    def test_get_completion_percent_empty(self, manager):
        """Test completion percentage with no achievements."""
        assert manager.get_completion_percent() == 100

    # -------------------------------------------------------------------------
    # Notification Tests
    # -------------------------------------------------------------------------

    def test_has_pending_notifications(self, manager):
        """Test checking for pending notifications."""
        manager.register_achievement("ach1", "Ach1", "Desc")

        assert not manager.has_pending_notifications()

        manager.unlock("ach1", notify=True)

        assert manager.has_pending_notifications()

    def test_get_pending_notification(self, manager):
        """Test getting pending notifications in FIFO order."""
        manager.register_achievement("ach1", "Ach1", "Desc")
        manager.register_achievement("ach2", "Ach2", "Desc")

        manager.unlock("ach1", notify=True)
        manager.unlock("ach2", notify=True)

        notification1 = manager.get_pending_notification()
        assert notification1.id == "ach1"

        notification2 = manager.get_pending_notification()
        assert notification2.id == "ach2"

        notification3 = manager.get_pending_notification()
        assert notification3 is None

    def test_notification_queue_empty_returns_none(self, manager):
        """Test that getting notification from empty queue returns None."""
        result = manager.get_pending_notification()
        assert result is None


class TestAchievementIntegration:
    """Integration tests for the achievement system."""

    @pytest.fixture
    def system(self, load_system):
        """Load the achievements system."""
        return load_system("achievements")

    @pytest.fixture
    def AchievementManager(self, system):
        """Get the AchievementManager class."""
        return system["AchievementManager"]

    def test_full_workflow(self, AchievementManager):
        """Test a complete achievement workflow."""
        manager = AchievementManager()

        # Register various achievements
        manager.register_achievement(
            "start_game", "First Steps", "Start the game", points=10
        )
        manager.register_achievement(
            "beat_boss", "Boss Slayer", "Defeat the boss", points=50
        )
        manager.register_progress_achievement(
            "collect_coins", "Coin Collector", "Collect 100 coins",
            target=100, points=25
        )
        manager.register_achievement(
            "secret", "Secret Finder", "Find the secret",
            hidden=True, points=30
        )

        # Initial state
        assert manager.get_total_count() == 4
        assert manager.get_unlock_count() == 0
        assert manager.get_total_points() == 0

        # Unlock first achievement
        manager.unlock("start_game", notify=False)
        assert manager.get_unlock_count() == 1
        assert manager.get_total_points() == 10

        # Add progress
        for _ in range(50):
            manager.add_progress("collect_coins", 1, notify=False)

        ach = manager.get("collect_coins")
        assert ach.current == 50
        assert not ach.unlocked

        # Complete progress
        manager.add_progress("collect_coins", 50, notify=False)
        assert manager.get("collect_coins").unlocked

        # Check stats
        assert manager.get_unlock_count() == 2
        assert manager.get_total_points() == 35

        # Unlock all remaining
        manager.unlock("beat_boss", notify=False)
        manager.unlock("secret", notify=False)

        assert manager.get_completion_percent() == 100
        assert manager.get_total_points() == 115

    def test_multiple_managers_independent(self, AchievementManager):
        """Test that multiple managers are independent."""
        manager1 = AchievementManager()
        manager2 = AchievementManager()

        manager1.register_achievement("ach1", "Ach1", "Desc")
        manager2.register_achievement("ach2", "Ach2", "Desc")

        manager1.unlock("ach1", notify=False)

        assert manager1.get_unlock_count() == 1
        assert manager2.get_unlock_count() == 0
        assert "ach1" not in manager2.achievements
        assert "ach2" not in manager1.achievements


class TestAchievementCategories:
    """Tests for achievement categories."""

    @pytest.fixture
    def system(self, load_system):
        """Load the achievements system."""
        return load_system("achievements")

    def test_categories_defined(self, system):
        """Test that achievement categories are defined."""
        categories = system["ACHIEVEMENT_CATEGORIES"]

        assert "story" in categories
        assert "exploration" in categories
        assert "social" in categories
        assert "completion" in categories
        assert "challenge" in categories
        assert "secret" in categories

    def test_category_structure(self, system):
        """Test that categories have required fields."""
        categories = system["ACHIEVEMENT_CATEGORIES"]

        for cat_id, cat_data in categories.items():
            assert "label" in cat_data
            assert "description" in cat_data


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def system(self, load_system):
        """Load the achievements system."""
        return load_system("achievements")

    @pytest.fixture
    def AchievementManager(self, system):
        """Get the AchievementManager class."""
        return system["AchievementManager"]

    @pytest.fixture
    def ProgressAchievement(self, system):
        """Get the ProgressAchievement class."""
        return system["ProgressAchievement"]

    def test_zero_point_achievement(self, AchievementManager):
        """Test achievement with zero points."""
        manager = AchievementManager()
        manager.register_achievement("zero", "Zero Points", "Worth nothing", points=0)

        manager.unlock("zero", notify=False)
        assert manager.get_total_points() == 0

    def test_very_high_target_progress(self, ProgressAchievement):
        """Test progress achievement with very high target."""
        ach = ProgressAchievement(
            id="high_target",
            name="Grind",
            description="Do this a million times",
            target=1000000
        )

        ach.add_progress(999999)
        assert not ach.unlocked
        assert ach.get_progress_percent() == 99

        ach.add_progress(1)
        assert ach.unlocked

    def test_empty_manager_statistics(self, AchievementManager):
        """Test statistics on empty manager."""
        manager = AchievementManager()

        assert manager.get_total_count() == 0
        assert manager.get_unlock_count() == 0
        assert manager.get_total_points() == 0
        assert manager.get_max_points() == 0
        assert manager.get_completion_percent() == 100  # 0/0 = 100%

    def test_get_nonexistent_achievement(self, AchievementManager):
        """Test getting a non-existent achievement returns None."""
        manager = AchievementManager()
        result = manager.get("nonexistent")
        assert result is None

    def test_special_characters_in_id(self, AchievementManager):
        """Test achievement IDs with special characters."""
        manager = AchievementManager()

        manager.register_achievement(
            "ach_with-special.chars",
            "Special ID",
            "Has special chars in ID"
        )

        ach = manager.get("ach_with-special.chars")
        assert ach is not None
        assert ach.name == "Special ID"

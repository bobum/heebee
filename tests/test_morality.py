"""
Tests for the Morality/Karma System.

This module contains comprehensive tests for the MoralityManager class,
karma modification, alignment calculation, karma-gated content, and decay.
"""
import pytest
import sys
import time
from pathlib import Path

# Add tests directory to path to import conftest utilities
TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR))

from conftest import load_rpy_classes, GAME_DIR


class TestMoralityManager:
    """Tests for the MoralityManager class."""

    @pytest.fixture
    def morality_namespace(self):
        """Load the morality system from morality.rpy."""
        rpy_path = GAME_DIR / "morality.rpy"
        if not rpy_path.exists():
            pytest.skip("morality.rpy not found")
        return load_rpy_classes(rpy_path)

    @pytest.fixture
    def MoralityManager(self, morality_namespace):
        """Get the MoralityManager class."""
        return morality_namespace["MoralityManager"]

    @pytest.fixture
    def KarmaEntry(self, morality_namespace):
        """Get the KarmaEntry class."""
        return morality_namespace["KarmaEntry"]

    @pytest.fixture
    def manager(self, MoralityManager):
        """Create a fresh MoralityManager instance."""
        return MoralityManager()

    # -------------------------------------------------------------------------
    # Initialization Tests
    # -------------------------------------------------------------------------

    def test_default_initialization(self, MoralityManager):
        """Test that MoralityManager initializes with correct defaults."""
        manager = MoralityManager()
        assert manager.karma == 0
        assert manager.karma_history == []
        assert manager.decay_enabled is False
        assert len(manager._unlocked_content) == 0

    def test_custom_initial_karma(self, MoralityManager):
        """Test initialization with custom karma value."""
        manager = MoralityManager(initial_karma=50)
        assert manager.karma == 50

    def test_initial_karma_clamped_max(self, MoralityManager):
        """Test that initial karma is clamped to max value."""
        manager = MoralityManager(initial_karma=150)
        assert manager.karma == 100

    def test_initial_karma_clamped_min(self, MoralityManager):
        """Test that initial karma is clamped to min value."""
        manager = MoralityManager(initial_karma=-150)
        assert manager.karma == -100

    def test_decay_initialization(self, MoralityManager):
        """Test initialization with decay enabled."""
        manager = MoralityManager(decay_enabled=True, decay_rate=2, decay_interval=60)
        assert manager.decay_enabled is True
        assert manager.decay_rate == 2
        assert manager.decay_interval == 60

    # -------------------------------------------------------------------------
    # Karma Modification Tests
    # -------------------------------------------------------------------------

    def test_modify_karma_positive(self, manager):
        """Test adding positive karma."""
        new_karma, unlocks = manager.modify_karma(10, "Did a good deed")
        assert new_karma == 10
        assert manager.karma == 10

    def test_modify_karma_negative(self, manager):
        """Test adding negative karma."""
        new_karma, unlocks = manager.modify_karma(-15, "Stole something")
        assert new_karma == -15
        assert manager.karma == -15

    def test_modify_karma_multiple(self, manager):
        """Test multiple karma modifications."""
        manager.modify_karma(20, "Good deed 1")
        manager.modify_karma(-5, "Minor bad deed")
        manager.modify_karma(10, "Good deed 2")
        assert manager.karma == 25

    def test_karma_clamped_at_max(self, manager):
        """Test that karma doesn't exceed maximum."""
        manager.modify_karma(150, "Heroic action")
        assert manager.karma == 100

    def test_karma_clamped_at_min(self, manager):
        """Test that karma doesn't go below minimum."""
        manager.modify_karma(-150, "Terrible action")
        assert manager.karma == -100

    def test_karma_history_recorded(self, manager):
        """Test that karma changes are recorded in history."""
        manager.modify_karma(10, "First deed")
        manager.modify_karma(-5, "Second deed")

        assert len(manager.karma_history) == 2
        assert manager.karma_history[0].amount == 10
        assert manager.karma_history[0].reason == "First deed"
        assert manager.karma_history[1].amount == -5
        assert manager.karma_history[1].reason == "Second deed"

    def test_karma_history_stores_resulting_karma(self, manager):
        """Test that history entries store the resulting karma value."""
        manager.modify_karma(10, "First")
        manager.modify_karma(15, "Second")

        assert manager.karma_history[0].resulting_karma == 10
        assert manager.karma_history[1].resulting_karma == 25

    # -------------------------------------------------------------------------
    # Alignment Tests
    # -------------------------------------------------------------------------

    def test_alignment_neutral_at_zero(self, manager):
        """Test neutral alignment at karma 0."""
        align_id, align_label, color = manager.get_alignment()
        assert align_id == "neutral"
        assert align_label == "Neutral"

    def test_alignment_neutral_range(self, manager):
        """Test neutral alignment within range."""
        manager.karma = 30
        assert manager.get_alignment_id() == "neutral"

        manager.karma = -30
        assert manager.get_alignment_id() == "neutral"

    def test_alignment_good(self, manager):
        """Test good alignment when karma is high."""
        manager.karma = 50
        align_id, align_label, color = manager.get_alignment()
        assert align_id == "good"
        assert align_label == "Good"
        assert color == "#33ff33"

    def test_alignment_evil(self, manager):
        """Test evil alignment when karma is low."""
        manager.karma = -50
        align_id, align_label, color = manager.get_alignment()
        assert align_id == "evil"
        assert align_label == "Evil"
        assert color == "#ff3333"

    def test_alignment_threshold_good_boundary(self, manager):
        """Test alignment at good threshold boundary."""
        manager.karma = 31
        assert manager.get_alignment_id() == "good"

        manager.karma = 30
        assert manager.get_alignment_id() == "neutral"

    def test_alignment_threshold_evil_boundary(self, manager):
        """Test alignment at evil threshold boundary."""
        manager.karma = -31
        assert manager.get_alignment_id() == "evil"

        manager.karma = -30
        assert manager.get_alignment_id() == "neutral"

    def test_alignment_property(self, manager):
        """Test the alignment property."""
        manager.karma = 50
        assert manager.alignment == ("good", "Good", "#33ff33")

    def test_get_alignment_label(self, manager):
        """Test get_alignment_label method."""
        manager.karma = -50
        assert manager.get_alignment_label() == "Evil"

    def test_get_alignment_color(self, manager):
        """Test get_alignment_color method."""
        manager.karma = 50
        assert manager.get_alignment_color() == "#33ff33"

    # -------------------------------------------------------------------------
    # Karma History Tests
    # -------------------------------------------------------------------------

    def test_get_karma_history_newest_first(self, manager):
        """Test that get_karma_history returns newest entries first."""
        manager.modify_karma(10, "First")
        manager.modify_karma(20, "Second")
        manager.modify_karma(30, "Third")

        history = manager.get_karma_history()
        assert len(history) == 3
        assert history[0].reason == "Third"
        assert history[1].reason == "Second"
        assert history[2].reason == "First"

    def test_get_karma_history_with_limit(self, manager):
        """Test get_karma_history with limit."""
        for i in range(10):
            manager.modify_karma(1, f"Deed {i}")

        history = manager.get_karma_history(limit=3)
        assert len(history) == 3
        assert history[0].reason == "Deed 9"

    def test_get_total_positive_karma(self, manager):
        """Test calculating total positive karma."""
        manager.modify_karma(10, "Good 1")
        manager.modify_karma(-5, "Bad 1")
        manager.modify_karma(20, "Good 2")

        assert manager.get_total_positive_karma() == 30

    def test_get_total_negative_karma(self, manager):
        """Test calculating total negative karma (as positive number)."""
        manager.modify_karma(10, "Good 1")
        manager.modify_karma(-5, "Bad 1")
        manager.modify_karma(-15, "Bad 2")

        assert manager.get_total_negative_karma() == 20

    def test_clear_history(self, manager):
        """Test clearing karma history."""
        manager.modify_karma(10, "Deed")
        manager.modify_karma(20, "Another deed")
        manager.clear_history()

        assert len(manager.karma_history) == 0
        assert manager.karma == 30  # Karma value preserved

    # -------------------------------------------------------------------------
    # Karma-Gated Content Tests
    # -------------------------------------------------------------------------

    def test_content_unlock_positive_threshold(self, manager):
        """Test content unlocks at positive karma thresholds."""
        # Start at 0, need 30 for trusted_helper
        new_karma, unlocks = manager.modify_karma(35, "Good deeds")
        assert "trusted_helper" in unlocks
        assert manager.is_content_available("trusted_helper")

    def test_content_unlock_negative_threshold(self, manager):
        """Test content unlocks at negative karma thresholds."""
        # Need -30 for intimidation_option
        new_karma, unlocks = manager.modify_karma(-35, "Bad deeds")
        assert "intimidation_option" in unlocks
        assert manager.is_content_available("intimidation_option")

    def test_content_not_unlocked_below_threshold(self, manager):
        """Test content remains locked below threshold."""
        manager.modify_karma(25, "Good deeds")
        assert not manager.is_content_available("trusted_helper")

    def test_content_stays_unlocked(self, manager):
        """Test that unlocked content stays unlocked even if karma changes."""
        manager.modify_karma(35, "Unlock trusted_helper")
        assert manager.is_content_available("trusted_helper")

        manager.modify_karma(-20, "Some bad deed")
        assert manager.is_content_available("trusted_helper")

    def test_multiple_unlocks_at_once(self, manager):
        """Test multiple content unlocks in one karma change."""
        new_karma, unlocks = manager.modify_karma(85, "Massive good deed")
        # Should unlock trusted_helper (30), hero_recognition (50), saintly_blessing (80)
        assert "trusted_helper" in unlocks
        assert "hero_recognition" in unlocks
        assert "saintly_blessing" in unlocks

    def test_check_karma_requirement_min(self, manager):
        """Test check_karma_requirement with min_karma."""
        manager.karma = 40
        assert manager.check_karma_requirement(min_karma=30) is True
        assert manager.check_karma_requirement(min_karma=50) is False

    def test_check_karma_requirement_max(self, manager):
        """Test check_karma_requirement with max_karma."""
        manager.karma = -40
        assert manager.check_karma_requirement(max_karma=-30) is True
        assert manager.check_karma_requirement(max_karma=-50) is False

    def test_check_karma_requirement_alignment(self, manager):
        """Test check_karma_requirement with alignment."""
        manager.karma = 50
        assert manager.check_karma_requirement(alignment="good") is True
        assert manager.check_karma_requirement(alignment="evil") is False

    def test_check_karma_requirement_combined(self, manager):
        """Test check_karma_requirement with multiple conditions."""
        manager.karma = 60
        assert manager.check_karma_requirement(min_karma=50, alignment="good") is True
        assert manager.check_karma_requirement(min_karma=70, alignment="good") is False

    def test_get_available_content(self, manager):
        """Test getting list of all unlocked content."""
        manager.modify_karma(85, "Unlock content")
        available = manager.get_available_content()
        assert isinstance(available, list)
        assert "trusted_helper" in available
        assert "hero_recognition" in available

    # -------------------------------------------------------------------------
    # Karma Decay Tests
    # -------------------------------------------------------------------------

    def test_decay_disabled_by_default(self, manager):
        """Test that decay is disabled by default."""
        assert manager.decay_enabled is False

    def test_enable_decay(self, manager):
        """Test enabling decay."""
        manager.enable_decay(rate=2, interval=60)
        assert manager.decay_enabled is True
        assert manager.decay_rate == 2
        assert manager.decay_interval == 60

    def test_disable_decay(self, manager):
        """Test disabling decay."""
        manager.enable_decay()
        manager.disable_decay()
        assert manager.decay_enabled is False

    def test_decay_no_effect_when_disabled(self, manager):
        """Test that decay has no effect when disabled."""
        manager.karma = 50
        result = manager.apply_decay()
        assert result == 0
        assert manager.karma == 50

    def test_decay_positive_karma(self, MoralityManager):
        """Test decay reduces positive karma toward zero."""
        manager = MoralityManager(initial_karma=50, decay_enabled=True, decay_rate=5, decay_interval=0.01)
        # Simulate time passing
        manager.last_decay_time = time.time() - 1

        decay = manager.apply_decay()
        assert decay > 0
        assert manager.karma < 50

    def test_decay_negative_karma(self, MoralityManager):
        """Test decay increases negative karma toward zero."""
        manager = MoralityManager(initial_karma=-50, decay_enabled=True, decay_rate=5, decay_interval=0.01)
        # Simulate time passing
        manager.last_decay_time = time.time() - 1

        decay = manager.apply_decay()
        assert decay > 0
        assert manager.karma > -50

    def test_decay_no_effect_at_zero(self, MoralityManager):
        """Test decay has no effect when karma is zero."""
        manager = MoralityManager(initial_karma=0, decay_enabled=True, decay_rate=5, decay_interval=0.01)
        manager.last_decay_time = time.time() - 1

        decay = manager.apply_decay()
        assert decay == 0
        assert manager.karma == 0

    def test_decay_not_before_interval(self, MoralityManager):
        """Test decay doesn't apply before interval passes."""
        manager = MoralityManager(initial_karma=50, decay_enabled=True, decay_rate=5, decay_interval=300)
        # Don't change last_decay_time

        decay = manager.apply_decay()
        assert decay == 0
        assert manager.karma == 50

    # -------------------------------------------------------------------------
    # Notification Tests
    # -------------------------------------------------------------------------

    def test_notification_created_on_karma_change(self, manager):
        """Test that notifications are created when karma changes."""
        manager.modify_karma(10, "Good deed")
        assert manager.has_pending_notifications()

    def test_get_pending_notification(self, manager):
        """Test getting pending notifications."""
        manager.modify_karma(10, "Test")
        notification = manager.get_pending_notification()

        assert notification is not None
        assert notification["amount"] == 10
        assert notification["reason"] == "Test"
        assert notification["old_karma"] == 0
        assert notification["new_karma"] == 10

    def test_notification_removed_after_get(self, manager):
        """Test notification is removed after getting it."""
        manager.modify_karma(10, "Test")
        manager.get_pending_notification()
        assert not manager.has_pending_notifications()

    def test_multiple_notifications_queue(self, manager):
        """Test multiple notifications are queued in order."""
        manager.modify_karma(10, "First")
        manager.modify_karma(20, "Second")

        notif1 = manager.get_pending_notification()
        notif2 = manager.get_pending_notification()

        assert notif1["reason"] == "First"
        assert notif2["reason"] == "Second"

    def test_clear_notifications(self, manager):
        """Test clearing all notifications."""
        manager.modify_karma(10, "Test")
        manager.clear_notifications()
        assert not manager.has_pending_notifications()

    def test_no_notification_for_zero_change(self, manager):
        """Test no notification for zero karma change."""
        manager.modify_karma(0, "No change")
        assert not manager.has_pending_notifications()

    # -------------------------------------------------------------------------
    # Utility Method Tests
    # -------------------------------------------------------------------------

    def test_reset(self, manager):
        """Test resetting the morality system."""
        manager.modify_karma(50, "Some deeds")
        manager.modify_karma(35, "Unlock content")
        manager.reset()

        assert manager.karma == 0
        assert len(manager.karma_history) == 0
        assert len(manager._unlocked_content) == 0
        assert not manager.has_pending_notifications()

    def test_reset_with_karma(self, manager):
        """Test reset with custom karma value."""
        manager.modify_karma(50, "Deeds")
        manager.reset(karma=-20)
        assert manager.karma == -20

    def test_get_karma_percentage(self, manager):
        """Test karma percentage calculation."""
        manager.karma = 0
        assert manager.get_karma_percentage() == 50.0

        manager.karma = 100
        assert manager.get_karma_percentage() == 100.0

        manager.karma = -100
        assert manager.get_karma_percentage() == 0.0

        manager.karma = 50
        assert manager.get_karma_percentage() == 75.0

    def test_get_status_summary(self, manager):
        """Test getting status summary."""
        manager.modify_karma(50, "Good deed")
        summary = manager.get_status_summary()

        assert summary["karma"] == 50
        assert summary["alignment"] == "Good"
        assert summary["alignment_id"] == "good"
        assert summary["color"] == "#33ff33"
        assert summary["total_positive"] == 50
        assert summary["total_negative"] == 0
        assert summary["changes_count"] == 1

    def test_karma_property_setter(self, manager):
        """Test direct karma property setting."""
        manager.karma = 75
        assert manager.karma == 75

    def test_karma_property_setter_clamped(self, manager):
        """Test karma property setter is clamped."""
        manager.karma = 200
        assert manager.karma == 100

        manager.karma = -200
        assert manager.karma == -100


class TestKarmaEntry:
    """Tests for the KarmaEntry class."""

    @pytest.fixture
    def morality_namespace(self):
        """Load the morality system."""
        rpy_path = GAME_DIR / "morality.rpy"
        if not rpy_path.exists():
            pytest.skip("morality.rpy not found")
        return load_rpy_classes(rpy_path)

    @pytest.fixture
    def KarmaEntry(self, morality_namespace):
        """Get the KarmaEntry class."""
        return morality_namespace["KarmaEntry"]

    def test_karma_entry_creation(self, KarmaEntry):
        """Test creating a KarmaEntry."""
        entry = KarmaEntry(10, "Test reason", 50)
        assert entry.amount == 10
        assert entry.reason == "Test reason"
        assert entry.resulting_karma == 50
        assert entry.timestamp is not None

    def test_karma_entry_custom_timestamp(self, KarmaEntry):
        """Test KarmaEntry with custom timestamp."""
        custom_time = 1234567890.0
        entry = KarmaEntry(10, "Test", 50, timestamp=custom_time)
        assert entry.timestamp == custom_time

    def test_karma_entry_repr_positive(self, KarmaEntry):
        """Test KarmaEntry repr for positive amount."""
        entry = KarmaEntry(10, "Good deed", 50)
        repr_str = repr(entry)
        assert "+10" in repr_str
        assert "Good deed" in repr_str

    def test_karma_entry_repr_negative(self, KarmaEntry):
        """Test KarmaEntry repr for negative amount."""
        entry = KarmaEntry(-5, "Bad deed", -5)
        repr_str = repr(entry)
        assert "-5" in repr_str
        assert "Bad deed" in repr_str


class TestAlignmentThresholds:
    """Tests for alignment threshold constants."""

    @pytest.fixture
    def morality_namespace(self):
        """Load the morality system."""
        rpy_path = GAME_DIR / "morality.rpy"
        if not rpy_path.exists():
            pytest.skip("morality.rpy not found")
        return load_rpy_classes(rpy_path)

    def test_thresholds_defined(self, morality_namespace):
        """Test that alignment thresholds are defined."""
        thresholds = morality_namespace["ALIGNMENT_THRESHOLDS"]
        assert "evil" in thresholds
        assert "neutral" in thresholds
        assert "good" in thresholds

    def test_threshold_ranges_no_gaps(self, morality_namespace):
        """Test that threshold ranges cover -100 to 100 with no gaps."""
        thresholds = morality_namespace["ALIGNMENT_THRESHOLDS"]

        # Evil range
        assert thresholds["evil"]["min"] == -100
        assert thresholds["evil"]["max"] == -31

        # Neutral range (should connect to evil and good)
        assert thresholds["neutral"]["min"] == -30
        assert thresholds["neutral"]["max"] == 30

        # Good range
        assert thresholds["good"]["min"] == 31
        assert thresholds["good"]["max"] == 100


class TestKarmaUnlocks:
    """Tests for karma unlock constants."""

    @pytest.fixture
    def morality_namespace(self):
        """Load the morality system."""
        rpy_path = GAME_DIR / "morality.rpy"
        if not rpy_path.exists():
            pytest.skip("morality.rpy not found")
        return load_rpy_classes(rpy_path)

    def test_unlocks_defined(self, morality_namespace):
        """Test that karma unlocks are defined."""
        unlocks = morality_namespace["KARMA_UNLOCKS"]
        assert len(unlocks) > 0

    def test_unlocks_have_both_polarities(self, morality_namespace):
        """Test that unlocks exist for both positive and negative karma."""
        unlocks = morality_namespace["KARMA_UNLOCKS"]
        negative_unlocks = [k for k in unlocks.keys() if k < 0]
        positive_unlocks = [k for k in unlocks.keys() if k > 0]

        assert len(negative_unlocks) > 0
        assert len(positive_unlocks) > 0


class TestDefaultManager:
    """Tests for the default morality_manager instance."""

    @pytest.fixture
    def morality_namespace(self):
        """Load the morality system."""
        rpy_path = GAME_DIR / "morality.rpy"
        if not rpy_path.exists():
            pytest.skip("morality.rpy not found")
        return load_rpy_classes(rpy_path)

    def test_default_manager_exists(self, morality_namespace):
        """Test that default morality_manager is created."""
        assert "morality_manager" in morality_namespace

    def test_default_manager_is_instance(self, morality_namespace):
        """Test that default manager is a MoralityManager instance."""
        manager = morality_namespace["morality_manager"]
        MoralityManager = morality_namespace["MoralityManager"]
        assert isinstance(manager, MoralityManager)

    def test_default_manager_starts_neutral(self, morality_namespace):
        """Test that default manager starts at neutral."""
        manager = morality_namespace["morality_manager"]
        assert manager.karma == 0
        assert manager.get_alignment_id() == "neutral"

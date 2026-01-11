"""
Comprehensive tests for the Dynamic Music System.

Tests cover:
- MusicLayer class functionality
- MusicManager class functionality
- Layer management (add/remove/get)
- Context switching and layer activation
- Intensity scaling
- Crossfade transitions
- Music ducking
- Volume calculations
- State management
"""
import pytest
import sys
from pathlib import Path

# Add tests directory to path for conftest imports
TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR))

from conftest import load_rpy_classes, GAME_DIR


@pytest.fixture
def music_classes():
    """Load the dynamic music system classes."""
    rpy_path = GAME_DIR / "dynamic_music.rpy"
    if not rpy_path.exists():
        pytest.skip("dynamic_music.rpy not found")
    return load_rpy_classes(rpy_path)


@pytest.fixture
def MusicLayer(music_classes):
    """Get the MusicLayer class."""
    return music_classes["MusicLayer"]


@pytest.fixture
def MusicManager(music_classes):
    """Get the MusicManager class."""
    return music_classes["MusicManager"]


@pytest.fixture
def manager(MusicManager):
    """Create a fresh MusicManager instance."""
    return MusicManager()


# =============================================================================
# MusicLayer Tests
# =============================================================================

class TestMusicLayer:
    """Tests for the MusicLayer class."""

    def test_create_layer(self, MusicLayer):
        """Test basic layer creation."""
        layer = MusicLayer("test", "audio/test.ogg")
        assert layer.id == "test"
        assert layer.file_path == "audio/test.ogg"
        assert layer.volume == 1.0
        assert layer.active is False

    def test_create_layer_with_volume(self, MusicLayer):
        """Test layer creation with custom volume."""
        layer = MusicLayer("test", "audio/test.ogg", volume=0.5)
        assert layer.volume == 0.5
        assert layer.base_volume == 0.5

    def test_create_layer_active(self, MusicLayer):
        """Test layer creation with active state."""
        layer = MusicLayer("test", "audio/test.ogg", active=True)
        assert layer.active is True

    def test_volume_clamping_high(self, MusicLayer):
        """Test that volume is clamped to 1.0 max."""
        layer = MusicLayer("test", "audio/test.ogg", volume=1.5)
        assert layer.volume == 1.0

    def test_volume_clamping_low(self, MusicLayer):
        """Test that volume is clamped to 0.0 min."""
        layer = MusicLayer("test", "audio/test.ogg", volume=-0.5)
        assert layer.volume == 0.0

    def test_set_volume(self, MusicLayer):
        """Test setting volume after creation."""
        layer = MusicLayer("test", "audio/test.ogg")
        layer.set_volume(0.7)
        assert layer.volume == 0.7

    def test_set_volume_clamped(self, MusicLayer):
        """Test that set_volume clamps values."""
        layer = MusicLayer("test", "audio/test.ogg")
        layer.set_volume(2.0)
        assert layer.volume == 1.0
        layer.set_volume(-1.0)
        assert layer.volume == 0.0

    def test_activate(self, MusicLayer):
        """Test activating a layer."""
        layer = MusicLayer("test", "audio/test.ogg")
        assert layer.active is False
        layer.activate()
        assert layer.active is True

    def test_deactivate(self, MusicLayer):
        """Test deactivating a layer."""
        layer = MusicLayer("test", "audio/test.ogg", active=True)
        assert layer.active is True
        layer.deactivate()
        assert layer.active is False

    def test_repr(self, MusicLayer):
        """Test string representation."""
        layer = MusicLayer("test", "audio/test.ogg", volume=0.8, active=True)
        repr_str = repr(layer)
        assert "test" in repr_str
        assert "audio/test.ogg" in repr_str
        assert "0.8" in repr_str
        assert "True" in repr_str


# =============================================================================
# MusicManager Layer Management Tests
# =============================================================================

class TestMusicManagerLayers:
    """Tests for MusicManager layer management."""

    def test_add_layer(self, manager):
        """Test adding a layer."""
        layer = manager.add_layer("base", "audio/base.ogg")
        assert layer.id == "base"
        assert "base" in manager.layers

    def test_add_layer_with_options(self, manager):
        """Test adding a layer with volume and active state."""
        layer = manager.add_layer("base", "audio/base.ogg", volume=0.8, active=True)
        assert layer.volume == 0.8
        assert layer.active is True

    def test_add_duplicate_layer_raises(self, manager):
        """Test that adding a duplicate layer raises ValueError."""
        manager.add_layer("base", "audio/base.ogg")
        with pytest.raises(ValueError, match="already exists"):
            manager.add_layer("base", "audio/other.ogg")

    def test_remove_layer(self, manager):
        """Test removing a layer."""
        manager.add_layer("base", "audio/base.ogg")
        removed = manager.remove_layer("base")
        assert removed.id == "base"
        assert "base" not in manager.layers

    def test_remove_nonexistent_layer_raises(self, manager):
        """Test that removing a nonexistent layer raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            manager.remove_layer("nonexistent")

    def test_get_layer(self, manager):
        """Test getting a layer by ID."""
        manager.add_layer("base", "audio/base.ogg")
        layer = manager.get_layer("base")
        assert layer is not None
        assert layer.id == "base"

    def test_get_nonexistent_layer(self, manager):
        """Test getting a nonexistent layer returns None."""
        layer = manager.get_layer("nonexistent")
        assert layer is None

    def test_get_active_layers(self, manager):
        """Test getting all active layers."""
        manager.add_layer("base", "audio/base.ogg", active=True)
        manager.add_layer("melody", "audio/melody.ogg", active=False)
        manager.add_layer("drums", "audio/drums.ogg", active=True)

        active = manager.get_active_layers()
        assert len(active) == 2
        active_ids = [l.id for l in active]
        assert "base" in active_ids
        assert "drums" in active_ids
        assert "melody" not in active_ids


# =============================================================================
# MusicManager Context Tests
# =============================================================================

class TestMusicManagerContext:
    """Tests for context-aware music selection."""

    def test_default_context(self, manager):
        """Test that default context is 'calm'."""
        assert manager.current_context == "calm"

    def test_set_context(self, manager):
        """Test setting a context."""
        # Add layers that the context expects
        manager.add_layer("base", "audio/base.ogg")
        manager.add_layer("tension", "audio/tension.ogg")
        manager.add_layer("percussion", "audio/percussion.ogg")

        manager.set_context("tension")
        assert manager.current_context == "tension"

    def test_set_context_activates_layers(self, manager):
        """Test that setting context activates appropriate layers."""
        manager.add_layer("base", "audio/base.ogg")
        manager.add_layer("ambient", "audio/ambient.ogg")
        manager.add_layer("tension", "audio/tension.ogg")

        manager.set_context("calm")  # calm uses base and ambient

        assert manager.get_layer("base").active is True
        assert manager.get_layer("ambient").active is True
        assert manager.get_layer("tension").active is False

    def test_set_context_deactivates_other_layers(self, manager):
        """Test that setting context deactivates non-matching layers."""
        manager.add_layer("base", "audio/base.ogg", active=True)
        manager.add_layer("combat", "audio/combat.ogg", active=True)

        manager.set_context("calm")  # calm doesn't use combat

        assert manager.get_layer("combat").active is False

    def test_set_unknown_context_raises(self, manager):
        """Test that setting an unknown context raises ValueError."""
        with pytest.raises(ValueError, match="Unknown context"):
            manager.set_context("nonexistent_context")

    def test_add_custom_context(self, manager):
        """Test adding a custom context."""
        manager.add_layer("custom1", "audio/custom1.ogg")
        manager.add_layer("custom2", "audio/custom2.ogg")

        manager.add_context("custom", ["custom1", "custom2"], (0.4, 0.9))
        manager.set_context("custom")

        assert manager.current_context == "custom"
        assert manager.get_layer("custom1").active is True
        assert manager.get_layer("custom2").active is True

    def test_context_with_missing_layers(self, manager):
        """Test that context activation handles missing layers gracefully."""
        # Add only some of the expected layers
        manager.add_layer("base", "audio/base.ogg")
        # Don't add "ambient" which calm context expects

        # Should not raise, just activate what's available
        manager.set_context("calm")
        assert manager.get_layer("base").active is True


# =============================================================================
# MusicManager Intensity Tests
# =============================================================================

class TestMusicManagerIntensity:
    """Tests for intensity scaling."""

    def test_default_intensity(self, manager):
        """Test that default intensity is 0.5."""
        assert manager.intensity == 0.5

    def test_set_intensity(self, manager):
        """Test setting intensity."""
        manager.set_intensity(0.8)
        assert manager.intensity == 0.8

    def test_intensity_clamped_high(self, manager):
        """Test that intensity is clamped to 1.0 max."""
        manager.set_intensity(1.5)
        assert manager.intensity == 1.0

    def test_intensity_clamped_low(self, manager):
        """Test that intensity is clamped to 0.0 min."""
        manager.set_intensity(-0.5)
        assert manager.intensity == 0.0

    def test_intensity_affects_volume(self, manager):
        """Test that intensity affects layer volumes."""
        manager.add_layer("base", "audio/base.ogg", volume=1.0, active=True)

        # Low intensity should reduce volume
        manager.set_intensity(0.0)
        low_volume = manager.get_layer("base").volume

        # High intensity should increase volume
        manager.set_intensity(1.0)
        high_volume = manager.get_layer("base").volume

        assert high_volume > low_volume

    def test_intensity_only_affects_active_layers(self, manager):
        """Test that intensity only affects active layers."""
        manager.add_layer("active", "audio/active.ogg", volume=1.0, active=True)
        manager.add_layer("inactive", "audio/inactive.ogg", volume=1.0, active=False)

        original_inactive_volume = manager.get_layer("inactive").volume
        manager.set_intensity(0.0)

        # Inactive layer volume should be unchanged
        assert manager.get_layer("inactive").volume == original_inactive_volume


# =============================================================================
# MusicManager Crossfade Tests
# =============================================================================

class TestMusicManagerCrossfade:
    """Tests for crossfade transitions."""

    def test_fade_to_track(self, manager):
        """Test fading to a new track."""
        result = manager.fade_to("audio/new_track.ogg", duration=1.0)
        assert result is True
        assert manager.current_track == "audio/new_track.ogg"

    def test_fade_to_none(self, manager):
        """Test fading out (fade to None)."""
        manager.fade_to("audio/track.ogg")
        result = manager.fade_to(None, duration=1.0)
        assert result is True
        assert manager.current_track is None

    def test_fade_with_zero_duration(self, manager):
        """Test that zero duration gets a minimum value."""
        result = manager.fade_to("audio/track.ogg", duration=0)
        assert result is True

    def test_fade_updates_current_track(self, manager):
        """Test that fade updates current track."""
        manager.fade_to("audio/track1.ogg")
        assert manager.current_track == "audio/track1.ogg"

        manager.fade_to("audio/track2.ogg")
        assert manager.current_track == "audio/track2.ogg"


# =============================================================================
# MusicManager Ducking Tests
# =============================================================================

class TestMusicManagerDucking:
    """Tests for music ducking during dialogue."""

    def test_default_not_ducked(self, manager):
        """Test that ducking is off by default."""
        assert manager.is_ducked is False

    def test_duck_music(self, manager):
        """Test enabling music ducking."""
        manager.duck_music(True)
        assert manager.is_ducked is True

    def test_unduck_music(self, manager):
        """Test disabling music ducking."""
        manager.duck_music(True)
        manager.duck_music(False)
        assert manager.is_ducked is False

    def test_set_duck_volume(self, manager):
        """Test setting duck volume."""
        manager.set_duck_volume(0.2)
        assert manager.duck_volume == 0.2

    def test_duck_volume_clamped(self, manager):
        """Test that duck volume is clamped."""
        manager.set_duck_volume(1.5)
        assert manager.duck_volume == 1.0
        manager.set_duck_volume(-0.5)
        assert manager.duck_volume == 0.0

    def test_ducking_affects_effective_volume(self, manager):
        """Test that ducking reduces effective volume."""
        manager.add_layer("base", "audio/base.ogg", volume=1.0, active=True)
        manager.set_duck_volume(0.3)

        unducked_volume = manager.get_effective_volume("base")
        manager.duck_music(True)
        ducked_volume = manager.get_effective_volume("base")

        assert ducked_volume < unducked_volume
        assert ducked_volume == pytest.approx(unducked_volume * 0.3, rel=0.01)


# =============================================================================
# MusicManager Volume Tests
# =============================================================================

class TestMusicManagerVolume:
    """Tests for volume management."""

    def test_default_master_volume(self, manager):
        """Test that default master volume is 1.0."""
        assert manager.master_volume == 1.0

    def test_set_master_volume(self, manager):
        """Test setting master volume."""
        manager.set_master_volume(0.7)
        assert manager.master_volume == 0.7

    def test_master_volume_clamped(self, manager):
        """Test that master volume is clamped."""
        manager.set_master_volume(1.5)
        assert manager.master_volume == 1.0
        manager.set_master_volume(-0.5)
        assert manager.master_volume == 0.0

    def test_effective_volume_with_master(self, manager):
        """Test that effective volume includes master volume."""
        manager.add_layer("base", "audio/base.ogg", volume=1.0, active=True)
        manager.set_master_volume(0.5)

        effective = manager.get_effective_volume("base")
        # Note: effective volume also includes intensity scaling
        assert effective <= 0.5

    def test_effective_volume_inactive_layer(self, manager):
        """Test that inactive layer has zero effective volume."""
        manager.add_layer("base", "audio/base.ogg", volume=1.0, active=False)
        assert manager.get_effective_volume("base") == 0.0

    def test_effective_volume_nonexistent_layer(self, manager):
        """Test that nonexistent layer has zero effective volume."""
        assert manager.get_effective_volume("nonexistent") == 0.0


# =============================================================================
# MusicManager State Tests
# =============================================================================

class TestMusicManagerState:
    """Tests for state management."""

    def test_get_state(self, manager):
        """Test getting the current state."""
        manager.add_layer("base", "audio/base.ogg", active=True)
        manager.set_context("calm")
        manager.set_intensity(0.7)

        state = manager.get_state()

        assert state["context"] == "calm"
        assert state["intensity"] == 0.7
        assert "base" in state["layers"]
        assert state["layers"]["base"]["active"] is True

    def test_reset(self, manager):
        """Test resetting the manager."""
        manager.add_layer("base", "audio/base.ogg", active=True)
        manager.set_context("tension")
        manager.set_intensity(0.9)
        manager.fade_to("audio/track.ogg")
        manager.duck_music(True)

        manager.reset()

        assert len(manager.layers) == 0
        assert manager.current_context == "calm"
        assert manager.current_track is None
        assert manager.intensity == 0.5
        assert manager.is_ducked is False


# =============================================================================
# Integration Tests
# =============================================================================

class TestMusicSystemIntegration:
    """Integration tests for the complete music system."""

    def test_full_scenario(self, manager):
        """Test a complete music scenario."""
        # Setup layers
        manager.add_layer("base", "audio/base.ogg", volume=1.0)
        manager.add_layer("ambient", "audio/ambient.ogg", volume=0.7)
        manager.add_layer("tension", "audio/tension.ogg", volume=0.8)
        manager.add_layer("combat", "audio/combat.ogg", volume=1.0)
        manager.add_layer("percussion", "audio/drums.ogg", volume=0.9)

        # Start with calm context
        manager.set_context("calm")
        assert manager.get_layer("base").active is True
        assert manager.get_layer("ambient").active is True
        assert manager.get_layer("combat").active is False

        # Transition to tension
        manager.set_context("tension")
        assert manager.get_layer("tension").active is True
        assert manager.get_layer("percussion").active is True

        # Increase intensity
        manager.set_intensity(0.9)
        tension_volume = manager.get_effective_volume("tension")

        # Duck for dialogue
        manager.duck_music(True)
        ducked_volume = manager.get_effective_volume("tension")
        assert ducked_volume < tension_volume

        # Restore after dialogue
        manager.duck_music(False)
        restored_volume = manager.get_effective_volume("tension")
        assert restored_volume == pytest.approx(tension_volume, rel=0.01)

    def test_layer_persistence_across_contexts(self, manager):
        """Test that layers persist when switching contexts."""
        manager.add_layer("base", "audio/base.ogg")
        manager.add_layer("strings", "audio/strings.ogg")
        manager.add_layer("melody", "audio/melody.ogg")

        manager.set_context("calm")
        manager.set_context("romance")  # uses base, melody, strings

        # All layers should still exist
        assert manager.get_layer("base") is not None
        assert manager.get_layer("strings") is not None
        assert manager.get_layer("melody") is not None

    def test_multiple_crossfades(self, manager):
        """Test multiple consecutive crossfades."""
        tracks = ["audio/track1.ogg", "audio/track2.ogg", "audio/track3.ogg"]

        for track in tracks:
            manager.fade_to(track, duration=0.5)
            assert manager.current_track == track

        # Fade out
        manager.fade_to(None)
        assert manager.current_track is None

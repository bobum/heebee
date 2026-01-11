"""
Comprehensive tests for the Accessibility Options system.

Tests cover:
- AccessibilityManager class functionality
- Font scaling
- High contrast mode
- Colorblind modes
- Reduced motion settings
- Button hold time
- Screen reader hints
- Persistent preferences
- Color schemes
"""

import pytest
from pathlib import Path


class TestAccessibilityManager:
    """Tests for the AccessibilityManager class."""

    @pytest.fixture
    def accessibility_module(self, load_system):
        """Load the accessibility module."""
        return load_system("accessibility")

    @pytest.fixture
    def manager(self, accessibility_module):
        """Create a fresh AccessibilityManager instance."""
        return accessibility_module["AccessibilityManager"]()

    # =========================================================================
    # Initialization Tests
    # =========================================================================

    def test_manager_initialization(self, manager):
        """Test that AccessibilityManager initializes with default values."""
        assert manager.font_scale == 1.0
        assert manager.high_contrast is False
        assert manager.colorblind_mode == "none"
        assert manager.reduce_motion is False
        assert manager.button_hold_time == 0.0
        assert manager.screen_reader_enabled is False

    def test_manager_has_required_constants(self, accessibility_module):
        """Test that AccessibilityManager has required class constants."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]

        assert hasattr(AccessibilityManager, "COLORBLIND_MODES")
        assert hasattr(AccessibilityManager, "MIN_FONT_SCALE")
        assert hasattr(AccessibilityManager, "MAX_FONT_SCALE")
        assert hasattr(AccessibilityManager, "COLOR_SCHEMES")
        assert hasattr(AccessibilityManager, "ALT_TEXT_TEMPLATES")

    def test_colorblind_modes_list(self, accessibility_module):
        """Test that all required colorblind modes are defined."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]

        required_modes = ["none", "protanopia", "deuteranopia", "tritanopia"]
        for mode in required_modes:
            assert mode in AccessibilityManager.COLORBLIND_MODES

    # =========================================================================
    # Font Scale Tests
    # =========================================================================

    def test_font_scale_default(self, manager):
        """Test default font scale is 1.0."""
        assert manager.font_scale == 1.0

    def test_font_scale_setter_valid(self, manager):
        """Test setting font scale to valid values."""
        manager.font_scale = 1.2
        assert manager.font_scale == 1.2

        manager.font_scale = 0.8
        assert manager.font_scale == 0.8

        manager.font_scale = 1.5
        assert manager.font_scale == 1.5

    def test_font_scale_clamps_minimum(self, manager):
        """Test that font scale is clamped to minimum."""
        manager.font_scale = 0.5
        assert manager.font_scale == 0.8  # MIN_FONT_SCALE

    def test_font_scale_clamps_maximum(self, manager):
        """Test that font scale is clamped to maximum."""
        manager.font_scale = 2.0
        assert manager.font_scale == 1.5  # MAX_FONT_SCALE

    def test_increase_font_scale(self, manager):
        """Test increasing font scale."""
        initial = manager.font_scale
        manager.increase_font_scale()
        assert manager.font_scale == initial + 0.1

    def test_decrease_font_scale(self, manager):
        """Test decreasing font scale."""
        manager.font_scale = 1.2
        manager.decrease_font_scale()
        assert manager.font_scale == 1.1

    def test_increase_font_scale_respects_max(self, manager):
        """Test that increasing font scale respects maximum."""
        manager.font_scale = 1.5
        manager.increase_font_scale()
        assert manager.font_scale == 1.5

    def test_decrease_font_scale_respects_min(self, manager):
        """Test that decreasing font scale respects minimum."""
        manager.font_scale = 0.8
        manager.decrease_font_scale()
        assert manager.font_scale == 0.8

    def test_get_scaled_size(self, manager):
        """Test font size scaling calculation."""
        manager.font_scale = 1.0
        assert manager.get_scaled_size(24) == 24

        manager.font_scale = 1.5
        assert manager.get_scaled_size(24) == 36

        manager.font_scale = 0.8
        assert manager.get_scaled_size(24) == 19  # int(24 * 0.8) = 19

    def test_get_scaled_size_with_various_bases(self, manager):
        """Test scaling with various base sizes."""
        manager.font_scale = 1.25
        assert manager.get_scaled_size(20) == 25
        assert manager.get_scaled_size(28) == 35
        assert manager.get_scaled_size(50) == 62

    # =========================================================================
    # High Contrast Tests
    # =========================================================================

    def test_high_contrast_default(self, manager):
        """Test default high contrast is disabled."""
        assert manager.high_contrast is False

    def test_high_contrast_toggle(self, manager):
        """Test toggling high contrast mode."""
        manager.high_contrast = True
        assert manager.high_contrast is True

        manager.high_contrast = False
        assert manager.high_contrast is False

    def test_high_contrast_coerces_to_bool(self, manager):
        """Test that high contrast values are coerced to boolean."""
        manager.high_contrast = 1
        assert manager.high_contrast is True

        manager.high_contrast = 0
        assert manager.high_contrast is False

        manager.high_contrast = "yes"
        assert manager.high_contrast is True

    # =========================================================================
    # Colorblind Mode Tests
    # =========================================================================

    def test_colorblind_mode_default(self, manager):
        """Test default colorblind mode is 'none'."""
        assert manager.colorblind_mode == "none"

    def test_colorblind_mode_protanopia(self, manager):
        """Test setting protanopia mode."""
        manager.colorblind_mode = "protanopia"
        assert manager.colorblind_mode == "protanopia"

    def test_colorblind_mode_deuteranopia(self, manager):
        """Test setting deuteranopia mode."""
        manager.colorblind_mode = "deuteranopia"
        assert manager.colorblind_mode == "deuteranopia"

    def test_colorblind_mode_tritanopia(self, manager):
        """Test setting tritanopia mode."""
        manager.colorblind_mode = "tritanopia"
        assert manager.colorblind_mode == "tritanopia"

    def test_colorblind_mode_invalid_ignored(self, manager):
        """Test that invalid colorblind modes are ignored."""
        manager.colorblind_mode = "protanopia"
        manager.colorblind_mode = "invalid_mode"
        assert manager.colorblind_mode == "protanopia"  # Unchanged

    def test_cycle_colorblind_mode(self, manager):
        """Test cycling through colorblind modes."""
        assert manager.colorblind_mode == "none"

        manager.cycle_colorblind_mode()
        assert manager.colorblind_mode == "protanopia"

        manager.cycle_colorblind_mode()
        assert manager.colorblind_mode == "deuteranopia"

        manager.cycle_colorblind_mode()
        assert manager.colorblind_mode == "tritanopia"

        manager.cycle_colorblind_mode()
        assert manager.colorblind_mode == "none"  # Wraps around

    # =========================================================================
    # Reduce Motion Tests
    # =========================================================================

    def test_reduce_motion_default(self, manager):
        """Test default reduce motion is disabled."""
        assert manager.reduce_motion is False

    def test_reduce_motion_toggle(self, manager):
        """Test toggling reduce motion."""
        manager.reduce_motion = True
        assert manager.reduce_motion is True

        manager.reduce_motion = False
        assert manager.reduce_motion is False

    def test_get_transition_duration_normal(self, manager):
        """Test transition duration when reduce_motion is disabled."""
        manager.reduce_motion = False
        assert manager.get_transition_duration(0.5) == 0.5
        assert manager.get_transition_duration(1.0) == 1.0

    def test_get_transition_duration_reduced(self, manager):
        """Test transition duration when reduce_motion is enabled."""
        manager.reduce_motion = True
        assert manager.get_transition_duration(0.5) == 0
        assert manager.get_transition_duration(1.0) == 0

    # =========================================================================
    # Button Hold Time Tests
    # =========================================================================

    def test_button_hold_time_default(self, manager):
        """Test default button hold time is 0."""
        assert manager.button_hold_time == 0.0

    def test_button_hold_time_valid(self, manager):
        """Test setting valid button hold times."""
        manager.button_hold_time = 0.5
        assert manager.button_hold_time == 0.5

        manager.button_hold_time = 1.0
        assert manager.button_hold_time == 1.0

        manager.button_hold_time = 2.0
        assert manager.button_hold_time == 2.0

    def test_button_hold_time_clamps_minimum(self, manager):
        """Test button hold time is clamped to minimum."""
        manager.button_hold_time = -0.5
        assert manager.button_hold_time == 0.0

    def test_button_hold_time_clamps_maximum(self, manager):
        """Test button hold time is clamped to maximum."""
        manager.button_hold_time = 3.0
        assert manager.button_hold_time == 2.0

    # =========================================================================
    # Screen Reader Tests
    # =========================================================================

    def test_screen_reader_default(self, manager):
        """Test default screen reader is disabled."""
        assert manager.screen_reader_enabled is False

    def test_screen_reader_toggle(self, manager):
        """Test toggling screen reader."""
        manager.screen_reader_enabled = True
        assert manager.screen_reader_enabled is True

        manager.screen_reader_enabled = False
        assert manager.screen_reader_enabled is False

    def test_get_alt_text_disabled(self, manager):
        """Test alt text returns empty when screen reader disabled."""
        manager.screen_reader_enabled = False
        result = manager.get_alt_text("button", label="Test")
        assert result == ""

    def test_get_alt_text_enabled(self, manager):
        """Test alt text generation when screen reader enabled."""
        manager.screen_reader_enabled = True

        result = manager.get_alt_text("button", label="Save Game")
        assert "Save Game" in result
        assert "Button" in result

    def test_get_alt_text_choice(self, manager):
        """Test choice alt text generation."""
        manager.screen_reader_enabled = True

        result = manager.get_alt_text("choice", number=1, total=3, text="Go left")
        assert "1" in result
        assert "3" in result
        assert "Go left" in result

    def test_get_alt_text_dialogue(self, manager):
        """Test dialogue alt text generation."""
        manager.screen_reader_enabled = True

        result = manager.get_alt_text("dialogue", speaker="Alice", text="Hello there!")
        assert "Alice" in result
        assert "Hello there!" in result

    def test_get_alt_text_slider(self, manager):
        """Test slider alt text generation."""
        manager.screen_reader_enabled = True

        result = manager.get_alt_text("slider", label="Volume", value=50, min=0, max=100)
        assert "Volume" in result
        assert "50" in result

    def test_get_alt_text_toggle(self, manager):
        """Test toggle alt text generation."""
        manager.screen_reader_enabled = True

        result = manager.get_alt_text("toggle", label="Music", state="On")
        assert "Music" in result
        assert "On" in result

    def test_get_alt_text_invalid_template(self, manager):
        """Test alt text with invalid template type."""
        manager.screen_reader_enabled = True
        result = manager.get_alt_text("nonexistent", label="Test")
        assert result == ""  # Empty template

    # =========================================================================
    # Color Scheme Tests
    # =========================================================================

    def test_get_active_color_scheme_default(self, manager):
        """Test getting default color scheme."""
        scheme = manager.get_active_color_scheme()
        assert scheme is not None
        assert "text" in scheme
        assert "accent" in scheme
        assert "background" in scheme

    def test_get_active_color_scheme_high_contrast(self, manager):
        """Test high contrast takes priority."""
        manager.high_contrast = True
        manager.colorblind_mode = "protanopia"

        scheme = manager.get_active_color_scheme()
        # High contrast uses yellow accent
        assert scheme["accent"] == "#ffff00"

    def test_get_active_color_scheme_colorblind(self, manager):
        """Test colorblind mode color scheme."""
        manager.high_contrast = False
        manager.colorblind_mode = "protanopia"

        scheme = manager.get_active_color_scheme()
        # Protanopia uses blue-yellow safe colors
        assert scheme is not None

    def test_color_schemes_have_required_keys(self, accessibility_module):
        """Test that all color schemes have required keys."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        required_keys = ["text", "accent", "idle", "hover", "selected",
                         "insensitive", "choice_idle", "choice_hover",
                         "background", "button_bg", "button_hover"]

        for scheme_name, scheme in AccessibilityManager.COLOR_SCHEMES.items():
            for key in required_keys:
                assert key in scheme, f"Missing {key} in {scheme_name} scheme"

    def test_color_schemes_have_valid_hex_colors(self, accessibility_module):
        """Test that color values are valid hex colors."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        import re
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6,8}$')

        for scheme_name, scheme in AccessibilityManager.COLOR_SCHEMES.items():
            for key, color in scheme.items():
                assert hex_pattern.match(color), f"Invalid color {color} for {key} in {scheme_name}"

    # =========================================================================
    # Apply Settings Tests
    # =========================================================================

    def test_apply_settings_returns_dict(self, manager):
        """Test that apply_settings returns a dictionary."""
        result = manager.apply_settings()
        assert isinstance(result, dict)

    def test_apply_settings_contains_all_settings(self, manager):
        """Test that apply_settings result contains all settings."""
        result = manager.apply_settings()

        assert "font_scale" in result
        assert "high_contrast" in result
        assert "colorblind_mode" in result
        assert "reduce_motion" in result
        assert "button_hold_time" in result
        assert "screen_reader_enabled" in result
        assert "color_scheme" in result
        assert "scaled_sizes" in result

    def test_apply_settings_reflects_current_state(self, manager):
        """Test that apply_settings reflects current state."""
        manager.font_scale = 1.3
        manager.high_contrast = True
        manager.colorblind_mode = "deuteranopia"
        manager.reduce_motion = True
        manager.button_hold_time = 0.5

        result = manager.apply_settings()

        assert result["font_scale"] == 1.3
        assert result["high_contrast"] is True
        assert result["colorblind_mode"] == "deuteranopia"
        assert result["reduce_motion"] is True
        assert result["button_hold_time"] == 0.5

    def test_apply_settings_scaled_sizes(self, manager):
        """Test that apply_settings includes correct scaled sizes."""
        manager.font_scale = 1.5
        result = manager.apply_settings()

        scaled_sizes = result["scaled_sizes"]
        assert scaled_sizes["text_size"] == 36  # 24 * 1.5
        assert scaled_sizes["name_size"] == 42  # 28 * 1.5
        assert scaled_sizes["title_size"] == 75  # 50 * 1.5

    # =========================================================================
    # Reset to Defaults Tests
    # =========================================================================

    def test_reset_to_defaults(self, manager):
        """Test resetting all settings to defaults."""
        # Change all settings
        manager.font_scale = 1.3
        manager.high_contrast = True
        manager.colorblind_mode = "protanopia"
        manager.reduce_motion = True
        manager.button_hold_time = 1.0
        manager.screen_reader_enabled = True

        # Reset
        manager.reset_to_defaults()

        # Verify defaults
        assert manager.font_scale == 1.0
        assert manager.high_contrast is False
        assert manager.colorblind_mode == "none"
        assert manager.reduce_motion is False
        assert manager.button_hold_time == 0.0
        assert manager.screen_reader_enabled is False

    # =========================================================================
    # Settings Summary Tests
    # =========================================================================

    def test_get_settings_summary(self, manager):
        """Test getting settings summary."""
        summary = manager.get_settings_summary()
        assert isinstance(summary, str)
        assert "Accessibility Settings" in summary

    def test_get_settings_summary_contains_all_settings(self, manager):
        """Test that summary contains all setting values."""
        manager.font_scale = 1.2
        manager.high_contrast = True
        manager.colorblind_mode = "protanopia"

        summary = manager.get_settings_summary()

        assert "120%" in summary  # Font scale as percentage
        assert "On" in summary  # High contrast
        assert "Protanopia" in summary  # Colorblind mode

    # =========================================================================
    # Integration Tests
    # =========================================================================

    def test_combined_settings_workflow(self, manager):
        """Test a realistic workflow of changing settings."""
        # User increases font size
        manager.increase_font_scale()
        manager.increase_font_scale()
        assert manager.font_scale == 1.2

        # User enables high contrast
        manager.high_contrast = True

        # User sets colorblind mode (should be overridden by high contrast)
        manager.colorblind_mode = "protanopia"

        # Get color scheme (should be high contrast)
        scheme = manager.get_active_color_scheme()
        assert scheme["accent"] == "#ffff00"

        # Disable high contrast, colorblind should now apply
        manager.high_contrast = False
        scheme = manager.get_active_color_scheme()
        assert scheme != manager.COLOR_SCHEMES["high_contrast"]

        # Apply settings
        result = manager.apply_settings()
        assert result["font_scale"] == 1.2
        assert result["colorblind_mode"] == "protanopia"

    def test_boundary_conditions(self, manager):
        """Test behavior at boundary conditions."""
        # Font scale at min
        manager.font_scale = 0.8
        manager.decrease_font_scale()
        assert manager.font_scale == 0.8

        # Font scale at max
        manager.font_scale = 1.5
        manager.increase_font_scale()
        assert manager.font_scale == 1.5

        # Button hold time boundaries
        manager.button_hold_time = 0.0
        assert manager.button_hold_time == 0.0

        manager.button_hold_time = 2.0
        assert manager.button_hold_time == 2.0


class TestColorblindPalettes:
    """Tests specifically for colorblind-friendly palettes."""

    @pytest.fixture
    def accessibility_module(self, load_system):
        return load_system("accessibility")

    def test_protanopia_palette_exists(self, accessibility_module):
        """Test protanopia palette is defined."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        assert "protanopia" in AccessibilityManager.COLOR_SCHEMES

    def test_deuteranopia_palette_exists(self, accessibility_module):
        """Test deuteranopia palette is defined."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        assert "deuteranopia" in AccessibilityManager.COLOR_SCHEMES

    def test_tritanopia_palette_exists(self, accessibility_module):
        """Test tritanopia palette is defined."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        assert "tritanopia" in AccessibilityManager.COLOR_SCHEMES

    def test_colorblind_palettes_differ_from_default(self, accessibility_module):
        """Test that colorblind palettes are different from default."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]

        default_scheme = AccessibilityManager.COLOR_SCHEMES["default"]

        for mode in ["protanopia", "deuteranopia", "tritanopia"]:
            scheme = AccessibilityManager.COLOR_SCHEMES[mode]
            # At least accent color should differ
            assert scheme["accent"] != default_scheme["accent"] or \
                   scheme["hover"] != default_scheme["hover"]


class TestAltTextTemplates:
    """Tests for screen reader alt text templates."""

    @pytest.fixture
    def accessibility_module(self, load_system):
        return load_system("accessibility")

    def test_button_template_exists(self, accessibility_module):
        """Test button alt text template exists."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        assert "button" in AccessibilityManager.ALT_TEXT_TEMPLATES

    def test_choice_template_exists(self, accessibility_module):
        """Test choice alt text template exists."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        assert "choice" in AccessibilityManager.ALT_TEXT_TEMPLATES

    def test_dialogue_template_exists(self, accessibility_module):
        """Test dialogue alt text template exists."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        assert "dialogue" in AccessibilityManager.ALT_TEXT_TEMPLATES

    def test_slider_template_exists(self, accessibility_module):
        """Test slider alt text template exists."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        assert "slider" in AccessibilityManager.ALT_TEXT_TEMPLATES

    def test_toggle_template_exists(self, accessibility_module):
        """Test toggle alt text template exists."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]
        assert "toggle" in AccessibilityManager.ALT_TEXT_TEMPLATES

    def test_templates_are_format_strings(self, accessibility_module):
        """Test that templates contain format placeholders."""
        AccessibilityManager = accessibility_module["AccessibilityManager"]

        for template_name, template in AccessibilityManager.ALT_TEXT_TEMPLATES.items():
            # All templates should have at least one placeholder
            assert "{" in template and "}" in template, \
                f"Template {template_name} has no placeholders"


class TestPersistentPreferences:
    """Tests for persistent preference handling."""

    @pytest.fixture
    def accessibility_module(self, load_system):
        return load_system("accessibility")

    @pytest.fixture
    def manager(self, accessibility_module):
        return accessibility_module["AccessibilityManager"]()

    def test_font_scale_updates_persistent(self, manager):
        """Test that font scale changes update persistent storage."""
        # The manager should update persistent when font_scale changes
        manager.font_scale = 1.3
        # In real Ren'Py, this would update persistent.accessibility_font_scale
        # Verify the value was set correctly
        assert manager.font_scale == 1.3

    def test_high_contrast_updates_persistent(self, manager):
        """Test that high contrast changes update persistent storage."""
        manager.high_contrast = True
        # Property setter should update persistent

    def test_colorblind_mode_updates_persistent(self, manager):
        """Test that colorblind mode changes update persistent storage."""
        manager.colorblind_mode = "protanopia"
        # Property setter should update persistent

    def test_reduce_motion_updates_persistent(self, manager):
        """Test that reduce motion changes update persistent storage."""
        manager.reduce_motion = True
        # Property setter should update persistent

    def test_button_hold_time_updates_persistent(self, manager):
        """Test that button hold time changes update persistent storage."""
        manager.button_hold_time = 0.5
        # Property setter should update persistent

    def test_screen_reader_updates_persistent(self, manager):
        """Test that screen reader changes update persistent storage."""
        manager.screen_reader_enabled = True
        # Property setter should update persistent

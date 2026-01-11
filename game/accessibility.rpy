# accessibility.rpy
# Accessibility Options System for Heebee Visual Novel
# Provides font scaling, high contrast, colorblind modes, and motion settings

# ============================================================================
# PERSISTENT DEFAULTS
# ============================================================================

default persistent.accessibility_font_scale = 1.0
default persistent.accessibility_high_contrast = False
default persistent.accessibility_colorblind_mode = "none"
default persistent.accessibility_reduce_motion = False
default persistent.accessibility_button_hold_time = 0.0
default persistent.accessibility_screen_reader_enabled = False

# ============================================================================
# ACCESSIBILITY MANAGER CLASS
# ============================================================================

init python:
    class AccessibilityManager:
        """
        Manages accessibility settings for the visual novel.

        Features:
        - Font size scaling (0.8 to 1.5)
        - High contrast mode for better visibility
        - Colorblind-friendly palettes (protanopia, deuteranopia, tritanopia)
        - Reduced motion option
        - Button hold time for motor accessibility
        - Screen reader hints
        """

        # Valid colorblind modes
        COLORBLIND_MODES = ["none", "protanopia", "deuteranopia", "tritanopia"]

        # Font scale limits
        MIN_FONT_SCALE = 0.8
        MAX_FONT_SCALE = 1.5
        FONT_SCALE_STEP = 0.1

        # Button hold time limits (in seconds)
        MIN_HOLD_TIME = 0.0
        MAX_HOLD_TIME = 2.0
        HOLD_TIME_STEP = 0.1

        # Color schemes for different modes
        COLOR_SCHEMES = {
            "default": {
                "text": "#ffffff",
                "accent": "#66aaff",
                "idle": "#aaaaaa",
                "hover": "#66ccff",
                "selected": "#ffffff",
                "insensitive": "#555555",
                "choice_idle": "#cccccc",
                "choice_hover": "#66ccff",
                "background": "#000000aa",
                "button_bg": "#333333cc",
                "button_hover": "#4444aacc",
            },
            "high_contrast": {
                "text": "#ffffff",
                "accent": "#ffff00",
                "idle": "#ffffff",
                "hover": "#ffff00",
                "selected": "#ffff00",
                "insensitive": "#888888",
                "choice_idle": "#ffffff",
                "choice_hover": "#ffff00",
                "background": "#000000",
                "button_bg": "#000000",
                "button_hover": "#333333",
            },
            "protanopia": {
                "text": "#ffffff",
                "accent": "#56b4e9",
                "idle": "#cccccc",
                "hover": "#f0e442",
                "selected": "#ffffff",
                "insensitive": "#666666",
                "choice_idle": "#cccccc",
                "choice_hover": "#f0e442",
                "background": "#000000aa",
                "button_bg": "#333333cc",
                "button_hover": "#0072b2cc",
            },
            "deuteranopia": {
                "text": "#ffffff",
                "accent": "#56b4e9",
                "idle": "#cccccc",
                "hover": "#f0e442",
                "selected": "#ffffff",
                "insensitive": "#666666",
                "choice_idle": "#cccccc",
                "choice_hover": "#f0e442",
                "background": "#000000aa",
                "button_bg": "#333333cc",
                "button_hover": "#0072b2cc",
            },
            "tritanopia": {
                "text": "#ffffff",
                "accent": "#e69f00",
                "idle": "#cccccc",
                "hover": "#cc79a7",
                "selected": "#ffffff",
                "insensitive": "#666666",
                "choice_idle": "#cccccc",
                "choice_hover": "#cc79a7",
                "background": "#000000aa",
                "button_bg": "#333333cc",
                "button_hover": "#d55e00cc",
            },
        }

        # Screen reader alt text templates
        ALT_TEXT_TEMPLATES = {
            "button": "Button: {label}",
            "choice": "Choice {number} of {total}: {text}",
            "dialogue": "{speaker} says: {text}",
            "menu_item": "Menu item: {label}",
            "slider": "{label}: {value} ({min} to {max})",
            "toggle": "{label}: {state}",
        }

        def __init__(self):
            """Initialize the accessibility manager with persistent settings."""
            self._font_scale = persistent.accessibility_font_scale or 1.0
            self._high_contrast = persistent.accessibility_high_contrast or False
            self._colorblind_mode = persistent.accessibility_colorblind_mode or "none"
            self._reduce_motion = persistent.accessibility_reduce_motion or False
            self._button_hold_time = persistent.accessibility_button_hold_time or 0.0
            self._screen_reader_enabled = persistent.accessibility_screen_reader_enabled or False

            # Base font sizes (before scaling)
            self._base_text_size = 24
            self._base_name_size = 28
            self._base_interface_size = 24
            self._base_label_size = 28
            self._base_notify_size = 20
            self._base_title_size = 50

        @property
        def font_scale(self):
            """Get the current font scale (0.8 to 1.5)."""
            return self._font_scale

        @font_scale.setter
        def font_scale(self, value):
            """Set the font scale, clamped to valid range."""
            self._font_scale = max(self.MIN_FONT_SCALE, min(self.MAX_FONT_SCALE, value))
            persistent.accessibility_font_scale = self._font_scale

        @property
        def high_contrast(self):
            """Get high contrast mode state."""
            return self._high_contrast

        @high_contrast.setter
        def high_contrast(self, value):
            """Set high contrast mode."""
            self._high_contrast = bool(value)
            persistent.accessibility_high_contrast = self._high_contrast

        @property
        def colorblind_mode(self):
            """Get current colorblind mode."""
            return self._colorblind_mode

        @colorblind_mode.setter
        def colorblind_mode(self, value):
            """Set colorblind mode if valid."""
            if value in self.COLORBLIND_MODES:
                self._colorblind_mode = value
                persistent.accessibility_colorblind_mode = self._colorblind_mode

        @property
        def reduce_motion(self):
            """Get reduced motion setting."""
            return self._reduce_motion

        @reduce_motion.setter
        def reduce_motion(self, value):
            """Set reduced motion preference."""
            self._reduce_motion = bool(value)
            persistent.accessibility_reduce_motion = self._reduce_motion

        @property
        def button_hold_time(self):
            """Get button hold time requirement (in seconds)."""
            return self._button_hold_time

        @button_hold_time.setter
        def button_hold_time(self, value):
            """Set button hold time, clamped to valid range."""
            self._button_hold_time = max(self.MIN_HOLD_TIME, min(self.MAX_HOLD_TIME, value))
            persistent.accessibility_button_hold_time = self._button_hold_time

        @property
        def screen_reader_enabled(self):
            """Get screen reader hint state."""
            return self._screen_reader_enabled

        @screen_reader_enabled.setter
        def screen_reader_enabled(self, value):
            """Enable or disable screen reader hints."""
            self._screen_reader_enabled = bool(value)
            persistent.accessibility_screen_reader_enabled = self._screen_reader_enabled

        def get_active_color_scheme(self):
            """
            Get the active color scheme based on current settings.

            Priority: high_contrast > colorblind_mode > default
            """
            if self._high_contrast:
                return self.COLOR_SCHEMES["high_contrast"]
            elif self._colorblind_mode != "none":
                return self.COLOR_SCHEMES.get(self._colorblind_mode, self.COLOR_SCHEMES["default"])
            else:
                return self.COLOR_SCHEMES["default"]

        def get_scaled_size(self, base_size):
            """Get a font size scaled by the current font_scale."""
            return int(base_size * self._font_scale)

        def get_transition_duration(self, default_duration=0.5):
            """
            Get transition duration based on reduce_motion setting.

            Returns 0 if reduce_motion is enabled, otherwise returns default.
            """
            if self._reduce_motion:
                return 0
            return default_duration

        def get_alt_text(self, template_type, **kwargs):
            """
            Generate screen reader alt text from a template.

            Args:
                template_type: Key from ALT_TEXT_TEMPLATES
                **kwargs: Values to substitute in the template

            Returns:
                Formatted alt text string, or empty string if screen reader disabled
            """
            if not self._screen_reader_enabled:
                return ""

            template = self.ALT_TEXT_TEMPLATES.get(template_type, "")
            try:
                return template.format(**kwargs)
            except KeyError:
                return template

        def increase_font_scale(self):
            """Increase font scale by one step."""
            new_scale = self._font_scale + self.FONT_SCALE_STEP
            self.font_scale = round(new_scale, 1)

        def decrease_font_scale(self):
            """Decrease font scale by one step."""
            new_scale = self._font_scale - self.FONT_SCALE_STEP
            self.font_scale = round(new_scale, 1)

        def cycle_colorblind_mode(self):
            """Cycle to the next colorblind mode."""
            current_index = self.COLORBLIND_MODES.index(self._colorblind_mode)
            next_index = (current_index + 1) % len(self.COLORBLIND_MODES)
            self.colorblind_mode = self.COLORBLIND_MODES[next_index]

        def reset_to_defaults(self):
            """Reset all accessibility settings to defaults."""
            self.font_scale = 1.0
            self.high_contrast = False
            self.colorblind_mode = "none"
            self.reduce_motion = False
            self.button_hold_time = 0.0
            self.screen_reader_enabled = False

        def apply_settings(self):
            """
            Apply current accessibility settings to the game.

            This updates GUI variables and styles based on current settings.
            Should be called after changing any settings.
            """
            # Get active color scheme
            scheme = self.get_active_color_scheme()

            # Apply scaled font sizes (stored for reference, actual application
            # happens through style system)
            scaled_sizes = {
                "text_size": self.get_scaled_size(self._base_text_size),
                "name_size": self.get_scaled_size(self._base_name_size),
                "interface_size": self.get_scaled_size(self._base_interface_size),
                "label_size": self.get_scaled_size(self._base_label_size),
                "notify_size": self.get_scaled_size(self._base_notify_size),
                "title_size": self.get_scaled_size(self._base_title_size),
            }

            # Return applied settings for verification
            return {
                "font_scale": self._font_scale,
                "high_contrast": self._high_contrast,
                "colorblind_mode": self._colorblind_mode,
                "reduce_motion": self._reduce_motion,
                "button_hold_time": self._button_hold_time,
                "screen_reader_enabled": self._screen_reader_enabled,
                "color_scheme": scheme,
                "scaled_sizes": scaled_sizes,
            }

        def get_settings_summary(self):
            """Get a human-readable summary of current settings."""
            lines = []
            lines.append("Accessibility Settings:")
            lines.append(f"  Font Scale: {int(self._font_scale * 100)}%")
            lines.append(f"  High Contrast: {'On' if self._high_contrast else 'Off'}")
            lines.append(f"  Colorblind Mode: {self._colorblind_mode.title()}")
            lines.append(f"  Reduce Motion: {'On' if self._reduce_motion else 'Off'}")
            lines.append(f"  Button Hold Time: {self._button_hold_time:.1f}s")
            lines.append(f"  Screen Reader: {'On' if self._screen_reader_enabled else 'Off'}")
            return "\n".join(lines)


# ============================================================================
# GLOBAL ACCESSIBILITY MANAGER INSTANCE
# ============================================================================

default accessibility_manager = AccessibilityManager()

# ============================================================================
# ACCESSIBILITY SCREENS
# ============================================================================

screen accessibility_settings():
    """Main accessibility settings menu."""

    tag menu
    modal True

    # Get current color scheme for styling
    $ scheme = accessibility_manager.get_active_color_scheme()

    frame:
        style "accessibility_frame"
        xalign 0.5
        yalign 0.5
        xsize 800
        ysize 600
        background Solid("#1a1a2e")
        padding (30, 30, 30, 30)

        vbox:
            spacing 20

            # Header
            text "Accessibility Options" size accessibility_manager.get_scaled_size(36) color scheme["accent"] xalign 0.5

            null height 10

            # Font Size Section
            frame:
                style "accessibility_section"
                background Solid("#2a2a4e")
                padding (20, 15, 20, 15)
                xfill True

                vbox:
                    spacing 10

                    text "Font Size" size accessibility_manager.get_scaled_size(24) color scheme["text"]

                    hbox:
                        spacing 20
                        yalign 0.5

                        textbutton "-" action Function(accessibility_manager.decrease_font_scale) style "accessibility_button"

                        text "[int(accessibility_manager.font_scale * 100)]%" size accessibility_manager.get_scaled_size(24) color scheme["text"] xalign 0.5 yalign 0.5 xsize 80

                        textbutton "+" action Function(accessibility_manager.increase_font_scale) style "accessibility_button"

                        null width 20

                        # Font preview
                        text "Preview Text" size accessibility_manager.get_scaled_size(24) color scheme["idle"]

            # High Contrast Section
            frame:
                style "accessibility_section"
                background Solid("#2a2a4e")
                padding (20, 15, 20, 15)
                xfill True

                hbox:
                    spacing 20

                    text "High Contrast Mode" size accessibility_manager.get_scaled_size(24) color scheme["text"] yalign 0.5

                    null width 50

                    textbutton ("On" if accessibility_manager.high_contrast else "Off"):
                        action ToggleField(accessibility_manager, "high_contrast")
                        style "accessibility_toggle"
                        text_color scheme["hover"] if accessibility_manager.high_contrast else scheme["idle"]

            # Colorblind Mode Section
            frame:
                style "accessibility_section"
                background Solid("#2a2a4e")
                padding (20, 15, 20, 15)
                xfill True

                vbox:
                    spacing 10

                    text "Colorblind Mode" size accessibility_manager.get_scaled_size(24) color scheme["text"]

                    hbox:
                        spacing 10

                        for mode in AccessibilityManager.COLORBLIND_MODES:
                            textbutton mode.title():
                                action SetField(accessibility_manager, "colorblind_mode", mode)
                                style "accessibility_choice"
                                text_color scheme["selected"] if accessibility_manager.colorblind_mode == mode else scheme["idle"]

            # Reduce Motion Section
            frame:
                style "accessibility_section"
                background Solid("#2a2a4e")
                padding (20, 15, 20, 15)
                xfill True

                hbox:
                    spacing 20

                    text "Reduce Motion" size accessibility_manager.get_scaled_size(24) color scheme["text"] yalign 0.5

                    null width 50

                    textbutton ("On" if accessibility_manager.reduce_motion else "Off"):
                        action ToggleField(accessibility_manager, "reduce_motion")
                        style "accessibility_toggle"
                        text_color scheme["hover"] if accessibility_manager.reduce_motion else scheme["idle"]

            # Button Hold Time Section
            frame:
                style "accessibility_section"
                background Solid("#2a2a4e")
                padding (20, 15, 20, 15)
                xfill True

                vbox:
                    spacing 10

                    text "Button Hold Time" size accessibility_manager.get_scaled_size(24) color scheme["text"]

                    hbox:
                        spacing 10

                        bar:
                            value FieldValue(accessibility_manager, "button_hold_time", range=2.0)
                            xsize 300
                            ysize 30
                            left_bar Solid(scheme["accent"])
                            right_bar Solid("#444444")

                        text "[accessibility_manager.button_hold_time:.1f]s" size accessibility_manager.get_scaled_size(20) color scheme["text"] yalign 0.5

            # Screen Reader Section
            frame:
                style "accessibility_section"
                background Solid("#2a2a4e")
                padding (20, 15, 20, 15)
                xfill True

                hbox:
                    spacing 20

                    text "Screen Reader Hints" size accessibility_manager.get_scaled_size(24) color scheme["text"] yalign 0.5

                    null width 50

                    textbutton ("On" if accessibility_manager.screen_reader_enabled else "Off"):
                        action ToggleField(accessibility_manager, "screen_reader_enabled")
                        style "accessibility_toggle"
                        text_color scheme["hover"] if accessibility_manager.screen_reader_enabled else scheme["idle"]

            null height 10

            # Bottom buttons
            hbox:
                spacing 20
                xalign 0.5

                textbutton "Reset Defaults":
                    action Function(accessibility_manager.reset_to_defaults)
                    style "accessibility_button"

                textbutton "Apply & Close":
                    action [Function(accessibility_manager.apply_settings), Return()]
                    style "accessibility_button"


screen font_size_preview():
    """Font size preview screen showing different text sizes."""

    modal True

    $ scheme = accessibility_manager.get_active_color_scheme()

    frame:
        xalign 0.5
        yalign 0.5
        xsize 600
        ysize 400
        background Solid("#1a1a2e")
        padding (30, 30, 30, 30)

        vbox:
            spacing 15

            text "Font Size Preview" size accessibility_manager.get_scaled_size(32) color scheme["accent"] xalign 0.5

            null height 20

            text "Title Text (50pt base)" size accessibility_manager.get_scaled_size(50) color scheme["text"]
            text "Character Name (28pt base)" size accessibility_manager.get_scaled_size(28) color scheme["accent"]
            text "Dialogue Text (24pt base)" size accessibility_manager.get_scaled_size(24) color scheme["text"]
            text "Interface Text (24pt base)" size accessibility_manager.get_scaled_size(24) color scheme["idle"]
            text "Notification (20pt base)" size accessibility_manager.get_scaled_size(20) color scheme["idle"]

            null height 20

            textbutton "Close":
                action Return()
                xalign 0.5
                style "accessibility_button"


screen color_scheme_selector():
    """Color scheme selection and preview screen."""

    modal True

    $ scheme = accessibility_manager.get_active_color_scheme()

    frame:
        xalign 0.5
        yalign 0.5
        xsize 700
        ysize 500
        background Solid("#1a1a2e")
        padding (30, 30, 30, 30)

        vbox:
            spacing 15

            text "Color Scheme" size accessibility_manager.get_scaled_size(32) color scheme["accent"] xalign 0.5

            null height 10

            # High contrast toggle
            hbox:
                spacing 20
                xalign 0.5

                text "High Contrast:" size accessibility_manager.get_scaled_size(24) color scheme["text"] yalign 0.5
                textbutton ("On" if accessibility_manager.high_contrast else "Off"):
                    action ToggleField(accessibility_manager, "high_contrast")
                    style "accessibility_toggle"

            null height 10

            # Colorblind mode selection
            text "Colorblind Mode:" size accessibility_manager.get_scaled_size(24) color scheme["text"] xalign 0.5

            hbox:
                spacing 15
                xalign 0.5

                for mode in AccessibilityManager.COLORBLIND_MODES:
                    textbutton mode.title():
                        action SetField(accessibility_manager, "colorblind_mode", mode)
                        style "accessibility_choice"
                        text_color scheme["selected"] if accessibility_manager.colorblind_mode == mode else scheme["idle"]

            null height 20

            # Color preview
            text "Color Preview:" size accessibility_manager.get_scaled_size(24) color scheme["text"] xalign 0.5

            frame:
                background Solid(scheme["background"])
                padding (20, 20, 20, 20)
                xalign 0.5

                vbox:
                    spacing 10

                    text "Accent Color Sample" color scheme["accent"]
                    text "Hover Color Sample" color scheme["hover"]
                    text "Idle Color Sample" color scheme["idle"]
                    text "Selected Color Sample" color scheme["selected"]

                    hbox:
                        spacing 10

                        frame:
                            background Solid(scheme["button_bg"])
                            padding (10, 5, 10, 5)
                            text "Button" color scheme["text"]

                        frame:
                            background Solid(scheme["button_hover"])
                            padding (10, 5, 10, 5)
                            text "Hover" color scheme["text"]

            null height 15

            textbutton "Close":
                action Return()
                xalign 0.5
                style "accessibility_button"


screen motion_settings():
    """Motion and animation settings screen."""

    modal True

    $ scheme = accessibility_manager.get_active_color_scheme()

    frame:
        xalign 0.5
        yalign 0.5
        xsize 600
        ysize 350
        background Solid("#1a1a2e")
        padding (30, 30, 30, 30)

        vbox:
            spacing 20

            text "Motion Settings" size accessibility_manager.get_scaled_size(32) color scheme["accent"] xalign 0.5

            null height 10

            # Reduce motion toggle
            frame:
                background Solid("#2a2a4e")
                padding (20, 15, 20, 15)
                xfill True

                hbox:
                    spacing 20

                    vbox:
                        text "Reduce Motion" size accessibility_manager.get_scaled_size(24) color scheme["text"]
                        text "Disables transitions and animations" size accessibility_manager.get_scaled_size(18) color scheme["idle"]

                    null width 50

                    textbutton ("On" if accessibility_manager.reduce_motion else "Off"):
                        action ToggleField(accessibility_manager, "reduce_motion")
                        style "accessibility_toggle"
                        yalign 0.5

            # Button hold time
            frame:
                background Solid("#2a2a4e")
                padding (20, 15, 20, 15)
                xfill True

                vbox:
                    spacing 10

                    text "Button Hold Time" size accessibility_manager.get_scaled_size(24) color scheme["text"]
                    text "Require holding buttons to prevent accidental clicks" size accessibility_manager.get_scaled_size(18) color scheme["idle"]

                    hbox:
                        spacing 15

                        bar:
                            value FieldValue(accessibility_manager, "button_hold_time", range=2.0)
                            xsize 250
                            ysize 25
                            left_bar Solid(scheme["accent"])
                            right_bar Solid("#444444")

                        text "[accessibility_manager.button_hold_time:.1f] seconds" size accessibility_manager.get_scaled_size(20) color scheme["text"] yalign 0.5

            null height 10

            textbutton "Close":
                action Return()
                xalign 0.5
                style "accessibility_button"


# ============================================================================
# ACCESSIBILITY STYLES
# ============================================================================

style accessibility_frame:
    background Solid("#1a1a2e")
    padding (30, 30, 30, 30)

style accessibility_section:
    background Solid("#2a2a4e")
    padding (20, 15, 20, 15)

style accessibility_button:
    background Solid("#333355")
    hover_background Solid("#4444aa")
    padding (15, 8, 15, 8)

style accessibility_button_text:
    color "#cccccc"
    hover_color "#ffffff"
    size 22

style accessibility_toggle:
    background Solid("#333355")
    hover_background Solid("#4444aa")
    padding (20, 8, 20, 8)

style accessibility_toggle_text:
    color "#cccccc"
    hover_color "#ffffff"
    size 22

style accessibility_choice:
    background Solid("#333355")
    hover_background Solid("#4444aa")
    padding (12, 6, 12, 6)

style accessibility_choice_text:
    color "#cccccc"
    hover_color "#ffffff"
    size 18

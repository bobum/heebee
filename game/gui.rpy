# gui.rpy
# This file contains GUI configuration variables.
# For a complete GUI customization, use Ren'Py's GUI generator.

init python:
    gui.init(1280, 720)

# ============================================================================
# COLORS
# ============================================================================

# The color of interface text
define gui.interface_text_color = "#ffffff"

# The accent color used throughout the interface
define gui.accent_color = "#66aaff"

# Colors for idle/hover/selected text
define gui.idle_color = "#aaaaaa"
define gui.idle_small_color = "#888888"
define gui.hover_color = "#66ccff"
define gui.selected_color = "#ffffff"
define gui.insensitive_color = "#555555"

# Colors for dialogue and menu text
define gui.text_color = "#ffffff"
define gui.choice_idle_color = "#cccccc"
define gui.choice_hover_color = "#66ccff"

# ============================================================================
# FONTS
# ============================================================================

# The font used for dialogue
define gui.text_font = "DejaVuSans.ttf"

# The font used for character names
define gui.name_text_font = "DejaVuSans.ttf"

# The font used for interface elements
define gui.interface_text_font = "DejaVuSans.ttf"

# ============================================================================
# FONT SIZES
# ============================================================================

define gui.text_size = 24
define gui.name_text_size = 28
define gui.interface_text_size = 24
define gui.label_text_size = 28
define gui.notify_text_size = 20
define gui.title_text_size = 50

# ============================================================================
# DIALOGUE BOX
# ============================================================================

# Height of the dialogue textbox
define gui.textbox_height = 185

# Placement of the textbox (x, y from bottom-left)
define gui.textbox_yalign = 1.0

# Placement of the speaking character's name
define gui.name_xpos = 240
define gui.name_ypos = 0

# Placement of dialogue text
define gui.dialogue_xpos = 268
define gui.dialogue_ypos = 50
define gui.dialogue_width = 744

# ============================================================================
# BUTTONS
# ============================================================================

define gui.button_width = None
define gui.button_height = 36
define gui.button_borders = Borders(4, 4, 4, 4)
define gui.button_text_font = gui.interface_text_font
define gui.button_text_size = gui.interface_text_size

# ============================================================================
# CHOICE MENUS
# ============================================================================

define gui.choice_button_width = 790
define gui.choice_button_height = None
define gui.choice_button_tile = False
define gui.choice_button_borders = Borders(100, 5, 100, 5)
define gui.choice_button_text_font = gui.text_font
define gui.choice_button_text_size = gui.text_size
define gui.choice_button_text_xalign = 0.5

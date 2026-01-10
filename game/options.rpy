# options.rpy
# This file contains options that can be changed to customize your game.

# ============================================================================
# BASIC GAME INFORMATION
# ============================================================================

# The title of the game (shown in window title bar)
define config.name = _("Heebee")

# The version of the game
define config.version = "0.1.0"

# Text placed on the About screen
define gui.about = _p("""
{b}Heebee{/b}

A visual novel created with Ren'Py.

Created by: [Your Name Here]
""")

# Short name used for executables and directories
define build.name = "Heebee"

# ============================================================================
# SOUND AND MUSIC
# ============================================================================

# Whether to show audio channels
define config.has_sound = True
define config.has_music = True
define config.has_voice = False

# Default volumes
define config.default_music_volume = 0.7
define config.default_sfx_volume = 0.7

# ============================================================================
# SAVE/LOAD SETTINGS
# ============================================================================

# The number of slots in each page of the save/load screen
define gui.file_slot_cols = 3
define gui.file_slot_rows = 2

# ============================================================================
# WINDOW SETTINGS
# ============================================================================

# Width and height of the game window
define config.screen_width = 1280
define config.screen_height = 720

# The title of the window
define config.window_title = "Heebee"

# ============================================================================
# BUILD CONFIGURATION
# ============================================================================

init python:
    # Classify files for building distributions

    # These files are not included in any build
    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)
    build.classify('**.rpy', None)  # Don't include source in release

    # Include these in all builds
    build.classify('game/**.rpyc', 'all')
    build.classify('game/**.png', 'all')
    build.classify('game/**.jpg', 'all')
    build.classify('game/**.mp3', 'all')
    build.classify('game/**.ogg', 'all')
    build.classify('game/**.wav', 'all')

    # Documentation
    build.documentation('*.html')
    build.documentation('*.txt')

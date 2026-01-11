# Heebee - A Ren'Py Visual Novel
# This is the main script file where your story lives.

# ============================================================================
# CHARACTER DEFINITIONS
# ============================================================================
# Define characters with their name and text color.
# The first argument is the variable name, the second is the display name.

define e = Character("Elena", color="#c8ffc8")
define m = Character("Marcus", color="#c8c8ff")
define narrator = Character(None)  # Standard ADV-mode narration

# ============================================================================
# IMAGE DEFINITIONS (Placeholders)
# ============================================================================
# Ren'Py will automatically find images in game/images/ folder
# For now, we'll use placeholder solid colors

image bg room = Solid("#2a2a3a")
image bg outside = Solid("#4a6a8a")
image bg sunset = Solid("#ff6644")

# Placeholder character images (solid colors with text)
image elena happy = Solid("#88cc88", xysize=(300, 400))
image elena sad = Solid("#668866", xysize=(300, 400))
image marcus neutral = Solid("#8888cc", xysize=(300, 400))
image marcus angry = Solid("#6666aa", xysize=(300, 400))

# ============================================================================
# GAME START
# ============================================================================
# The 'label start' is where your game begins - this is required!

label start:
    # Scene setup - show a background with a transition
    scene bg room with fade

    # Narration (no character speaking)
    "The old library was quiet, dust motes dancing in the afternoon light."

    "You've been searching for answers for weeks now, and today might finally be the day."

    # Show a character on screen
    show elena happy at center with dissolve

    # Character dialogue
    e "Oh! I didn't expect anyone else to be here."

    e "Are you researching the old legends too?"

    # Player choice - this creates a branching path
    menu:
        "How do you respond?"

        "Yes, I've been fascinated by them.":
            jump friendly_path

        "That's none of your business.":
            jump cold_path

        "What legends are you talking about?":
            jump curious_path

# ============================================================================
# BRANCHING PATHS
# ============================================================================

label friendly_path:
    show elena happy

    e "Really? That's wonderful!"

    e "I'm Elena, by the way. I've been studying the folklore of this region for years."

    "She pulls out a worn leather journal."

    show marcus neutral at right with moveinright

    m "Elena! There you are. I've been looking everywhere."

    e "Marcus! Meet my new research partner."

    m "Another one? Well, the more the merrier, I suppose."

    jump common_path

label cold_path:
    show elena sad with dissolve

    e "Oh... I see. I'm sorry for bothering you."

    "She turns to leave, but hesitates."

    e "Just... be careful with those old texts. Some knowledge has a price."

    show marcus neutral at right with moveinright

    m "Elena, who's this?"

    e "Just a stranger. Let's go, Marcus."

    "They leave together, and you're left wondering if you made a mistake."

    jump common_path

label curious_path:
    show elena happy

    e "You don't know? This library is famous for its collection on local mythology!"

    e "Stories of spirits, ancient pacts, hidden treasures..."

    show marcus neutral at right with moveinright

    m "Elena, please don't fill their head with nonsense."

    e "It's not nonsense, Marcus! I have proof!"

    m "You have speculation and coincidence."

    "The two seem to have this argument often."

    jump common_path

# ============================================================================
# COMMON PATH - Where all branches converge
# ============================================================================

label common_path:
    scene bg outside with fade

    "Later that evening..."

    scene bg sunset with dissolve

    "The sun sets over the old town, painting everything in shades of gold and crimson."

    "Your adventure is just beginning."

    # This is a simple example ending
    # In a full game, you would continue the story here

    "TO BE CONTINUED..."

    # Return to the main menu
    return

# ============================================================================
# TIPS FOR EXPANDING YOUR GAME:
# ============================================================================
#
# 1. ADD REAL IMAGES:
#    - Place character sprites in game/images/characters/
#    - Place backgrounds in game/images/backgrounds/
#    - Ren'Py will auto-detect them by filename
#
# 2. ADD MUSIC AND SOUND:
#    - play music "audio/bgm.mp3"
#    - play sound "audio/door_open.wav"
#
# 3. ADD VARIABLES TO TRACK CHOICES:
#    - default relationship = 0
#    - $ relationship += 1
#
# 4. ADD MORE COMPLEX MENUS:
#    - Use conditions: "Choice" if variable > 5:
#
# 5. ADD TRANSITIONS:
#    - with fade, with dissolve, with slide
#    - with Dissolve(2.0) for custom timing
#
# For more, visit: https://www.renpy.org/doc/html/

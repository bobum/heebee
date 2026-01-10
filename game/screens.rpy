# screens.rpy
# This file contains minimal screen definitions.
# For a full set of screens, use Ren'Py's default screens.rpy

# ============================================================================
# SAY SCREEN - Displays dialogue
# ============================================================================

screen say(who, what):
    style_prefix "say"

    window:
        id "window"

        if who is not None:
            window:
                id "namebox"
                style "namebox"
                text who id "who"

        text what id "what"

style window:
    xfill True
    yalign 1.0
    ysize gui.textbox_height
    background Solid("#000000aa")

style namebox:
    xpos gui.name_xpos
    xanchor 0
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height
    background Solid("#333333cc")
    padding (5, 5, 5, 5)

style say_label:
    color gui.accent_color
    size gui.name_text_size

style say_dialogue:
    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos
    color gui.text_color

# ============================================================================
# CHOICE SCREEN - Displays menu choices
# ============================================================================

screen choice(items):
    style_prefix "choice"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 22

        for i in items:
            textbutton i.caption action i.action

style choice_vbox:
    xalign 0.5
    yalign 0.5

style choice_button:
    xsize gui.choice_button_width
    background Solid("#333333cc")
    hover_background Solid("#4444aacc")
    padding (20, 10, 20, 10)

style choice_button_text:
    xalign 0.5
    color gui.choice_idle_color
    hover_color gui.choice_hover_color

# ============================================================================
# INPUT SCREEN - For player name entry, etc.
# ============================================================================

screen input(prompt):
    style_prefix "input"

    window:
        vbox:
            xanchor 0.5
            xpos 0.5
            yanchor 0.5
            ypos 0.5

            text prompt style "input_prompt"
            input id "input"

style input_prompt:
    xalign 0.5

# ============================================================================
# NVL SCREEN - For NVL-mode dialogue
# ============================================================================

screen nvl(dialogue, items=None):
    window:
        style "nvl_window"

        has vbox:
            spacing 10

        use nvl_dialogue(dialogue)

        for i in items:
            textbutton i.caption action i.action

screen nvl_dialogue(dialogue):
    for d in dialogue:
        window:
            id d.window_id

            if d.who is not None:
                text d.who id d.who_id

            text d.what id d.what_id

style nvl_window:
    xfill True
    yfill True
    background Solid("#000000dd")
    padding (30, 30, 30, 30)

# ============================================================================
# QUICK MENU - Buttons shown during gameplay
# ============================================================================

screen quick_menu():
    zorder 100

    hbox:
        style_prefix "quick"
        xalign 0.5
        yalign 1.0
        yoffset -10

        textbutton _("Back") action Rollback()
        textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
        textbutton _("Auto") action Preference("auto-forward", "toggle")
        textbutton _("Save") action ShowMenu('save')
        textbutton _("Load") action ShowMenu('load')
        textbutton _("Prefs") action ShowMenu('preferences')

style quick_button:
    background None
    padding (10, 5, 10, 5)

style quick_button_text:
    size 16
    color "#aaaaaa"
    hover_color "#ffffff"

init python:
    config.overlay_screens.append("quick_menu")

# ============================================================================
# MAIN MENU SCREEN
# ============================================================================

screen main_menu():
    tag menu

    add Solid("#1a1a2e")

    frame:
        xalign 0.5
        yalign 0.5
        padding (50, 50, 50, 50)
        background Solid("#2a2a4e")

        vbox:
            spacing 20

            text "HEEBEE" xalign 0.5 size 60 color "#66aaff"
            text "A Visual Novel" xalign 0.5 size 24 color "#aaaaaa"

            null height 30

            textbutton _("Start") action Start() xalign 0.5
            textbutton _("Load") action ShowMenu("load") xalign 0.5
            textbutton _("Preferences") action ShowMenu("preferences") xalign 0.5
            textbutton _("Quit") action Quit(confirm=not main_menu) xalign 0.5

style main_menu_frame:
    background None

style main_menu_text:
    color "#ffffff"

style main_menu_button:
    background Solid("#333355")
    hover_background Solid("#4444aa")
    xsize 300
    padding (20, 10, 20, 10)

style main_menu_button_text:
    xalign 0.5
    color "#cccccc"
    hover_color "#ffffff"

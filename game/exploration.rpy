# exploration.rpy
# Point-and-Click Exploration System for Ren'Py
# This module provides a complete exploration framework with locations, hotspots, and items.

# ============================================================================
# PYTHON CLASSES AND EXPLORATION MANAGER
# ============================================================================

init python:
    import pygame

    class Hotspot:
        """
        Represents a clickable area in a location.

        Attributes:
            id: Unique identifier for this hotspot
            position: Tuple (x, y) for the top-left corner
            size: Tuple (width, height) of the clickable area
            action: The action to perform when clicked (string label or callable)
            hover_text: Text to display when hovering over this hotspot
            required_item: Item ID required to interact (None if no requirement)
            visible: Whether this hotspot is currently visible
            visible_condition: A callable that returns True if hotspot should be visible
            one_time: If True, hotspot disappears after first interaction
            interacted: Whether this hotspot has been interacted with
        """
        def __init__(self, id, position, size, action, hover_text="",
                     required_item=None, visible=True, visible_condition=None,
                     one_time=False):
            self.id = id
            self.position = position
            self.size = size
            self.action = action
            self.hover_text = hover_text
            self.required_item = required_item
            self.visible = visible
            self.visible_condition = visible_condition
            self.one_time = one_time
            self.interacted = False

        def get_rect(self):
            """Returns a pygame Rect for collision detection."""
            return pygame.Rect(self.position[0], self.position[1],
                             self.size[0], self.size[1])

        def is_visible(self):
            """Check if hotspot should be visible based on conditions."""
            if not self.visible:
                return False
            if self.one_time and self.interacted:
                return False
            if self.visible_condition is not None:
                return self.visible_condition()
            return True

        def can_interact(self, inventory):
            """Check if player can interact with this hotspot."""
            if self.required_item is None:
                return True
            return self.required_item in inventory

    class Location:
        """
        Represents an explorable location in the game.

        Attributes:
            id: Unique identifier for this location
            name: Display name of the location
            background: Image path for the background
            hotspots: List of Hotspot objects in this location
            items: List of item IDs that can be picked up here
            exits: Dict mapping direction names to location IDs
            discovered: Whether the player has visited this location
            ambient_sound: Optional ambient sound file to play
            on_enter: Optional callback when entering location
            on_exit: Optional callback when leaving location
        """
        def __init__(self, id, name, background, hotspots=None, items=None,
                     exits=None, ambient_sound=None, on_enter=None, on_exit=None):
            self.id = id
            self.name = name
            self.background = background
            self.hotspots = hotspots if hotspots is not None else []
            self.items = items if items is not None else []
            self.exits = exits if exits is not None else {}
            self.discovered = False
            self.ambient_sound = ambient_sound
            self.on_enter = on_enter
            self.on_exit = on_exit

        def add_hotspot(self, hotspot):
            """Add a hotspot to this location."""
            self.hotspots.append(hotspot)

        def remove_hotspot(self, hotspot_id):
            """Remove a hotspot by ID."""
            self.hotspots = [h for h in self.hotspots if h.id != hotspot_id]

        def get_hotspot(self, hotspot_id):
            """Get a hotspot by ID."""
            for h in self.hotspots:
                if h.id == hotspot_id:
                    return h
            return None

        def add_item(self, item_id):
            """Add an item to this location."""
            if item_id not in self.items:
                self.items.append(item_id)

        def remove_item(self, item_id):
            """Remove an item from this location."""
            if item_id in self.items:
                self.items.remove(item_id)

        def get_visible_hotspots(self):
            """Get all currently visible hotspots."""
            return [h for h in self.hotspots if h.is_visible()]

    class ExplorationManager:
        """
        Manages the exploration system including locations, inventory, and navigation.

        Attributes:
            locations: Dict mapping location IDs to Location objects
            current_location: Currently active Location object
            discovered_locations: Set of discovered location IDs
            inventory: List of item IDs in player's inventory
            examined_objects: Set of object IDs that have been examined
            tooltip_text: Current tooltip text to display
            selected_item: Currently selected inventory item for use
        """
        def __init__(self):
            self.locations = {}
            self.current_location = None
            self.discovered_locations = set()
            self.inventory = []
            self.examined_objects = set()
            self.tooltip_text = ""
            self.selected_item = None

        def register_location(self, location):
            """Register a location with the manager."""
            self.locations[location.id] = location

        def get_location(self, location_id):
            """Get a location by ID."""
            return self.locations.get(location_id)

        def move_to_location(self, location_id):
            """
            Move the player to a new location.
            Returns True if successful, False otherwise.
            """
            if location_id not in self.locations:
                return False

            # Call on_exit for current location
            if self.current_location and self.current_location.on_exit:
                self.current_location.on_exit()

            # Update current location
            new_location = self.locations[location_id]
            self.current_location = new_location

            # Mark as discovered
            new_location.discovered = True
            self.discovered_locations.add(location_id)

            # Call on_enter for new location
            if new_location.on_enter:
                new_location.on_enter()

            # Clear tooltip
            self.tooltip_text = ""

            return True

        def interact_with_hotspot(self, hotspot_id):
            """
            Interact with a hotspot in the current location.
            Returns the action to perform, or None if interaction not possible.
            """
            if not self.current_location:
                return None

            hotspot = self.current_location.get_hotspot(hotspot_id)
            if not hotspot or not hotspot.is_visible():
                return None

            if not hotspot.can_interact(self.inventory):
                return ("need_item", hotspot.required_item)

            # Mark as interacted
            hotspot.interacted = True

            # Consume required item if specified
            if hotspot.required_item and hotspot.required_item in self.inventory:
                # Note: We don't automatically consume items - the action can do that
                pass

            return ("success", hotspot.action)

        def examine(self, object_id, description=""):
            """
            Examine an object, marking it as examined.
            Returns the description.
            """
            self.examined_objects.add(object_id)
            return description

        def has_examined(self, object_id):
            """Check if an object has been examined."""
            return object_id in self.examined_objects

        def pick_up_item(self, item_id):
            """
            Pick up an item from the current location.
            Returns True if successful, False otherwise.
            """
            if not self.current_location:
                return False

            if item_id not in self.current_location.items:
                return False

            # Remove from location and add to inventory
            self.current_location.remove_item(item_id)
            if item_id not in self.inventory:
                self.inventory.append(item_id)

            return True

        def has_item(self, item_id):
            """Check if player has an item in inventory."""
            return item_id in self.inventory

        def remove_item(self, item_id):
            """Remove an item from inventory."""
            if item_id in self.inventory:
                self.inventory.remove(item_id)
                if self.selected_item == item_id:
                    self.selected_item = None
                return True
            return False

        def select_item(self, item_id):
            """Select an item for use."""
            if item_id in self.inventory:
                self.selected_item = item_id
                return True
            return False

        def deselect_item(self):
            """Deselect the currently selected item."""
            self.selected_item = None

        def set_tooltip(self, text):
            """Set the current tooltip text."""
            self.tooltip_text = text

        def clear_tooltip(self):
            """Clear the tooltip text."""
            self.tooltip_text = ""

        def get_discovered_locations(self):
            """Get all discovered locations for fast travel."""
            return [self.locations[lid] for lid in self.discovered_locations
                    if lid in self.locations]

        def can_fast_travel_to(self, location_id):
            """Check if player can fast travel to a location."""
            return location_id in self.discovered_locations

# ============================================================================
# GLOBAL EXPLORATION MANAGER INSTANCE
# ============================================================================

default exploration_manager = ExplorationManager()

# ============================================================================
# ITEM DEFINITIONS
# ============================================================================

# Define items with their display names and descriptions
define item_data = {
    "old_key": {
        "name": "Old Key",
        "description": "A rusty old key. It looks like it might open an antique lock.",
        "icon": "gui/items/old_key.png"
    },
    "flashlight": {
        "name": "Flashlight",
        "description": "A battery-powered flashlight. Still works!",
        "icon": "gui/items/flashlight.png"
    },
    "mysterious_note": {
        "name": "Mysterious Note",
        "description": "A crumpled note with strange symbols.",
        "icon": "gui/items/note.png"
    },
    "garden_flower": {
        "name": "Garden Flower",
        "description": "A beautiful flower from the garden. Someone might appreciate this.",
        "icon": "gui/items/flower.png"
    },
    "ancient_book": {
        "name": "Ancient Book",
        "description": "A leather-bound book with arcane symbols on the cover.",
        "icon": "gui/items/book.png"
    }
}

# ============================================================================
# PLACEHOLDER BACKGROUNDS FOR EXPLORATION
# ============================================================================

image bg_explore_room = Solid("#3a3a4e")
image bg_explore_hallway = Solid("#4a3a3a")
image bg_explore_garden = Solid("#2a4a2a")

# Hotspot highlight overlay (for debug/development)
image hotspot_highlight = Solid("#ffff0044")

# ============================================================================
# EXPLORATION SCREEN
# ============================================================================

screen exploration():
    tag exploration
    modal True

    # Background
    if exploration_manager.current_location:
        add exploration_manager.current_location.background

    # Location name display
    if exploration_manager.current_location:
        frame:
            xalign 0.5
            yalign 0.02
            padding (20, 10)
            background Solid("#000000aa")
            text exploration_manager.current_location.name:
                size 28
                color "#ffffff"

    # Clickable hotspots
    if exploration_manager.current_location:
        for hotspot in exploration_manager.current_location.get_visible_hotspots():
            button:
                xpos hotspot.position[0]
                ypos hotspot.position[1]
                xsize hotspot.size[0]
                ysize hotspot.size[1]
                background Solid("#ffffff11")
                hover_background Solid("#ffffff33")
                action Function(handle_hotspot_click, hotspot.id)
                hovered Function(exploration_manager.set_tooltip, hotspot.hover_text)
                unhovered Function(exploration_manager.clear_tooltip)

                # Visual indicator that something is here
                add Solid("#ffffff22"):
                    xsize hotspot.size[0]
                    ysize hotspot.size[1]

    # Exit buttons
    if exploration_manager.current_location:
        for direction, target_id in exploration_manager.current_location.exits.items():
            $ exit_pos = get_exit_position(direction)
            button:
                xpos exit_pos[0]
                ypos exit_pos[1]
                padding (15, 10)
                background Solid("#333366cc")
                hover_background Solid("#4444aacc")
                action Function(exploration_manager.move_to_location, target_id)
                hovered Function(exploration_manager.set_tooltip, "Go to " + direction)
                unhovered Function(exploration_manager.clear_tooltip)

                text direction.capitalize():
                    size 18
                    color "#ffffff"

    # Tooltip display
    if exploration_manager.tooltip_text:
        frame:
            xalign 0.5
            yalign 0.92
            padding (20, 10)
            background Solid("#000000dd")
            text exploration_manager.tooltip_text:
                size 22
                color "#ffff88"

    # Inventory bar at bottom
    hbox:
        xalign 0.5
        yalign 0.99
        spacing 10

        for item_id in exploration_manager.inventory:
            $ item_info = item_data.get(item_id, {"name": item_id, "icon": None})
            button:
                xsize 60
                ysize 60
                background Solid("#444444cc") if exploration_manager.selected_item != item_id else Solid("#666688cc")
                hover_background Solid("#555555cc")
                action Function(toggle_item_selection, item_id)
                hovered Function(exploration_manager.set_tooltip, item_info.get("name", item_id))
                unhovered Function(exploration_manager.clear_tooltip)

                text item_id[:3].upper():
                    xalign 0.5
                    yalign 0.5
                    size 14
                    color "#ffffff"

    # Control buttons
    hbox:
        xalign 0.98
        yalign 0.02
        spacing 10

        textbutton "Map":
            text_size 18
            action ShowMenu("location_map")

        textbutton "Exit":
            text_size 18
            action Return()

# ============================================================================
# LOCATION MAP / FAST TRAVEL SCREEN
# ============================================================================

screen location_map():
    tag menu
    modal True

    add Solid("#1a1a2e")

    frame:
        xalign 0.5
        yalign 0.5
        padding (40, 40)
        background Solid("#2a2a4e")

        vbox:
            spacing 20

            text "Location Map" xalign 0.5 size 36 color "#66aaff"

            null height 20

            text "Discovered Locations:" xalign 0.5 size 24 color "#aaaaaa"

            null height 10

            # List of discovered locations
            vbox:
                spacing 10
                xalign 0.5

                for location in exploration_manager.get_discovered_locations():
                    $ is_current = (exploration_manager.current_location and
                                   exploration_manager.current_location.id == location.id)
                    button:
                        xsize 300
                        padding (20, 10)
                        background Solid("#333355") if not is_current else Solid("#555577")
                        hover_background Solid("#4444aa")
                        action [
                            Function(exploration_manager.move_to_location, location.id),
                            Hide("location_map")
                        ] if not is_current else NullAction()

                        hbox:
                            spacing 10
                            text location.name:
                                size 20
                                color "#ffffff" if not is_current else "#88ff88"
                            if is_current:
                                text "(Current)" size 16 color "#88ff88" yalign 0.5

            null height 20

            textbutton "Close" action Hide("location_map") xalign 0.5

# ============================================================================
# ITEM EXAMINATION SCREEN
# ============================================================================

screen examine_item(item_id):
    tag menu
    modal True

    $ item_info = item_data.get(item_id, {"name": item_id, "description": "No description available."})

    add Solid("#00000099")

    frame:
        xalign 0.5
        yalign 0.5
        padding (40, 40)
        background Solid("#2a2a4e")
        xsize 500

        vbox:
            spacing 20

            text item_info.get("name", item_id):
                xalign 0.5
                size 32
                color "#ffcc66"

            null height 10

            # Item icon placeholder
            frame:
                xalign 0.5
                xsize 100
                ysize 100
                background Solid("#444444")

                text item_id[:3].upper():
                    xalign 0.5
                    yalign 0.5
                    size 24
                    color "#ffffff"

            null height 10

            text item_info.get("description", ""):
                xalign 0.5
                size 20
                color "#cccccc"
                text_align 0.5

            null height 20

            textbutton "Close" action Hide("examine_item") xalign 0.5

# ============================================================================
# HOTSPOT INTERACTION SCREEN
# ============================================================================

screen hotspot_message(title, message):
    tag menu
    modal True

    add Solid("#00000099")

    frame:
        xalign 0.5
        yalign 0.5
        padding (40, 40)
        background Solid("#2a2a4e")
        xsize 500

        vbox:
            spacing 20

            text title:
                xalign 0.5
                size 28
                color "#ffcc66"

            null height 10

            text message:
                xalign 0.5
                size 20
                color "#cccccc"
                text_align 0.5

            null height 20

            textbutton "OK" action Hide("hotspot_message") xalign 0.5

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

init python:
    def get_exit_position(direction):
        """Get screen position for exit buttons based on direction."""
        positions = {
            "north": (0.5 * config.screen_width - 50, 50),
            "south": (0.5 * config.screen_width - 50, config.screen_height - 100),
            "east": (config.screen_width - 120, 0.5 * config.screen_height),
            "west": (20, 0.5 * config.screen_height),
            "up": (config.screen_width - 120, 100),
            "down": (config.screen_width - 120, config.screen_height - 150),
        }
        return positions.get(direction.lower(), (0.5 * config.screen_width, 0.5 * config.screen_height))

    def handle_hotspot_click(hotspot_id):
        """Handle clicking on a hotspot."""
        result = exploration_manager.interact_with_hotspot(hotspot_id)

        if result is None:
            return

        status, data = result

        if status == "need_item":
            item_name = item_data.get(data, {}).get("name", data)
            renpy.show_screen("hotspot_message",
                            title="Cannot Interact",
                            message="You need the {} to interact with this.".format(item_name))
        elif status == "success":
            if isinstance(data, str):
                # It's a label to jump to
                renpy.call_in_new_context(data)
            elif callable(data):
                # It's a function to call
                data()

    def toggle_item_selection(item_id):
        """Toggle selection of an inventory item."""
        if exploration_manager.selected_item == item_id:
            exploration_manager.deselect_item()
        else:
            exploration_manager.select_item(item_id)

    def show_item_pickup_message(item_id):
        """Show a message when picking up an item."""
        item_name = item_data.get(item_id, {}).get("name", item_id)
        renpy.show_screen("hotspot_message",
                         title="Item Found!",
                         message="You picked up: {}".format(item_name))

# ============================================================================
# EXAMPLE LOCATIONS SETUP
# ============================================================================

init python:
    def setup_example_locations():
        """Set up example exploration locations."""
        global exploration_manager

        # Create the Room location
        room = Location(
            id="room",
            name="The Study",
            background="bg_explore_room",
            exits={"hallway": "hallway"}
        )

        # Add hotspots to the room
        room.add_hotspot(Hotspot(
            id="room_desk",
            position=(100, 200),
            size=(200, 150),
            action="examine_desk",
            hover_text="An old wooden desk"
        ))

        room.add_hotspot(Hotspot(
            id="room_bookshelf",
            position=(400, 100),
            size=(180, 300),
            action="examine_bookshelf",
            hover_text="A dusty bookshelf"
        ))

        room.add_hotspot(Hotspot(
            id="room_safe",
            position=(650, 250),
            size=(100, 100),
            action="examine_safe",
            hover_text="A locked safe",
            required_item="old_key",
            visible_condition=lambda: exploration_manager.has_examined("room_bookshelf")
        ))

        # Add an item that can be picked up
        room.add_item("flashlight")
        room.add_hotspot(Hotspot(
            id="room_flashlight",
            position=(300, 350),
            size=(80, 40),
            action=lambda: pickup_and_notify("flashlight"),
            hover_text="A flashlight on the floor",
            one_time=True
        ))

        # Create the Hallway location
        hallway = Location(
            id="hallway",
            name="Main Hallway",
            background="bg_explore_hallway",
            exits={"study": "room", "garden": "garden"}
        )

        hallway.add_hotspot(Hotspot(
            id="hallway_painting",
            position=(200, 100),
            size=(150, 200),
            action="examine_painting",
            hover_text="A mysterious painting"
        ))

        hallway.add_hotspot(Hotspot(
            id="hallway_cabinet",
            position=(500, 200),
            size=(120, 180),
            action="examine_cabinet",
            hover_text="An antique cabinet"
        ))

        hallway.add_item("old_key")
        hallway.add_hotspot(Hotspot(
            id="hallway_key",
            position=(350, 380),
            size=(60, 30),
            action=lambda: pickup_and_notify("old_key"),
            hover_text="Something shiny on the floor",
            one_time=True
        ))

        # Create the Garden location
        garden = Location(
            id="garden",
            name="Garden",
            background="bg_explore_garden",
            exits={"inside": "hallway"}
        )

        garden.add_hotspot(Hotspot(
            id="garden_fountain",
            position=(300, 150),
            size=(200, 200),
            action="examine_fountain",
            hover_text="An old stone fountain"
        ))

        garden.add_hotspot(Hotspot(
            id="garden_flowers",
            position=(100, 300),
            size=(150, 100),
            action=lambda: pickup_and_notify("garden_flower"),
            hover_text="Beautiful flowers",
            one_time=True
        ))

        garden.add_item("garden_flower")

        garden.add_hotspot(Hotspot(
            id="garden_statue",
            position=(550, 200),
            size=(120, 250),
            action="examine_statue",
            hover_text="A weathered statue",
            visible_condition=lambda: exploration_manager.has_item("flashlight")
        ))

        # Register all locations
        exploration_manager.register_location(room)
        exploration_manager.register_location(hallway)
        exploration_manager.register_location(garden)

    def pickup_and_notify(item_id):
        """Helper to pick up an item and show notification."""
        if exploration_manager.pick_up_item(item_id):
            show_item_pickup_message(item_id)

# ============================================================================
# EXPLORATION INTERACTION LABELS
# ============================================================================

label examine_desk:
    $ exploration_manager.examine("room_desk")
    "You examine the old wooden desk."
    "There are papers scattered across its surface, but nothing immediately useful."
    "Wait... there's a note tucked under a paperweight."
    $ exploration_manager.pick_up_item("mysterious_note") if "mysterious_note" not in exploration_manager.inventory else None
    if "mysterious_note" in exploration_manager.inventory:
        "You found a Mysterious Note!"
    return

label examine_bookshelf:
    $ exploration_manager.examine("room_bookshelf")
    "The bookshelf is filled with ancient tomes and dusty volumes."
    "As you examine the books, you notice one section seems different..."
    "There's a gap behind some of the books. Something is hidden here!"
    "You notice what appears to be a safe hidden behind a false panel."
    return

label examine_safe:
    if exploration_manager.has_item("old_key"):
        "You use the old key to open the safe..."
        $ exploration_manager.remove_item("old_key")
        "Click! The safe opens!"
        "Inside, you find an ancient leather-bound book."
        $ exploration_manager.inventory.append("ancient_book") if "ancient_book" not in exploration_manager.inventory else None
        "You obtained the Ancient Book!"
    else:
        "The safe is locked. You need a key to open it."
    return

label examine_painting:
    $ exploration_manager.examine("hallway_painting")
    "A portrait of someone from long ago stares back at you."
    "The eyes seem to follow you as you move..."
    "There's something unsettling about this painting."
    return

label examine_cabinet:
    $ exploration_manager.examine("hallway_cabinet")
    "An ornate cabinet filled with curiosities."
    "Most of the drawers are stuck shut with age."
    "One drawer contains only old photographs and yellowed letters."
    return

label examine_fountain:
    $ exploration_manager.examine("garden_fountain")
    "The fountain hasn't run in years."
    "Moss covers the stone, and the basin is filled with fallen leaves."
    "Something glints at the bottom of the empty basin..."
    return

label examine_statue:
    $ exploration_manager.examine("garden_statue")
    if exploration_manager.has_item("flashlight"):
        "You shine your flashlight on the weathered statue."
        "The light reveals an inscription you couldn't see before:"
        "\"The truth lies where shadows cannot reach.\""
    else:
        "The statue is too dark to examine properly."
        "You might need a light source."
    return

# ============================================================================
# EXPLORATION ENTRY POINT
# ============================================================================

label start_exploration:
    # Initialize locations if not already done
    $ setup_example_locations()

    # Start in the room
    $ exploration_manager.move_to_location("room")

    "You find yourself in a mysterious old house..."
    "Click around to explore and find clues."

    # Show the exploration screen
    call screen exploration

    "You finished exploring for now."
    return

# ============================================================================
# INTEGRATION EXAMPLE
# ============================================================================
# To use this exploration system in your game, add this to your script:
#
#   label some_point_in_story:
#       "The character enters an explorable area..."
#       call start_exploration
#       "After exploring..."
#       # Continue your story
#
# Or create your own locations:
#
#   init python:
#       my_location = Location(
#           id="my_loc",
#           name="My Custom Location",
#           background="bg_my_location",
#           exits={"exit": "other_location"}
#       )
#       my_location.add_hotspot(Hotspot(
#           id="my_hotspot",
#           position=(100, 100),
#           size=(50, 50),
#           action="my_interaction_label",
#           hover_text="Click me!"
#       ))
#       exploration_manager.register_location(my_location)

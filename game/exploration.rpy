# Point-and-Click Exploration System for Heebee
# Imagemaps with clickable hotspots, location navigation, and discovery

init python:
    class Hotspot:
        """Represents a clickable area in a location"""
        def __init__(self, hotspot_id, name, x, y, width, height, **kwargs):
            self.id = hotspot_id
            self.name = name
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.description = kwargs.get("description", "")
            self.interaction_label = kwargs.get("interaction_label", None)
            self.required_item = kwargs.get("required_item", None)
            self.gives_item = kwargs.get("gives_item", None)
            self.one_time = kwargs.get("one_time", False)
            self.interacted = False
            self.visible = kwargs.get("visible", True)
            self.enabled = kwargs.get("enabled", True)
            self.hover_text = kwargs.get("hover_text", name)
            self.destination = kwargs.get("destination", None)  # For exits

        def get_rect(self):
            """Get rectangle tuple for imagemap"""
            return (self.x, self.y, self.x + self.width, self.y + self.height)

        def can_interact(self, inventory=None):
            """Check if player can interact with this hotspot"""
            if not self.visible or not self.enabled:
                return False
            if self.one_time and self.interacted:
                return False
            if self.required_item and inventory:
                if not inventory.has_item(self.required_item):
                    return False
            return True

        def interact(self, inventory=None):
            """Perform interaction, return label to call or None"""
            if not self.can_interact(inventory):
                return None

            self.interacted = True

            # Give item if configured
            if self.gives_item and inventory:
                inventory.add_item(self.gives_item)

            return self.interaction_label

    class Location:
        """Represents a location that can be explored"""
        def __init__(self, location_id, name, background, **kwargs):
            self.id = location_id
            self.name = name
            self.background = background  # Image path
            self.hotspots = {}
            self.description = kwargs.get("description", "")
            self.ambient_sound = kwargs.get("ambient_sound", None)
            self.music = kwargs.get("music", None)
            self.discovered = kwargs.get("discovered", False)
            self.accessible = kwargs.get("accessible", True)
            self.visited_count = 0
            self.connected_locations = []  # List of location IDs
            self.entry_label = kwargs.get("entry_label", None)
            self.exit_label = kwargs.get("exit_label", None)
            self.idle_animation = kwargs.get("idle_animation", None)

        def add_hotspot(self, hotspot):
            """Add a hotspot to this location"""
            self.hotspots[hotspot.id] = hotspot

        def remove_hotspot(self, hotspot_id):
            """Remove a hotspot"""
            if hotspot_id in self.hotspots:
                del self.hotspots[hotspot_id]

        def get_hotspot(self, hotspot_id):
            """Get a specific hotspot"""
            return self.hotspots.get(hotspot_id)

        def get_visible_hotspots(self):
            """Get all visible hotspots"""
            return [h for h in self.hotspots.values() if h.visible]

        def connect_to(self, location_id):
            """Connect this location to another"""
            if location_id not in self.connected_locations:
                self.connected_locations.append(location_id)

        def visit(self):
            """Mark location as visited"""
            self.visited_count += 1
            self.discovered = True

    class ExplorationManager:
        """Manages all locations and exploration state"""
        def __init__(self):
            self.locations = {}
            self.current_location = None
            self.previous_location = None
            self.discovered_items = []
            self.exploration_progress = {}

        def add_location(self, location):
            """Add a location to the world"""
            self.locations[location.id] = location

        def get_location(self, location_id):
            """Get a location by ID"""
            return self.locations.get(location_id)

        def travel_to(self, location_id):
            """Travel to a new location"""
            if location_id not in self.locations:
                return False

            location = self.locations[location_id]
            if not location.accessible:
                return False

            self.previous_location = self.current_location
            self.current_location = location_id
            location.visit()
            return True

        def get_current_location(self):
            """Get the current location object"""
            if self.current_location:
                return self.locations.get(self.current_location)
            return None

        def get_connected_locations(self):
            """Get locations connected to current location"""
            current = self.get_current_location()
            if not current:
                return []
            return [self.locations[loc_id] for loc_id in current.connected_locations
                    if loc_id in self.locations and self.locations[loc_id].accessible]

        def get_discovered_locations(self):
            """Get all discovered locations"""
            return [loc for loc in self.locations.values() if loc.discovered]

        def unlock_location(self, location_id):
            """Make a location accessible"""
            if location_id in self.locations:
                self.locations[location_id].accessible = True
                self.locations[location_id].discovered = True

        def lock_location(self, location_id):
            """Make a location inaccessible"""
            if location_id in self.locations:
                self.locations[location_id].accessible = False

# Initialize exploration system
default exploration_manager = ExplorationManager()

# Setup example locations
init python:
    def setup_exploration():
        em = exploration_manager

        # Create town square location
        town_square = Location(
            "town_square",
            "Town Square",
            "images/locations/town_square.png",
            description="The bustling center of town.",
            discovered=True
        )
        town_square.add_hotspot(Hotspot(
            "fountain", "Fountain", 400, 300, 200, 150,
            description="A beautiful stone fountain.",
            hover_text="Examine the fountain",
            interaction_label="examine_fountain"
        ))
        town_square.add_hotspot(Hotspot(
            "notice_board", "Notice Board", 100, 200, 80, 120,
            description="A board full of postings.",
            hover_text="Read the notices",
            interaction_label="read_notices"
        ))
        town_square.add_hotspot(Hotspot(
            "to_market", "To Market", 700, 400, 100, 200,
            description="Path to the market district.",
            hover_text="Go to Market",
            destination="market"
        ))
        town_square.add_hotspot(Hotspot(
            "to_tavern", "To Tavern", 50, 400, 100, 200,
            description="The local tavern entrance.",
            hover_text="Enter the Tavern",
            destination="tavern"
        ))
        em.add_location(town_square)

        # Create market location
        market = Location(
            "market",
            "Market District",
            "images/locations/market.png",
            description="Stalls and shops line the streets."
        )
        market.add_hotspot(Hotspot(
            "weapon_shop", "Weapon Shop", 200, 250, 150, 200,
            description="A shop selling weapons and armor.",
            hover_text="Enter Weapon Shop",
            interaction_label="enter_weapon_shop"
        ))
        market.add_hotspot(Hotspot(
            "potion_stall", "Potion Stall", 500, 300, 100, 150,
            description="A stall selling potions and remedies.",
            hover_text="Browse Potions",
            interaction_label="browse_potions"
        ))
        market.add_hotspot(Hotspot(
            "hidden_coin", "Shiny Object", 650, 450, 30, 30,
            description="Something shiny on the ground.",
            hover_text="Pick up",
            gives_item="gold_coin",
            one_time=True,
            visible=True
        ))
        market.add_hotspot(Hotspot(
            "to_town_square", "To Town Square", 400, 500, 200, 100,
            hover_text="Return to Town Square",
            destination="town_square"
        ))
        em.add_location(market)

        # Create tavern location
        tavern = Location(
            "tavern",
            "The Rusty Anchor Tavern",
            "images/locations/tavern.png",
            description="A cozy tavern filled with travelers."
        )
        tavern.add_hotspot(Hotspot(
            "bartender", "Bartender", 350, 200, 100, 200,
            description="The friendly bartender.",
            hover_text="Talk to Bartender",
            interaction_label="talk_bartender"
        ))
        tavern.add_hotspot(Hotspot(
            "mysterious_stranger", "Hooded Figure", 600, 300, 80, 150,
            description="A mysterious figure in the corner.",
            hover_text="Approach the stranger",
            interaction_label="approach_stranger"
        ))
        tavern.add_hotspot(Hotspot(
            "fireplace", "Fireplace", 100, 250, 120, 180,
            description="A warm, crackling fireplace.",
            hover_text="Warm yourself",
            interaction_label="use_fireplace"
        ))
        tavern.add_hotspot(Hotspot(
            "exit_tavern", "Exit", 400, 500, 200, 100,
            hover_text="Leave the Tavern",
            destination="town_square"
        ))
        em.add_location(tavern)

        # Connect locations
        town_square.connect_to("market")
        town_square.connect_to("tavern")
        market.connect_to("town_square")
        tavern.connect_to("town_square")

        # Set starting location
        em.travel_to("town_square")

# Main exploration screen
screen exploration_screen():
    tag exploration

    # Get current location
    $ current_loc = exploration_manager.get_current_location()

    if current_loc:
        # Background image
        add current_loc.background

        # Location name
        frame:
            xalign 0.5
            yalign 0.02
            padding (20, 10)
            text current_loc.name size 28 bold True

        # Hotspots as buttons
        for hotspot_id, hotspot in current_loc.hotspots.items():
            if hotspot.visible:
                $ rect = hotspot.get_rect()
                button:
                    xpos rect[0]
                    ypos rect[1]
                    xsize hotspot.width
                    ysize hotspot.height
                    action Return(("hotspot", hotspot_id))
                    tooltip hotspot.hover_text

                    # Visual indicator (semi-transparent)
                    if hotspot.enabled:
                        background "#ffffff20"
                        hover_background "#ffffff40"
                    else:
                        background "#ff000020"

        # Tooltip display
        $ tooltip_text = GetTooltip()
        if tooltip_text:
            frame:
                xalign 0.5
                yalign 0.95
                padding (15, 8)
                text tooltip_text size 18

        # Navigation buttons
        hbox:
            xalign 0.02
            yalign 0.98
            spacing 10

            textbutton "Map" action Return(("map", None))
            textbutton "Inventory" action Return(("inventory", None))
            textbutton "Back" action Return(("back", None))

# Map screen showing discovered locations
screen map_screen():
    tag menu

    frame:
        xfill True
        yfill True
        padding (50, 50)

        vbox:
            spacing 20

            text "World Map" size 32 bold True xalign 0.5

            null height 20

            text "Discovered Locations:" size 24

            $ discovered = exploration_manager.get_discovered_locations()

            for loc in discovered:
                hbox:
                    spacing 20
                    $ is_current = (loc.id == exploration_manager.current_location)
                    $ can_travel = loc.accessible and not is_current

                    text loc.name size 20:
                        if is_current:
                            color "#FFD700"
                        elif not loc.accessible:
                            color "#888888"

                    if can_travel:
                        textbutton "Travel" action Return(("travel", loc.id))
                    elif is_current:
                        text "(Current)" size 16 yalign 0.5

            null height 30

            textbutton "Close Map" action Return(("close", None)) xalign 0.5

# Hotspot interaction labels
label examine_fountain:
    "The fountain features an elegant statue of a mermaid."
    "Crystal clear water flows from her outstretched hands."
    "You notice some coins at the bottom. Make a wish?"
    menu:
        "Toss a coin and make a wish":
            "You toss a coin into the fountain."
            "You feel... lucky?"
        "Just admire it":
            "You simply enjoy the peaceful sound of flowing water."
    return

label read_notices:
    "The notice board is covered with various postings."
    menu:
        "Read 'Help Wanted' poster":
            "The local guild is seeking adventurers for a quest."
            "Reward: 500 Gold"
        "Read 'Missing Pet' notice":
            "Someone's cat named 'Whiskers' has gone missing."
            "Last seen near the market."
        "Read 'Town Event' announcement":
            "The annual harvest festival is next week!"
        "Step away":
            pass
    return

label talk_bartender:
    "Bartender" "Welcome, traveler! What can I get for ya?"
    menu:
        "Ask for a drink":
            "Bartender" "Coming right up!"
            "You enjoy a refreshing beverage."
        "Ask for information":
            "Bartender" "Looking for rumors, eh? Well..."
            "Bartender" "I heard there's treasure hidden in the old ruins north of town."
        "Just browsing":
            "Bartender" "Take your time, friend."
    return

label approach_stranger:
    "You approach the hooded figure cautiously."
    "???" "..."
    "???" "You seek something. I can see it in your eyes."
    menu:
        "Ask about the stranger":
            "???" "Who I am matters not. What matters is your journey."
        "Ask about the town":
            "???" "This town holds many secrets. Look beneath the surface."
        "Leave them alone":
            "You decide not to disturb them further."
    return

label use_fireplace:
    "You warm yourself by the crackling fire."
    "The warmth is comforting after your travels."
    "You feel refreshed."
    return

label enter_weapon_shop:
    "You enter the weapon shop."
    "Rows of swords, axes, and armor line the walls."
    # Could integrate with shop system here
    return

label browse_potions:
    "The potion seller greets you with a toothy grin."
    "Potion Seller" "Potions! Get your potions here!"
    # Could integrate with shop system here
    return

# Main exploration loop
label exploration_demo:
    python:
        setup_exploration()

    "Welcome to the exploration demo!"
    "Click on highlighted areas to interact with them."
    "Use the map to travel between discovered locations."

label exploration_loop:
    call screen exploration_screen
    $ result = _return

    if result[0] == "hotspot":
        $ hotspot_id = result[1]
        $ current_loc = exploration_manager.get_current_location()
        $ hotspot = current_loc.get_hotspot(hotspot_id)

        if hotspot and hotspot.destination:
            # Travel to destination
            $ success = exploration_manager.travel_to(hotspot.destination)
            if success:
                $ new_loc = exploration_manager.get_current_location()
                "You travel to [new_loc.name]."
            else:
                "You can't go there right now."
        elif hotspot and hotspot.interaction_label:
            call expression hotspot.interaction_label from _call_hotspot_interaction

    elif result[0] == "map":
        call screen map_screen
        $ map_result = _return
        if map_result[0] == "travel":
            $ success = exploration_manager.travel_to(map_result[1])
            if success:
                $ new_loc = exploration_manager.get_current_location()
                "You travel to [new_loc.name]."

    elif result[0] == "inventory":
        # Could show inventory screen here
        "Inventory functionality would go here."

    elif result[0] == "back":
        if exploration_manager.previous_location:
            $ exploration_manager.travel_to(exploration_manager.previous_location)
        else:
            "You have nowhere to go back to."

    jump exploration_loop

# World Map Travel System for Ren'Py Visual Novel
# This module provides a comprehensive world map system with location management,
# travel mechanics, random travel events, and travel time calculations.

init python:
    import math

    # =========================================================================
    # MAP LOCATION CLASS - Represents a location on the world map
    # =========================================================================

    class MapLocation:
        """
        Represents a location on the world map that the player can visit.

        Attributes:
            id (str): Unique identifier for the location
            name (str): Display name of the location
            description (str): Description shown when viewing location info
            position (tuple): (x, y) coordinates on the map (0-100 scale)
            unlocked (bool): Whether the location is available for travel
            connected_locations (list): List of location IDs that can be reached
            icon (str): Path to location icon image
            visited (bool): Whether player has visited this location
            region (str): Region/area the location belongs to
        """

        def __init__(self, id, name, description="", position=(0, 0),
                     unlocked=False, connected_locations=None, icon=None, region=None):
            self.id = id
            self.name = name
            self.description = description
            self.position = position
            self.unlocked = unlocked
            self.connected_locations = connected_locations if connected_locations else []
            self.icon = icon
            self.visited = False
            self.region = region

        def unlock(self):
            """Unlock this location for travel."""
            self.unlocked = True

        def lock(self):
            """Lock this location from travel."""
            self.unlocked = False

        def mark_visited(self):
            """Mark this location as visited."""
            self.visited = True

        def add_connection(self, location_id):
            """Add a connection to another location."""
            if location_id not in self.connected_locations:
                self.connected_locations.append(location_id)

        def remove_connection(self, location_id):
            """Remove a connection to another location."""
            if location_id in self.connected_locations:
                self.connected_locations.remove(location_id)

        def is_connected_to(self, location_id):
            """Check if this location is connected to another location."""
            return location_id in self.connected_locations

        def get_distance_to(self, other_location):
            """Calculate Euclidean distance to another location."""
            dx = self.position[0] - other_location.position[0]
            dy = self.position[1] - other_location.position[1]
            return math.sqrt(dx * dx + dy * dy)

    # =========================================================================
    # TRAVEL EVENT CLASS - Represents random events during travel
    # =========================================================================

    class TravelEvent:
        """
        Represents a random event that can occur during travel.

        Attributes:
            id (str): Unique identifier for the event
            description (str): Description shown when event triggers
            chance (float): Probability of event occurring (0.0 to 1.0)
            effect_label (str): Ren'Py label to call when event triggers
            min_distance (float): Minimum travel distance for event to trigger
            regions (list): List of regions where event can occur (None = all)
            one_time (bool): Whether event can only occur once
            triggered (bool): Whether event has been triggered (for one-time events)
        """

        def __init__(self, id, description="", chance=0.1, effect_label=None,
                     min_distance=0, regions=None, one_time=False):
            self.id = id
            self.description = description
            self.chance = max(0.0, min(1.0, chance))
            self.effect_label = effect_label
            self.min_distance = min_distance
            self.regions = regions
            self.one_time = one_time
            self.triggered = False

        def can_trigger(self, distance, region=None):
            """Check if this event can trigger based on conditions."""
            if self.one_time and self.triggered:
                return False
            if distance < self.min_distance:
                return False
            if self.regions and region and region not in self.regions:
                return False
            return True

        def should_trigger(self, distance, region=None):
            """Roll to see if event triggers (checks conditions and chance)."""
            if not self.can_trigger(distance, region):
                return False
            return renpy.random.random() < self.chance

        def mark_triggered(self):
            """Mark this event as triggered."""
            self.triggered = True

        def reset(self):
            """Reset the triggered state."""
            self.triggered = False

    # =========================================================================
    # WORLD MAP MANAGER CLASS - Central manager for world map system
    # =========================================================================

    class WorldMapManager:
        """
        Central manager for the world map travel system.

        Manages locations, travel between locations, random events,
        and travel time/cost calculations.

        Attributes:
            locations (dict): Dictionary of location_id -> MapLocation
            travel_events (list): List of possible TravelEvent objects
            current_location_id (str): ID of player's current location
            travel_speed (float): Units traveled per time unit (default 10)
            travel_cost_per_unit (float): Gold cost per unit distance (default 1)
        """

        def __init__(self, travel_speed=10.0, travel_cost_per_unit=1.0):
            self.locations = {}
            self.travel_events = []
            self.current_location_id = None
            self.travel_speed = travel_speed
            self.travel_cost_per_unit = travel_cost_per_unit
            self._travel_history = []

        # ---------------------------------------------------------------------
        # Location Management
        # ---------------------------------------------------------------------

        def register_location(self, location):
            """
            Register a new location on the world map.

            Args:
                location (MapLocation): The location to register

            Returns:
                MapLocation: The registered location
            """
            self.locations[location.id] = location
            return location

        def get_location(self, location_id):
            """
            Get a location by its ID.

            Args:
                location_id (str): The location identifier

            Returns:
                MapLocation: The location or None if not found
            """
            return self.locations.get(location_id, None)

        def remove_location(self, location_id):
            """
            Remove a location from the world map.

            Args:
                location_id (str): The location identifier

            Returns:
                bool: True if removed, False if not found
            """
            if location_id in self.locations:
                # Remove connections to this location from other locations
                for loc in self.locations.values():
                    if location_id in loc.connected_locations:
                        loc.connected_locations.remove(location_id)
                del self.locations[location_id]
                return True
            return False

        def get_all_locations(self):
            """Get list of all locations."""
            return list(self.locations.values())

        def get_unlocked_locations(self):
            """Get list of all unlocked locations."""
            return [loc for loc in self.locations.values() if loc.unlocked]

        def get_visited_locations(self):
            """Get list of all visited locations."""
            return [loc for loc in self.locations.values() if loc.visited]

        def get_locations_by_region(self, region):
            """Get all locations in a specific region."""
            return [loc for loc in self.locations.values() if loc.region == region]

        # ---------------------------------------------------------------------
        # Location Discovery/Unlocking
        # ---------------------------------------------------------------------

        def unlock_location(self, location_id):
            """
            Unlock a location for travel.

            Args:
                location_id (str): The location identifier

            Returns:
                bool: True if unlocked, False if not found
            """
            location = self.get_location(location_id)
            if location:
                location.unlock()
                return True
            return False

        def lock_location(self, location_id):
            """
            Lock a location from travel.

            Args:
                location_id (str): The location identifier

            Returns:
                bool: True if locked, False if not found
            """
            location = self.get_location(location_id)
            if location:
                location.lock()
                return True
            return False

        def discover_location(self, location_id):
            """
            Discover and unlock a location.

            Args:
                location_id (str): The location identifier

            Returns:
                bool: True if discovered, False if not found
            """
            return self.unlock_location(location_id)

        # ---------------------------------------------------------------------
        # Current Location Management
        # ---------------------------------------------------------------------

        def get_current_location(self):
            """
            Get the player's current location.

            Returns:
                MapLocation: Current location or None
            """
            if self.current_location_id:
                return self.get_location(self.current_location_id)
            return None

        def set_current_location(self, location_id):
            """
            Set the player's current location.

            Args:
                location_id (str): The location identifier

            Returns:
                bool: True if set, False if location not found
            """
            location = self.get_location(location_id)
            if location:
                self.current_location_id = location_id
                location.mark_visited()
                return True
            return False

        def get_connected_locations(self):
            """
            Get locations connected to current location.

            Returns:
                list: List of connected MapLocation objects
            """
            current = self.get_current_location()
            if not current:
                return []
            return [self.get_location(loc_id)
                    for loc_id in current.connected_locations
                    if self.get_location(loc_id)]

        def get_available_destinations(self):
            """
            Get unlocked locations connected to current location.

            Returns:
                list: List of available MapLocation objects
            """
            return [loc for loc in self.get_connected_locations()
                    if loc and loc.unlocked]

        # ---------------------------------------------------------------------
        # Travel Time and Cost Calculations
        # ---------------------------------------------------------------------

        def calculate_travel_time(self, from_location_id, to_location_id):
            """
            Calculate travel time between two locations.

            Args:
                from_location_id (str): Starting location ID
                to_location_id (str): Destination location ID

            Returns:
                float: Travel time in time units, or -1 if invalid
            """
            from_loc = self.get_location(from_location_id)
            to_loc = self.get_location(to_location_id)

            if not from_loc or not to_loc:
                return -1

            distance = from_loc.get_distance_to(to_loc)
            return distance / self.travel_speed

        def calculate_travel_cost(self, from_location_id, to_location_id):
            """
            Calculate travel cost between two locations.

            Args:
                from_location_id (str): Starting location ID
                to_location_id (str): Destination location ID

            Returns:
                float: Travel cost in gold, or -1 if invalid
            """
            from_loc = self.get_location(from_location_id)
            to_loc = self.get_location(to_location_id)

            if not from_loc or not to_loc:
                return -1

            distance = from_loc.get_distance_to(to_loc)
            return distance * self.travel_cost_per_unit

        def get_travel_info(self, from_location_id, to_location_id):
            """
            Get complete travel information between two locations.

            Args:
                from_location_id (str): Starting location ID
                to_location_id (str): Destination location ID

            Returns:
                dict: Travel info including distance, time, cost, or None
            """
            from_loc = self.get_location(from_location_id)
            to_loc = self.get_location(to_location_id)

            if not from_loc or not to_loc:
                return None

            distance = from_loc.get_distance_to(to_loc)

            return {
                "from": from_loc,
                "to": to_loc,
                "distance": distance,
                "time": distance / self.travel_speed,
                "cost": distance * self.travel_cost_per_unit,
                "can_travel": to_loc.unlocked and from_loc.is_connected_to(to_location_id)
            }

        # ---------------------------------------------------------------------
        # Travel Events
        # ---------------------------------------------------------------------

        def register_travel_event(self, event):
            """
            Register a new travel event.

            Args:
                event (TravelEvent): The event to register

            Returns:
                TravelEvent: The registered event
            """
            self.travel_events.append(event)
            return event

        def get_travel_event(self, event_id):
            """
            Get a travel event by ID.

            Args:
                event_id (str): The event identifier

            Returns:
                TravelEvent: The event or None
            """
            for event in self.travel_events:
                if event.id == event_id:
                    return event
            return None

        def remove_travel_event(self, event_id):
            """
            Remove a travel event.

            Args:
                event_id (str): The event identifier

            Returns:
                bool: True if removed, False if not found
            """
            event = self.get_travel_event(event_id)
            if event:
                self.travel_events.remove(event)
                return True
            return False

        def check_for_travel_event(self, distance, region=None):
            """
            Roll for a random travel event.

            Args:
                distance (float): Distance of travel
                region (str): Current region (optional)

            Returns:
                TravelEvent: Triggered event or None
            """
            # Shuffle events for fairness
            events = list(self.travel_events)
            renpy.random.shuffle(events)

            for event in events:
                if event.should_trigger(distance, region):
                    if event.one_time:
                        event.mark_triggered()
                    return event

            return None

        def reset_travel_events(self):
            """Reset all one-time travel events."""
            for event in self.travel_events:
                event.reset()

        # ---------------------------------------------------------------------
        # Travel Execution
        # ---------------------------------------------------------------------

        def can_travel_to(self, location_id):
            """
            Check if player can travel to a location.

            Args:
                location_id (str): Destination location ID

            Returns:
                tuple: (can_travel, reason) where reason explains why not
            """
            current = self.get_current_location()
            if not current:
                return False, "No current location set"

            destination = self.get_location(location_id)
            if not destination:
                return False, "Destination not found"

            if not destination.unlocked:
                return False, "Destination is locked"

            if not current.is_connected_to(location_id):
                return False, "Destination is not connected"

            return True, "Travel allowed"

        def travel_to(self, location_id):
            """
            Execute travel to a location.

            Args:
                location_id (str): Destination location ID

            Returns:
                dict: Travel result including success, event, time, cost
            """
            can_travel, reason = self.can_travel_to(location_id)

            if not can_travel:
                return {
                    "success": False,
                    "reason": reason,
                    "event": None,
                    "time": 0,
                    "cost": 0
                }

            current = self.get_current_location()
            destination = self.get_location(location_id)

            # Calculate travel details
            distance = current.get_distance_to(destination)
            travel_time = distance / self.travel_speed
            travel_cost = distance * self.travel_cost_per_unit

            # Check for random event
            event = self.check_for_travel_event(distance, destination.region)

            # Record travel history
            self._travel_history.append({
                "from": current.id,
                "to": destination.id,
                "distance": distance,
                "time": travel_time,
                "cost": travel_cost,
                "event": event.id if event else None
            })

            # Update current location
            self.set_current_location(location_id)

            return {
                "success": True,
                "reason": "Travel complete",
                "event": event,
                "time": travel_time,
                "cost": travel_cost,
                "from_location": current,
                "to_location": destination
            }

        def get_travel_history(self):
            """Get the travel history log."""
            return list(self._travel_history)

        # ---------------------------------------------------------------------
        # Connection Management
        # ---------------------------------------------------------------------

        def connect_locations(self, location_id_1, location_id_2, bidirectional=True):
            """
            Create a connection between two locations.

            Args:
                location_id_1 (str): First location ID
                location_id_2 (str): Second location ID
                bidirectional (bool): If True, connection works both ways

            Returns:
                bool: True if connected, False if either location not found
            """
            loc1 = self.get_location(location_id_1)
            loc2 = self.get_location(location_id_2)

            if not loc1 or not loc2:
                return False

            loc1.add_connection(location_id_2)
            if bidirectional:
                loc2.add_connection(location_id_1)

            return True

        def disconnect_locations(self, location_id_1, location_id_2, bidirectional=True):
            """
            Remove a connection between two locations.

            Args:
                location_id_1 (str): First location ID
                location_id_2 (str): Second location ID
                bidirectional (bool): If True, removes connection both ways

            Returns:
                bool: True if disconnected, False if either location not found
            """
            loc1 = self.get_location(location_id_1)
            loc2 = self.get_location(location_id_2)

            if not loc1 or not loc2:
                return False

            loc1.remove_connection(location_id_2)
            if bidirectional:
                loc2.remove_connection(location_id_1)

            return True

# =============================================================================
# GLOBAL WORLD MAP MANAGER INSTANCE
# =============================================================================

default world_map_manager = WorldMapManager()

# =============================================================================
# EXAMPLE LOCATION SETUP
# =============================================================================

init python:
    def setup_example_world_map():
        """Initialize example world map locations and events."""

        # Create example locations
        starting_village = MapLocation(
            id="starting_village",
            name="Willowbrook Village",
            description="A peaceful village nestled in a quiet valley. Your journey begins here.",
            position=(20, 70),
            unlocked=True,
            icon="images/map/village.png",
            region="valley"
        )

        forest = MapLocation(
            id="mystic_forest",
            name="Mystic Forest",
            description="An ancient forest filled with mysterious creatures and hidden secrets.",
            position=(40, 50),
            unlocked=True,
            icon="images/map/forest.png",
            region="wildlands"
        )

        mountain = MapLocation(
            id="crystal_peak",
            name="Crystal Peak",
            description="A towering mountain said to contain rare crystals of immense power.",
            position=(70, 30),
            unlocked=False,
            icon="images/map/mountain.png",
            region="highlands"
        )

        castle = MapLocation(
            id="valdoria_castle",
            name="Valdoria Castle",
            description="The grand castle of House Valdoria, seat of noble power.",
            position=(80, 60),
            unlocked=False,
            icon="images/map/castle.png",
            region="highlands"
        )

        port = MapLocation(
            id="harbor_city",
            name="Harbor City",
            description="A bustling port city where merchants from all lands trade their wares.",
            position=(50, 80),
            unlocked=True,
            icon="images/map/port.png",
            region="coast"
        )

        ruins = MapLocation(
            id="ancient_ruins",
            name="Ancient Ruins",
            description="Mysterious ruins of a civilization long forgotten.",
            position=(30, 20),
            unlocked=False,
            icon="images/map/ruins.png",
            region="wildlands"
        )

        # Register locations
        world_map_manager.register_location(starting_village)
        world_map_manager.register_location(forest)
        world_map_manager.register_location(mountain)
        world_map_manager.register_location(castle)
        world_map_manager.register_location(port)
        world_map_manager.register_location(ruins)

        # Set up connections (bidirectional)
        world_map_manager.connect_locations("starting_village", "mystic_forest")
        world_map_manager.connect_locations("starting_village", "harbor_city")
        world_map_manager.connect_locations("mystic_forest", "crystal_peak")
        world_map_manager.connect_locations("mystic_forest", "ancient_ruins")
        world_map_manager.connect_locations("crystal_peak", "valdoria_castle")
        world_map_manager.connect_locations("valdoria_castle", "harbor_city")
        world_map_manager.connect_locations("harbor_city", "ancient_ruins")

        # Set starting location
        world_map_manager.set_current_location("starting_village")

        # Create example travel events
        bandit_ambush = TravelEvent(
            id="bandit_ambush",
            description="Bandits appear from the shadows and demand your gold!",
            chance=0.15,
            effect_label="travel_event_bandit",
            min_distance=10,
            regions=["wildlands", "highlands"]
        )

        merchant_encounter = TravelEvent(
            id="merchant_encounter",
            description="A friendly merchant crosses your path with wares to sell.",
            chance=0.2,
            effect_label="travel_event_merchant",
            min_distance=5
        )

        treasure_discovery = TravelEvent(
            id="treasure_discovery",
            description="You stumble upon a hidden cache of treasure!",
            chance=0.05,
            effect_label="travel_event_treasure",
            min_distance=15,
            one_time=True
        )

        mysterious_stranger = TravelEvent(
            id="mysterious_stranger",
            description="A cloaked figure approaches with cryptic words.",
            chance=0.1,
            effect_label="travel_event_stranger",
            min_distance=20,
            regions=["wildlands"]
        )

        # Register travel events
        world_map_manager.register_travel_event(bandit_ambush)
        world_map_manager.register_travel_event(merchant_encounter)
        world_map_manager.register_travel_event(treasure_discovery)
        world_map_manager.register_travel_event(mysterious_stranger)

# Initialize world map when game starts
label setup_world_map:
    $ setup_example_world_map()
    return

# =============================================================================
# WORLD MAP SCREEN UI
# =============================================================================

screen world_map_screen():
    tag menu
    modal True

    # Background
    add "#1a1a2e" # Dark background

    # Title
    text "World Map" align (0.5, 0.05) size 48 color "#ffffff"

    # Map area
    frame:
        area (50, 80, 1180, 560)
        background "#2a2a4e"

        # Draw connection lines between locations
        for loc in world_map_manager.get_all_locations():
            for connected_id in loc.connected_locations:
                $ other = world_map_manager.get_location(connected_id)
                if other:
                    $ x1 = int(loc.position[0] * 11.8)
                    $ y1 = int(loc.position[1] * 5.6)
                    $ x2 = int(other.position[0] * 11.8)
                    $ y2 = int(other.position[1] * 5.6)
                    # Line represented as a thin frame
                    # Note: Ren'Py doesn't have native line drawing, this is a visual approximation

        # Draw location nodes
        for loc in world_map_manager.get_all_locations():
            $ x_pos = int(loc.position[0] * 11.8)
            $ y_pos = int(loc.position[1] * 5.6)
            $ is_current = (loc.id == world_map_manager.current_location_id)
            $ can_reach = loc.id in (world_map_manager.get_current_location().connected_locations if world_map_manager.get_current_location() else [])

            button:
                pos (x_pos - 25, y_pos - 25)
                xysize (50, 50)
                action ShowTransient("location_info_popup", location=loc)
                sensitive loc.unlocked

                if is_current:
                    background "#00ff00"  # Green for current
                elif loc.unlocked and can_reach:
                    background "#4488ff"  # Blue for reachable
                elif loc.unlocked:
                    background "#888888"  # Gray for unlocked but not reachable
                else:
                    background "#333333"  # Dark for locked

                text loc.name[0:2] align (0.5, 0.5) size 16 color "#ffffff"

            # Location label
            text loc.name:
                pos (x_pos - 50, y_pos + 30)
                size 12
                color "#ffffff" if loc.unlocked else "#666666"
                xalign 0.5

    # Current location info panel
    frame:
        area (50, 660, 400, 100)
        background "#333355"
        padding (15, 10)

        vbox:
            spacing 5
            text "Current Location:" size 16 color "#aaaaaa"
            if world_map_manager.get_current_location():
                $ current = world_map_manager.get_current_location()
                text current.name size 24 color "#ffffff"
                text current.description size 12 color "#888888"
            else:
                text "Unknown" size 24 color "#ff6666"

    # Legend
    frame:
        area (480, 660, 350, 100)
        background "#333355"
        padding (15, 10)

        vbox:
            spacing 5
            text "Legend:" size 16 color "#aaaaaa"
            hbox:
                spacing 20
                hbox:
                    frame:
                        xysize (20, 20)
                        background "#00ff00"
                    text " Current" size 14 color "#ffffff"
                hbox:
                    frame:
                        xysize (20, 20)
                        background "#4488ff"
                    text " Reachable" size 14 color "#ffffff"
                hbox:
                    frame:
                        xysize (20, 20)
                        background "#333333"
                    text " Locked" size 14 color "#666666"

    # Close button
    textbutton "Close Map":
        align (0.95, 0.95)
        action Return()
        text_size 20
        text_color "#ffffff"

# =============================================================================
# LOCATION INFO POPUP SCREEN
# =============================================================================

screen location_info_popup(location):
    modal True

    frame:
        align (0.5, 0.5)
        xysize (500, 400)
        background "#2a2a4e"
        padding (30, 25)

        vbox:
            spacing 15

            # Location name
            text location.name size 32 color "#ffffff" xalign 0.5

            # Region tag
            if location.region:
                text "Region: [location.region.title()]" size 16 color "#888888" xalign 0.5

            null height 10

            # Description
            text location.description size 18 color "#cccccc"

            null height 10

            # Status info
            hbox:
                spacing 20
                xalign 0.5
                if location.visited:
                    text "Visited" size 14 color "#66cc66"
                else:
                    text "Not Visited" size 14 color "#cc6666"

                if location.unlocked:
                    text "Unlocked" size 14 color "#66cc66"
                else:
                    text "Locked" size 14 color "#cc6666"

            null height 20

            # Travel button (if not current location)
            if location.id != world_map_manager.current_location_id:
                $ can_travel, reason = world_map_manager.can_travel_to(location.id)
                $ travel_info = world_map_manager.get_travel_info(
                    world_map_manager.current_location_id, location.id)

                if travel_info:
                    hbox:
                        spacing 30
                        xalign 0.5
                        text "Time: [travel_info['time']:.1f] hrs" size 14 color "#aaaaaa"
                        text "Cost: [travel_info['cost']:.0f] gold" size 14 color "#ffcc66"

                if can_travel:
                    textbutton "Travel Here":
                        xalign 0.5
                        action [Hide("location_info_popup"),
                               Show("travel_confirmation_screen",
                                    destination=location)]
                        text_size 20
                        text_color "#66ff66"
                else:
                    text reason size 16 color "#ff6666" xalign 0.5
            else:
                text "You are here" size 18 color "#66ff66" xalign 0.5

            # Close button
            textbutton "Close":
                xalign 0.5
                action Hide("location_info_popup")
                text_size 18
                text_color "#aaaaaa"

# =============================================================================
# TRAVEL CONFIRMATION SCREEN
# =============================================================================

screen travel_confirmation_screen(destination):
    modal True

    $ travel_info = world_map_manager.get_travel_info(
        world_map_manager.current_location_id, destination.id)

    frame:
        align (0.5, 0.5)
        xysize (450, 320)
        background "#2a2a4e"
        padding (30, 25)

        vbox:
            spacing 15

            text "Confirm Travel" size 28 color "#ffffff" xalign 0.5

            null height 10

            # Journey details
            if travel_info:
                text "From: [travel_info['from'].name]" size 18 color "#aaaaaa"
                text "To: [travel_info['to'].name]" size 18 color "#ffffff"

                null height 10

                hbox:
                    spacing 40
                    xalign 0.5
                    vbox:
                        text "Travel Time" size 14 color "#888888" xalign 0.5
                        text "[travel_info['time']:.1f] hours" size 20 color "#66ccff" xalign 0.5
                    vbox:
                        text "Travel Cost" size 14 color "#888888" xalign 0.5
                        text "[travel_info['cost']:.0f] gold" size 20 color "#ffcc66" xalign 0.5

            null height 20

            # Warning about possible events
            text "Random events may occur during travel!" size 14 color "#ff9966" xalign 0.5

            null height 20

            # Buttons
            hbox:
                spacing 30
                xalign 0.5

                textbutton "Travel":
                    action [Hide("travel_confirmation_screen"),
                           Function(execute_travel, destination.id)]
                    text_size 20
                    text_color "#66ff66"

                textbutton "Cancel":
                    action Hide("travel_confirmation_screen")
                    text_size 20
                    text_color "#ff6666"

# =============================================================================
# TRAVEL EVENT DISPLAY SCREEN
# =============================================================================

screen travel_event_screen(event, travel_result):
    modal True

    frame:
        align (0.5, 0.5)
        xysize (550, 350)
        background "#3a2a2a"
        padding (30, 25)

        vbox:
            spacing 15

            text "Travel Event!" size 32 color "#ffcc00" xalign 0.5

            null height 10

            # Event description
            text event.description size 20 color "#ffffff"

            null height 20

            # Travel summary
            text "Journey Complete" size 16 color "#888888" xalign 0.5
            text "Arrived at: [travel_result['to_location'].name]" size 18 color "#66ff66" xalign 0.5

            null height 20

            # Continue button
            textbutton "Continue":
                xalign 0.5
                action [Hide("travel_event_screen"),
                       Call(event.effect_label) if event.effect_label else NullAction()]
                text_size 22
                text_color "#ffffff"

# =============================================================================
# TRAVEL COMPLETE SCREEN (no event)
# =============================================================================

screen travel_complete_screen(travel_result):
    modal True

    frame:
        align (0.5, 0.5)
        xysize (450, 280)
        background "#2a3a2a"
        padding (30, 25)

        vbox:
            spacing 15

            text "Journey Complete" size 28 color "#66ff66" xalign 0.5

            null height 10

            text "You have arrived at:" size 16 color "#aaaaaa" xalign 0.5
            text travel_result['to_location'].name size 24 color "#ffffff" xalign 0.5

            null height 10

            hbox:
                spacing 40
                xalign 0.5
                text "Time: [travel_result['time']:.1f] hrs" size 16 color "#66ccff"
                text "Cost: [travel_result['cost']:.0f] gold" size 16 color "#ffcc66"

            null height 20

            textbutton "Continue":
                xalign 0.5
                action Hide("travel_complete_screen")
                text_size 22
                text_color "#ffffff"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

init python:
    def execute_travel(destination_id):
        """Execute travel and show appropriate result screen."""
        result = world_map_manager.travel_to(destination_id)

        if result["success"]:
            if result["event"]:
                renpy.show_screen("travel_event_screen",
                                 event=result["event"],
                                 travel_result=result)
            else:
                renpy.show_screen("travel_complete_screen",
                                 travel_result=result)
        else:
            renpy.notify("Travel failed: " + result["reason"])

# =============================================================================
# TRAVEL EVENT LABELS
# =============================================================================

label travel_event_bandit:
    "Bandits block your path!"
    "They demand 50 gold for safe passage."
    menu:
        "Pay the bandits":
            "You reluctantly hand over the gold."
            # $ player_gold -= 50
        "Fight them":
            "You draw your weapon and prepare to fight!"
            # Combat system would go here
        "Try to flee":
            "You make a run for it!"
            # Skill check would go here
    return

label travel_event_merchant:
    "A traveling merchant waves you down."
    "\"Greetings, traveler! Care to see my wares?\""
    menu:
        "Browse goods":
            "You look through the merchant's inventory."
            # Shop screen would go here
        "Decline politely":
            "\"Safe travels!\" the merchant says as you continue on."
    return

label travel_event_treasure:
    "You notice something glinting in the underbrush."
    "Investigation reveals a small chest hidden beneath some rocks!"
    "You found 100 gold and a mysterious amulet!"
    # $ player_gold += 100
    # $ inventory.add("mysterious_amulet")
    return

label travel_event_stranger:
    "A cloaked figure emerges from the shadows."
    "\"The path you walk leads to great danger... and great reward.\""
    "\"Seek the ancient ruins when the moon is full.\""
    "Before you can respond, the figure vanishes into the mist."
    return

# =============================================================================
# HELPER LABELS FOR COMMON ACTIONS
# =============================================================================

# Open the world map screen
label open_world_map:
    call screen world_map_screen
    return

# Unlock a location with notification
label unlock_location(location_id, notify=True):
    $ success = world_map_manager.unlock_location(location_id)
    if success and notify:
        $ loc = world_map_manager.get_location(location_id)
        if loc:
            $ renpy.notify("New location discovered: [loc.name]")
    return

# Travel directly to a location
label travel_to_location(location_id):
    $ result = world_map_manager.travel_to(location_id)
    if result["success"]:
        if result["event"]:
            call screen travel_event_screen(event=result["event"], travel_result=result)
            if result["event"].effect_label:
                call expression result["event"].effect_label
        else:
            call screen travel_complete_screen(travel_result=result)
    else:
        "Travel failed: [result['reason']]"
    return

# =============================================================================
# STYLES FOR WORLD MAP SCREENS
# =============================================================================

style world_map_button:
    background "#444466"
    hover_background "#5555aa"
    padding (10, 5)

style world_map_button_text:
    color "#ffffff"
    size 16

style world_map_frame:
    background "#2a2a4e"
    padding (20, 15)

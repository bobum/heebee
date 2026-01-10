"""
Tests for the exploration system (exploration.rpy).

Covers:
- Location creation and properties
- Hotspot positioning and interaction
- Travel between connected locations
- Discovered vs undiscovered locations
- One-time interaction tracking
- Item requirements for hotspots
"""
import pytest


class MockInventory:
    """Mock inventory for testing item requirements."""

    def __init__(self, items=None):
        self._items = set(items) if items else set()

    def has_item(self, item_id):
        return item_id in self._items

    def add_item(self, item_id):
        self._items.add(item_id)

    def remove_item(self, item_id):
        self._items.discard(item_id)


class TestHotspot:
    """Tests for the Hotspot class."""

    def test_hotspot_creation_basic(self, load_system):
        """Test basic hotspot creation with required parameters."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot("test_spot", "Test Spot", 100, 200, 50, 75)

        assert hotspot.id == "test_spot"
        assert hotspot.name == "Test Spot"
        assert hotspot.x == 100
        assert hotspot.y == 200
        assert hotspot.width == 50
        assert hotspot.height == 75

    def test_hotspot_creation_with_kwargs(self, load_system):
        """Test hotspot creation with optional keyword arguments."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot(
            "detailed_spot",
            "Detailed Spot",
            10,
            20,
            30,
            40,
            description="A detailed description",
            interaction_label="interact_label",
            required_item="magic_key",
            gives_item="treasure",
            one_time=True,
            visible=False,
            enabled=False,
            hover_text="Custom hover",
            destination="next_room",
        )

        assert hotspot.description == "A detailed description"
        assert hotspot.interaction_label == "interact_label"
        assert hotspot.required_item == "magic_key"
        assert hotspot.gives_item == "treasure"
        assert hotspot.one_time is True
        assert hotspot.visible is False
        assert hotspot.enabled is False
        assert hotspot.hover_text == "Custom hover"
        assert hotspot.destination == "next_room"

    def test_hotspot_default_values(self, load_system):
        """Test that hotspot has sensible defaults."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot("spot", "Spot", 0, 0, 10, 10)

        assert hotspot.description == ""
        assert hotspot.interaction_label is None
        assert hotspot.required_item is None
        assert hotspot.gives_item is None
        assert hotspot.one_time is False
        assert hotspot.interacted is False
        assert hotspot.visible is True
        assert hotspot.enabled is True
        assert hotspot.hover_text == "Spot"  # Defaults to name
        assert hotspot.destination is None

    def test_get_rect(self, load_system):
        """Test get_rect returns correct imagemap rectangle."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot("rect_test", "Rect Test", 100, 150, 50, 75)
        rect = hotspot.get_rect()

        assert rect == (100, 150, 150, 225)  # (x, y, x+width, y+height)

    def test_can_interact_basic(self, load_system):
        """Test basic interaction check for visible, enabled hotspot."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot("interactive", "Interactive", 0, 0, 10, 10)

        assert hotspot.can_interact() is True

    def test_can_interact_not_visible(self, load_system):
        """Test that invisible hotspots cannot be interacted with."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot("hidden", "Hidden", 0, 0, 10, 10, visible=False)

        assert hotspot.can_interact() is False

    def test_can_interact_not_enabled(self, load_system):
        """Test that disabled hotspots cannot be interacted with."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot("disabled", "Disabled", 0, 0, 10, 10, enabled=False)

        assert hotspot.can_interact() is False

    def test_can_interact_one_time_already_used(self, load_system):
        """Test that one-time hotspots cannot be used twice."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot("one_time", "One Time", 0, 0, 10, 10, one_time=True)

        assert hotspot.can_interact() is True

        # First interaction
        hotspot.interact()

        # Should not be interactable after one-time use
        assert hotspot.can_interact() is False

    def test_can_interact_requires_item_without_inventory(self, load_system):
        """Test item requirement when no inventory provided."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot(
            "locked", "Locked", 0, 0, 10, 10, required_item="key"
        )

        # Without inventory, should be able to interact (can't check)
        assert hotspot.can_interact() is True

    def test_can_interact_requires_item_missing(self, load_system):
        """Test interaction blocked when required item is missing."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot(
            "locked", "Locked", 0, 0, 10, 10, required_item="key"
        )
        inventory = MockInventory()

        assert hotspot.can_interact(inventory) is False

    def test_can_interact_requires_item_present(self, load_system):
        """Test interaction allowed when required item is present."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot(
            "locked", "Locked", 0, 0, 10, 10, required_item="key"
        )
        inventory = MockInventory(["key"])

        assert hotspot.can_interact(inventory) is True

    def test_interact_returns_label(self, load_system):
        """Test that interact returns the interaction label."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot(
            "labeled", "Labeled", 0, 0, 10, 10,
            interaction_label="do_something"
        )

        result = hotspot.interact()

        assert result == "do_something"
        assert hotspot.interacted is True

    def test_interact_marks_as_interacted(self, load_system):
        """Test that interacting marks the hotspot as interacted."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot("track", "Track", 0, 0, 10, 10)

        assert hotspot.interacted is False
        hotspot.interact()
        assert hotspot.interacted is True

    def test_interact_gives_item(self, load_system):
        """Test that interaction adds item to inventory."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot(
            "giver", "Giver", 0, 0, 10, 10, gives_item="gold_coin"
        )
        inventory = MockInventory()

        hotspot.interact(inventory)

        assert inventory.has_item("gold_coin")

    def test_interact_blocked_returns_none(self, load_system):
        """Test that blocked interactions return None."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        hotspot = Hotspot(
            "blocked", "Blocked", 0, 0, 10, 10,
            visible=False,
            interaction_label="should_not_run"
        )

        result = hotspot.interact()

        assert result is None


class TestLocation:
    """Tests for the Location class."""

    def test_location_creation_basic(self, load_system):
        """Test basic location creation."""
        ns = load_system("exploration")
        Location = ns["Location"]

        location = Location("forest", "Dark Forest", "images/forest.png")

        assert location.id == "forest"
        assert location.name == "Dark Forest"
        assert location.background == "images/forest.png"
        assert location.hotspots == {}
        assert location.connected_locations == []

    def test_location_creation_with_kwargs(self, load_system):
        """Test location creation with optional arguments."""
        ns = load_system("exploration")
        Location = ns["Location"]

        location = Location(
            "castle",
            "Royal Castle",
            "images/castle.png",
            description="A grand castle",
            ambient_sound="castle_ambience.ogg",
            music="castle_theme.ogg",
            discovered=True,
            accessible=False,
            entry_label="enter_castle",
            exit_label="exit_castle",
            idle_animation="castle_idle",
        )

        assert location.description == "A grand castle"
        assert location.ambient_sound == "castle_ambience.ogg"
        assert location.music == "castle_theme.ogg"
        assert location.discovered is True
        assert location.accessible is False
        assert location.entry_label == "enter_castle"
        assert location.exit_label == "exit_castle"
        assert location.idle_animation == "castle_idle"

    def test_location_default_values(self, load_system):
        """Test location default values."""
        ns = load_system("exploration")
        Location = ns["Location"]

        location = Location("test", "Test", "test.png")

        assert location.description == ""
        assert location.ambient_sound is None
        assert location.music is None
        assert location.discovered is False
        assert location.accessible is True
        assert location.visited_count == 0
        assert location.entry_label is None
        assert location.exit_label is None
        assert location.idle_animation is None

    def test_add_hotspot(self, load_system):
        """Test adding a hotspot to a location."""
        ns = load_system("exploration")
        Location = ns["Location"]
        Hotspot = ns["Hotspot"]

        location = Location("room", "Room", "room.png")
        hotspot = Hotspot("door", "Door", 100, 200, 50, 100)

        location.add_hotspot(hotspot)

        assert "door" in location.hotspots
        assert location.hotspots["door"] is hotspot

    def test_remove_hotspot(self, load_system):
        """Test removing a hotspot from a location."""
        ns = load_system("exploration")
        Location = ns["Location"]
        Hotspot = ns["Hotspot"]

        location = Location("room", "Room", "room.png")
        hotspot = Hotspot("door", "Door", 100, 200, 50, 100)

        location.add_hotspot(hotspot)
        assert "door" in location.hotspots

        location.remove_hotspot("door")
        assert "door" not in location.hotspots

    def test_remove_nonexistent_hotspot(self, load_system):
        """Test that removing nonexistent hotspot doesn't raise error."""
        ns = load_system("exploration")
        Location = ns["Location"]

        location = Location("room", "Room", "room.png")

        # Should not raise an error
        location.remove_hotspot("nonexistent")

    def test_get_hotspot(self, load_system):
        """Test getting a specific hotspot."""
        ns = load_system("exploration")
        Location = ns["Location"]
        Hotspot = ns["Hotspot"]

        location = Location("room", "Room", "room.png")
        hotspot = Hotspot("window", "Window", 300, 100, 80, 120)
        location.add_hotspot(hotspot)

        result = location.get_hotspot("window")

        assert result is hotspot

    def test_get_nonexistent_hotspot(self, load_system):
        """Test getting a nonexistent hotspot returns None."""
        ns = load_system("exploration")
        Location = ns["Location"]

        location = Location("room", "Room", "room.png")

        result = location.get_hotspot("nonexistent")

        assert result is None

    def test_get_visible_hotspots(self, load_system):
        """Test filtering to visible hotspots only."""
        ns = load_system("exploration")
        Location = ns["Location"]
        Hotspot = ns["Hotspot"]

        location = Location("room", "Room", "room.png")
        visible1 = Hotspot("vis1", "Visible 1", 0, 0, 10, 10, visible=True)
        visible2 = Hotspot("vis2", "Visible 2", 20, 0, 10, 10, visible=True)
        hidden = Hotspot("hid", "Hidden", 40, 0, 10, 10, visible=False)

        location.add_hotspot(visible1)
        location.add_hotspot(visible2)
        location.add_hotspot(hidden)

        visible = location.get_visible_hotspots()

        assert len(visible) == 2
        assert visible1 in visible
        assert visible2 in visible
        assert hidden not in visible

    def test_connect_to(self, load_system):
        """Test connecting locations."""
        ns = load_system("exploration")
        Location = ns["Location"]

        location = Location("hub", "Hub", "hub.png")

        location.connect_to("north_room")
        location.connect_to("south_room")

        assert "north_room" in location.connected_locations
        assert "south_room" in location.connected_locations

    def test_connect_to_no_duplicates(self, load_system):
        """Test that duplicate connections are prevented."""
        ns = load_system("exploration")
        Location = ns["Location"]

        location = Location("hub", "Hub", "hub.png")

        location.connect_to("north_room")
        location.connect_to("north_room")  # Duplicate

        assert location.connected_locations.count("north_room") == 1

    def test_visit_increments_count(self, load_system):
        """Test that visiting increments visit count."""
        ns = load_system("exploration")
        Location = ns["Location"]

        location = Location("room", "Room", "room.png")

        assert location.visited_count == 0

        location.visit()
        assert location.visited_count == 1

        location.visit()
        assert location.visited_count == 2

    def test_visit_marks_discovered(self, load_system):
        """Test that visiting marks location as discovered."""
        ns = load_system("exploration")
        Location = ns["Location"]

        location = Location("hidden", "Hidden", "hidden.png", discovered=False)

        assert location.discovered is False

        location.visit()

        assert location.discovered is True


class TestExplorationManager:
    """Tests for the ExplorationManager class."""

    def test_manager_creation(self, load_system):
        """Test exploration manager initial state."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]

        manager = ExplorationManager()

        assert manager.locations == {}
        assert manager.current_location is None
        assert manager.previous_location is None
        assert manager.discovered_items == []
        assert manager.exploration_progress == {}

    def test_add_location(self, load_system):
        """Test adding a location to the manager."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()
        location = Location("room", "Room", "room.png")

        manager.add_location(location)

        assert "room" in manager.locations
        assert manager.locations["room"] is location

    def test_get_location(self, load_system):
        """Test retrieving a location by ID."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()
        location = Location("room", "Room", "room.png")
        manager.add_location(location)

        result = manager.get_location("room")

        assert result is location

    def test_get_nonexistent_location(self, load_system):
        """Test getting nonexistent location returns None."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]

        manager = ExplorationManager()

        result = manager.get_location("nowhere")

        assert result is None

    def test_travel_to_valid_location(self, load_system):
        """Test traveling to a valid accessible location."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()
        location = Location("forest", "Forest", "forest.png")
        manager.add_location(location)

        result = manager.travel_to("forest")

        assert result is True
        assert manager.current_location == "forest"
        assert location.visited_count == 1
        assert location.discovered is True

    def test_travel_to_nonexistent_location(self, load_system):
        """Test traveling to nonexistent location fails."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]

        manager = ExplorationManager()

        result = manager.travel_to("nowhere")

        assert result is False
        assert manager.current_location is None

    def test_travel_to_inaccessible_location(self, load_system):
        """Test traveling to inaccessible location fails."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()
        location = Location("locked", "Locked", "locked.png", accessible=False)
        manager.add_location(location)

        result = manager.travel_to("locked")

        assert result is False
        assert manager.current_location is None

    def test_travel_updates_previous_location(self, load_system):
        """Test that traveling updates previous location."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()
        loc1 = Location("first", "First", "first.png")
        loc2 = Location("second", "Second", "second.png")
        manager.add_location(loc1)
        manager.add_location(loc2)

        manager.travel_to("first")
        manager.travel_to("second")

        assert manager.previous_location == "first"
        assert manager.current_location == "second"

    def test_get_current_location(self, load_system):
        """Test getting current location object."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()
        location = Location("here", "Here", "here.png")
        manager.add_location(location)
        manager.travel_to("here")

        result = manager.get_current_location()

        assert result is location

    def test_get_current_location_when_none(self, load_system):
        """Test getting current location when none set."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]

        manager = ExplorationManager()

        result = manager.get_current_location()

        assert result is None

    def test_get_connected_locations(self, load_system):
        """Test getting connected accessible locations."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()

        hub = Location("hub", "Hub", "hub.png")
        north = Location("north", "North", "north.png")
        south = Location("south", "South", "south.png")
        locked = Location("locked", "Locked", "locked.png", accessible=False)

        hub.connect_to("north")
        hub.connect_to("south")
        hub.connect_to("locked")

        manager.add_location(hub)
        manager.add_location(north)
        manager.add_location(south)
        manager.add_location(locked)
        manager.travel_to("hub")

        connected = manager.get_connected_locations()

        assert len(connected) == 2
        assert north in connected
        assert south in connected
        assert locked not in connected

    def test_get_connected_locations_when_none_current(self, load_system):
        """Test getting connected locations when no current location."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]

        manager = ExplorationManager()

        connected = manager.get_connected_locations()

        assert connected == []

    def test_get_discovered_locations(self, load_system):
        """Test getting all discovered locations."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()

        discovered = Location("disc", "Discovered", "disc.png", discovered=True)
        undiscovered = Location("undisc", "Undiscovered", "undisc.png", discovered=False)
        also_discovered = Location("also", "Also Discovered", "also.png", discovered=True)

        manager.add_location(discovered)
        manager.add_location(undiscovered)
        manager.add_location(also_discovered)

        result = manager.get_discovered_locations()

        assert len(result) == 2
        assert discovered in result
        assert also_discovered in result
        assert undiscovered not in result

    def test_unlock_location(self, load_system):
        """Test unlocking a location."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()
        location = Location(
            "secret", "Secret", "secret.png",
            accessible=False,
            discovered=False
        )
        manager.add_location(location)

        manager.unlock_location("secret")

        assert location.accessible is True
        assert location.discovered is True

    def test_unlock_nonexistent_location(self, load_system):
        """Test unlocking nonexistent location doesn't error."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]

        manager = ExplorationManager()

        # Should not raise an error
        manager.unlock_location("nonexistent")

    def test_lock_location(self, load_system):
        """Test locking a location."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]

        manager = ExplorationManager()
        location = Location("open", "Open", "open.png", accessible=True)
        manager.add_location(location)

        manager.lock_location("open")

        assert location.accessible is False

    def test_lock_nonexistent_location(self, load_system):
        """Test locking nonexistent location doesn't error."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]

        manager = ExplorationManager()

        # Should not raise an error
        manager.lock_location("nonexistent")


class TestExplorationIntegration:
    """Integration tests for exploration system scenarios."""

    def test_complete_exploration_workflow(self, load_system):
        """Test a complete exploration workflow."""
        ns = load_system("exploration")
        ExplorationManager = ns["ExplorationManager"]
        Location = ns["Location"]
        Hotspot = ns["Hotspot"]

        manager = ExplorationManager()

        # Create locations
        town = Location("town", "Town Square", "town.png", discovered=True)
        shop = Location("shop", "General Store", "shop.png")
        dungeon = Location("dungeon", "Dark Dungeon", "dungeon.png", accessible=False)

        # Add hotspots
        town.add_hotspot(Hotspot(
            "exit_shop", "Shop Door", 100, 200, 50, 100,
            destination="shop",
            hover_text="Enter the shop"
        ))
        town.add_hotspot(Hotspot(
            "exit_dungeon", "Dungeon Entrance", 300, 200, 50, 100,
            destination="dungeon",
            hover_text="Enter the dungeon"
        ))

        shop.add_hotspot(Hotspot(
            "chest", "Treasure Chest", 200, 300, 60, 60,
            gives_item="dungeon_key",
            one_time=True
        ))
        shop.add_hotspot(Hotspot(
            "exit_town", "Exit", 400, 400, 80, 50,
            destination="town"
        ))

        # Connect locations
        town.connect_to("shop")
        town.connect_to("dungeon")
        shop.connect_to("town")

        # Add to manager
        manager.add_location(town)
        manager.add_location(shop)
        manager.add_location(dungeon)

        # Start in town
        assert manager.travel_to("town")
        assert manager.current_location == "town"

        # Travel to shop
        assert manager.travel_to("shop")
        assert manager.current_location == "shop"
        assert shop.discovered is True

        # Try to enter dungeon (should fail - locked)
        assert manager.travel_to("dungeon") is False

        # Unlock dungeon and try again
        manager.unlock_location("dungeon")
        assert manager.travel_to("dungeon")
        assert manager.current_location == "dungeon"

        # Check discovered locations
        discovered = manager.get_discovered_locations()
        assert len(discovered) == 3

    def test_one_time_item_collection(self, load_system):
        """Test collecting a one-time item from a hotspot."""
        ns = load_system("exploration")
        Location = ns["Location"]
        Hotspot = ns["Hotspot"]

        location = Location("room", "Room", "room.png")
        hotspot = Hotspot(
            "coin", "Gold Coin", 150, 150, 20, 20,
            gives_item="gold_coin",
            one_time=True,
            interaction_label="pick_up_coin"
        )
        location.add_hotspot(hotspot)

        inventory = MockInventory()

        # First interaction - should work
        assert hotspot.can_interact(inventory)
        result = hotspot.interact(inventory)

        assert result == "pick_up_coin"
        assert inventory.has_item("gold_coin")
        assert hotspot.interacted is True

        # Second interaction - should fail
        assert hotspot.can_interact(inventory) is False
        result = hotspot.interact(inventory)
        assert result is None

    def test_locked_door_with_key(self, load_system):
        """Test a door that requires a key item."""
        ns = load_system("exploration")
        Hotspot = ns["Hotspot"]

        door = Hotspot(
            "locked_door", "Locked Door", 200, 100, 60, 120,
            required_item="brass_key",
            destination="treasure_room",
            hover_text="A locked door"
        )

        inventory_without_key = MockInventory()
        inventory_with_key = MockInventory(["brass_key"])

        # Without key
        assert door.can_interact(inventory_without_key) is False

        # With key
        assert door.can_interact(inventory_with_key) is True

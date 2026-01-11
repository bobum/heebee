"""
Tests for the World Map Travel System.

This module contains comprehensive tests for:
- MapLocation class
- TravelEvent class
- WorldMapManager class
"""
import pytest
import math
import sys
from pathlib import Path

# Add the tests directory to path for conftest imports
tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))

from conftest import load_rpy_classes, GAME_DIR


@pytest.fixture
def world_map_classes():
    """Load the world map classes from world_map.rpy."""
    rpy_path = GAME_DIR / "world_map.rpy"
    if not rpy_path.exists():
        pytest.skip("world_map.rpy not found")
    return load_rpy_classes(rpy_path)


@pytest.fixture
def MapLocation(world_map_classes):
    """Get the MapLocation class."""
    return world_map_classes["MapLocation"]


@pytest.fixture
def TravelEvent(world_map_classes):
    """Get the TravelEvent class."""
    return world_map_classes["TravelEvent"]


@pytest.fixture
def WorldMapManager(world_map_classes):
    """Get the WorldMapManager class."""
    return world_map_classes["WorldMapManager"]


# =============================================================================
# MapLocation Tests
# =============================================================================

class TestMapLocation:
    """Tests for the MapLocation class."""

    def test_init_defaults(self, MapLocation):
        """Test MapLocation initialization with default values."""
        loc = MapLocation(id="test", name="Test Location")

        assert loc.id == "test"
        assert loc.name == "Test Location"
        assert loc.description == ""
        assert loc.position == (0, 0)
        assert loc.unlocked is False
        assert loc.connected_locations == []
        assert loc.icon is None
        assert loc.visited is False
        assert loc.region is None

    def test_init_custom_values(self, MapLocation):
        """Test MapLocation initialization with custom values."""
        loc = MapLocation(
            id="village",
            name="Mystic Village",
            description="A small village",
            position=(50, 30),
            unlocked=True,
            connected_locations=["forest", "mountain"],
            icon="village.png",
            region="plains"
        )

        assert loc.id == "village"
        assert loc.name == "Mystic Village"
        assert loc.description == "A small village"
        assert loc.position == (50, 30)
        assert loc.unlocked is True
        assert loc.connected_locations == ["forest", "mountain"]
        assert loc.icon == "village.png"
        assert loc.region == "plains"

    def test_unlock(self, MapLocation):
        """Test unlocking a location."""
        loc = MapLocation(id="test", name="Test", unlocked=False)
        assert loc.unlocked is False

        loc.unlock()
        assert loc.unlocked is True

    def test_lock(self, MapLocation):
        """Test locking a location."""
        loc = MapLocation(id="test", name="Test", unlocked=True)
        assert loc.unlocked is True

        loc.lock()
        assert loc.unlocked is False

    def test_mark_visited(self, MapLocation):
        """Test marking a location as visited."""
        loc = MapLocation(id="test", name="Test")
        assert loc.visited is False

        loc.mark_visited()
        assert loc.visited is True

    def test_add_connection(self, MapLocation):
        """Test adding a connection to another location."""
        loc = MapLocation(id="test", name="Test")
        assert "other" not in loc.connected_locations

        loc.add_connection("other")
        assert "other" in loc.connected_locations

        # Adding same connection again should not duplicate
        loc.add_connection("other")
        assert loc.connected_locations.count("other") == 1

    def test_remove_connection(self, MapLocation):
        """Test removing a connection."""
        loc = MapLocation(id="test", name="Test", connected_locations=["a", "b", "c"])

        loc.remove_connection("b")
        assert "b" not in loc.connected_locations
        assert "a" in loc.connected_locations
        assert "c" in loc.connected_locations

        # Removing non-existent connection should not raise
        loc.remove_connection("nonexistent")

    def test_is_connected_to(self, MapLocation):
        """Test checking connection status."""
        loc = MapLocation(id="test", name="Test", connected_locations=["forest", "mountain"])

        assert loc.is_connected_to("forest") is True
        assert loc.is_connected_to("mountain") is True
        assert loc.is_connected_to("castle") is False

    def test_get_distance_to(self, MapLocation):
        """Test distance calculation between locations."""
        loc1 = MapLocation(id="loc1", name="Location 1", position=(0, 0))
        loc2 = MapLocation(id="loc2", name="Location 2", position=(3, 4))

        distance = loc1.get_distance_to(loc2)
        assert distance == 5.0  # 3-4-5 right triangle

        # Test with different positions
        loc3 = MapLocation(id="loc3", name="Location 3", position=(10, 10))
        loc4 = MapLocation(id="loc4", name="Location 4", position=(20, 10))

        distance2 = loc3.get_distance_to(loc4)
        assert distance2 == 10.0

    def test_get_distance_to_same_location(self, MapLocation):
        """Test distance to same position is zero."""
        loc1 = MapLocation(id="loc1", name="Location 1", position=(50, 50))
        loc2 = MapLocation(id="loc2", name="Location 2", position=(50, 50))

        assert loc1.get_distance_to(loc2) == 0.0


# =============================================================================
# TravelEvent Tests
# =============================================================================

class TestTravelEvent:
    """Tests for the TravelEvent class."""

    def test_init_defaults(self, TravelEvent):
        """Test TravelEvent initialization with defaults."""
        event = TravelEvent(id="test_event")

        assert event.id == "test_event"
        assert event.description == ""
        assert event.chance == 0.1
        assert event.effect_label is None
        assert event.min_distance == 0
        assert event.regions is None
        assert event.one_time is False
        assert event.triggered is False

    def test_init_custom_values(self, TravelEvent):
        """Test TravelEvent initialization with custom values."""
        event = TravelEvent(
            id="bandit",
            description="Bandits attack!",
            chance=0.25,
            effect_label="bandit_encounter",
            min_distance=10,
            regions=["forest", "mountains"],
            one_time=True
        )

        assert event.id == "bandit"
        assert event.description == "Bandits attack!"
        assert event.chance == 0.25
        assert event.effect_label == "bandit_encounter"
        assert event.min_distance == 10
        assert event.regions == ["forest", "mountains"]
        assert event.one_time is True
        assert event.triggered is False

    def test_chance_clamping(self, TravelEvent):
        """Test that chance is clamped between 0 and 1."""
        event_high = TravelEvent(id="high", chance=1.5)
        assert event_high.chance == 1.0

        event_low = TravelEvent(id="low", chance=-0.5)
        assert event_low.chance == 0.0

    def test_can_trigger_basic(self, TravelEvent):
        """Test basic can_trigger logic."""
        event = TravelEvent(id="test", min_distance=5)

        assert event.can_trigger(distance=10) is True
        assert event.can_trigger(distance=3) is False

    def test_can_trigger_one_time(self, TravelEvent):
        """Test that one-time events cannot trigger after being triggered."""
        event = TravelEvent(id="test", one_time=True)

        assert event.can_trigger(distance=10) is True
        event.mark_triggered()
        assert event.can_trigger(distance=10) is False

    def test_can_trigger_regions(self, TravelEvent):
        """Test region-based triggering."""
        event = TravelEvent(id="test", regions=["forest", "swamp"])

        assert event.can_trigger(distance=10, region="forest") is True
        assert event.can_trigger(distance=10, region="swamp") is True
        assert event.can_trigger(distance=10, region="desert") is False
        assert event.can_trigger(distance=10, region=None) is True  # No region specified

    def test_should_trigger_respects_conditions(self, TravelEvent):
        """Test that should_trigger respects can_trigger conditions."""
        event = TravelEvent(id="test", chance=1.0, min_distance=20)

        # Even with 100% chance, should not trigger if distance is too low
        # Run multiple times to be sure (since it involves randomness)
        for _ in range(10):
            result = event.should_trigger(distance=5)
            assert result is False

    def test_mark_triggered(self, TravelEvent):
        """Test marking an event as triggered."""
        event = TravelEvent(id="test", one_time=True)
        assert event.triggered is False

        event.mark_triggered()
        assert event.triggered is True

    def test_reset(self, TravelEvent):
        """Test resetting triggered state."""
        event = TravelEvent(id="test", one_time=True)
        event.mark_triggered()
        assert event.triggered is True

        event.reset()
        assert event.triggered is False


# =============================================================================
# WorldMapManager Tests
# =============================================================================

class TestWorldMapManager:
    """Tests for the WorldMapManager class."""

    def test_init(self, WorldMapManager):
        """Test WorldMapManager initialization."""
        manager = WorldMapManager()

        assert manager.locations == {}
        assert manager.travel_events == []
        assert manager.current_location_id is None
        assert manager.travel_speed == 10.0
        assert manager.travel_cost_per_unit == 1.0

    def test_init_custom_values(self, WorldMapManager):
        """Test WorldMapManager with custom travel parameters."""
        manager = WorldMapManager(travel_speed=20.0, travel_cost_per_unit=2.5)

        assert manager.travel_speed == 20.0
        assert manager.travel_cost_per_unit == 2.5

    # -------------------------------------------------------------------------
    # Location Management Tests
    # -------------------------------------------------------------------------

    def test_register_location(self, WorldMapManager, MapLocation):
        """Test registering a location."""
        manager = WorldMapManager()
        loc = MapLocation(id="village", name="Village")

        result = manager.register_location(loc)

        assert result == loc
        assert "village" in manager.locations
        assert manager.get_location("village") == loc

    def test_get_location_not_found(self, WorldMapManager):
        """Test getting a non-existent location."""
        manager = WorldMapManager()
        assert manager.get_location("nonexistent") is None

    def test_remove_location(self, WorldMapManager, MapLocation):
        """Test removing a location."""
        manager = WorldMapManager()
        loc = MapLocation(id="village", name="Village")
        manager.register_location(loc)

        result = manager.remove_location("village")

        assert result is True
        assert "village" not in manager.locations
        assert manager.get_location("village") is None

    def test_remove_location_updates_connections(self, WorldMapManager, MapLocation):
        """Test that removing a location cleans up connections."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", connected_locations=["a"])
        manager.register_location(loc1)
        manager.register_location(loc2)

        manager.remove_location("b")

        assert "b" not in loc1.connected_locations

    def test_remove_location_not_found(self, WorldMapManager):
        """Test removing a non-existent location."""
        manager = WorldMapManager()
        assert manager.remove_location("nonexistent") is False

    def test_get_all_locations(self, WorldMapManager, MapLocation):
        """Test getting all locations."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A")
        loc2 = MapLocation(id="b", name="B")
        manager.register_location(loc1)
        manager.register_location(loc2)

        locations = manager.get_all_locations()

        assert len(locations) == 2
        assert loc1 in locations
        assert loc2 in locations

    def test_get_unlocked_locations(self, WorldMapManager, MapLocation):
        """Test getting only unlocked locations."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", unlocked=True)
        loc2 = MapLocation(id="b", name="B", unlocked=False)
        loc3 = MapLocation(id="c", name="C", unlocked=True)
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.register_location(loc3)

        unlocked = manager.get_unlocked_locations()

        assert len(unlocked) == 2
        assert loc1 in unlocked
        assert loc2 not in unlocked
        assert loc3 in unlocked

    def test_get_visited_locations(self, WorldMapManager, MapLocation):
        """Test getting only visited locations."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A")
        loc2 = MapLocation(id="b", name="B")
        loc1.mark_visited()
        manager.register_location(loc1)
        manager.register_location(loc2)

        visited = manager.get_visited_locations()

        assert len(visited) == 1
        assert loc1 in visited

    def test_get_locations_by_region(self, WorldMapManager, MapLocation):
        """Test filtering locations by region."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", region="forest")
        loc2 = MapLocation(id="b", name="B", region="mountain")
        loc3 = MapLocation(id="c", name="C", region="forest")
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.register_location(loc3)

        forest_locs = manager.get_locations_by_region("forest")

        assert len(forest_locs) == 2
        assert loc1 in forest_locs
        assert loc3 in forest_locs
        assert loc2 not in forest_locs

    # -------------------------------------------------------------------------
    # Location Discovery/Unlocking Tests
    # -------------------------------------------------------------------------

    def test_unlock_location(self, WorldMapManager, MapLocation):
        """Test unlocking a location."""
        manager = WorldMapManager()
        loc = MapLocation(id="castle", name="Castle", unlocked=False)
        manager.register_location(loc)

        result = manager.unlock_location("castle")

        assert result is True
        assert loc.unlocked is True

    def test_unlock_location_not_found(self, WorldMapManager):
        """Test unlocking non-existent location."""
        manager = WorldMapManager()
        assert manager.unlock_location("nonexistent") is False

    def test_lock_location(self, WorldMapManager, MapLocation):
        """Test locking a location."""
        manager = WorldMapManager()
        loc = MapLocation(id="castle", name="Castle", unlocked=True)
        manager.register_location(loc)

        result = manager.lock_location("castle")

        assert result is True
        assert loc.unlocked is False

    def test_discover_location(self, WorldMapManager, MapLocation):
        """Test discovering a location (alias for unlock)."""
        manager = WorldMapManager()
        loc = MapLocation(id="ruins", name="Ruins", unlocked=False)
        manager.register_location(loc)

        result = manager.discover_location("ruins")

        assert result is True
        assert loc.unlocked is True

    # -------------------------------------------------------------------------
    # Current Location Tests
    # -------------------------------------------------------------------------

    def test_set_current_location(self, WorldMapManager, MapLocation):
        """Test setting current location."""
        manager = WorldMapManager()
        loc = MapLocation(id="village", name="Village")
        manager.register_location(loc)

        result = manager.set_current_location("village")

        assert result is True
        assert manager.current_location_id == "village"
        assert loc.visited is True

    def test_set_current_location_not_found(self, WorldMapManager):
        """Test setting current location to non-existent location."""
        manager = WorldMapManager()
        result = manager.set_current_location("nonexistent")
        assert result is False
        assert manager.current_location_id is None

    def test_get_current_location(self, WorldMapManager, MapLocation):
        """Test getting current location."""
        manager = WorldMapManager()
        loc = MapLocation(id="village", name="Village")
        manager.register_location(loc)
        manager.set_current_location("village")

        current = manager.get_current_location()

        assert current == loc

    def test_get_current_location_none(self, WorldMapManager):
        """Test getting current location when none set."""
        manager = WorldMapManager()
        assert manager.get_current_location() is None

    def test_get_connected_locations(self, WorldMapManager, MapLocation):
        """Test getting connected locations from current."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", connected_locations=["b", "c"])
        loc2 = MapLocation(id="b", name="B")
        loc3 = MapLocation(id="c", name="C")
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.register_location(loc3)
        manager.set_current_location("a")

        connected = manager.get_connected_locations()

        assert len(connected) == 2
        assert loc2 in connected
        assert loc3 in connected

    def test_get_available_destinations(self, WorldMapManager, MapLocation):
        """Test getting available (unlocked and connected) destinations."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", unlocked=True, connected_locations=["b", "c"])
        loc2 = MapLocation(id="b", name="B", unlocked=True)
        loc3 = MapLocation(id="c", name="C", unlocked=False)
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.register_location(loc3)
        manager.set_current_location("a")

        available = manager.get_available_destinations()

        assert len(available) == 1
        assert loc2 in available
        assert loc3 not in available

    # -------------------------------------------------------------------------
    # Travel Time and Cost Tests
    # -------------------------------------------------------------------------

    def test_calculate_travel_time(self, WorldMapManager, MapLocation):
        """Test travel time calculation."""
        manager = WorldMapManager(travel_speed=10.0)
        loc1 = MapLocation(id="a", name="A", position=(0, 0))
        loc2 = MapLocation(id="b", name="B", position=(30, 40))  # distance = 50
        manager.register_location(loc1)
        manager.register_location(loc2)

        time = manager.calculate_travel_time("a", "b")

        assert time == 5.0  # 50 / 10 = 5

    def test_calculate_travel_time_invalid(self, WorldMapManager, MapLocation):
        """Test travel time with invalid locations."""
        manager = WorldMapManager()
        loc = MapLocation(id="a", name="A")
        manager.register_location(loc)

        assert manager.calculate_travel_time("a", "nonexistent") == -1
        assert manager.calculate_travel_time("nonexistent", "a") == -1

    def test_calculate_travel_cost(self, WorldMapManager, MapLocation):
        """Test travel cost calculation."""
        manager = WorldMapManager(travel_cost_per_unit=2.0)
        loc1 = MapLocation(id="a", name="A", position=(0, 0))
        loc2 = MapLocation(id="b", name="B", position=(3, 4))  # distance = 5
        manager.register_location(loc1)
        manager.register_location(loc2)

        cost = manager.calculate_travel_cost("a", "b")

        assert cost == 10.0  # 5 * 2 = 10

    def test_get_travel_info(self, WorldMapManager, MapLocation):
        """Test getting complete travel information."""
        manager = WorldMapManager(travel_speed=10.0, travel_cost_per_unit=1.0)
        loc1 = MapLocation(id="a", name="A", position=(0, 0), connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", position=(30, 40), unlocked=True)
        manager.register_location(loc1)
        manager.register_location(loc2)

        info = manager.get_travel_info("a", "b")

        assert info["from"] == loc1
        assert info["to"] == loc2
        assert info["distance"] == 50.0
        assert info["time"] == 5.0
        assert info["cost"] == 50.0
        assert info["can_travel"] is True

    def test_get_travel_info_cannot_travel(self, WorldMapManager, MapLocation):
        """Test travel info when travel is not possible."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", position=(0, 0))  # Not connected
        loc2 = MapLocation(id="b", name="B", position=(10, 0), unlocked=True)
        manager.register_location(loc1)
        manager.register_location(loc2)

        info = manager.get_travel_info("a", "b")

        assert info["can_travel"] is False

    def test_get_travel_info_invalid(self, WorldMapManager):
        """Test travel info with invalid locations."""
        manager = WorldMapManager()
        assert manager.get_travel_info("a", "b") is None

    # -------------------------------------------------------------------------
    # Travel Event Tests
    # -------------------------------------------------------------------------

    def test_register_travel_event(self, WorldMapManager, TravelEvent):
        """Test registering a travel event."""
        manager = WorldMapManager()
        event = TravelEvent(id="bandit", description="Bandits!")

        result = manager.register_travel_event(event)

        assert result == event
        assert event in manager.travel_events

    def test_get_travel_event(self, WorldMapManager, TravelEvent):
        """Test getting a travel event by ID."""
        manager = WorldMapManager()
        event = TravelEvent(id="bandit", description="Bandits!")
        manager.register_travel_event(event)

        found = manager.get_travel_event("bandit")

        assert found == event

    def test_get_travel_event_not_found(self, WorldMapManager):
        """Test getting non-existent travel event."""
        manager = WorldMapManager()
        assert manager.get_travel_event("nonexistent") is None

    def test_remove_travel_event(self, WorldMapManager, TravelEvent):
        """Test removing a travel event."""
        manager = WorldMapManager()
        event = TravelEvent(id="bandit")
        manager.register_travel_event(event)

        result = manager.remove_travel_event("bandit")

        assert result is True
        assert event not in manager.travel_events

    def test_check_for_travel_event_guaranteed(self, WorldMapManager, TravelEvent):
        """Test checking for travel event with 100% chance."""
        manager = WorldMapManager()
        event = TravelEvent(id="always", chance=1.0, min_distance=0)
        manager.register_travel_event(event)

        # Should always trigger with 100% chance
        triggered = manager.check_for_travel_event(distance=10)

        assert triggered == event

    def test_check_for_travel_event_never(self, WorldMapManager, TravelEvent):
        """Test checking for travel event with 0% chance."""
        manager = WorldMapManager()
        event = TravelEvent(id="never", chance=0.0)
        manager.register_travel_event(event)

        # Run multiple times to be sure
        for _ in range(10):
            triggered = manager.check_for_travel_event(distance=10)
            assert triggered is None

    def test_check_for_travel_event_min_distance(self, WorldMapManager, TravelEvent):
        """Test that min_distance is respected."""
        manager = WorldMapManager()
        event = TravelEvent(id="far", chance=1.0, min_distance=20)
        manager.register_travel_event(event)

        # Should not trigger with short distance
        assert manager.check_for_travel_event(distance=5) is None

        # Should trigger with sufficient distance
        assert manager.check_for_travel_event(distance=25) == event

    def test_check_for_travel_event_one_time(self, WorldMapManager, TravelEvent):
        """Test that one-time events only trigger once."""
        manager = WorldMapManager()
        event = TravelEvent(id="once", chance=1.0, one_time=True)
        manager.register_travel_event(event)

        # First trigger should work
        first = manager.check_for_travel_event(distance=10)
        assert first == event
        assert event.triggered is True

        # Second trigger should fail
        second = manager.check_for_travel_event(distance=10)
        assert second is None

    def test_reset_travel_events(self, WorldMapManager, TravelEvent):
        """Test resetting one-time events."""
        manager = WorldMapManager()
        event = TravelEvent(id="once", chance=1.0, one_time=True)
        manager.register_travel_event(event)
        event.mark_triggered()

        manager.reset_travel_events()

        assert event.triggered is False

    # -------------------------------------------------------------------------
    # Travel Execution Tests
    # -------------------------------------------------------------------------

    def test_can_travel_to_success(self, WorldMapManager, MapLocation):
        """Test can_travel_to when travel is possible."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", unlocked=True, connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", unlocked=True)
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.set_current_location("a")

        can_travel, reason = manager.can_travel_to("b")

        assert can_travel is True
        assert reason == "Travel allowed"

    def test_can_travel_to_no_current(self, WorldMapManager, MapLocation):
        """Test can_travel_to with no current location."""
        manager = WorldMapManager()
        loc = MapLocation(id="b", name="B", unlocked=True)
        manager.register_location(loc)

        can_travel, reason = manager.can_travel_to("b")

        assert can_travel is False
        assert "No current location" in reason

    def test_can_travel_to_destination_not_found(self, WorldMapManager, MapLocation):
        """Test can_travel_to with non-existent destination."""
        manager = WorldMapManager()
        loc = MapLocation(id="a", name="A", unlocked=True)
        manager.register_location(loc)
        manager.set_current_location("a")

        can_travel, reason = manager.can_travel_to("nonexistent")

        assert can_travel is False
        assert "not found" in reason

    def test_can_travel_to_locked(self, WorldMapManager, MapLocation):
        """Test can_travel_to with locked destination."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", unlocked=True, connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", unlocked=False)
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.set_current_location("a")

        can_travel, reason = manager.can_travel_to("b")

        assert can_travel is False
        assert "locked" in reason.lower()

    def test_can_travel_to_not_connected(self, WorldMapManager, MapLocation):
        """Test can_travel_to with unconnected destination."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", unlocked=True)  # No connections
        loc2 = MapLocation(id="b", name="B", unlocked=True)
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.set_current_location("a")

        can_travel, reason = manager.can_travel_to("b")

        assert can_travel is False
        assert "not connected" in reason.lower()

    def test_travel_to_success(self, WorldMapManager, MapLocation):
        """Test successful travel."""
        manager = WorldMapManager(travel_speed=10.0, travel_cost_per_unit=1.0)
        loc1 = MapLocation(id="a", name="A", position=(0, 0), unlocked=True, connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", position=(30, 40), unlocked=True)
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.set_current_location("a")

        result = manager.travel_to("b")

        assert result["success"] is True
        assert result["time"] == 5.0
        assert result["cost"] == 50.0
        assert manager.current_location_id == "b"
        assert loc2.visited is True

    def test_travel_to_failure(self, WorldMapManager, MapLocation):
        """Test failed travel."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", unlocked=True)
        loc2 = MapLocation(id="b", name="B", unlocked=False)
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.set_current_location("a")

        result = manager.travel_to("b")

        assert result["success"] is False
        assert manager.current_location_id == "a"

    def test_travel_to_triggers_event(self, WorldMapManager, MapLocation, TravelEvent):
        """Test that travel can trigger events."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", position=(0, 0), unlocked=True, connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", position=(100, 0), unlocked=True)  # Far away
        event = TravelEvent(id="test", chance=1.0, min_distance=50)
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.register_travel_event(event)
        manager.set_current_location("a")

        result = manager.travel_to("b")

        assert result["success"] is True
        assert result["event"] == event

    def test_travel_history(self, WorldMapManager, MapLocation):
        """Test that travel history is recorded."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", position=(0, 0), unlocked=True, connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", position=(10, 0), unlocked=True)
        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.set_current_location("a")

        manager.travel_to("b")

        history = manager.get_travel_history()
        assert len(history) == 1
        assert history[0]["from"] == "a"
        assert history[0]["to"] == "b"

    # -------------------------------------------------------------------------
    # Connection Management Tests
    # -------------------------------------------------------------------------

    def test_connect_locations_bidirectional(self, WorldMapManager, MapLocation):
        """Test bidirectional connection."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A")
        loc2 = MapLocation(id="b", name="B")
        manager.register_location(loc1)
        manager.register_location(loc2)

        result = manager.connect_locations("a", "b", bidirectional=True)

        assert result is True
        assert loc1.is_connected_to("b")
        assert loc2.is_connected_to("a")

    def test_connect_locations_one_way(self, WorldMapManager, MapLocation):
        """Test one-way connection."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A")
        loc2 = MapLocation(id="b", name="B")
        manager.register_location(loc1)
        manager.register_location(loc2)

        result = manager.connect_locations("a", "b", bidirectional=False)

        assert result is True
        assert loc1.is_connected_to("b")
        assert not loc2.is_connected_to("a")

    def test_connect_locations_invalid(self, WorldMapManager, MapLocation):
        """Test connecting with invalid location."""
        manager = WorldMapManager()
        loc = MapLocation(id="a", name="A")
        manager.register_location(loc)

        result = manager.connect_locations("a", "nonexistent")

        assert result is False

    def test_disconnect_locations_bidirectional(self, WorldMapManager, MapLocation):
        """Test bidirectional disconnection."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", connected_locations=["a"])
        manager.register_location(loc1)
        manager.register_location(loc2)

        result = manager.disconnect_locations("a", "b", bidirectional=True)

        assert result is True
        assert not loc1.is_connected_to("b")
        assert not loc2.is_connected_to("a")

    def test_disconnect_locations_one_way(self, WorldMapManager, MapLocation):
        """Test one-way disconnection."""
        manager = WorldMapManager()
        loc1 = MapLocation(id="a", name="A", connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", connected_locations=["a"])
        manager.register_location(loc1)
        manager.register_location(loc2)

        result = manager.disconnect_locations("a", "b", bidirectional=False)

        assert result is True
        assert not loc1.is_connected_to("b")
        assert loc2.is_connected_to("a")  # Still connected this way


# =============================================================================
# Integration Tests
# =============================================================================

class TestWorldMapIntegration:
    """Integration tests for the complete world map system."""

    def test_full_travel_workflow(self, WorldMapManager, MapLocation, TravelEvent):
        """Test a complete travel workflow."""
        # Setup
        manager = WorldMapManager(travel_speed=10.0, travel_cost_per_unit=0.5)

        village = MapLocation(id="village", name="Village", position=(0, 0), unlocked=True)
        forest = MapLocation(id="forest", name="Forest", position=(30, 40), unlocked=True)
        castle = MapLocation(id="castle", name="Castle", position=(60, 80), unlocked=False)

        manager.register_location(village)
        manager.register_location(forest)
        manager.register_location(castle)

        manager.connect_locations("village", "forest")
        manager.connect_locations("forest", "castle")

        manager.set_current_location("village")

        # Travel to forest
        result1 = manager.travel_to("forest")
        assert result1["success"] is True
        assert manager.current_location_id == "forest"

        # Cannot travel to locked castle
        result2 = manager.travel_to("castle")
        assert result2["success"] is False

        # Unlock and travel to castle
        manager.unlock_location("castle")
        result3 = manager.travel_to("castle")
        assert result3["success"] is True
        assert manager.current_location_id == "castle"

        # Check history
        history = manager.get_travel_history()
        assert len(history) == 2

    def test_event_region_filtering(self, WorldMapManager, MapLocation, TravelEvent):
        """Test that events respect region filtering."""
        manager = WorldMapManager()

        loc1 = MapLocation(id="a", name="A", position=(0, 0), unlocked=True, region="forest", connected_locations=["b"])
        loc2 = MapLocation(id="b", name="B", position=(100, 0), unlocked=True, region="desert")

        # Event only triggers in forest
        forest_event = TravelEvent(id="forest_event", chance=1.0, regions=["forest"])

        manager.register_location(loc1)
        manager.register_location(loc2)
        manager.register_travel_event(forest_event)
        manager.set_current_location("a")

        # Traveling to desert should not trigger forest event
        result = manager.travel_to("b")

        # The event should not trigger because destination is desert
        assert result["event"] is None

"""
Comprehensive tests for the Character Route System.

Tests cover:
- Route class functionality
- RouteManager registration and retrieval
- Route availability checking with relationship requirements
- Route lock-in mechanics
- Route compatibility checks
- Route content flags
- Route indicator/tracking
"""
import pytest
import sys
from pathlib import Path

# Add tests directory to path for conftest imports
sys.path.insert(0, str(Path(__file__).parent))
from conftest import load_rpy_classes


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def route_classes(load_system):
    """Load Route and RouteManager classes from routes.rpy."""
    return load_system("routes")


@pytest.fixture
def relationship_classes(load_system):
    """Load Character and RelationshipManager classes from relationships.rpy."""
    return load_system("relationships")


@pytest.fixture
def Route(route_classes):
    """Get the Route class."""
    return route_classes["Route"]


@pytest.fixture
def RouteManager(route_classes):
    """Get the RouteManager class."""
    return route_classes["RouteManager"]


@pytest.fixture
def Character():
    """Provide a mock Character class for route testing."""
    class MockCharacter:
        def __init__(self, name="", id="", affection=50, trust=50, respect=50, romance_available=False):
            self.name = name
            self.id = id
            self.affection = affection
            self.trust = trust
            self.respect = respect
            self.romance_available = romance_available
    return MockCharacter


@pytest.fixture
def RelationshipManager():
    """Provide a mock RelationshipManager for route testing."""
    class MockRelationshipManager:
        def __init__(self):
            self.characters = {}

        def add_character(self, character):
            self.characters[character.id] = character

        def get_character(self, char_id):
            return self.characters.get(char_id)
    return MockRelationshipManager


@pytest.fixture
def sample_route(Route):
    """Create a sample route for testing."""
    return Route(
        id="elena",
        character_name="Elena Brightwood",
        description="Adventure awaits!",
        requirements={"affection": 50, "trust": 30, "respect": 20},
        incompatible_routes=["victoria"],
        priority=1
    )


@pytest.fixture
def sample_routes(Route):
    """Create multiple sample routes for testing."""
    elena = Route(
        id="elena",
        character_name="Elena Brightwood",
        description="Adventure route",
        requirements={"affection": 50, "trust": 30, "respect": 20},
        incompatible_routes=["victoria"],
        priority=1
    )
    marcus = Route(
        id="marcus",
        character_name="Marcus Sterling",
        description="Merchant route",
        requirements={"affection": 40, "trust": 40, "respect": 30},
        incompatible_routes=[],
        priority=2
    )
    victoria = Route(
        id="victoria",
        character_name="Lady Victoria",
        description="Noble route",
        requirements={"affection": 60, "trust": 20, "respect": 50},
        incompatible_routes=["elena"],
        priority=3
    )
    return {"elena": elena, "marcus": marcus, "victoria": victoria}


@pytest.fixture
def manager_with_routes(RouteManager, sample_routes):
    """Create a RouteManager with sample routes registered."""
    manager = RouteManager()
    for route in sample_routes.values():
        manager.register_route(route)
    return manager


@pytest.fixture
def relationship_manager_with_chars(RelationshipManager, Character):
    """Create a RelationshipManager with test characters."""
    rm = RelationshipManager()

    elena = Character(
        name="Elena Brightwood",
        id="elena",
        affection=60,
        trust=40,
        respect=30,
        romance_available=True
    )

    marcus = Character(
        name="Marcus Sterling",
        id="marcus",
        affection=50,
        trust=50,
        respect=40,
        romance_available=True
    )

    victoria = Character(
        name="Lady Victoria",
        id="victoria",
        affection=70,
        trust=30,
        respect=60,
        romance_available=True
    )

    rm.add_character(elena)
    rm.add_character(marcus)
    rm.add_character(victoria)

    return rm


# =============================================================================
# ROUTE CLASS TESTS
# =============================================================================

class TestRouteClass:
    """Tests for the Route class."""

    def test_route_creation(self, Route):
        """Test basic route creation with required parameters."""
        route = Route(id="test", character_name="Test Character")

        assert route.id == "test"
        assert route.character_name == "Test Character"
        assert route.description == ""
        assert route.locked_in is False
        assert route.requirements == {"affection": 0, "trust": 0, "respect": 0}
        assert route.incompatible_routes == []
        assert route.content_flags == set()
        assert route.priority == 100

    def test_route_creation_with_all_params(self, Route):
        """Test route creation with all parameters."""
        route = Route(
            id="elena",
            character_name="Elena",
            description="Test description",
            requirements={"affection": 50, "trust": 30, "respect": 20},
            incompatible_routes=["marcus"],
            icon="test.png",
            priority=5
        )

        assert route.id == "elena"
        assert route.character_name == "Elena"
        assert route.description == "Test description"
        assert route.requirements == {"affection": 50, "trust": 30, "respect": 20}
        assert route.incompatible_routes == ["marcus"]
        assert route.icon == "test.png"
        assert route.priority == 5

    def test_set_requirement(self, sample_route):
        """Test setting individual requirements."""
        sample_route.set_requirement("affection", 75)
        assert sample_route.requirements["affection"] == 75

        sample_route.set_requirement("trust", 50)
        assert sample_route.requirements["trust"] == 50

        sample_route.set_requirement("respect", 40)
        assert sample_route.requirements["respect"] == 40

    def test_set_requirement_invalid_stat(self, sample_route):
        """Test that setting an invalid stat is ignored."""
        original = sample_route.requirements.copy()
        sample_route.set_requirement("invalid_stat", 100)
        assert sample_route.requirements == original

    def test_add_incompatible_route(self, sample_route):
        """Test adding incompatible routes."""
        assert "marcus" not in sample_route.incompatible_routes

        sample_route.add_incompatible_route("marcus")
        assert "marcus" in sample_route.incompatible_routes

        # Adding same route again should not duplicate
        sample_route.add_incompatible_route("marcus")
        assert sample_route.incompatible_routes.count("marcus") == 1

    def test_remove_incompatible_route(self, sample_route):
        """Test removing incompatible routes."""
        assert "victoria" in sample_route.incompatible_routes

        sample_route.remove_incompatible_route("victoria")
        assert "victoria" not in sample_route.incompatible_routes

        # Removing non-existent route should not raise
        sample_route.remove_incompatible_route("nonexistent")

    def test_content_flag_operations(self, sample_route):
        """Test content flag add/remove/has operations."""
        assert not sample_route.has_content_flag("test_flag")

        sample_route.add_content_flag("test_flag")
        assert sample_route.has_content_flag("test_flag")

        sample_route.add_content_flag("another_flag")
        assert sample_route.has_content_flag("another_flag")

        sample_route.remove_content_flag("test_flag")
        assert not sample_route.has_content_flag("test_flag")
        assert sample_route.has_content_flag("another_flag")

        # Removing non-existent flag should not raise
        sample_route.remove_content_flag("nonexistent")

    def test_lock_and_unlock(self, sample_route):
        """Test locking and unlocking routes."""
        assert not sample_route.locked_in
        assert sample_route.get_lock_point() is None

        sample_route.lock("chapter_3")
        assert sample_route.locked_in
        assert sample_route.get_lock_point() == "chapter_3"

        sample_route.unlock()
        assert not sample_route.locked_in
        assert sample_route.get_lock_point() is None

    def test_lock_without_point(self, sample_route):
        """Test locking without specifying a lock point."""
        sample_route.lock()
        assert sample_route.locked_in
        assert sample_route.get_lock_point() is None

    def test_route_repr(self, sample_route):
        """Test route string representation."""
        repr_str = repr(sample_route)
        assert "elena" in repr_str
        assert "Elena Brightwood" in repr_str
        assert "locked_in=False" in repr_str


# =============================================================================
# ROUTE MANAGER - REGISTRATION TESTS
# =============================================================================

class TestRouteManagerRegistration:
    """Tests for RouteManager registration functionality."""

    def test_register_route(self, RouteManager, Route):
        """Test basic route registration."""
        manager = RouteManager()
        route = Route(id="test", character_name="Test")

        result = manager.register_route(route)
        assert result == route
        assert manager.get_route("test") == route

    def test_register_multiple_routes(self, RouteManager, sample_routes):
        """Test registering multiple routes."""
        manager = RouteManager()

        for route in sample_routes.values():
            manager.register_route(route)

        assert len(manager.routes) == 3
        assert manager.get_route("elena") is not None
        assert manager.get_route("marcus") is not None
        assert manager.get_route("victoria") is not None

    def test_unregister_route(self, manager_with_routes):
        """Test unregistering a route."""
        assert manager_with_routes.get_route("elena") is not None

        result = manager_with_routes.unregister_route("elena")
        assert result is True
        assert manager_with_routes.get_route("elena") is None

    def test_unregister_nonexistent_route(self, manager_with_routes):
        """Test unregistering a route that doesn't exist."""
        result = manager_with_routes.unregister_route("nonexistent")
        assert result is False

    def test_get_route_nonexistent(self, manager_with_routes):
        """Test getting a route that doesn't exist."""
        result = manager_with_routes.get_route("nonexistent")
        assert result is None

    def test_get_all_routes_sorted_by_priority(self, manager_with_routes):
        """Test that get_all_routes returns routes sorted by priority."""
        routes = manager_with_routes.get_all_routes()

        assert len(routes) == 3
        assert routes[0].id == "elena"  # priority 1
        assert routes[1].id == "marcus"  # priority 2
        assert routes[2].id == "victoria"  # priority 3


# =============================================================================
# ROUTE MANAGER - REQUIREMENTS CHECKING TESTS
# =============================================================================

class TestRouteManagerRequirements:
    """Tests for RouteManager requirements checking."""

    def test_check_requirements_met(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test checking requirements when they are met."""
        # Elena requires: affection=50, trust=30, respect=20
        # Character has: affection=60, trust=40, respect=30
        result = manager_with_routes.check_requirements(
            "elena", relationship_manager_with_chars
        )
        assert result is True

    def test_check_requirements_not_met_affection(
        self, manager_with_routes, RelationshipManager, Character
    ):
        """Test checking requirements when affection is too low."""
        rm = RelationshipManager()
        rm.add_character(Character(
            name="Elena", id="elena",
            affection=30,  # Too low (needs 50)
            trust=40, respect=30
        ))

        result = manager_with_routes.check_requirements("elena", rm)
        assert result is False

    def test_check_requirements_not_met_trust(
        self, manager_with_routes, RelationshipManager, Character
    ):
        """Test checking requirements when trust is too low."""
        rm = RelationshipManager()
        rm.add_character(Character(
            name="Elena", id="elena",
            affection=60,
            trust=20,  # Too low (needs 30)
            respect=30
        ))

        result = manager_with_routes.check_requirements("elena", rm)
        assert result is False

    def test_check_requirements_not_met_respect(
        self, manager_with_routes, RelationshipManager, Character
    ):
        """Test checking requirements when respect is too low."""
        rm = RelationshipManager()
        rm.add_character(Character(
            name="Elena", id="elena",
            affection=60, trust=40,
            respect=10  # Too low (needs 20)
        ))

        result = manager_with_routes.check_requirements("elena", rm)
        assert result is False

    def test_check_requirements_exact_match(
        self, manager_with_routes, RelationshipManager, Character
    ):
        """Test that exact requirement values pass."""
        rm = RelationshipManager()
        rm.add_character(Character(
            name="Elena", id="elena",
            affection=50,  # Exactly 50
            trust=30,  # Exactly 30
            respect=20  # Exactly 20
        ))

        result = manager_with_routes.check_requirements("elena", rm)
        assert result is True

    def test_check_requirements_nonexistent_route(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test checking requirements for non-existent route."""
        result = manager_with_routes.check_requirements(
            "nonexistent", relationship_manager_with_chars
        )
        assert result is False

    def test_check_requirements_with_char_directly(self, manager_with_routes, Character):
        """Test check_requirements_with_char using character object."""
        char = Character(
            name="Elena", id="elena",
            affection=60, trust=40, respect=30
        )

        result = manager_with_routes.check_requirements_with_char("elena", char)
        assert result is True

    def test_check_requirements_with_char_not_met(self, manager_with_routes, Character):
        """Test check_requirements_with_char when requirements not met."""
        char = Character(
            name="Elena", id="elena",
            affection=10, trust=10, respect=10
        )

        result = manager_with_routes.check_requirements_with_char("elena", char)
        assert result is False


# =============================================================================
# ROUTE MANAGER - AVAILABILITY TESTS
# =============================================================================

class TestRouteManagerAvailability:
    """Tests for RouteManager availability checking."""

    def test_is_route_available_basic(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test basic route availability check."""
        result = manager_with_routes.is_route_available(
            "elena", relationship_manager_with_chars
        )
        assert result is True

    def test_is_route_available_nonexistent(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test availability of non-existent route."""
        result = manager_with_routes.is_route_available(
            "nonexistent", relationship_manager_with_chars
        )
        assert result is False

    def test_route_blocked_by_locked_incompatible(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test that a route is blocked when an incompatible route is locked."""
        # Lock into Elena's route
        manager_with_routes.lock_into_route("elena")

        # Victoria should now be blocked (Elena blocks Victoria)
        result = manager_with_routes.is_route_available(
            "victoria", relationship_manager_with_chars
        )
        assert result is False

        # Marcus should still be available (not blocked by Elena)
        result = manager_with_routes.is_route_available(
            "marcus", relationship_manager_with_chars
        )
        assert result is True

    def test_get_available_routes(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test getting all available routes."""
        available = manager_with_routes.get_available_routes(
            relationship_manager_with_chars
        )

        assert len(available) == 3
        route_ids = [r.id for r in available]
        assert "elena" in route_ids
        assert "marcus" in route_ids
        assert "victoria" in route_ids

    def test_get_available_routes_with_blocked(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test get_available_routes excludes blocked routes."""
        manager_with_routes.lock_into_route("elena")

        available = manager_with_routes.get_available_routes(
            relationship_manager_with_chars
        )

        route_ids = [r.id for r in available]
        assert "elena" in route_ids  # Locked route is still "available"
        assert "marcus" in route_ids
        assert "victoria" not in route_ids  # Blocked by Elena

    def test_get_available_routes_sorted(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test that available routes are sorted by priority."""
        available = manager_with_routes.get_available_routes(
            relationship_manager_with_chars
        )

        priorities = [r.priority for r in available]
        assert priorities == sorted(priorities)


# =============================================================================
# ROUTE MANAGER - LOCK-IN TESTS
# =============================================================================

class TestRouteManagerLockIn:
    """Tests for RouteManager lock-in functionality."""

    def test_lock_into_route(self, manager_with_routes):
        """Test basic lock-in."""
        result = manager_with_routes.lock_into_route("elena")

        assert result is True
        assert manager_with_routes.is_locked_in()
        assert manager_with_routes.get_current_route_id() == "elena"

        current = manager_with_routes.get_current_route()
        assert current is not None
        assert current.id == "elena"
        assert current.locked_in is True

    def test_lock_into_route_with_lock_point(self, manager_with_routes):
        """Test lock-in with lock point tracking."""
        manager_with_routes.lock_into_route("elena", lock_point="chapter_3_decision")

        route = manager_with_routes.get_route("elena")
        assert route.get_lock_point() == "chapter_3_decision"

    def test_lock_into_nonexistent_route(self, manager_with_routes):
        """Test locking into a route that doesn't exist."""
        result = manager_with_routes.lock_into_route("nonexistent")

        assert result is False
        assert not manager_with_routes.is_locked_in()
        assert manager_with_routes.get_current_route() is None

    def test_lock_in_adds_content_flags(self, manager_with_routes):
        """Test that locking in adds default content flags."""
        manager_with_routes.lock_into_route("elena")

        route = manager_with_routes.get_route("elena")
        assert route.has_content_flag("route_elena_locked")
        assert route.has_content_flag("route_elena_content")

    def test_unlock_route(self, manager_with_routes):
        """Test unlocking a route."""
        manager_with_routes.lock_into_route("elena")
        assert manager_with_routes.is_locked_in()

        result = manager_with_routes.unlock_route("elena")

        assert result is True
        assert not manager_with_routes.is_locked_in()
        assert manager_with_routes.get_current_route() is None

        route = manager_with_routes.get_route("elena")
        assert not route.locked_in
        assert not route.has_content_flag("route_elena_locked")

    def test_unlock_nonexistent_route(self, manager_with_routes):
        """Test unlocking a route that doesn't exist."""
        result = manager_with_routes.unlock_route("nonexistent")
        assert result is False

    def test_get_route_history(self, manager_with_routes):
        """Test that route history is tracked."""
        manager_with_routes.lock_into_route("elena", "point1")

        history = manager_with_routes.get_route_history()
        assert len(history) == 1
        assert history[0]["route_id"] == "elena"
        assert history[0]["lock_point"] == "point1"
        assert history[0]["action"] == "locked_in"


# =============================================================================
# ROUTE MANAGER - COMPATIBILITY TESTS
# =============================================================================

class TestRouteManagerCompatibility:
    """Tests for RouteManager compatibility checking."""

    def test_check_compatibility_compatible(self, manager_with_routes):
        """Test compatibility between compatible routes."""
        # Elena and Marcus don't block each other
        result = manager_with_routes.check_compatibility("elena", "marcus")
        assert result is True

    def test_check_compatibility_incompatible(self, manager_with_routes):
        """Test compatibility between incompatible routes."""
        # Elena blocks Victoria and vice versa
        result = manager_with_routes.check_compatibility("elena", "victoria")
        assert result is False

    def test_check_compatibility_nonexistent(self, manager_with_routes):
        """Test compatibility with non-existent route."""
        result = manager_with_routes.check_compatibility("elena", "nonexistent")
        assert result is False

    def test_get_blocked_routes_by_specific(self, manager_with_routes):
        """Test getting routes blocked by a specific route."""
        blocked = manager_with_routes.get_blocked_routes("elena")

        assert "victoria" in blocked
        assert "marcus" not in blocked

    def test_get_blocked_routes_current(self, manager_with_routes):
        """Test getting all currently blocked routes."""
        manager_with_routes.lock_into_route("elena")

        blocked = manager_with_routes.get_blocked_routes()
        assert "victoria" in blocked

    def test_get_blocked_routes_none_locked(self, manager_with_routes):
        """Test getting blocked routes when none are locked."""
        blocked = manager_with_routes.get_blocked_routes()
        assert len(blocked) == 0


# =============================================================================
# ROUTE MANAGER - CONTENT FLAGS TESTS
# =============================================================================

class TestRouteManagerContentFlags:
    """Tests for RouteManager content flag functionality."""

    def test_has_route_flag_locked_route(self, manager_with_routes):
        """Test checking for flag on locked route."""
        manager_with_routes.lock_into_route("elena")

        # Default flags added on lock
        assert manager_with_routes.has_route_flag("route_elena_locked")
        assert manager_with_routes.has_route_flag("route_elena_content")

    def test_has_route_flag_unlocked_route(self, manager_with_routes):
        """Test that unlocked routes don't contribute flags."""
        route = manager_with_routes.get_route("elena")
        route.add_content_flag("test_flag")

        # Route not locked, so flag shouldn't be "active"
        assert not manager_with_routes.has_route_flag("test_flag")

    def test_get_active_content_flags(self, manager_with_routes):
        """Test getting all active content flags."""
        manager_with_routes.lock_into_route("elena")

        route = manager_with_routes.get_route("elena")
        route.add_content_flag("custom_flag")

        flags = manager_with_routes.get_active_content_flags()
        assert "route_elena_locked" in flags
        assert "route_elena_content" in flags
        assert "custom_flag" in flags

    def test_set_route_content_flag(self, manager_with_routes):
        """Test setting a content flag on a route."""
        result = manager_with_routes.set_route_content_flag("elena", "new_flag")

        assert result is True
        route = manager_with_routes.get_route("elena")
        assert route.has_content_flag("new_flag")

    def test_set_route_content_flag_nonexistent(self, manager_with_routes):
        """Test setting a flag on non-existent route."""
        result = manager_with_routes.set_route_content_flag("nonexistent", "flag")
        assert result is False


# =============================================================================
# ROUTE MANAGER - UTILITY TESTS
# =============================================================================

class TestRouteManagerUtility:
    """Tests for RouteManager utility methods."""

    def test_reset(self, manager_with_routes):
        """Test resetting all routes."""
        # Lock into a route and add flags
        manager_with_routes.lock_into_route("elena")
        route = manager_with_routes.get_route("elena")
        route.add_content_flag("custom_flag")

        # Reset
        manager_with_routes.reset()

        # Verify reset state
        assert not manager_with_routes.is_locked_in()
        assert manager_with_routes.get_current_route() is None
        assert len(manager_with_routes.get_route_history()) == 0

        for r in manager_with_routes.get_all_routes():
            assert not r.locked_in
            assert len(r.content_flags) == 0

    def test_get_route_status(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test getting detailed route status."""
        status = manager_with_routes.get_route_status(
            "elena", relationship_manager_with_chars
        )

        assert status is not None
        assert status["id"] == "elena"
        assert status["character_name"] == "Elena Brightwood"
        assert status["locked_in"] is False
        assert status["is_current"] is False
        assert status["available"] is True
        assert status["requirements_met"] is True
        assert "victoria" in status["blocks"]

    def test_get_route_status_locked(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test route status when locked in."""
        manager_with_routes.lock_into_route("elena")

        status = manager_with_routes.get_route_status(
            "elena", relationship_manager_with_chars
        )

        assert status["locked_in"] is True
        assert status["is_current"] is True

    def test_get_route_status_blocked(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test route status when blocked by another route."""
        manager_with_routes.lock_into_route("elena")

        status = manager_with_routes.get_route_status(
            "victoria", relationship_manager_with_chars
        )

        assert status["available"] is False
        assert "elena" in status["blocked_by"]

    def test_get_route_status_nonexistent(
        self, manager_with_routes, relationship_manager_with_chars
    ):
        """Test getting status for non-existent route."""
        status = manager_with_routes.get_route_status(
            "nonexistent", relationship_manager_with_chars
        )
        assert status is None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestRouteSystemIntegration:
    """Integration tests for the complete route system."""

    def test_full_route_selection_flow(
        self, RouteManager, Route, RelationshipManager, Character
    ):
        """Test a complete route selection flow."""
        # Setup
        route_mgr = RouteManager()
        rel_mgr = RelationshipManager()

        # Create routes
        route_a = Route(
            id="char_a", character_name="Character A",
            requirements={"affection": 50, "trust": 30, "respect": 20},
            incompatible_routes=["char_b"]
        )
        route_b = Route(
            id="char_b", character_name="Character B",
            requirements={"affection": 40, "trust": 40, "respect": 30},
            incompatible_routes=["char_a"]
        )

        route_mgr.register_route(route_a)
        route_mgr.register_route(route_b)

        # Create characters with low stats
        char_a = Character("A", "char_a", affection=30, trust=20, respect=10)
        char_b = Character("B", "char_b", affection=30, trust=20, respect=10)
        rel_mgr.add_character(char_a)
        rel_mgr.add_character(char_b)

        # Initially, no routes should be available
        available = route_mgr.get_available_routes(rel_mgr)
        assert len(available) == 0

        # Increase relationship with char_a to meet requirements
        char_a.affection = 50
        char_a.trust = 30
        char_a.respect = 20

        # Now route A should be available
        available = route_mgr.get_available_routes(rel_mgr)
        assert len(available) == 1
        assert available[0].id == "char_a"

        # Lock into route A
        route_mgr.lock_into_route("char_a")

        # Route B should now be blocked
        assert not route_mgr.is_route_available("char_b", rel_mgr)

        # Even if we increase char_b's stats
        char_b.affection = 50
        char_b.trust = 50
        char_b.respect = 40

        # Route B is still blocked
        assert not route_mgr.is_route_available("char_b", rel_mgr)

    def test_multiple_compatible_routes(
        self, RouteManager, Route, RelationshipManager, Character
    ):
        """Test scenario where multiple compatible routes are available."""
        route_mgr = RouteManager()
        rel_mgr = RelationshipManager()

        # Create compatible routes
        route_a = Route(
            id="char_a", character_name="Character A",
            requirements={"affection": 30, "trust": 20, "respect": 10},
            incompatible_routes=[]
        )
        route_b = Route(
            id="char_b", character_name="Character B",
            requirements={"affection": 30, "trust": 20, "respect": 10},
            incompatible_routes=[]
        )

        route_mgr.register_route(route_a)
        route_mgr.register_route(route_b)

        # Characters meeting requirements
        rel_mgr.add_character(Character("A", "char_a", affection=40, trust=30, respect=20))
        rel_mgr.add_character(Character("B", "char_b", affection=40, trust=30, respect=20))

        # Both should be available
        available = route_mgr.get_available_routes(rel_mgr)
        assert len(available) == 2

        # Lock into A
        route_mgr.lock_into_route("char_a")

        # B should still be available (compatible)
        assert route_mgr.is_route_available("char_b", rel_mgr)

    def test_content_flag_based_content(self, manager_with_routes):
        """Test using content flags for conditional content."""
        # Before locking in
        assert not manager_with_routes.has_route_flag("route_elena_content")

        # Lock into route
        manager_with_routes.lock_into_route("elena")

        # Set custom story flags
        route = manager_with_routes.get_route("elena")
        route.add_content_flag("elena_confession_seen")
        route.add_content_flag("elena_date_1_complete")

        # Check flags
        assert manager_with_routes.has_route_flag("route_elena_content")
        assert manager_with_routes.has_route_flag("elena_confession_seen")
        assert manager_with_routes.has_route_flag("elena_date_1_complete")
        assert not manager_with_routes.has_route_flag("marcus_content")


# =============================================================================
# EDGE CASES TESTS
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_requirements(self, RouteManager, Route, RelationshipManager, Character):
        """Test route with no requirements (always available)."""
        route_mgr = RouteManager()
        rel_mgr = RelationshipManager()

        route = Route(id="easy", character_name="Easy Route")
        route_mgr.register_route(route)

        # Character with 0 stats
        rel_mgr.add_character(Character("Easy", "easy", affection=0, trust=0, respect=0))

        assert route_mgr.is_route_available("easy", rel_mgr)

    def test_self_incompatibility(self, Route):
        """Test that a route can't be incompatible with itself."""
        route = Route(id="self", character_name="Self Route")
        route.add_incompatible_route("self")

        # Should work but be illogical
        assert "self" in route.incompatible_routes

    def test_mutual_incompatibility(self, RouteManager, Route):
        """Test mutual incompatibility is correctly handled."""
        route_mgr = RouteManager()

        route_a = Route(id="a", character_name="A", incompatible_routes=["b"])
        route_b = Route(id="b", character_name="B", incompatible_routes=["a"])

        route_mgr.register_route(route_a)
        route_mgr.register_route(route_b)

        # Both should be incompatible with each other
        assert not route_mgr.check_compatibility("a", "b")
        assert not route_mgr.check_compatibility("b", "a")

    def test_very_high_requirements(
        self, RouteManager, Route, RelationshipManager, Character
    ):
        """Test route with very high requirements."""
        route_mgr = RouteManager()
        rel_mgr = RelationshipManager()

        route = Route(
            id="hard",
            character_name="Hard Route",
            requirements={"affection": 150, "trust": 100, "respect": 100}
        )
        route_mgr.register_route(route)

        # Max stats character
        char = Character("Hard", "hard", affection=150, trust=100, respect=100)
        rel_mgr.add_character(char)

        assert route_mgr.is_route_available("hard", rel_mgr)

        # Slightly below max
        char.affection = 149
        assert not route_mgr.is_route_available("hard", rel_mgr)

    def test_zero_priority_routes(self, RouteManager, Route):
        """Test routes with priority 0."""
        route_mgr = RouteManager()

        route = Route(id="zero", character_name="Zero Priority", priority=0)
        route_mgr.register_route(route)

        all_routes = route_mgr.get_all_routes()
        assert all_routes[0].id == "zero"

    def test_negative_priority_routes(self, RouteManager, Route):
        """Test routes with negative priority."""
        route_mgr = RouteManager()

        route_neg = Route(id="neg", character_name="Negative Priority", priority=-10)
        route_pos = Route(id="pos", character_name="Positive Priority", priority=10)

        route_mgr.register_route(route_pos)
        route_mgr.register_route(route_neg)

        all_routes = route_mgr.get_all_routes()
        assert all_routes[0].id == "neg"
        assert all_routes[1].id == "pos"

"""
Tests for the Attributes/Stats System (game/stats.rpy)
"""
import pytest


class TestPlayer:
    """Test the Player class."""

    @pytest.fixture
    def player_class(self, load_system):
        """Load Player class from stats.rpy."""
        ns = load_system("stats")
        return ns["Player"]

    @pytest.fixture
    def player(self, player_class):
        """Create a default player instance."""
        return player_class("TestHero")

    # Initialization tests
    def test_player_initialization(self, player):
        """Test default player initialization."""
        assert player.name == "TestHero"
        assert player.level == 1
        assert player.xp == 0
        assert player.hp == 100
        assert player.max_hp == 100
        assert player.mp == 50
        assert player.max_mp == 50

    def test_player_default_stats(self, player):
        """Test default core stat values."""
        assert player.strength == 10
        assert player.defense == 10
        assert player.agility == 10
        assert player.charisma == 10
        assert player.intelligence == 10
        assert player.luck == 10

    # Stat modification tests
    def test_get_stat(self, player):
        """Test getting stat values."""
        assert player.get_stat("strength") == 10
        assert player.get_stat("STRENGTH") == 10  # Case insensitive
        assert player.get_stat("nonexistent") is None

    def test_set_stat(self, player):
        """Test setting stat values."""
        assert player.set_stat("strength", 20) is True
        assert player.strength == 20

    def test_set_stat_clamping(self, player):
        """Test stat values are clamped to bounds."""
        # HP clamped to max_hp
        player.set_stat("hp", 200)
        assert player.hp == player.max_hp

        # HP can't go below 0
        player.set_stat("hp", -50)
        assert player.hp == 0

        # Core stats clamped to MAX_STAT
        player.set_stat("strength", 99999)
        assert player.strength == 999

    def test_add_stat(self, player):
        """Test adding to stat values."""
        player.add_stat("strength", 5)
        assert player.strength == 15

    def test_subtract_stat(self, player):
        """Test subtracting from stat values."""
        player.subtract_stat("strength", 3)
        assert player.strength == 7

    # Damage and healing tests
    def test_heal(self, player):
        """Test healing restores HP."""
        player.hp = 50
        player.heal(30)
        assert player.hp == 80

    def test_heal_capped_at_max(self, player):
        """Test healing doesn't exceed max HP."""
        player.hp = 90
        player.heal(50)
        assert player.hp == player.max_hp

    def test_restore_mp(self, player):
        """Test MP restoration."""
        player.mp = 20
        player.restore_mp(15)
        assert player.mp == 35

    def test_take_damage(self, player):
        """Test damage calculation with defense."""
        initial_hp = player.hp
        # Damage formula: damage - (defense / 2)
        # With defense=10: 20 - 5 = 15 actual damage
        actual_damage = player.take_damage(20)
        assert actual_damage == 15
        assert player.hp == initial_hp - 15

    def test_take_damage_minimum(self, player):
        """Test minimum damage is 1."""
        player.defense = 100  # High defense
        actual_damage = player.take_damage(10)
        assert actual_damage >= 1

    def test_is_alive(self, player):
        """Test alive check."""
        assert player.is_alive() is True
        player.hp = 0
        assert player.is_alive() is False

    def test_full_restore(self, player):
        """Test full HP/MP restoration."""
        player.hp = 10
        player.mp = 5
        player.full_restore()
        assert player.hp == player.max_hp
        assert player.mp == player.max_mp

    # XP and leveling tests
    def test_add_xp(self, player):
        """Test adding XP."""
        player.add_xp(50)
        assert player.xp == 50

    def test_level_up_on_xp(self, player):
        """Test automatic level up when XP threshold reached."""
        levels_gained = player.add_xp(100)  # Exactly enough for level 2
        assert levels_gained == 1
        assert player.level == 2

    def test_level_up_stat_increases(self, player):
        """Test stats increase on level up."""
        initial_max_hp = player.max_hp
        initial_strength = player.strength

        player.level_up()

        assert player.max_hp == initial_max_hp + 10
        assert player.strength == initial_strength + 1
        assert player.hp == player.max_hp  # Full heal on level up

    def test_xp_progress(self, player):
        """Test XP progress calculation."""
        assert player.get_xp_progress() == 0.0
        player.xp = 50
        assert player.get_xp_progress() == 0.5

    def test_max_level_cap(self, player_class):
        """Test level cannot exceed MAX_LEVEL."""
        player = player_class("MaxLevel")
        player.level = 99
        player.xp_to_next_level = 100

        result = player.level_up()
        assert result is True
        assert player.level == 100

        # Can't go past 100
        result = player.level_up()
        assert result is False
        assert player.level == 100

    # Serialization tests
    def test_to_dict(self, player):
        """Test player serialization to dict."""
        player.strength = 15
        player.level = 5

        data = player.to_dict()

        assert data["name"] == "TestHero"
        assert data["strength"] == 15
        assert data["level"] == 5

    def test_from_dict(self, player_class):
        """Test player deserialization from dict."""
        data = {
            "name": "LoadedHero",
            "level": 10,
            "strength": 25,
            "hp": 80,
            "max_hp": 150
        }

        player = player_class.from_dict(data)

        assert player.name == "LoadedHero"
        assert player.level == 10
        assert player.strength == 25
        assert player.hp == 80
        assert player.max_hp == 150

    def test_get_all_stats(self, player):
        """Test getting all stats as dictionary."""
        stats = player.get_all_stats()

        assert "level" in stats
        assert "hp" in stats
        assert "strength" in stats
        assert stats["level"] == 1
        assert stats["hp"] == 100


class TestHelperFunctions:
    """Test global helper functions."""

    @pytest.fixture
    def stats_module(self, load_system):
        """Load the stats module."""
        return load_system("stats")

    def test_create_new_player(self, stats_module):
        """Test create_new_player helper."""
        create_new_player = stats_module["create_new_player"]
        player = create_new_player("NewHero")

        assert player.name == "NewHero"
        assert player.level == 1

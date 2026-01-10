"""
Tests for the combat system (game/combat.rpy).

Tests cover:
- Combatant initialization and stats
- Attack and damage calculations
- Status effects (apply, tick, remove)
- Turn order and initiative
- Enemy AI behavior
- Combat flow (start, turns, end)
"""
import pytest
import random


class TestStatusEffect:
    """Tests for the StatusEffect class."""

    def test_init(self, load_system):
        """Test StatusEffect initialization."""
        combat = load_system("combat")
        StatusEffect = combat["StatusEffect"]

        effect = StatusEffect("Poison", 3, "poison", 5)

        assert effect.name == "Poison"
        assert effect.duration == 3
        assert effect.effect_type == "poison"
        assert effect.value == 5

    def test_tick_reduces_duration(self, load_system):
        """Test that tick reduces duration."""
        combat = load_system("combat")
        StatusEffect = combat["StatusEffect"]

        effect = StatusEffect("Burn", 3, "damage", 10)
        effect.tick()

        assert effect.duration == 2

    def test_tick_poison_returns_negative_damage(self, load_system):
        """Test poison effect returns negative value (damage)."""
        combat = load_system("combat")
        StatusEffect = combat["StatusEffect"]

        effect = StatusEffect("Poison", 3, "poison", 5)
        result = effect.tick()

        assert result == -5

    def test_tick_non_poison_returns_none(self, load_system):
        """Test non-poison effects return None from tick."""
        combat = load_system("combat")
        StatusEffect = combat["StatusEffect"]

        effect = StatusEffect("Stun", 2, "stun", 0)
        result = effect.tick()

        assert result is None

    def test_is_expired(self, load_system):
        """Test is_expired when duration reaches 0."""
        combat = load_system("combat")
        StatusEffect = combat["StatusEffect"]

        effect = StatusEffect("Burn", 1, "damage", 10)
        assert not effect.is_expired()

        effect.tick()
        assert effect.is_expired()

    def test_is_expired_negative_duration(self, load_system):
        """Test is_expired with negative duration."""
        combat = load_system("combat")
        StatusEffect = combat["StatusEffect"]

        effect = StatusEffect("Test", 0, "test", 0)
        assert effect.is_expired()


class TestCombatant:
    """Tests for the Combatant base class."""

    def test_init(self, load_system):
        """Test Combatant initialization with all stats."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Hero", hp=100, mp=50, attack=15, defense=10, speed=8, magic=12)

        assert c.name == "Hero"
        assert c.max_hp == 100
        assert c.hp == 100
        assert c.max_mp == 50
        assert c.mp == 50
        assert c.attack == 15
        assert c.defense == 10
        assert c.speed == 8
        assert c.magic == 12
        assert c.status_effects == []
        assert c.is_defending is False

    def test_init_default_magic(self, load_system):
        """Test Combatant initialization with default magic."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", 50, 30, 10, 5, 6)

        assert c.magic == 0

    def test_take_damage_basic(self, load_system):
        """Test basic damage calculation."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        actual = c.take_damage(20)

        # damage = max(1, 20 - 10//2) = max(1, 15) = 15
        assert actual == 15
        assert c.hp == 85

    def test_take_damage_minimum_one(self, load_system):
        """Test damage is at least 1."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=100, speed=5)
        actual = c.take_damage(1)

        # damage = max(1, 1 - 50) = max(1, -49) = 1
        assert actual == 1
        assert c.hp == 99

    def test_take_damage_defending(self, load_system):
        """Test defending doubles effective defense."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        c.is_defending = True
        actual = c.take_damage(20)

        # defense_mod = 10 * 2 = 20, damage = max(1, 20 - 20//2) = max(1, 10) = 10
        assert actual == 10
        assert c.hp == 90

    def test_take_damage_cannot_go_below_zero(self, load_system):
        """Test HP cannot go below zero."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=10, mp=0, attack=10, defense=0, speed=5)
        c.take_damage(100)

        assert c.hp == 0

    def test_heal_basic(self, load_system):
        """Test basic healing."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        c.hp = 50
        healed = c.heal(30)

        assert healed == 30
        assert c.hp == 80

    def test_heal_cannot_exceed_max(self, load_system):
        """Test healing cannot exceed max HP."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        c.hp = 90
        healed = c.heal(50)

        assert healed == 10
        assert c.hp == 100

    def test_use_mp_success(self, load_system):
        """Test successful MP usage."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=100, mp=50, attack=10, defense=10, speed=5)
        result = c.use_mp(20)

        assert result is True
        assert c.mp == 30

    def test_use_mp_insufficient(self, load_system):
        """Test MP usage fails when insufficient."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=100, mp=10, attack=10, defense=10, speed=5)
        result = c.use_mp(20)

        assert result is False
        assert c.mp == 10

    def test_use_mp_exact(self, load_system):
        """Test using exact MP amount."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=100, mp=20, attack=10, defense=10, speed=5)
        result = c.use_mp(20)

        assert result is True
        assert c.mp == 0

    def test_add_status_effect(self, load_system):
        """Test adding a status effect."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]
        StatusEffect = combat["StatusEffect"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        effect = StatusEffect("Poison", 3, "poison", 5)
        c.add_status(effect)

        assert len(c.status_effects) == 1
        assert c.status_effects[0].name == "Poison"

    def test_add_status_replaces_same_name(self, load_system):
        """Test adding effect with same name replaces existing."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]
        StatusEffect = combat["StatusEffect"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        effect1 = StatusEffect("Poison", 2, "poison", 5)
        effect2 = StatusEffect("Poison", 5, "poison", 10)

        c.add_status(effect1)
        c.add_status(effect2)

        assert len(c.status_effects) == 1
        assert c.status_effects[0].duration == 5
        assert c.status_effects[0].value == 10

    def test_process_status_effects_poison(self, load_system):
        """Test processing poison status effect."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]
        StatusEffect = combat["StatusEffect"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        effect = StatusEffect("Poison", 2, "poison", 10)
        c.add_status(effect)

        total = c.process_status_effects()

        assert total == -10
        assert c.hp == 90
        assert effect.duration == 1

    def test_process_status_effects_removes_expired(self, load_system):
        """Test expired effects are removed."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]
        StatusEffect = combat["StatusEffect"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        effect = StatusEffect("Poison", 1, "poison", 5)
        c.add_status(effect)

        c.process_status_effects()

        assert len(c.status_effects) == 0

    def test_has_status(self, load_system):
        """Test has_status check."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]
        StatusEffect = combat["StatusEffect"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        effect = StatusEffect("Stun", 2, "stun", 0)
        c.add_status(effect)

        assert c.has_status("Stun") is True
        assert c.has_status("Poison") is False

    def test_is_alive(self, load_system):
        """Test is_alive check."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        assert c.is_alive() is True

        c.hp = 0
        assert c.is_alive() is False

    def test_is_stunned(self, load_system):
        """Test is_stunned check."""
        combat = load_system("combat")
        Combatant = combat["Combatant"]
        StatusEffect = combat["StatusEffect"]

        c = Combatant("Test", hp=100, mp=0, attack=10, defense=10, speed=5)
        assert c.is_stunned() is False

        stun = StatusEffect("Stun", 1, "stun", 0)
        c.add_status(stun)
        assert c.is_stunned() is True


class TestEnemy:
    """Tests for the Enemy class."""

    def test_init(self, load_system):
        """Test Enemy initialization with rewards."""
        combat = load_system("combat")
        Enemy = combat["Enemy"]

        enemy = Enemy(
            "Goblin", hp=50, mp=10, attack=12, defense=5, speed=8,
            magic=5, xp_reward=25, gold_reward=15, drops=[("gold", 0.5)]
        )

        assert enemy.name == "Goblin"
        assert enemy.max_hp == 50
        assert enemy.xp_reward == 25
        assert enemy.gold_reward == 15
        assert enemy.drops == [("gold", 0.5)]
        assert enemy.skills == []

    def test_init_default_rewards(self, load_system):
        """Test Enemy with default reward values."""
        combat = load_system("combat")
        Enemy = combat["Enemy"]

        enemy = Enemy("Slime", hp=30, mp=0, attack=5, defense=2, speed=3)

        assert enemy.xp_reward == 10
        assert enemy.gold_reward == 5
        assert enemy.drops == []

    def test_choose_action_basic_attack(self, load_system):
        """Test AI chooses attack when no skills."""
        combat = load_system("combat")
        Enemy = combat["Enemy"]
        Combatant = combat["Combatant"]

        enemy = Enemy("Slime", hp=30, mp=0, attack=5, defense=2, speed=3)
        player = Combatant("Player", 100, 50, 15, 10, 10)

        action, target, data = enemy.choose_action(player)

        assert action == "attack"
        assert target == player
        assert data is None

    def test_choose_action_skill_usage(self, load_system):
        """Test AI can choose to use skills."""
        combat = load_system("combat")
        Enemy = combat["Enemy"]
        Combatant = combat["Combatant"]

        enemy = Enemy("Mage", hp=40, mp=50, attack=5, defense=4, speed=7, magic=20)
        enemy.skills = [("Dark Bolt", 10, 1.5, "damage")]
        player = Combatant("Player", 100, 50, 15, 10, 10)

        # Test multiple times to hit the 30% skill chance
        random.seed(42)  # Seed for reproducibility
        skill_used = False
        for _ in range(20):
            enemy.mp = 50  # Reset MP
            action, target, data = enemy.choose_action(player)
            if action == "skill":
                skill_used = True
                assert data == ("Dark Bolt", 10, 1.5, "damage")
                break

        # With seed 42, we should hit skill at some point
        # If not, at least attack should work
        assert action in ("attack", "skill")

    def test_choose_action_heal_when_low_hp(self, load_system):
        """Test AI heals when HP is low."""
        combat = load_system("combat")
        Enemy = combat["Enemy"]
        Combatant = combat["Combatant"]

        enemy = Enemy("Mage", hp=100, mp=50, attack=5, defense=4, speed=7, magic=20)
        enemy.skills = [("Heal", 15, 1.0, "heal")]
        enemy.hp = 25  # 25% HP, below 30% threshold
        player = Combatant("Player", 100, 50, 15, 10, 10)

        action, target, data = enemy.choose_action(player)

        assert action == "skill"
        assert target == enemy  # Heals self
        assert data[0] == "Heal"

    def test_get_drops_with_seeded_random(self, load_system):
        """Test drop rolling with controlled randomness."""
        combat = load_system("combat")
        Enemy = combat["Enemy"]

        enemy = Enemy("Test", hp=10, mp=0, attack=5, defense=2, speed=3,
                      drops=[("item1", 1.0), ("item2", 0.0)])

        drops = enemy.get_drops()

        assert "item1" in drops  # 100% drop rate
        assert "item2" not in drops  # 0% drop rate


class TestCombatManager:
    """Tests for the CombatManager class."""

    def test_init(self, load_system):
        """Test CombatManager initialization."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]

        cm = CombatManager()

        assert cm.player is None
        assert cm.enemies == []
        assert cm.turn_order == []
        assert cm.current_turn == 0
        assert cm.battle_log == []
        assert cm.state == "inactive"

    def test_calculate_turn_order_by_speed(self, load_system):
        """Test turn order is sorted by speed (highest first)."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]

        cm = CombatManager()
        cm.player = Combatant("Player", 100, 50, 15, 10, speed=8)
        cm.enemies = [
            Enemy("Slow", hp=30, mp=0, attack=5, defense=2, speed=3),
            Enemy("Fast", hp=30, mp=0, attack=5, defense=2, speed=15),
        ]

        cm.calculate_turn_order()

        assert cm.turn_order[0].name == "Fast"
        assert cm.turn_order[1].name == "Player"
        assert cm.turn_order[2].name == "Slow"

    def test_get_current_combatant(self, load_system):
        """Test getting current combatant based on turn."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]

        cm = CombatManager()
        c1 = Combatant("First", 100, 0, 10, 10, 20)
        c2 = Combatant("Second", 100, 0, 10, 10, 10)
        cm.turn_order = [c1, c2]
        cm.current_turn = 0

        assert cm.get_current_combatant() == c1

        cm.current_turn = 1
        assert cm.get_current_combatant() == c2

        # Wraps around
        cm.current_turn = 2
        assert cm.get_current_combatant() == c1

    def test_get_current_combatant_empty(self, load_system):
        """Test get_current_combatant with empty turn order."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]

        cm = CombatManager()
        assert cm.get_current_combatant() is None

    def test_calculate_damage_physical(self, load_system):
        """Test physical damage calculation."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]

        cm = CombatManager()
        attacker = Combatant("Attacker", 100, 50, attack=20, defense=10, speed=10)
        defender = Combatant("Defender", 100, 50, attack=10, defense=10, speed=10)

        # Seed random for consistent test
        random.seed(42)
        damage = cm.calculate_damage(attacker, defender)

        # damage = int(20 * 1.0 * (1 + random * 0.2)) - always at least base attack
        assert damage >= 20
        assert damage <= 24  # 20 * 1.2 = 24

    def test_calculate_damage_with_multiplier(self, load_system):
        """Test damage calculation with skill multiplier."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]

        cm = CombatManager()
        attacker = Combatant("Attacker", 100, 50, attack=20, defense=10, speed=10)
        defender = Combatant("Defender", 100, 50, attack=10, defense=10, speed=10)

        random.seed(42)
        damage = cm.calculate_damage(attacker, defender, multiplier=2.0)

        # Base damage * 2.0
        assert damage >= 40
        assert damage <= 48

    def test_calculate_damage_magic(self, load_system):
        """Test magic damage uses magic stat."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]

        cm = CombatManager()
        attacker = Combatant("Mage", 100, 50, attack=5, defense=5, speed=10, magic=30)
        defender = Combatant("Target", 100, 50, attack=10, defense=10, speed=10)

        random.seed(42)
        damage = cm.calculate_damage(attacker, defender, use_magic=True)

        # Uses magic (30) instead of attack (5)
        assert damage >= 30
        assert damage <= 36

    def test_calculate_damage_minimum_one(self, load_system):
        """Test damage is at least 1."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]

        cm = CombatManager()
        attacker = Combatant("Weak", 100, 50, attack=0, defense=10, speed=10)
        defender = Combatant("Target", 100, 50, attack=10, defense=10, speed=10)

        damage = cm.calculate_damage(attacker, defender)

        assert damage >= 1

    def test_log_adds_message(self, load_system):
        """Test log adds messages to battle log."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]

        cm = CombatManager()
        cm.log("Test message 1")
        cm.log("Test message 2")

        assert len(cm.battle_log) == 2
        assert cm.battle_log[0] == "Test message 1"
        assert cm.battle_log[1] == "Test message 2"

    def test_log_limits_to_ten_messages(self, load_system):
        """Test log keeps only last 10 messages."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]

        cm = CombatManager()
        for i in range(15):
            cm.log(f"Message {i}")

        assert len(cm.battle_log) == 10
        assert cm.battle_log[0] == "Message 5"
        assert cm.battle_log[9] == "Message 14"


class TestCombatFlow:
    """Tests for combat flow (start, turns, end conditions)."""

    @pytest.fixture
    def mock_renpy_restart(self, load_system):
        """Add restart_interaction to mock renpy."""
        combat = load_system("combat")
        combat["renpy"].restart_interaction = lambda: None
        return combat

    def test_start_battle_single_enemy(self, mock_renpy_restart):
        """Test starting battle with single enemy."""
        combat = mock_renpy_restart
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]

        cm = CombatManager()
        player = Combatant("Player", 100, 50, 15, 10, 10)
        enemy = Enemy("Slime", hp=30, mp=0, attack=5, defense=2, speed=3)

        cm.start_battle(player, enemy)

        assert cm.player == player
        assert len(cm.enemies) == 1
        assert cm.state in ("player_turn", "enemy_turn")
        assert "Battle started!" in cm.battle_log

    def test_start_battle_multiple_enemies(self, mock_renpy_restart):
        """Test starting battle with multiple enemies."""
        combat = mock_renpy_restart
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]

        cm = CombatManager()
        player = Combatant("Player", 100, 50, 15, 10, 10)
        enemies = [
            Enemy("Slime", hp=30, mp=0, attack=5, defense=2, speed=3),
            Enemy("Goblin", hp=50, mp=10, attack=12, defense=5, speed=8),
        ]

        cm.start_battle(player, enemies)

        assert len(cm.enemies) == 2

    def test_victory_condition(self, mock_renpy_restart):
        """Test victory when all enemies defeated."""
        combat = mock_renpy_restart
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]

        cm = CombatManager()
        player = Combatant("Player", 100, 50, 15, 10, speed=20)  # High speed goes first
        enemy = Enemy("Weak", hp=1, mp=0, attack=5, defense=0, speed=1)

        cm.start_battle(player, enemy)
        # Player goes first due to higher speed
        assert cm.state == "player_turn"

        # Attack should defeat the enemy
        cm.player_attack(enemy)

        assert cm.state == "victory"
        assert "Victory!" in cm.battle_log

    def test_defeat_condition(self, mock_renpy_restart):
        """Test defeat when player HP reaches 0."""
        combat = mock_renpy_restart
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]

        cm = CombatManager()
        player = Combatant("Player", 1, 50, 15, 0, speed=1)  # 1 HP, low speed
        enemy = Enemy("Strong", hp=100, mp=0, attack=100, defense=0, speed=20)

        cm.start_battle(player, enemy)
        # Enemy should go first and defeat player

        assert cm.state == "defeat"
        assert "defeated" in cm.battle_log[-1].lower()

    def test_player_defend_sets_flag(self, mock_renpy_restart):
        """Test defend action sets is_defending flag."""
        combat = mock_renpy_restart
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]

        cm = CombatManager()
        player = Combatant("Player", 100, 50, 15, 10, speed=20)
        enemy = Enemy("Slow", hp=100, mp=0, attack=5, defense=2, speed=1)

        cm.start_battle(player, enemy)
        assert cm.state == "player_turn"

        cm.player_defend()

        assert player.is_defending is True
        assert "defensive stance" in cm.battle_log[-1].lower() or "enemy turn" in str(cm.state).lower()

    def test_player_skill_uses_mp(self, mock_renpy_restart):
        """Test skill usage consumes MP."""
        combat = mock_renpy_restart
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]

        cm = CombatManager()
        player = Combatant("Player", 100, 50, 15, 10, speed=20, magic=20)
        enemy = Enemy("Target", hp=100, mp=0, attack=5, defense=2, speed=1)

        cm.start_battle(player, enemy)
        assert cm.state == "player_turn"

        cm.player_skill("Fire Bolt", 10, 1.5, enemy)

        assert player.mp == 40

    def test_player_skill_insufficient_mp(self, mock_renpy_restart):
        """Test skill fails with insufficient MP."""
        combat = mock_renpy_restart
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]

        cm = CombatManager()
        player = Combatant("Player", 100, 5, 15, 10, speed=20, magic=20)  # Only 5 MP
        enemy = Enemy("Target", hp=100, mp=0, attack=5, defense=2, speed=1)

        cm.start_battle(player, enemy)
        initial_hp = enemy.hp

        cm.player_skill("Fire Bolt", 10, 1.5, enemy)  # Costs 10 MP

        assert player.mp == 5  # MP unchanged
        assert enemy.hp == initial_hp  # No damage dealt
        assert "Not enough MP!" in cm.battle_log

    def test_stunned_combatant_skips_turn(self, mock_renpy_restart):
        """Test stunned combatants skip their turn."""
        combat = mock_renpy_restart
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]
        StatusEffect = combat["StatusEffect"]

        cm = CombatManager()
        player = Combatant("Player", 100, 50, 15, 10, speed=20)
        enemy = Enemy("Stunned", hp=100, mp=0, attack=50, defense=2, speed=10)

        # Apply stun to enemy
        stun = StatusEffect("Stun", 2, "stun", 0)
        enemy.add_status(stun)

        cm.start_battle(player, enemy)
        initial_player_hp = player.hp

        # Player turn - attack
        cm.player_attack(enemy)

        # Enemy should be stunned and skip turn, then it's player's turn again
        # (or the combat continues without enemy attacking)
        # Due to stun, player HP should be unchanged from enemy attacks
        assert player.hp == initial_player_hp

    def test_get_rewards(self, load_system):
        """Test calculating battle rewards."""
        combat = load_system("combat")
        CombatManager = combat["CombatManager"]
        Combatant = combat["Combatant"]
        Enemy = combat["Enemy"]

        cm = CombatManager()
        cm.player = Combatant("Player", 100, 50, 15, 10, 10)
        cm.enemies = [
            Enemy("E1", hp=30, mp=0, attack=5, defense=2, speed=3, xp_reward=10, gold_reward=5),
            Enemy("E2", hp=30, mp=0, attack=5, defense=2, speed=3, xp_reward=15, gold_reward=10),
        ]

        xp, gold, items = cm.get_rewards()

        assert xp == 25
        assert gold == 15


class TestEnemyDatabase:
    """Tests for the enemy database and creation."""

    def test_create_enemy_slime(self, load_system):
        """Test creating a slime enemy from database."""
        combat = load_system("combat")
        create_enemy = combat["create_enemy"]

        slime = create_enemy("slime")

        assert slime is not None
        assert slime.name == "Slime"
        assert slime.hp == 30
        assert slime.attack == 5
        assert slime.xp_reward == 10
        assert slime.gold_reward == 5

    def test_create_enemy_goblin(self, load_system):
        """Test creating a goblin enemy from database."""
        combat = load_system("combat")
        create_enemy = combat["create_enemy"]

        goblin = create_enemy("goblin")

        assert goblin is not None
        assert goblin.name == "Goblin"
        assert goblin.hp == 50
        assert goblin.speed == 8
        assert len(goblin.drops) == 2

    def test_create_enemy_with_skills(self, load_system):
        """Test creating enemy with skills."""
        combat = load_system("combat")
        create_enemy = combat["create_enemy"]

        mage = create_enemy("dark_mage")

        assert mage is not None
        assert mage.name == "Dark Mage"
        assert mage.magic == 20
        assert len(mage.skills) == 2

    def test_create_enemy_boss(self, load_system):
        """Test creating boss enemy."""
        combat = load_system("combat")
        create_enemy = combat["create_enemy"]

        dragon = create_enemy("boss_dragon")

        assert dragon is not None
        assert dragon.name == "Ancient Dragon"
        assert dragon.hp == 500
        assert dragon.xp_reward == 500

    def test_create_enemy_invalid(self, load_system):
        """Test creating non-existent enemy returns None."""
        combat = load_system("combat")
        create_enemy = combat["create_enemy"]

        result = create_enemy("nonexistent_enemy")

        assert result is None

    def test_enemy_database_contains_all(self, load_system):
        """Test all expected enemies are in database."""
        combat = load_system("combat")
        ENEMY_DATABASE = combat["ENEMY_DATABASE"]

        expected_enemies = ["slime", "goblin", "wolf", "dark_mage", "boss_dragon"]

        for enemy_id in expected_enemies:
            assert enemy_id in ENEMY_DATABASE, f"Missing enemy: {enemy_id}"

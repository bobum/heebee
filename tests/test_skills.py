"""
Tests for the Heebee Skill Tree System.

Tests cover:
- Skill creation and requirements
- Unlocking skills with points
- Prerequisite checking
- Skill tree branches
- Point allocation and refunds
"""
import pytest


class TestSkillCreation:
    """Tests for Skill class creation and properties."""

    def test_skill_basic_creation(self, load_system):
        """Test creating a skill with basic parameters."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("test_skill", "Test Skill", "A test skill description")

        assert skill.skill_id == "test_skill"
        assert skill.name == "Test Skill"
        assert skill.description == "A test skill description"
        assert skill.cost == 1  # Default cost
        assert skill.category == "general"  # Default category
        assert skill.prerequisites == []
        assert skill.effects == {}
        assert skill.unlocked is False

    def test_skill_with_custom_cost(self, load_system):
        """Test creating a skill with custom cost."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("expensive", "Expensive Skill", "Costs a lot", cost=5)
        assert skill.cost == 5

    def test_skill_minimum_cost(self, load_system):
        """Test that skill cost cannot be less than 1."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("cheap", "Cheap Skill", "Should cost at least 1", cost=0)
        assert skill.cost == 1

        skill_negative = Skill("negative", "Negative Cost", "Negative cost", cost=-5)
        assert skill_negative.cost == 1

    def test_skill_with_prerequisites(self, load_system):
        """Test creating a skill with prerequisites."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("advanced", "Advanced Skill", "Requires basics",
                      prerequisites=["basic1", "basic2"])

        assert skill.prerequisites == ["basic1", "basic2"]

    def test_skill_with_effects(self, load_system):
        """Test creating a skill with stat effects."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        effects = {"strength_bonus": 5, "agility_bonus": 3}
        skill = Skill("powerful", "Powerful Skill", "Boosts stats", effects=effects)

        assert skill.effects == {"strength_bonus": 5, "agility_bonus": 3}

    def test_skill_with_category(self, load_system):
        """Test creating a skill with a specific category."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("magic_bolt", "Magic Bolt", "A magic attack", category="magic")
        assert skill.category == "magic"

    def test_skill_repr(self, load_system):
        """Test skill string representation."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("test", "Test", "Test desc")
        assert "test" in repr(skill)
        assert "Test" in repr(skill)
        assert "locked" in repr(skill)

        skill.unlock()
        assert "unlocked" in repr(skill)


class TestSkillPrerequisites:
    """Tests for skill prerequisite checking."""

    def test_can_unlock_no_prerequisites(self, load_system):
        """Test that skill without prerequisites can be unlocked."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("basic", "Basic", "No prereqs")
        assert skill.can_unlock(set()) is True
        assert skill.can_unlock([]) is True

    def test_can_unlock_with_met_prerequisites(self, load_system):
        """Test unlock check when prerequisites are met."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("advanced", "Advanced", "Needs prereqs",
                      prerequisites=["prereq1", "prereq2"])

        unlocked = {"prereq1", "prereq2", "other_skill"}
        assert skill.can_unlock(unlocked) is True

    def test_cannot_unlock_missing_prerequisites(self, load_system):
        """Test unlock check when prerequisites are not met."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("advanced", "Advanced", "Needs prereqs",
                      prerequisites=["prereq1", "prereq2"])

        # Missing prereq2
        unlocked = {"prereq1"}
        assert skill.can_unlock(unlocked) is False

        # Missing all
        assert skill.can_unlock(set()) is False

    def test_cannot_unlock_already_unlocked(self, load_system):
        """Test that already unlocked skill cannot be unlocked again."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("basic", "Basic", "Already unlocked")
        skill.unlock()

        assert skill.can_unlock(set()) is False

    def test_get_missing_prerequisites(self, load_system):
        """Test getting list of missing prerequisites."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("advanced", "Advanced", "Needs prereqs",
                      prerequisites=["prereq1", "prereq2", "prereq3"])

        # Only prereq1 unlocked
        missing = skill.get_missing_prerequisites({"prereq1"})
        assert "prereq2" in missing
        assert "prereq3" in missing
        assert "prereq1" not in missing

        # All met
        missing_all = skill.get_missing_prerequisites({"prereq1", "prereq2", "prereq3"})
        assert missing_all == []

    def test_skill_unlock_and_lock(self, load_system):
        """Test unlocking and locking a skill."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("test", "Test", "Test skill")

        assert skill.unlocked is False
        skill.unlock()
        assert skill.unlocked is True
        skill.lock()
        assert skill.unlocked is False


class TestSkillSerialization:
    """Tests for skill serialization (to_dict/from_dict)."""

    def test_skill_to_dict(self, load_system):
        """Test converting skill to dictionary."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        skill = Skill("fireball", "Fireball", "Cast fire",
                      cost=2, category="magic",
                      prerequisites=["spark"],
                      effects={"fire_damage": 10})
        skill.unlock()

        data = skill.to_dict()

        assert data["skill_id"] == "fireball"
        assert data["name"] == "Fireball"
        assert data["description"] == "Cast fire"
        assert data["cost"] == 2
        assert data["category"] == "magic"
        assert data["prerequisites"] == ["spark"]
        assert data["effects"] == {"fire_damage": 10}
        assert data["unlocked"] is True

    def test_skill_from_dict(self, load_system):
        """Test creating skill from dictionary."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        data = {
            "skill_id": "fireball",
            "name": "Fireball",
            "description": "Cast fire",
            "cost": 2,
            "category": "magic",
            "prerequisites": ["spark"],
            "effects": {"fire_damage": 10},
            "unlocked": True
        }

        skill = Skill.from_dict(data)

        assert skill.skill_id == "fireball"
        assert skill.name == "Fireball"
        assert skill.cost == 2
        assert skill.prerequisites == ["spark"]
        assert skill.effects == {"fire_damage": 10}
        assert skill.unlocked is True

    def test_skill_round_trip(self, load_system):
        """Test that to_dict and from_dict are reversible."""
        ns = load_system("skills")
        Skill = ns["Skill"]

        original = Skill("test", "Test Skill", "Description",
                         cost=3, category="test",
                         prerequisites=["a", "b"],
                         effects={"bonus": 5})
        original.unlock()

        restored = Skill.from_dict(original.to_dict())

        assert restored.skill_id == original.skill_id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.cost == original.cost
        assert restored.category == original.category
        assert restored.prerequisites == original.prerequisites
        assert restored.effects == original.effects
        assert restored.unlocked == original.unlocked


class TestSkillTree:
    """Tests for SkillTree class."""

    def test_skill_tree_creation(self, load_system):
        """Test creating a skill tree branch."""
        ns = load_system("skills")
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat", "Physical combat skills")

        assert tree.name == "Combat"
        assert tree.category == "combat"
        assert tree.description == "Physical combat skills"
        assert tree.skills == {}

    def test_add_skill_to_tree(self, load_system):
        """Test adding a skill to a tree."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        skill = Skill("slash", "Slash", "Basic attack")

        result = tree.add_skill(skill)

        assert result is True
        assert "slash" in tree.skills
        assert tree.skills["slash"] == skill
        assert skill.category == "combat"  # Category updated to match tree

    def test_add_duplicate_skill(self, load_system):
        """Test that adding duplicate skill ID fails."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        skill1 = Skill("slash", "Slash", "First slash")
        skill2 = Skill("slash", "Slash 2", "Different slash")

        tree.add_skill(skill1)
        result = tree.add_skill(skill2)

        assert result is False
        assert tree.skills["slash"].name == "Slash"  # First one kept

    def test_remove_skill(self, load_system):
        """Test removing a skill from tree."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        skill = Skill("slash", "Slash", "Basic attack")
        tree.add_skill(skill)

        removed = tree.remove_skill("slash")

        assert removed == skill
        assert "slash" not in tree.skills

    def test_remove_nonexistent_skill(self, load_system):
        """Test removing a skill that doesn't exist."""
        ns = load_system("skills")
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        result = tree.remove_skill("nonexistent")

        assert result is None

    def test_get_skill(self, load_system):
        """Test getting a skill from tree."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        skill = Skill("slash", "Slash", "Basic attack")
        tree.add_skill(skill)

        assert tree.get_skill("slash") == skill
        assert tree.get_skill("nonexistent") is None

    def test_get_unlocked_skills(self, load_system):
        """Test getting unlocked skills from tree."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        skill1 = Skill("slash", "Slash", "Attack 1")
        skill2 = Skill("thrust", "Thrust", "Attack 2")
        skill3 = Skill("parry", "Parry", "Defense")

        tree.add_skill(skill1)
        tree.add_skill(skill2)
        tree.add_skill(skill3)

        skill1.unlock()
        skill3.unlock()

        unlocked = tree.get_unlocked_skills()
        assert len(unlocked) == 2
        assert skill1 in unlocked
        assert skill3 in unlocked
        assert skill2 not in unlocked

    def test_get_available_skills(self, load_system):
        """Test getting skills available to unlock."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        basic = Skill("basic", "Basic", "No prereqs")
        advanced = Skill("advanced", "Advanced", "Needs basic", prerequisites=["basic"])

        tree.add_skill(basic)
        tree.add_skill(advanced)

        # Nothing unlocked
        available = tree.get_available_skills(set())
        assert len(available) == 1
        assert basic in available

        # Basic unlocked
        basic.unlock()
        available_after = tree.get_available_skills({"basic"})
        assert len(available_after) == 1
        assert advanced in available_after

    def test_get_total_points_spent(self, load_system):
        """Test calculating total points spent in tree."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        tree.add_skill(Skill("s1", "S1", "D1", cost=2))
        tree.add_skill(Skill("s2", "S2", "D2", cost=3))
        tree.add_skill(Skill("s3", "S3", "D3", cost=5))

        tree.skills["s1"].unlock()
        tree.skills["s3"].unlock()

        assert tree.get_total_points_spent() == 7  # 2 + 5

    def test_skill_counts(self, load_system):
        """Test skill count methods."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        tree.add_skill(Skill("s1", "S1", "D1"))
        tree.add_skill(Skill("s2", "S2", "D2"))
        tree.add_skill(Skill("s3", "S3", "D3"))

        tree.skills["s1"].unlock()

        assert tree.get_skill_count() == 3
        assert tree.get_unlocked_count() == 1

    def test_skill_tree_repr(self, load_system):
        """Test skill tree string representation."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Combat", "combat")
        tree.add_skill(Skill("s1", "S1", "D1"))
        tree.add_skill(Skill("s2", "S2", "D2"))
        tree.skills["s1"].unlock()

        assert "Combat" in repr(tree)
        assert "1/2" in repr(tree)


class TestSkillTreeSerialization:
    """Tests for SkillTree serialization."""

    def test_skill_tree_round_trip(self, load_system):
        """Test that skill tree can be serialized and restored."""
        ns = load_system("skills")
        Skill = ns["Skill"]
        SkillTree = ns["SkillTree"]

        tree = SkillTree("Magic", "magic", "Arcane arts")
        tree.add_skill(Skill("fireball", "Fireball", "Fire", cost=2))
        tree.add_skill(Skill("icebolt", "Ice Bolt", "Ice", cost=2))
        tree.skills["fireball"].unlock()

        data = tree.to_dict()
        restored = SkillTree.from_dict(data)

        assert restored.name == tree.name
        assert restored.category == tree.category
        assert restored.description == tree.description
        assert len(restored.skills) == 2
        assert restored.skills["fireball"].unlocked is True
        assert restored.skills["icebolt"].unlocked is False


class TestSkillManager:
    """Tests for SkillManager class."""

    def test_skill_manager_creation(self, load_system):
        """Test creating a skill manager."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]

        manager = SkillManager()

        assert manager.skill_points == 0
        assert manager.total_points_earned == 0
        assert manager.skill_trees == {}

    def test_add_skill_points(self, load_system):
        """Test adding skill points."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]

        manager = SkillManager()

        result = manager.add_skill_points(10)

        assert result == 10
        assert manager.skill_points == 10
        assert manager.total_points_earned == 10

        manager.add_skill_points(5)
        assert manager.skill_points == 15
        assert manager.total_points_earned == 15

    def test_add_negative_points(self, load_system):
        """Test that adding negative points does nothing."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]

        manager = SkillManager()
        manager.add_skill_points(10)
        manager.add_skill_points(-5)

        assert manager.skill_points == 10

    def test_create_skill_tree(self, load_system):
        """Test creating a skill tree via manager."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]

        manager = SkillManager()
        tree = manager.create_skill_tree("Combat", "combat", "Fight skills")

        assert tree is not None
        assert tree.name == "Combat"
        assert "combat" in manager.skill_trees

    def test_create_duplicate_tree(self, load_system):
        """Test that creating duplicate category returns None."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]

        manager = SkillManager()
        manager.create_skill_tree("Combat", "combat")
        result = manager.create_skill_tree("Combat 2", "combat")

        assert result is None

    def test_add_skill_tree(self, load_system):
        """Test adding an existing skill tree."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        SkillTree = ns["SkillTree"]
        Skill = ns["Skill"]

        manager = SkillManager()
        tree = SkillTree("Combat", "combat")
        tree.add_skill(Skill("slash", "Slash", "Attack"))

        result = manager.add_skill_tree(tree)

        assert result is True
        assert manager.get_skill("slash") is not None

    def test_register_skill(self, load_system):
        """Test registering a skill directly."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        skill = Skill("fireball", "Fireball", "Fire", category="magic")

        result = manager.register_skill(skill)

        assert result is True
        assert "magic" in manager.skill_trees  # Tree auto-created
        assert manager.get_skill("fireball") == skill


class TestSkillUnlocking:
    """Tests for skill unlocking mechanics."""

    def test_unlock_skill_success(self, load_system):
        """Test successfully unlocking a skill."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(5)
        manager.register_skill(Skill("basic", "Basic", "Simple", cost=2))

        result = manager.unlock_skill("basic")

        assert result is True
        assert manager.is_unlocked("basic") is True
        assert manager.skill_points == 3

    def test_unlock_skill_insufficient_points(self, load_system):
        """Test unlocking fails with insufficient points."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(1)
        manager.register_skill(Skill("expensive", "Expensive", "Costly", cost=5))

        result = manager.unlock_skill("expensive")

        assert result is False
        assert manager.is_unlocked("expensive") is False
        assert manager.skill_points == 1

    def test_unlock_skill_missing_prerequisites(self, load_system):
        """Test unlocking fails when prerequisites not met."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)
        manager.register_skill(Skill("basic", "Basic", "First"))
        manager.register_skill(Skill("advanced", "Advanced", "Second",
                                     prerequisites=["basic"]))

        result = manager.unlock_skill("advanced")

        assert result is False
        assert manager.is_unlocked("advanced") is False

    def test_unlock_skill_with_prerequisites(self, load_system):
        """Test unlocking skill after meeting prerequisites."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)
        manager.register_skill(Skill("basic", "Basic", "First"))
        manager.register_skill(Skill("advanced", "Advanced", "Second",
                                     prerequisites=["basic"]))

        manager.unlock_skill("basic")
        result = manager.unlock_skill("advanced")

        assert result is True
        assert manager.is_unlocked("advanced") is True

    def test_unlock_nonexistent_skill(self, load_system):
        """Test unlocking a skill that doesn't exist."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]

        manager = SkillManager()
        manager.add_skill_points(10)

        result = manager.unlock_skill("nonexistent")

        assert result is False

    def test_can_unlock_checks(self, load_system):
        """Test can_unlock method variations."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(5)
        manager.register_skill(Skill("cheap", "Cheap", "Low cost", cost=1))
        manager.register_skill(Skill("pricey", "Pricey", "High cost", cost=10))

        assert manager.can_unlock("cheap") is True
        assert manager.can_unlock("pricey") is False  # Not enough points
        assert manager.can_unlock("nonexistent") is False

    def test_get_unlocked_skill_ids(self, load_system):
        """Test getting set of unlocked skill IDs."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)
        manager.register_skill(Skill("s1", "S1", "D1"))
        manager.register_skill(Skill("s2", "S2", "D2"))
        manager.register_skill(Skill("s3", "S3", "D3"))

        manager.unlock_skill("s1")
        manager.unlock_skill("s3")

        unlocked = manager.get_unlocked_skill_ids()

        assert unlocked == {"s1", "s3"}

    def test_get_available_skills(self, load_system):
        """Test getting available skills to unlock."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)
        manager.register_skill(Skill("basic", "Basic", "Start", category="combat"))
        manager.register_skill(Skill("advanced", "Advanced", "Next",
                                     category="combat", prerequisites=["basic"]))
        manager.register_skill(Skill("magic", "Magic", "Spell", category="magic"))

        available = manager.get_available_skills()
        assert len(available) == 2  # basic and magic

        manager.unlock_skill("basic")
        available_after = manager.get_available_skills()
        assert len(available_after) == 2  # advanced and magic

        # Filter by category
        combat_available = manager.get_available_skills("combat")
        assert len(combat_available) == 1


class TestSkillRefunding:
    """Tests for skill refund mechanics."""

    def test_refund_skill_success(self, load_system):
        """Test successfully refunding a skill."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)
        manager.register_skill(Skill("basic", "Basic", "Simple", cost=3))
        manager.unlock_skill("basic")

        assert manager.skill_points == 7

        refunded = manager.refund_skill("basic")

        assert refunded == 3
        assert manager.skill_points == 10
        assert manager.is_unlocked("basic") is False

    def test_refund_locked_skill(self, load_system):
        """Test refunding a skill that's not unlocked."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.register_skill(Skill("basic", "Basic", "Simple"))

        refunded = manager.refund_skill("basic")

        assert refunded == 0

    def test_refund_with_dependents(self, load_system):
        """Test that skill with unlocked dependents cannot be refunded."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)
        manager.register_skill(Skill("basic", "Basic", "First"))
        manager.register_skill(Skill("advanced", "Advanced", "Second",
                                     prerequisites=["basic"]))

        manager.unlock_skill("basic")
        manager.unlock_skill("advanced")

        # Cannot refund basic because advanced depends on it
        assert manager.can_refund("basic") is False
        refunded = manager.refund_skill("basic")
        assert refunded == 0
        assert manager.is_unlocked("basic") is True

        # Can refund advanced
        assert manager.can_refund("advanced") is True

    def test_refund_after_dependent_refunded(self, load_system):
        """Test refunding prerequisite after dependent is refunded."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)
        manager.register_skill(Skill("basic", "Basic", "First", cost=2))
        manager.register_skill(Skill("advanced", "Advanced", "Second",
                                     cost=3, prerequisites=["basic"]))

        manager.unlock_skill("basic")
        manager.unlock_skill("advanced")

        assert manager.skill_points == 5

        # Refund in order
        manager.refund_skill("advanced")
        assert manager.skill_points == 8

        manager.refund_skill("basic")
        assert manager.skill_points == 10

    def test_get_dependent_skills(self, load_system):
        """Test getting skills that depend on a given skill."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.register_skill(Skill("basic", "Basic", "First"))
        manager.register_skill(Skill("adv1", "Advanced 1", "Dep 1",
                                     prerequisites=["basic"]))
        manager.register_skill(Skill("adv2", "Advanced 2", "Dep 2",
                                     prerequisites=["basic"]))
        manager.register_skill(Skill("other", "Other", "No dep"))

        dependents = manager.get_dependent_skills("basic")

        assert len(dependents) == 2
        dep_ids = [d.skill_id for d in dependents]
        assert "adv1" in dep_ids
        assert "adv2" in dep_ids


class TestPointAllocation:
    """Tests for point allocation and tracking."""

    def test_total_points_spent(self, load_system):
        """Test tracking total points spent across all trees."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(20)

        # Add skills to different trees
        manager.register_skill(Skill("combat1", "C1", "D1", cost=3, category="combat"))
        manager.register_skill(Skill("magic1", "M1", "D1", cost=5, category="magic"))
        manager.register_skill(Skill("magic2", "M2", "D2", cost=2, category="magic"))

        manager.unlock_skill("combat1")
        manager.unlock_skill("magic1")

        assert manager.get_total_points_spent() == 8
        assert manager.skill_points == 12

    def test_reset_all_skills(self, load_system):
        """Test resetting all skills and refunding points."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(20)

        manager.register_skill(Skill("s1", "S1", "D1", cost=3, category="combat"))
        manager.register_skill(Skill("s2", "S2", "D2", cost=5, category="magic"))

        manager.unlock_skill("s1")
        manager.unlock_skill("s2")

        assert manager.skill_points == 12

        refunded = manager.reset_all()

        assert refunded == 8
        assert manager.skill_points == 20
        assert manager.is_unlocked("s1") is False
        assert manager.is_unlocked("s2") is False

    def test_reset_single_tree(self, load_system):
        """Test resetting a single skill tree."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(20)

        manager.register_skill(Skill("c1", "C1", "D1", cost=3, category="combat"))
        manager.register_skill(Skill("m1", "M1", "D1", cost=5, category="magic"))

        manager.unlock_skill("c1")
        manager.unlock_skill("m1")

        refunded = manager.reset_tree("combat")

        assert refunded == 3
        assert manager.skill_points == 15
        assert manager.is_unlocked("c1") is False
        assert manager.is_unlocked("m1") is True  # Magic unchanged

    def test_reset_nonexistent_tree(self, load_system):
        """Test resetting a tree that doesn't exist."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]

        manager = SkillManager()

        refunded = manager.reset_tree("nonexistent")

        assert refunded == 0


class TestSkillEffects:
    """Tests for skill effect calculations."""

    def test_get_total_effects(self, load_system):
        """Test calculating combined effects from unlocked skills."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(20)

        manager.register_skill(Skill("s1", "S1", "D1",
                                     effects={"strength_bonus": 5, "agility_bonus": 2}))
        manager.register_skill(Skill("s2", "S2", "D2",
                                     effects={"strength_bonus": 3, "intelligence_bonus": 4}))
        manager.register_skill(Skill("s3", "S3", "D3",
                                     effects={"defense_bonus": 10}))

        manager.unlock_skill("s1")
        manager.unlock_skill("s2")
        # s3 not unlocked

        effects = manager.get_total_effects()

        assert effects["strength_bonus"] == 8  # 5 + 3
        assert effects["agility_bonus"] == 2
        assert effects["intelligence_bonus"] == 4
        assert "defense_bonus" not in effects  # s3 not unlocked

    def test_get_single_effect(self, load_system):
        """Test getting a specific effect value."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)

        manager.register_skill(Skill("s1", "S1", "D1",
                                     effects={"strength_bonus": 5}))
        manager.unlock_skill("s1")

        assert manager.get_effect("strength_bonus") == 5
        assert manager.get_effect("nonexistent") == 0

    def test_effects_empty_when_no_skills(self, load_system):
        """Test that effects are empty with no unlocked skills."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.register_skill(Skill("s1", "S1", "D1",
                                     effects={"strength_bonus": 5}))

        effects = manager.get_total_effects()

        assert effects == {}


class TestSkillManagerSerialization:
    """Tests for SkillManager serialization."""

    def test_skill_manager_round_trip(self, load_system):
        """Test that manager can be serialized and restored."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(15)

        manager.register_skill(Skill("s1", "S1", "D1", cost=3, category="combat"))
        manager.register_skill(Skill("s2", "S2", "D2", cost=2, category="magic",
                                     effects={"bonus": 5}))

        manager.unlock_skill("s1")

        # Serialize
        data = manager.to_dict()

        # Restore
        restored = SkillManager.from_dict(data)

        assert restored.skill_points == 12  # 15 - 3
        assert restored.total_points_earned == 15
        assert len(restored.skill_trees) == 2
        assert restored.is_unlocked("s1") is True
        assert restored.is_unlocked("s2") is False
        assert restored.get_skill("s2").effects == {"bonus": 5}


class TestSkillManagerStatistics:
    """Tests for skill statistics."""

    def test_get_statistics(self, load_system):
        """Test getting skill progression statistics."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)

        manager.register_skill(Skill("s1", "S1", "D1", cost=2, category="combat"))
        manager.register_skill(Skill("s2", "S2", "D2", cost=3, category="combat"))
        manager.register_skill(Skill("s3", "S3", "D3", cost=1, category="magic"))
        manager.register_skill(Skill("s4", "S4", "D4", cost=2, category="magic"))

        manager.unlock_skill("s1")
        manager.unlock_skill("s3")

        stats = manager.get_statistics()

        assert stats["total_skills"] == 4
        assert stats["unlocked_skills"] == 2
        assert stats["locked_skills"] == 2
        assert stats["completion_percent"] == 50.0
        assert stats["skill_points"] == 7  # 10 - 2 - 1
        assert stats["total_points_earned"] == 10
        assert stats["total_points_spent"] == 3  # 2 + 1
        assert stats["tree_count"] == 2

    def test_statistics_empty_manager(self, load_system):
        """Test statistics with no skills."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]

        manager = SkillManager()

        stats = manager.get_statistics()

        assert stats["total_skills"] == 0
        assert stats["completion_percent"] == 0


class TestDefaultSkillTrees:
    """Tests for the default skill tree setup."""

    def test_create_default_skill_trees(self, load_system):
        """Test creating default skill trees."""
        ns = load_system("skills")
        create_default = ns["create_default_skill_trees"]

        manager = create_default()

        # Check that trees were created
        assert "combat" in manager.skill_trees
        assert "magic" in manager.skill_trees
        assert "stealth" in manager.skill_trees

        # Check some skills exist
        assert manager.get_skill("power_strike") is not None
        assert manager.get_skill("fireball") is not None
        assert manager.get_skill("sneak") is not None

    def test_default_tree_prerequisites(self, load_system):
        """Test that default trees have proper prerequisite chains."""
        ns = load_system("skills")
        create_default = ns["create_default_skill_trees"]

        manager = create_default()
        manager.add_skill_points(20)

        # Cannot unlock berserker without power_strike
        assert manager.can_unlock("berserker") is False

        manager.unlock_skill("power_strike")
        assert manager.can_unlock("berserker") is True

    def test_default_tree_effects(self, load_system):
        """Test that default skills have effects."""
        ns = load_system("skills")
        create_default = ns["create_default_skill_trees"]

        manager = create_default()

        power_strike = manager.get_skill("power_strike")
        assert "strength_bonus" in power_strike.effects

        fireball = manager.get_skill("fireball")
        assert "intelligence_bonus" in fireball.effects


class TestSkillManagerRepr:
    """Tests for SkillManager string representation."""

    def test_manager_repr(self, load_system):
        """Test manager string representation."""
        ns = load_system("skills")
        SkillManager = ns["SkillManager"]
        Skill = ns["Skill"]

        manager = SkillManager()
        manager.add_skill_points(10)
        manager.register_skill(Skill("s1", "S1", "D1"))
        manager.register_skill(Skill("s2", "S2", "D2"))
        manager.unlock_skill("s1")

        rep = repr(manager)
        assert "1/2" in rep
        assert "10" in rep or "points" in rep.lower()

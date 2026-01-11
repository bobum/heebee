"""
Comprehensive tests for the relationship system.

Tests cover:
- Relationship initialization and properties
- Affection/trust/respect modifications
- Status calculations (friend, lover, etc.)
- Romance unlock conditions
- Faction reputation and ranks
- Milestone unlocking
"""
import pytest


class TestRelationshipInitialization:
    """Tests for Relationship class initialization."""

    def test_default_initialization(self, load_system):
        """Test Relationship initializes with default values."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")

        assert rel.name == "TestChar"
        assert rel.affection == 50
        assert rel.trust == 50
        assert rel.respect == 50
        assert rel.history == []
        assert rel.unlocked_events == []
        assert rel.met is False
        assert rel.romance_available is False
        assert rel.romance_active is False

    def test_custom_initialization(self, load_system):
        """Test Relationship initializes with custom values."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("CustomChar", initial_affection=75, initial_trust=60, initial_respect=80)

        assert rel.name == "CustomChar"
        assert rel.affection == 75
        assert rel.trust == 60
        assert rel.respect == 80

    def test_partial_custom_initialization(self, load_system):
        """Test Relationship with some custom values."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("PartialChar", initial_affection=30)

        assert rel.affection == 30
        assert rel.trust == 50
        assert rel.respect == 50


class TestAffectionModification:
    """Tests for affection stat modifications."""

    def test_modify_affection_positive(self, load_system):
        """Test increasing affection."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        change = rel.modify_affection(20, "Helped out")

        assert rel.affection == 70
        assert change == 20
        assert len(rel.history) == 1
        assert rel.history[0] == ("affection", 20, "Helped out")

    def test_modify_affection_negative(self, load_system):
        """Test decreasing affection."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        change = rel.modify_affection(-15, "Was rude")

        assert rel.affection == 35
        assert change == -15
        assert len(rel.history) == 1
        assert rel.history[0] == ("affection", -15, "Was rude")

    def test_affection_clamped_at_max(self, load_system):
        """Test affection cannot exceed 100."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=90)
        change = rel.modify_affection(50)

        assert rel.affection == 100
        assert change == 10

    def test_affection_clamped_at_min(self, load_system):
        """Test affection cannot go below 0."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=10)
        change = rel.modify_affection(-30)

        assert rel.affection == 0
        assert change == -10

    def test_affection_no_reason_no_history(self, load_system):
        """Test modification without reason doesn't add to history."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        rel.modify_affection(10)

        assert rel.affection == 60
        assert len(rel.history) == 0


class TestTrustModification:
    """Tests for trust stat modifications."""

    def test_modify_trust_positive(self, load_system):
        """Test increasing trust."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        change = rel.modify_trust(25, "Kept a secret")

        assert rel.trust == 75
        assert change == 25
        assert ("trust", 25, "Kept a secret") in rel.history

    def test_modify_trust_negative(self, load_system):
        """Test decreasing trust."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        change = rel.modify_trust(-20, "Broke promise")

        assert rel.trust == 30
        assert change == -20

    def test_trust_clamped_at_max(self, load_system):
        """Test trust cannot exceed 100."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_trust=95)
        change = rel.modify_trust(20)

        assert rel.trust == 100
        assert change == 5

    def test_trust_clamped_at_min(self, load_system):
        """Test trust cannot go below 0."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_trust=5)
        change = rel.modify_trust(-50)

        assert rel.trust == 0
        assert change == -5


class TestRespectModification:
    """Tests for respect stat modifications."""

    def test_modify_respect_positive(self, load_system):
        """Test increasing respect."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        change = rel.modify_respect(30, "Showed competence")

        assert rel.respect == 80
        assert change == 30

    def test_modify_respect_negative(self, load_system):
        """Test decreasing respect."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        change = rel.modify_respect(-10, "Made mistake")

        assert rel.respect == 40
        assert change == -10

    def test_respect_clamped_at_max(self, load_system):
        """Test respect cannot exceed 100."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_respect=85)
        change = rel.modify_respect(50)

        assert rel.respect == 100
        assert change == 15

    def test_respect_clamped_at_min(self, load_system):
        """Test respect cannot go below 0."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_respect=15)
        change = rel.modify_respect(-40)

        assert rel.respect == 0
        assert change == -15


class TestModifyAll:
    """Tests for modifying all stats at once."""

    def test_modify_all_positive(self, load_system):
        """Test increasing all stats."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        rel.modify_all(10, "Great impression")

        assert rel.affection == 60
        assert rel.trust == 60
        assert rel.respect == 60
        assert len(rel.history) == 3

    def test_modify_all_negative(self, load_system):
        """Test decreasing all stats."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        rel.modify_all(-20, "Major offense")

        assert rel.affection == 30
        assert rel.trust == 30
        assert rel.respect == 30


class TestOverallScore:
    """Tests for overall relationship score calculation."""

    def test_get_overall_equal_stats(self, load_system):
        """Test overall with equal stats."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=60, initial_trust=60, initial_respect=60)

        assert rel.get_overall() == 60

    def test_get_overall_varied_stats(self, load_system):
        """Test overall with varied stats."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=30, initial_trust=60, initial_respect=90)

        assert rel.get_overall() == 60

    def test_get_overall_rounds_down(self, load_system):
        """Test overall rounds down to integer."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=33, initial_trust=33, initial_respect=33)

        assert rel.get_overall() == 33
        assert isinstance(rel.get_overall(), int)


class TestStatusCalculation:
    """Tests for relationship status text calculation."""

    def test_status_stranger(self, load_system):
        """Test Stranger status (overall < 15)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=10, initial_trust=10, initial_respect=10)

        assert rel.get_status() == "Stranger"

    def test_status_distant(self, load_system):
        """Test Distant status (15-29)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=20, initial_trust=20, initial_respect=20)

        assert rel.get_status() == "Distant"

    def test_status_acquaintance(self, load_system):
        """Test Acquaintance status (30-44)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=35, initial_trust=35, initial_respect=35)

        assert rel.get_status() == "Acquaintance"

    def test_status_friend(self, load_system):
        """Test Friend status (45-59)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=50, initial_trust=50, initial_respect=50)

        assert rel.get_status() == "Friend"

    def test_status_good_friend(self, load_system):
        """Test Good Friend status (60-74, no romance)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=65, initial_trust=65, initial_respect=65)

        assert rel.get_status() == "Good Friend"

    def test_status_dating_with_romance(self, load_system):
        """Test Dating status (60-74, with romance)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=65, initial_trust=65, initial_respect=65)
        rel.romance_available = True
        rel.start_romance()

        assert rel.get_status() == "Dating"

    def test_status_close_friend(self, load_system):
        """Test Close Friend status (75-89, no romance)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=80, initial_trust=80, initial_respect=80)

        assert rel.get_status() == "Close Friend"

    def test_status_lover_with_romance(self, load_system):
        """Test Lover status (75-89, with romance)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=80, initial_trust=80, initial_respect=80)
        rel.romance_available = True
        rel.start_romance()

        assert rel.get_status() == "Lover"

    def test_status_best_friend(self, load_system):
        """Test Best Friend status (90+, no romance)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=95, initial_trust=95, initial_respect=95)

        assert rel.get_status() == "Best Friend"

    def test_status_soulmate_with_romance(self, load_system):
        """Test Soulmate status (90+, with romance)."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=95, initial_trust=95, initial_respect=95)
        rel.romance_available = True
        rel.start_romance()

        assert rel.get_status() == "Soulmate"


class TestRomanceUnlockConditions:
    """Tests for romance unlock conditions."""

    def test_romance_not_unlocked_initially(self, load_system):
        """Test romance is not available by default."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")

        assert rel.romance_available is False

    def test_romance_unlocked_at_threshold(self, load_system):
        """Test romance unlocks at 60 affection and 50 trust."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=55, initial_trust=50)
        assert rel.romance_available is False

        rel.modify_affection(5)
        assert rel.romance_available is True
        assert "romance_unlocked" in rel.unlocked_events

    def test_romance_not_unlocked_low_trust(self, load_system):
        """Test romance not unlocked with low trust."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=70, initial_trust=40)
        # Trigger milestone check
        rel.modify_affection(1)
        rel.modify_affection(-1)

        assert rel.romance_available is False

    def test_romance_not_unlocked_low_affection(self, load_system):
        """Test romance not unlocked with low affection."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=50, initial_trust=80)
        rel.modify_trust(1)
        rel.modify_trust(-1)

        assert rel.romance_available is False

    def test_start_romance_success(self, load_system):
        """Test starting romance when available."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=65, initial_trust=55)
        rel.modify_affection(1)  # Trigger milestone check

        assert rel.romance_available is True
        result = rel.start_romance()

        assert result is True
        assert rel.romance_active is True

    def test_start_romance_failure(self, load_system):
        """Test starting romance when not available."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar")
        result = rel.start_romance()

        assert result is False
        assert rel.romance_active is False

    def test_end_romance(self, load_system):
        """Test ending a romance."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=70, initial_trust=60)
        rel.modify_affection(1)  # Trigger milestone check
        rel.start_romance()

        initial_affection = rel.affection
        initial_trust = rel.trust

        rel.end_romance()

        assert rel.romance_active is False
        assert rel.affection == initial_affection - 20
        assert rel.trust == initial_trust - 10
        assert ("affection", -20, "Breakup") in rel.history
        assert ("trust", -10, "Breakup") in rel.history


class TestMilestoneUnlocking:
    """Tests for milestone event unlocking."""

    def test_milestone_75_unlocked(self, load_system):
        """Test milestone_75 event unlocked at overall 75."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=74, initial_trust=75, initial_respect=76)
        rel.modify_affection(1)  # Trigger check

        assert "milestone_75" in rel.unlocked_events

    def test_milestone_75_not_unlocked_below(self, load_system):
        """Test milestone_75 not unlocked below threshold."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=70, initial_trust=70, initial_respect=70)
        rel.modify_affection(1)

        assert "milestone_75" not in rel.unlocked_events

    def test_milestone_90_unlocked(self, load_system):
        """Test milestone_90 event unlocked at overall 90."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=90, initial_trust=90, initial_respect=90)
        rel.modify_affection(1)
        rel.modify_affection(-1)

        assert "milestone_90" in rel.unlocked_events

    def test_milestones_not_duplicated(self, load_system):
        """Test milestones are not added multiple times."""
        ns = load_system("relationships")
        Relationship = ns["Relationship"]

        rel = Relationship("TestChar", initial_affection=95, initial_trust=95, initial_respect=95)
        rel.modify_affection(1)
        rel.modify_affection(1)
        rel.modify_affection(1)

        assert rel.unlocked_events.count("milestone_90") == 1
        assert rel.unlocked_events.count("milestone_75") == 1


class TestFactionInitialization:
    """Tests for Faction class initialization."""

    def test_default_initialization(self, load_system):
        """Test Faction initializes with default values."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction")

        assert faction.name == "TestFaction"
        assert faction.reputation == 0
        assert faction.rank == "Neutral"
        assert faction.perks_unlocked == []

    def test_custom_initialization(self, load_system):
        """Test Faction initializes with custom reputation."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("CustomFaction", initial_rep=50)

        assert faction.reputation == 50
        assert faction.rank == "Honored"


class TestFactionReputationModification:
    """Tests for faction reputation modifications."""

    def test_modify_reputation_positive(self, load_system):
        """Test increasing reputation."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction")
        change = faction.modify_reputation(30)

        assert faction.reputation == 30
        assert change == 30

    def test_modify_reputation_negative(self, load_system):
        """Test decreasing reputation."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction")
        change = faction.modify_reputation(-25)

        assert faction.reputation == -25
        assert change == -25

    def test_reputation_clamped_at_max(self, load_system):
        """Test reputation cannot exceed 100."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=80)
        change = faction.modify_reputation(50)

        assert faction.reputation == 100
        assert change == 20

    def test_reputation_clamped_at_min(self, load_system):
        """Test reputation cannot go below -100."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=-80)
        change = faction.modify_reputation(-50)

        assert faction.reputation == -100
        assert change == -20


class TestFactionRanks:
    """Tests for faction rank calculations."""

    def test_rank_exalted(self, load_system):
        """Test Exalted rank at 80+."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=85)

        assert faction.rank == "Exalted"

    def test_rank_revered(self, load_system):
        """Test Revered rank at 60-79."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=70)

        assert faction.rank == "Revered"

    def test_rank_honored(self, load_system):
        """Test Honored rank at 40-59."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=50)

        assert faction.rank == "Honored"

    def test_rank_friendly(self, load_system):
        """Test Friendly rank at 20-39."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=30)

        assert faction.rank == "Friendly"

    def test_rank_neutral(self, load_system):
        """Test Neutral rank at -20 to 19."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=0)
        assert faction.rank == "Neutral"

        faction2 = Faction("TestFaction2", initial_rep=-15)
        assert faction2.rank == "Neutral"

    def test_rank_unfriendly(self, load_system):
        """Test Unfriendly rank at -40 to -21."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=-30)

        assert faction.rank == "Unfriendly"

    def test_rank_hostile(self, load_system):
        """Test Hostile rank at -60 to -41."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=-50)

        assert faction.rank == "Hostile"

    def test_rank_hated(self, load_system):
        """Test Hated rank at -61 and below."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=-75)

        assert faction.rank == "Hated"

    def test_rank_updates_on_modification(self, load_system):
        """Test rank updates when reputation changes."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=10)
        assert faction.rank == "Neutral"

        faction.modify_reputation(15)
        assert faction.rank == "Friendly"

        faction.modify_reputation(20)
        assert faction.rank == "Honored"


class TestFactionPerks:
    """Tests for faction perk unlocking."""

    def test_discount_10_unlocked_at_40(self, load_system):
        """Test 10% discount unlocked at reputation 40."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=35)
        assert "discount_10" not in faction.perks_unlocked

        faction.modify_reputation(10)
        assert "discount_10" in faction.perks_unlocked

    def test_discount_20_unlocked_at_60(self, load_system):
        """Test 20% discount unlocked at reputation 60."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=55)
        assert "discount_20" not in faction.perks_unlocked

        faction.modify_reputation(10)
        assert "discount_20" in faction.perks_unlocked

    def test_exclusive_items_unlocked_at_80(self, load_system):
        """Test exclusive items unlocked at reputation 80."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=75)
        assert "exclusive_items" not in faction.perks_unlocked

        faction.modify_reputation(10)
        assert "exclusive_items" in faction.perks_unlocked

    def test_get_discount_no_perk(self, load_system):
        """Test get_discount returns 0 with no perks."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=30)

        assert faction.get_discount() == 0.0

    def test_get_discount_10_percent(self, load_system):
        """Test get_discount returns 0.10 with discount_10."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=45)

        assert faction.get_discount() == 0.10

    def test_get_discount_20_percent(self, load_system):
        """Test get_discount returns 0.20 with discount_20."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=70)

        assert faction.get_discount() == 0.20

    def test_perks_not_duplicated(self, load_system):
        """Test perks are not added multiple times."""
        ns = load_system("relationships")
        Faction = ns["Faction"]

        faction = Faction("TestFaction", initial_rep=85)
        faction.modify_reputation(5)
        faction.modify_reputation(5)

        assert faction.perks_unlocked.count("discount_10") == 1
        assert faction.perks_unlocked.count("discount_20") == 1
        assert faction.perks_unlocked.count("exclusive_items") == 1


class TestRelationshipManager:
    """Tests for RelationshipManager class."""

    def test_initialization(self, load_system):
        """Test RelationshipManager initializes empty."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()

        assert manager.relationships == {}
        assert manager.factions == {}

    def test_add_character(self, load_system):
        """Test adding a character."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_character("elena", "Elena", initial_affection=60)

        assert "elena" in manager.relationships
        assert manager.relationships["elena"].name == "Elena"
        assert manager.relationships["elena"].affection == 60

    def test_add_faction(self, load_system):
        """Test adding a faction."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_faction("guild", "Adventurer's Guild", 20)

        assert "guild" in manager.factions
        assert manager.factions["guild"].name == "Adventurer's Guild"
        assert manager.factions["guild"].reputation == 20

    def test_get_relationship(self, load_system):
        """Test getting a relationship."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_character("test", "Test Character")

        rel = manager.get_relationship("test")
        assert rel.name == "Test Character"

        missing = manager.get_relationship("nonexistent")
        assert missing is None

    def test_get_faction(self, load_system):
        """Test getting a faction."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_faction("test_faction", "Test Faction")

        faction = manager.get_faction("test_faction")
        assert faction.name == "Test Faction"

        missing = manager.get_faction("nonexistent")
        assert missing is None

    def test_meet_character(self, load_system):
        """Test marking character as met."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_character("elena", "Elena")

        assert manager.relationships["elena"].met is False
        manager.meet_character("elena")
        assert manager.relationships["elena"].met is True

    def test_meet_nonexistent_character(self, load_system):
        """Test meeting nonexistent character doesn't crash."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.meet_character("nonexistent")  # Should not raise

    def test_get_met_characters(self, load_system):
        """Test getting list of met characters."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_character("elena", "Elena")
        manager.add_character("marcus", "Marcus")
        manager.add_character("sophia", "Sophia")

        manager.meet_character("elena")
        manager.meet_character("sophia")

        met = manager.get_met_characters()
        names = [r.name for r in met]

        assert len(met) == 2
        assert "Elena" in names
        assert "Sophia" in names
        assert "Marcus" not in names

    def test_get_romance_options(self, load_system):
        """Test getting available romance options."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_character("elena", "Elena", initial_affection=65, initial_trust=55)
        manager.add_character("marcus", "Marcus", initial_affection=40, initial_trust=50)
        manager.add_character("sophia", "Sophia", initial_affection=70, initial_trust=60)

        # Trigger milestone checks
        manager.relationships["elena"].modify_affection(1)
        manager.relationships["marcus"].modify_affection(1)
        manager.relationships["sophia"].modify_affection(1)

        options = manager.get_romance_options()
        names = [r.name for r in options]

        assert len(options) == 2
        assert "Elena" in names
        assert "Sophia" in names
        assert "Marcus" not in names

    def test_get_romance_options_excludes_active(self, load_system):
        """Test romance options exclude active romances."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_character("elena", "Elena", initial_affection=65, initial_trust=55)
        manager.add_character("sophia", "Sophia", initial_affection=70, initial_trust=60)

        manager.relationships["elena"].modify_affection(1)
        manager.relationships["sophia"].modify_affection(1)

        manager.relationships["elena"].start_romance()

        options = manager.get_romance_options()
        names = [r.name for r in options]

        assert len(options) == 1
        assert "Sophia" in names
        assert "Elena" not in names

    def test_get_active_romances(self, load_system):
        """Test getting active romances."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_character("elena", "Elena", initial_affection=65, initial_trust=55)
        manager.add_character("sophia", "Sophia", initial_affection=70, initial_trust=60)

        manager.relationships["elena"].modify_affection(1)
        manager.relationships["sophia"].modify_affection(1)

        assert len(manager.get_active_romances()) == 0

        manager.relationships["elena"].start_romance()

        active = manager.get_active_romances()
        assert len(active) == 1
        assert active[0].name == "Elena"

    def test_multiple_active_romances(self, load_system):
        """Test tracking multiple active romances."""
        ns = load_system("relationships")
        RelationshipManager = ns["RelationshipManager"]

        manager = RelationshipManager()
        manager.add_character("elena", "Elena", initial_affection=65, initial_trust=55)
        manager.add_character("sophia", "Sophia", initial_affection=70, initial_trust=60)

        manager.relationships["elena"].modify_affection(1)
        manager.relationships["sophia"].modify_affection(1)

        manager.relationships["elena"].start_romance()
        manager.relationships["sophia"].start_romance()

        active = manager.get_active_romances()
        names = [r.name for r in active]

        assert len(active) == 2
        assert "Elena" in names
        assert "Sophia" in names

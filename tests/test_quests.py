"""
Comprehensive tests for the Quest/Mission Log System.

Tests cover QuestObjective, QuestRewards, Quest, and QuestManager classes.
"""
import pytest


class TestQuestObjective:
    """Tests for the QuestObjective class."""

    def test_create_objective_defaults(self, load_system):
        """Test creating an objective with default values."""
        ns = load_system("quests")
        QuestObjective = ns["QuestObjective"]

        obj = QuestObjective("Find the sword")

        assert obj.description == "Find the sword"
        assert obj.completed is False
        assert obj.optional is False

    def test_create_optional_objective(self, load_system):
        """Test creating an optional objective."""
        ns = load_system("quests")
        QuestObjective = ns["QuestObjective"]

        obj = QuestObjective("Find bonus treasure", optional=True)

        assert obj.description == "Find bonus treasure"
        assert obj.completed is False
        assert obj.optional is True

    def test_complete_objective(self, load_system):
        """Test completing an objective."""
        ns = load_system("quests")
        QuestObjective = ns["QuestObjective"]

        obj = QuestObjective("Defeat the boss")
        assert obj.completed is False

        obj.complete()

        assert obj.completed is True

    def test_reset_objective(self, load_system):
        """Test resetting an objective."""
        ns = load_system("quests")
        QuestObjective = ns["QuestObjective"]

        obj = QuestObjective("Collect items")
        obj.complete()
        assert obj.completed is True

        obj.reset()

        assert obj.completed is False

    def test_objective_repr(self, load_system):
        """Test objective string representation."""
        ns = load_system("quests")
        QuestObjective = ns["QuestObjective"]

        obj = QuestObjective("Test objective")
        assert "Test objective" in repr(obj)
        assert "pending" in repr(obj)

        obj.complete()
        assert "done" in repr(obj)

        optional_obj = QuestObjective("Optional task", optional=True)
        assert "optional" in repr(optional_obj)


class TestQuestRewards:
    """Tests for the QuestRewards class."""

    def test_create_rewards_defaults(self, load_system):
        """Test creating rewards with default values."""
        ns = load_system("quests")
        QuestRewards = ns["QuestRewards"]

        rewards = QuestRewards()

        assert rewards.gold == 0
        assert rewards.xp == 0
        assert rewards.items == []
        assert rewards.has_rewards() is False

    def test_create_rewards_with_values(self, load_system):
        """Test creating rewards with specified values."""
        ns = load_system("quests")
        QuestRewards = ns["QuestRewards"]

        rewards = QuestRewards(gold=100, xp=50, items=["sword", "shield"])

        assert rewards.gold == 100
        assert rewards.xp == 50
        assert rewards.items == ["sword", "shield"]
        assert rewards.has_rewards() is True

    def test_has_rewards_with_gold_only(self, load_system):
        """Test has_rewards with only gold."""
        ns = load_system("quests")
        QuestRewards = ns["QuestRewards"]

        rewards = QuestRewards(gold=50)

        assert rewards.has_rewards() is True

    def test_has_rewards_with_xp_only(self, load_system):
        """Test has_rewards with only XP."""
        ns = load_system("quests")
        QuestRewards = ns["QuestRewards"]

        rewards = QuestRewards(xp=100)

        assert rewards.has_rewards() is True

    def test_has_rewards_with_items_only(self, load_system):
        """Test has_rewards with only items."""
        ns = load_system("quests")
        QuestRewards = ns["QuestRewards"]

        rewards = QuestRewards(items=["potion"])

        assert rewards.has_rewards() is True

    def test_rewards_repr(self, load_system):
        """Test rewards string representation."""
        ns = load_system("quests")
        QuestRewards = ns["QuestRewards"]

        rewards = QuestRewards(gold=50, xp=25, items=["key"])
        repr_str = repr(rewards)

        assert "gold=50" in repr_str
        assert "xp=25" in repr_str
        assert "key" in repr_str


class TestQuest:
    """Tests for the Quest class."""

    def test_create_quest_defaults(self, load_system):
        """Test creating a quest with default values."""
        ns = load_system("quests")
        Quest = ns["Quest"]
        QUEST_STATUS_AVAILABLE = ns["QUEST_STATUS_AVAILABLE"]
        QUEST_CATEGORY_SIDE = ns["QUEST_CATEGORY_SIDE"]

        quest = Quest(
            id="test_quest",
            name="Test Quest",
            description="A test quest."
        )

        assert quest.id == "test_quest"
        assert quest.name == "Test Quest"
        assert quest.description == "A test quest."
        assert quest.objectives == []
        assert quest.status == QUEST_STATUS_AVAILABLE
        assert quest.category == QUEST_CATEGORY_SIDE

    def test_create_main_quest(self, load_system):
        """Test creating a main story quest."""
        ns = load_system("quests")
        Quest = ns["Quest"]
        QUEST_CATEGORY_MAIN = ns["QUEST_CATEGORY_MAIN"]

        quest = Quest(
            id="main_01",
            name="Main Story",
            description="The main story quest.",
            category=QUEST_CATEGORY_MAIN
        )

        assert quest.category == QUEST_CATEGORY_MAIN
        assert quest.is_main_quest() is True
        assert quest.is_side_quest() is False

    def test_create_side_quest(self, load_system):
        """Test creating a side quest."""
        ns = load_system("quests")
        Quest = ns["Quest"]
        QUEST_CATEGORY_SIDE = ns["QUEST_CATEGORY_SIDE"]

        quest = Quest(
            id="side_01",
            name="Side Quest",
            description="An optional side quest.",
            category=QUEST_CATEGORY_SIDE
        )

        assert quest.category == QUEST_CATEGORY_SIDE
        assert quest.is_side_quest() is True
        assert quest.is_main_quest() is False

    def test_add_objective(self, load_system):
        """Test adding objectives to a quest."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test", description="Test")
        obj1 = quest.add_objective("First objective")
        obj2 = quest.add_objective("Optional objective", optional=True)

        assert len(quest.objectives) == 2
        assert obj1.description == "First objective"
        assert obj1.optional is False
        assert obj2.description == "Optional objective"
        assert obj2.optional is True

    def test_complete_objective_by_index(self, load_system):
        """Test completing objectives by index."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test", description="Test")
        quest.add_objective("Objective 1")
        quest.add_objective("Objective 2")

        result = quest.complete_objective(0)

        assert result is True
        assert quest.objectives[0].completed is True
        assert quest.objectives[1].completed is False

    def test_complete_objective_invalid_index(self, load_system):
        """Test completing objective with invalid index."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test", description="Test")
        quest.add_objective("Only objective")

        result = quest.complete_objective(5)

        assert result is False

    def test_get_required_objectives(self, load_system):
        """Test getting non-optional objectives."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test", description="Test")
        quest.add_objective("Required 1")
        quest.add_objective("Optional 1", optional=True)
        quest.add_objective("Required 2")

        required = quest.get_required_objectives()

        assert len(required) == 2
        assert all(not obj.optional for obj in required)

    def test_get_optional_objectives(self, load_system):
        """Test getting optional objectives."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test", description="Test")
        quest.add_objective("Required")
        quest.add_objective("Optional 1", optional=True)
        quest.add_objective("Optional 2", optional=True)

        optional = quest.get_optional_objectives()

        assert len(optional) == 2
        assert all(obj.optional for obj in optional)

    def test_are_required_objectives_complete(self, load_system):
        """Test checking if all required objectives are complete."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test", description="Test")
        quest.add_objective("Required 1")
        quest.add_objective("Optional", optional=True)
        quest.add_objective("Required 2")

        assert quest.are_required_objectives_complete() is False

        quest.complete_objective(0)
        assert quest.are_required_objectives_complete() is False

        quest.complete_objective(2)
        assert quest.are_required_objectives_complete() is True

    def test_are_required_objectives_complete_no_objectives(self, load_system):
        """Test checking completion with no objectives."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test", description="Test")

        assert quest.are_required_objectives_complete() is True

    def test_get_progress(self, load_system):
        """Test getting quest progress."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test", description="Test")
        quest.add_objective("Objective 1")
        quest.add_objective("Objective 2")
        quest.add_objective("Optional", optional=True)

        completed, total, percentage = quest.get_progress()
        assert completed == 0
        assert total == 2  # Only required objectives
        assert percentage == 0.0

        quest.complete_objective(0)
        completed, total, percentage = quest.get_progress()
        assert completed == 1
        assert total == 2
        assert percentage == 50.0

        quest.complete_objective(1)
        completed, total, percentage = quest.get_progress()
        assert completed == 2
        assert total == 2
        assert percentage == 100.0

    def test_get_progress_no_objectives(self, load_system):
        """Test progress with no objectives."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test", description="Test")

        completed, total, percentage = quest.get_progress()
        assert completed == 0
        assert total == 0
        assert percentage == 100.0

    def test_quest_status_methods(self, load_system):
        """Test quest status check methods."""
        ns = load_system("quests")
        Quest = ns["Quest"]
        QUEST_STATUS_AVAILABLE = ns["QUEST_STATUS_AVAILABLE"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]
        QUEST_STATUS_COMPLETED = ns["QUEST_STATUS_COMPLETED"]
        QUEST_STATUS_FAILED = ns["QUEST_STATUS_FAILED"]

        quest = Quest(id="test", name="Test", description="Test")

        assert quest.is_available() is True
        assert quest.is_active() is False
        assert quest.is_completed() is False
        assert quest.is_failed() is False

        quest.status = QUEST_STATUS_ACTIVE
        assert quest.is_available() is False
        assert quest.is_active() is True

        quest.status = QUEST_STATUS_COMPLETED
        assert quest.is_completed() is True

        quest.status = QUEST_STATUS_FAILED
        assert quest.is_failed() is True

    def test_quest_with_rewards(self, load_system):
        """Test quest with rewards."""
        ns = load_system("quests")
        Quest = ns["Quest"]
        QuestRewards = ns["QuestRewards"]

        rewards = QuestRewards(gold=100, xp=50, items=["sword"])
        quest = Quest(
            id="rewarded",
            name="Rewarded Quest",
            description="Has rewards",
            rewards=rewards
        )

        assert quest.rewards.gold == 100
        assert quest.rewards.xp == 50
        assert "sword" in quest.rewards.items

    def test_quest_repr(self, load_system):
        """Test quest string representation."""
        ns = load_system("quests")
        Quest = ns["Quest"]

        quest = Quest(id="test", name="Test Quest", description="Test")
        repr_str = repr(quest)

        assert "test" in repr_str
        assert "Test Quest" in repr_str
        assert "available" in repr_str


class TestQuestManager:
    """Tests for the QuestManager class."""

    def test_create_manager(self, load_system):
        """Test creating a quest manager."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]

        manager = QuestManager()

        assert manager.quests == {}

    def test_add_quest(self, load_system):
        """Test adding a quest to the manager."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()
        quest = Quest(id="test", name="Test", description="Test")

        result = manager.add_quest(quest)

        assert result is quest
        assert "test" in manager.quests
        assert manager.quests["test"] is quest

    def test_create_quest(self, load_system):
        """Test creating a quest through the manager."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        QuestRewards = ns["QuestRewards"]
        QUEST_CATEGORY_MAIN = ns["QUEST_CATEGORY_MAIN"]

        manager = QuestManager()
        rewards = QuestRewards(gold=100)

        quest = manager.create_quest(
            id="created",
            name="Created Quest",
            description="Manager created",
            category=QUEST_CATEGORY_MAIN,
            rewards=rewards
        )

        assert quest.id == "created"
        assert quest.name == "Created Quest"
        assert quest.category == QUEST_CATEGORY_MAIN
        assert quest.rewards.gold == 100
        assert "created" in manager.quests

    def test_get_quest(self, load_system):
        """Test getting a quest by ID."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()
        quest = Quest(id="findme", name="Find Me", description="Test")
        manager.add_quest(quest)

        result = manager.get_quest("findme")
        assert result is quest

        not_found = manager.get_quest("nonexistent")
        assert not_found is None

    def test_remove_quest(self, load_system):
        """Test removing a quest."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()
        quest = Quest(id="removeme", name="Remove Me", description="Test")
        manager.add_quest(quest)

        result = manager.remove_quest("removeme")

        assert result is True
        assert "removeme" not in manager.quests

        result = manager.remove_quest("nonexistent")
        assert result is False

    def test_start_quest(self, load_system):
        """Test starting a quest."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]

        manager = QuestManager()
        quest = Quest(id="start", name="Start Quest", description="Test")
        manager.add_quest(quest)

        result = manager.start_quest("start")

        assert result is True
        assert quest.status == QUEST_STATUS_ACTIVE

    def test_start_quest_not_available(self, load_system):
        """Test starting a quest that's not available."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]

        manager = QuestManager()
        quest = Quest(id="active", name="Active", description="Test",
                      status=QUEST_STATUS_ACTIVE)
        manager.add_quest(quest)

        result = manager.start_quest("active")

        assert result is False

    def test_complete_quest(self, load_system):
        """Test completing a quest."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QuestRewards = ns["QuestRewards"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]
        QUEST_STATUS_COMPLETED = ns["QUEST_STATUS_COMPLETED"]

        manager = QuestManager()
        rewards = QuestRewards(gold=50, xp=100)
        quest = Quest(id="complete", name="Complete", description="Test",
                      status=QUEST_STATUS_ACTIVE, rewards=rewards)
        manager.add_quest(quest)

        result = manager.complete_quest("complete")

        assert result is rewards
        assert quest.status == QUEST_STATUS_COMPLETED

    def test_complete_quest_not_active(self, load_system):
        """Test completing a quest that's not active."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()
        quest = Quest(id="notactive", name="Not Active", description="Test")
        manager.add_quest(quest)

        result = manager.complete_quest("notactive")

        assert result is None

    def test_fail_quest(self, load_system):
        """Test failing a quest."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]
        QUEST_STATUS_FAILED = ns["QUEST_STATUS_FAILED"]

        manager = QuestManager()
        quest = Quest(id="fail", name="Fail Quest", description="Test",
                      status=QUEST_STATUS_ACTIVE)
        manager.add_quest(quest)

        result = manager.fail_quest("fail")

        assert result is True
        assert quest.status == QUEST_STATUS_FAILED

    def test_fail_quest_not_active(self, load_system):
        """Test failing a quest that's not active."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()
        quest = Quest(id="notactive", name="Not Active", description="Test")
        manager.add_quest(quest)

        result = manager.fail_quest("notactive")

        assert result is False

    def test_reset_quest(self, load_system):
        """Test resetting a quest."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_COMPLETED = ns["QUEST_STATUS_COMPLETED"]
        QUEST_STATUS_AVAILABLE = ns["QUEST_STATUS_AVAILABLE"]

        manager = QuestManager()
        quest = Quest(id="reset", name="Reset Quest", description="Test",
                      status=QUEST_STATUS_COMPLETED)
        quest.add_objective("Objective 1")
        quest.complete_objective(0)
        manager.add_quest(quest)

        result = manager.reset_quest("reset")

        assert result is True
        assert quest.status == QUEST_STATUS_AVAILABLE
        assert quest.objectives[0].completed is False

    def test_get_quests_by_status(self, load_system):
        """Test getting quests by status."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_AVAILABLE = ns["QUEST_STATUS_AVAILABLE"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]
        QUEST_STATUS_COMPLETED = ns["QUEST_STATUS_COMPLETED"]

        manager = QuestManager()
        manager.add_quest(Quest(id="avail1", name="Available 1", description="Test"))
        manager.add_quest(Quest(id="avail2", name="Available 2", description="Test"))
        manager.add_quest(Quest(id="active1", name="Active 1", description="Test",
                                status=QUEST_STATUS_ACTIVE))
        manager.add_quest(Quest(id="complete1", name="Complete 1", description="Test",
                                status=QUEST_STATUS_COMPLETED))

        available = manager.get_quests_by_status(QUEST_STATUS_AVAILABLE)
        active = manager.get_quests_by_status(QUEST_STATUS_ACTIVE)
        completed = manager.get_quests_by_status(QUEST_STATUS_COMPLETED)

        assert len(available) == 2
        assert len(active) == 1
        assert len(completed) == 1

    def test_get_active_quests(self, load_system):
        """Test getting active quests."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]

        manager = QuestManager()
        manager.add_quest(Quest(id="avail", name="Available", description="Test"))
        manager.add_quest(Quest(id="active", name="Active", description="Test",
                                status=QUEST_STATUS_ACTIVE))

        active = manager.get_active_quests()

        assert len(active) == 1
        assert active[0].id == "active"

    def test_get_quests_by_category(self, load_system):
        """Test getting quests by category."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_CATEGORY_MAIN = ns["QUEST_CATEGORY_MAIN"]
        QUEST_CATEGORY_SIDE = ns["QUEST_CATEGORY_SIDE"]

        manager = QuestManager()
        manager.add_quest(Quest(id="main1", name="Main 1", description="Test",
                                category=QUEST_CATEGORY_MAIN))
        manager.add_quest(Quest(id="main2", name="Main 2", description="Test",
                                category=QUEST_CATEGORY_MAIN))
        manager.add_quest(Quest(id="side1", name="Side 1", description="Test",
                                category=QUEST_CATEGORY_SIDE))

        main_quests = manager.get_main_quests()
        side_quests = manager.get_side_quests()

        assert len(main_quests) == 2
        assert len(side_quests) == 1

    def test_get_active_main_and_side_quests(self, load_system):
        """Test getting active main and side quests."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_CATEGORY_MAIN = ns["QUEST_CATEGORY_MAIN"]
        QUEST_CATEGORY_SIDE = ns["QUEST_CATEGORY_SIDE"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]

        manager = QuestManager()
        manager.add_quest(Quest(id="main1", name="Main Active", description="Test",
                                category=QUEST_CATEGORY_MAIN, status=QUEST_STATUS_ACTIVE))
        manager.add_quest(Quest(id="main2", name="Main Available", description="Test",
                                category=QUEST_CATEGORY_MAIN))
        manager.add_quest(Quest(id="side1", name="Side Active", description="Test",
                                category=QUEST_CATEGORY_SIDE, status=QUEST_STATUS_ACTIVE))

        active_main = manager.get_active_main_quests()
        active_side = manager.get_active_side_quests()

        assert len(active_main) == 1
        assert active_main[0].id == "main1"
        assert len(active_side) == 1
        assert active_side[0].id == "side1"

    def test_complete_objective(self, load_system):
        """Test completing objective through manager."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]

        manager = QuestManager()
        quest = Quest(id="obj_test", name="Objective Test", description="Test",
                      status=QUEST_STATUS_ACTIVE)
        quest.add_objective("First objective")
        quest.add_objective("Second objective")
        manager.add_quest(quest)

        result = manager.complete_objective("obj_test", 0)

        assert result is True
        assert quest.objectives[0].completed is True

    def test_complete_objective_not_active(self, load_system):
        """Test completing objective on inactive quest."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()
        quest = Quest(id="inactive", name="Inactive", description="Test")
        quest.add_objective("Objective")
        manager.add_quest(quest)

        result = manager.complete_objective("inactive", 0)

        assert result is False

    def test_add_objective_to_quest(self, load_system):
        """Test adding objective through manager."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()
        quest = Quest(id="add_obj", name="Add Objective", description="Test")
        manager.add_quest(quest)

        obj = manager.add_objective("add_obj", "New objective", optional=True)

        assert obj is not None
        assert len(quest.objectives) == 1
        assert quest.objectives[0].description == "New objective"
        assert quest.objectives[0].optional is True

    def test_add_objective_quest_not_found(self, load_system):
        """Test adding objective to nonexistent quest."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]

        manager = QuestManager()

        result = manager.add_objective("nonexistent", "Objective")

        assert result is None

    def test_get_quest_progress(self, load_system):
        """Test getting quest progress through manager."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()
        quest = Quest(id="progress", name="Progress", description="Test")
        quest.add_objective("Obj 1")
        quest.add_objective("Obj 2")
        quest.complete_objective(0)
        manager.add_quest(quest)

        result = manager.get_quest_progress("progress")

        assert result == (1, 2, 50.0)

    def test_get_quest_progress_not_found(self, load_system):
        """Test getting progress for nonexistent quest."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]

        manager = QuestManager()

        result = manager.get_quest_progress("nonexistent")

        assert result is None

    def test_check_quest_completable(self, load_system):
        """Test checking if quest can be completed."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]

        manager = QuestManager()
        quest = Quest(id="completable", name="Completable", description="Test",
                      status=QUEST_STATUS_ACTIVE)
        quest.add_objective("Required")
        quest.add_objective("Optional", optional=True)
        manager.add_quest(quest)

        assert manager.check_quest_completable("completable") is False

        quest.complete_objective(0)

        assert manager.check_quest_completable("completable") is True

    def test_get_stats(self, load_system):
        """Test getting quest statistics."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_CATEGORY_MAIN = ns["QUEST_CATEGORY_MAIN"]
        QUEST_CATEGORY_SIDE = ns["QUEST_CATEGORY_SIDE"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]
        QUEST_STATUS_COMPLETED = ns["QUEST_STATUS_COMPLETED"]
        QUEST_STATUS_FAILED = ns["QUEST_STATUS_FAILED"]

        manager = QuestManager()
        manager.add_quest(Quest(id="main1", name="Main 1", description="Test",
                                category=QUEST_CATEGORY_MAIN))
        manager.add_quest(Quest(id="main2", name="Main 2", description="Test",
                                category=QUEST_CATEGORY_MAIN, status=QUEST_STATUS_ACTIVE))
        manager.add_quest(Quest(id="side1", name="Side 1", description="Test",
                                category=QUEST_CATEGORY_SIDE, status=QUEST_STATUS_COMPLETED))
        manager.add_quest(Quest(id="side2", name="Side 2", description="Test",
                                category=QUEST_CATEGORY_SIDE, status=QUEST_STATUS_FAILED))

        stats = manager.get_stats()

        assert stats["total"] == 4
        assert stats["active"] == 1
        assert stats["completed"] == 1
        assert stats["failed"] == 1
        assert stats["available"] == 1
        assert stats["main_quests"] == 2
        assert stats["side_quests"] == 2

    def test_quest_complete_callback(self, load_system):
        """Test quest completion callback."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]

        manager = QuestManager()
        completed_quests = []

        def on_complete(quest):
            completed_quests.append(quest.id)

        manager.on_quest_complete(on_complete)

        quest = Quest(id="callback", name="Callback Test", description="Test",
                      status=QUEST_STATUS_ACTIVE)
        manager.add_quest(quest)
        manager.complete_quest("callback")

        assert "callback" in completed_quests

    def test_quest_fail_callback(self, load_system):
        """Test quest failure callback."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]

        manager = QuestManager()
        failed_quests = []

        def on_fail(quest):
            failed_quests.append(quest.id)

        manager.on_quest_fail(on_fail)

        quest = Quest(id="fail_callback", name="Fail Callback", description="Test",
                      status=QUEST_STATUS_ACTIVE)
        manager.add_quest(quest)
        manager.fail_quest("fail_callback")

        assert "fail_callback" in failed_quests

    def test_get_all_quests(self, load_system):
        """Test getting all quests."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()
        manager.add_quest(Quest(id="q1", name="Quest 1", description="Test"))
        manager.add_quest(Quest(id="q2", name="Quest 2", description="Test"))
        manager.add_quest(Quest(id="q3", name="Quest 3", description="Test"))

        all_quests = manager.get_all_quests()

        assert len(all_quests) == 3

    def test_get_completed_quests(self, load_system):
        """Test getting completed quests."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_COMPLETED = ns["QUEST_STATUS_COMPLETED"]

        manager = QuestManager()
        manager.add_quest(Quest(id="done1", name="Done 1", description="Test",
                                status=QUEST_STATUS_COMPLETED))
        manager.add_quest(Quest(id="done2", name="Done 2", description="Test",
                                status=QUEST_STATUS_COMPLETED))
        manager.add_quest(Quest(id="pending", name="Pending", description="Test"))

        completed = manager.get_completed_quests()

        assert len(completed) == 2
        assert all(q.is_completed() for q in completed)

    def test_get_failed_quests(self, load_system):
        """Test getting failed quests."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_FAILED = ns["QUEST_STATUS_FAILED"]

        manager = QuestManager()
        manager.add_quest(Quest(id="failed1", name="Failed 1", description="Test",
                                status=QUEST_STATUS_FAILED))
        manager.add_quest(Quest(id="active", name="Active", description="Test"))

        failed = manager.get_failed_quests()

        assert len(failed) == 1
        assert failed[0].id == "failed1"

    def test_get_available_quests(self, load_system):
        """Test getting available quests."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_STATUS_ACTIVE = ns["QUEST_STATUS_ACTIVE"]

        manager = QuestManager()
        manager.add_quest(Quest(id="avail", name="Available", description="Test"))
        manager.add_quest(Quest(id="active", name="Active", description="Test",
                                status=QUEST_STATUS_ACTIVE))

        available = manager.get_available_quests()

        assert len(available) == 1
        assert available[0].id == "avail"


class TestQuestIntegration:
    """Integration tests for the quest system."""

    def test_full_quest_workflow(self, load_system):
        """Test a complete quest workflow from start to finish."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QuestRewards = ns["QuestRewards"]
        QUEST_CATEGORY_MAIN = ns["QUEST_CATEGORY_MAIN"]

        manager = QuestManager()

        # Create quest with objectives and rewards
        rewards = QuestRewards(gold=100, xp=50, items=["legendary_sword"])
        quest = Quest(
            id="hero_journey",
            name="The Hero's Journey",
            description="Complete the epic quest to save the kingdom.",
            category=QUEST_CATEGORY_MAIN,
            rewards=rewards
        )
        quest.add_objective("Find the ancient map")
        quest.add_objective("Traverse the Dark Forest")
        quest.add_objective("Defeat the Dragon")
        quest.add_objective("Collect dragon scales", optional=True)

        manager.add_quest(quest)

        # Quest should be available
        assert quest.is_available()
        assert len(manager.get_available_quests()) == 1

        # Start the quest
        assert manager.start_quest("hero_journey") is True
        assert quest.is_active()
        assert len(manager.get_active_main_quests()) == 1

        # Complete objectives one by one
        manager.complete_objective("hero_journey", 0)
        completed, total, pct = quest.get_progress()
        assert completed == 1
        assert total == 3

        manager.complete_objective("hero_journey", 1)
        manager.complete_objective("hero_journey", 2)

        # Check quest is completable
        assert manager.check_quest_completable("hero_journey") is True

        # Complete the quest
        returned_rewards = manager.complete_quest("hero_journey")
        assert returned_rewards is rewards
        assert quest.is_completed()
        assert len(manager.get_completed_quests()) == 1

    def test_quest_failure_workflow(self, load_system):
        """Test quest failure workflow."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_CATEGORY_SIDE = ns["QUEST_CATEGORY_SIDE"]

        manager = QuestManager()

        quest = Quest(
            id="timed_quest",
            name="Race Against Time",
            description="Complete before time runs out!",
            category=QUEST_CATEGORY_SIDE
        )
        quest.add_objective("Reach the destination")

        manager.add_quest(quest)
        manager.start_quest("timed_quest")

        # Quest fails (time ran out)
        assert manager.fail_quest("timed_quest") is True
        assert quest.is_failed()
        assert len(manager.get_failed_quests()) == 1

    def test_quest_reset_and_retry(self, load_system):
        """Test resetting and retrying a failed quest."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()

        quest = Quest(id="retry", name="Retry Quest", description="Can be retried")
        quest.add_objective("Complete the challenge")
        manager.add_quest(quest)

        # Start and fail
        manager.start_quest("retry")
        manager.complete_objective("retry", 0)
        manager.fail_quest("retry")

        assert quest.is_failed()
        assert quest.objectives[0].completed is True

        # Reset and retry
        manager.reset_quest("retry")

        assert quest.is_available()
        assert quest.objectives[0].completed is False

        # Start again
        manager.start_quest("retry")
        assert quest.is_active()

    def test_multiple_active_quests(self, load_system):
        """Test managing multiple active quests."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]
        QUEST_CATEGORY_MAIN = ns["QUEST_CATEGORY_MAIN"]
        QUEST_CATEGORY_SIDE = ns["QUEST_CATEGORY_SIDE"]

        manager = QuestManager()

        # Add multiple quests
        main_quest = Quest(
            id="main",
            name="Main Quest",
            description="The main story",
            category=QUEST_CATEGORY_MAIN
        )
        main_quest.add_objective("Main objective")

        side1 = Quest(
            id="side1",
            name="Side Quest 1",
            description="First side quest",
            category=QUEST_CATEGORY_SIDE
        )
        side1.add_objective("Side 1 objective")

        side2 = Quest(
            id="side2",
            name="Side Quest 2",
            description="Second side quest",
            category=QUEST_CATEGORY_SIDE
        )
        side2.add_objective("Side 2 objective")

        manager.add_quest(main_quest)
        manager.add_quest(side1)
        manager.add_quest(side2)

        # Start all quests
        manager.start_quest("main")
        manager.start_quest("side1")
        manager.start_quest("side2")

        assert len(manager.get_active_quests()) == 3
        assert len(manager.get_active_main_quests()) == 1
        assert len(manager.get_active_side_quests()) == 2

        # Complete side quests while main is still active
        manager.complete_objective("side1", 0)
        manager.complete_quest("side1")
        manager.complete_objective("side2", 0)
        manager.complete_quest("side2")

        assert len(manager.get_active_quests()) == 1
        assert len(manager.get_completed_quests()) == 2
        assert main_quest.is_active()

    def test_optional_objectives_dont_block_completion(self, load_system):
        """Test that optional objectives don't prevent quest completion."""
        ns = load_system("quests")
        QuestManager = ns["QuestManager"]
        Quest = ns["Quest"]

        manager = QuestManager()

        quest = Quest(id="optional_test", name="Optional Test", description="Test")
        quest.add_objective("Required objective")
        quest.add_objective("Optional bonus", optional=True)
        quest.add_objective("Another optional", optional=True)

        manager.add_quest(quest)
        manager.start_quest("optional_test")

        # Complete only required objective
        manager.complete_objective("optional_test", 0)

        # Quest should be completable even without optional objectives
        assert manager.check_quest_completable("optional_test") is True

        # Complete quest
        manager.complete_quest("optional_test")
        assert quest.is_completed()

        # Optional objectives still incomplete
        assert quest.objectives[1].completed is False
        assert quest.objectives[2].completed is False

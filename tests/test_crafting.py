"""
Comprehensive tests for the Crafting System.

Tests cover:
- Recipe class functionality
- CraftingManager class operations
- Recipe registration and management
- Crafting operations (can_craft, craft, craft_multiple)
- Recipe discovery/unlocking
- Inventory integration
- Edge cases and error handling
"""
import pytest
from pathlib import Path


class TestRecipe:
    """Tests for the Recipe class."""

    @pytest.fixture
    def load_crafting(self, load_system):
        """Load the crafting system."""
        return load_system("crafting")

    def test_recipe_creation_basic(self, load_crafting):
        """Test basic recipe creation with required fields."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="test_recipe",
            name="Test Recipe",
            ingredients={"wood": 2, "stone": 1},
            result_item="test_item"
        )

        assert recipe.id == "test_recipe"
        assert recipe.name == "Test Recipe"
        assert recipe.ingredients == {"wood": 2, "stone": 1}
        assert recipe.result_item == "test_item"
        assert recipe.result_quantity == 1  # default
        assert recipe.unlocked is True  # no unlock_condition means auto-unlocked
        assert recipe.category == "misc"  # default

    def test_recipe_creation_full(self, load_crafting):
        """Test recipe creation with all fields."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="full_recipe",
            name="Full Recipe",
            ingredients={"iron": 3, "coal": 2},
            result_item="iron_sword",
            result_quantity=1,
            unlock_condition="learned_smithing",
            description="A powerful sword.",
            category="weapons"
        )

        assert recipe.id == "full_recipe"
        assert recipe.name == "Full Recipe"
        assert recipe.ingredients == {"iron": 3, "coal": 2}
        assert recipe.result_item == "iron_sword"
        assert recipe.result_quantity == 1
        assert recipe.unlock_condition == "learned_smithing"
        assert recipe.description == "A powerful sword."
        assert recipe.category == "weapons"
        assert recipe.unlocked is False  # has unlock_condition

    def test_recipe_result_quantity(self, load_crafting):
        """Test recipe with multiple result items."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="bulk_recipe",
            name="Bulk Recipe",
            ingredients={"cloth": 3},
            result_item="bandage",
            result_quantity=5
        )

        assert recipe.result_quantity == 5

    def test_recipe_get_ingredients_list(self, load_crafting):
        """Test getting ingredients as list of tuples."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="test",
            name="Test",
            ingredients={"wood": 2, "stone": 1, "iron": 3},
            result_item="item"
        )

        ingredients_list = recipe.get_ingredients_list()
        assert isinstance(ingredients_list, list)
        assert len(ingredients_list) == 3
        assert ("wood", 2) in ingredients_list
        assert ("stone", 1) in ingredients_list
        assert ("iron", 3) in ingredients_list

    def test_recipe_repr(self, load_crafting):
        """Test recipe string representation."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="repr_test",
            name="Repr Test",
            ingredients={},
            result_item="item"
        )

        assert "repr_test" in repr(recipe)
        assert "Repr Test" in repr(recipe)


class TestCraftingManagerBasic:
    """Tests for basic CraftingManager functionality."""

    @pytest.fixture
    def load_crafting(self, load_system):
        """Load the crafting system."""
        return load_system("crafting")

    @pytest.fixture
    def manager(self, load_crafting):
        """Create a fresh CraftingManager instance."""
        CraftingManager = load_crafting["CraftingManager"]
        return CraftingManager()

    @pytest.fixture
    def sample_recipe(self, load_crafting):
        """Create a sample recipe."""
        Recipe = load_crafting["Recipe"]
        return Recipe(
            id="health_potion",
            name="Health Potion",
            ingredients={"herb": 2, "water": 1},
            result_item="health_potion",
            result_quantity=1,
            description="Restores health.",
            category="potions"
        )

    def test_manager_creation(self, manager):
        """Test CraftingManager initialization."""
        assert manager.recipes == {}
        assert manager._inventory_getter is None

    def test_register_recipe(self, manager, sample_recipe):
        """Test registering a single recipe."""
        result = manager.register_recipe(sample_recipe)

        assert result == sample_recipe
        assert "health_potion" in manager.recipes
        assert manager.recipes["health_potion"] == sample_recipe

    def test_register_multiple_recipes(self, manager, load_crafting):
        """Test registering multiple recipes at once."""
        Recipe = load_crafting["Recipe"]

        recipes = [
            Recipe(id="r1", name="R1", ingredients={}, result_item="i1"),
            Recipe(id="r2", name="R2", ingredients={}, result_item="i2"),
            Recipe(id="r3", name="R3", ingredients={}, result_item="i3"),
        ]

        result = manager.register_recipes(recipes)

        assert len(result) == 3
        assert "r1" in manager.recipes
        assert "r2" in manager.recipes
        assert "r3" in manager.recipes

    def test_get_recipe(self, manager, sample_recipe):
        """Test retrieving a recipe by ID."""
        manager.register_recipe(sample_recipe)

        result = manager.get_recipe("health_potion")
        assert result == sample_recipe

    def test_get_recipe_not_found(self, manager):
        """Test retrieving non-existent recipe."""
        result = manager.get_recipe("nonexistent")
        assert result is None

    def test_remove_recipe(self, manager, sample_recipe):
        """Test removing a recipe."""
        manager.register_recipe(sample_recipe)
        assert "health_potion" in manager.recipes

        result = manager.remove_recipe("health_potion")
        assert result is True
        assert "health_potion" not in manager.recipes

    def test_remove_recipe_not_found(self, manager):
        """Test removing non-existent recipe."""
        result = manager.remove_recipe("nonexistent")
        assert result is False

    def test_get_all_recipes(self, manager, load_crafting):
        """Test getting all recipes."""
        Recipe = load_crafting["Recipe"]

        r1 = Recipe(id="r1", name="R1", ingredients={}, result_item="i1")
        r2 = Recipe(id="r2", name="R2", ingredients={}, result_item="i2")

        manager.register_recipe(r1)
        manager.register_recipe(r2)

        all_recipes = manager.get_all_recipes()
        assert len(all_recipes) == 2
        assert r1 in all_recipes
        assert r2 in all_recipes

    def test_get_recipes_by_category(self, manager, load_crafting):
        """Test filtering recipes by category."""
        Recipe = load_crafting["Recipe"]

        r1 = Recipe(id="r1", name="R1", ingredients={}, result_item="i1", category="weapons")
        r2 = Recipe(id="r2", name="R2", ingredients={}, result_item="i2", category="potions")
        r3 = Recipe(id="r3", name="R3", ingredients={}, result_item="i3", category="weapons")

        manager.register_recipes([r1, r2, r3])

        weapons = manager.get_recipes_by_category("weapons")
        assert len(weapons) == 2
        assert r1 in weapons
        assert r3 in weapons
        assert r2 not in weapons

    def test_get_categories(self, manager, load_crafting):
        """Test getting all unique categories."""
        Recipe = load_crafting["Recipe"]

        r1 = Recipe(id="r1", name="R1", ingredients={}, result_item="i1", category="weapons")
        r2 = Recipe(id="r2", name="R2", ingredients={}, result_item="i2", category="potions")
        r3 = Recipe(id="r3", name="R3", ingredients={}, result_item="i3", category="weapons")

        manager.register_recipes([r1, r2, r3])

        categories = manager.get_categories()
        assert len(categories) == 2
        assert "weapons" in categories
        assert "potions" in categories


class TestRecipeUnlocking:
    """Tests for recipe unlocking/discovery system."""

    @pytest.fixture
    def load_crafting(self, load_system):
        """Load the crafting system."""
        return load_system("crafting")

    @pytest.fixture
    def manager(self, load_crafting):
        """Create a fresh CraftingManager instance."""
        CraftingManager = load_crafting["CraftingManager"]
        return CraftingManager()

    def test_recipe_auto_unlock_no_condition(self, load_crafting, manager):
        """Test that recipes without unlock_condition are auto-unlocked."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="basic",
            name="Basic",
            ingredients={},
            result_item="item",
            unlock_condition=None
        )
        manager.register_recipe(recipe)

        assert recipe.unlocked is True
        assert manager.is_recipe_unlocked("basic") is True

    def test_recipe_locked_with_condition(self, load_crafting, manager):
        """Test that recipes with unlock_condition start locked."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="advanced",
            name="Advanced",
            ingredients={},
            result_item="item",
            unlock_condition="learned_skill"
        )
        manager.register_recipe(recipe)

        assert recipe.unlocked is False
        assert manager.is_recipe_unlocked("advanced") is False

    def test_unlock_recipe(self, load_crafting, manager):
        """Test manually unlocking a recipe."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="locked",
            name="Locked",
            ingredients={},
            result_item="item",
            unlock_condition="some_condition"
        )
        manager.register_recipe(recipe)

        assert recipe.unlocked is False
        result = manager.unlock_recipe("locked")
        assert result is True
        assert recipe.unlocked is True

    def test_unlock_already_unlocked(self, load_crafting, manager):
        """Test unlocking an already unlocked recipe returns False."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="unlocked",
            name="Unlocked",
            ingredients={},
            result_item="item"
        )
        manager.register_recipe(recipe)

        result = manager.unlock_recipe("unlocked")
        assert result is False  # Already unlocked

    def test_unlock_nonexistent_recipe(self, manager):
        """Test unlocking non-existent recipe."""
        result = manager.unlock_recipe("nonexistent")
        assert result is False

    def test_lock_recipe(self, load_crafting, manager):
        """Test locking a recipe."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="to_lock",
            name="To Lock",
            ingredients={},
            result_item="item"
        )
        manager.register_recipe(recipe)

        assert recipe.unlocked is True
        result = manager.lock_recipe("to_lock")
        assert result is True
        assert recipe.unlocked is False

    def test_get_unlocked_recipes(self, load_crafting, manager):
        """Test getting all unlocked recipes."""
        Recipe = load_crafting["Recipe"]

        r1 = Recipe(id="r1", name="R1", ingredients={}, result_item="i1")
        r2 = Recipe(id="r2", name="R2", ingredients={}, result_item="i2", unlock_condition="cond")
        r3 = Recipe(id="r3", name="R3", ingredients={}, result_item="i3")

        manager.register_recipes([r1, r2, r3])

        unlocked = manager.get_unlocked_recipes()
        assert len(unlocked) == 2
        assert r1 in unlocked
        assert r3 in unlocked
        assert r2 not in unlocked

    def test_get_locked_recipes(self, load_crafting, manager):
        """Test getting all locked recipes."""
        Recipe = load_crafting["Recipe"]

        r1 = Recipe(id="r1", name="R1", ingredients={}, result_item="i1")
        r2 = Recipe(id="r2", name="R2", ingredients={}, result_item="i2", unlock_condition="cond")
        r3 = Recipe(id="r3", name="R3", ingredients={}, result_item="i3", unlock_condition="cond2")

        manager.register_recipes([r1, r2, r3])

        locked = manager.get_locked_recipes()
        assert len(locked) == 2
        assert r2 in locked
        assert r3 in locked
        assert r1 not in locked

    def test_check_unlock_conditions_string(self, load_crafting, manager):
        """Test checking unlock conditions with string flags."""
        Recipe = load_crafting["Recipe"]

        r1 = Recipe(id="r1", name="R1", ingredients={}, result_item="i1", unlock_condition="flag1")
        r2 = Recipe(id="r2", name="R2", ingredients={}, result_item="i2", unlock_condition="flag2")

        manager.register_recipes([r1, r2])

        # Neither should be unlocked yet
        assert r1.unlocked is False
        assert r2.unlocked is False

        # Check with context containing flag1
        newly_unlocked = manager.check_unlock_conditions({"flag1": True})

        assert "r1" in newly_unlocked
        assert "r2" not in newly_unlocked
        assert r1.unlocked is True
        assert r2.unlocked is False

    def test_check_unlock_conditions_callable(self, load_crafting, manager):
        """Test checking unlock conditions with callable."""
        Recipe = load_crafting["Recipe"]

        def check_level(context):
            return context and context.get("level", 0) >= 5

        recipe = Recipe(
            id="level_locked",
            name="Level Locked",
            ingredients={},
            result_item="item",
            unlock_condition=check_level
        )
        manager.register_recipe(recipe)

        # Level too low
        unlocked = manager.check_unlock_conditions({"level": 3})
        assert len(unlocked) == 0
        assert recipe.unlocked is False

        # Level high enough
        unlocked = manager.check_unlock_conditions({"level": 5})
        assert "level_locked" in unlocked
        assert recipe.unlocked is True


class TestInventoryIntegration:
    """Tests for inventory integration with CraftingManager."""

    @pytest.fixture
    def load_crafting(self, load_system):
        """Load the crafting system."""
        return load_system("crafting")

    @pytest.fixture
    def manager_with_inventory(self, load_crafting):
        """Create a CraftingManager with mock inventory."""
        CraftingManager = load_crafting["CraftingManager"]
        manager = CraftingManager()

        # Create a simple mock inventory
        inventory = {"herb": 10, "water": 5, "wood": 3}

        def get_inv():
            return inventory

        def set_inv(new_inv):
            nonlocal inventory
            inventory = new_inv

        def add_item(item_id, qty):
            inventory[item_id] = inventory.get(item_id, 0) + qty

        def remove_item(item_id, qty):
            if inventory.get(item_id, 0) >= qty:
                inventory[item_id] -= qty
                if inventory[item_id] == 0:
                    del inventory[item_id]
                return True
            return False

        manager.set_inventory_callbacks(get_inv, set_inv, add_item, remove_item)
        manager._test_inventory = inventory  # For test access
        return manager

    def test_set_inventory_callbacks(self, load_crafting):
        """Test setting inventory callbacks."""
        CraftingManager = load_crafting["CraftingManager"]
        manager = CraftingManager()

        def getter():
            return {}

        def setter(inv):
            pass

        manager.set_inventory_callbacks(getter, setter)

        assert manager._inventory_getter == getter
        assert manager._inventory_setter == setter

    def test_get_inventory(self, manager_with_inventory):
        """Test getting inventory through manager."""
        inv = manager_with_inventory.get_inventory()

        assert inv["herb"] == 10
        assert inv["water"] == 5
        assert inv["wood"] == 3

    def test_add_item(self, manager_with_inventory):
        """Test adding items through manager."""
        manager_with_inventory.add_item("stone", 5)
        inv = manager_with_inventory.get_inventory()

        assert inv["stone"] == 5

    def test_add_item_existing(self, manager_with_inventory):
        """Test adding to existing item quantity."""
        manager_with_inventory.add_item("herb", 5)
        inv = manager_with_inventory.get_inventory()

        assert inv["herb"] == 15  # 10 + 5

    def test_remove_item(self, manager_with_inventory):
        """Test removing items through manager."""
        manager_with_inventory.remove_item("herb", 3)
        inv = manager_with_inventory.get_inventory()

        assert inv["herb"] == 7  # 10 - 3

    def test_remove_item_completely(self, manager_with_inventory):
        """Test removing all of an item removes it from inventory."""
        manager_with_inventory.remove_item("wood", 3)
        inv = manager_with_inventory.get_inventory()

        assert "wood" not in inv


class TestCraftingOperations:
    """Tests for crafting operations."""

    @pytest.fixture
    def load_crafting(self, load_system):
        """Load the crafting system."""
        return load_system("crafting")

    @pytest.fixture
    def manager_with_inventory(self, load_crafting):
        """Create a CraftingManager with mock inventory and recipes."""
        CraftingManager = load_crafting["CraftingManager"]
        Recipe = load_crafting["Recipe"]
        manager = CraftingManager()

        # Create a simple mock inventory
        inventory = {"herb": 10, "water": 5, "cloth": 8}

        def get_inv():
            return inventory

        def set_inv(new_inv):
            nonlocal inventory
            inventory = new_inv

        def add_item(item_id, qty):
            inventory[item_id] = inventory.get(item_id, 0) + qty

        def remove_item(item_id, qty):
            if inventory.get(item_id, 0) >= qty:
                inventory[item_id] -= qty
                if inventory[item_id] == 0:
                    del inventory[item_id]
                return True
            return False

        manager.set_inventory_callbacks(get_inv, set_inv, add_item, remove_item)

        # Register test recipes
        manager.register_recipe(Recipe(
            id="health_potion",
            name="Health Potion",
            ingredients={"herb": 2, "water": 1},
            result_item="health_potion",
            result_quantity=1,
            category="potions"
        ))

        manager.register_recipe(Recipe(
            id="bandage",
            name="Bandage",
            ingredients={"cloth": 2},
            result_item="bandage",
            result_quantity=3,
            category="consumables"
        ))

        manager.register_recipe(Recipe(
            id="locked_recipe",
            name="Locked Recipe",
            ingredients={"herb": 1},
            result_item="special_item",
            unlock_condition="special_unlock"
        ))

        return manager

    def test_can_craft_true(self, manager_with_inventory):
        """Test can_craft returns True when materials available."""
        assert manager_with_inventory.can_craft("health_potion") is True

    def test_can_craft_false_no_materials(self, load_crafting, manager_with_inventory):
        """Test can_craft returns False when materials missing."""
        Recipe = load_crafting["Recipe"]

        manager_with_inventory.register_recipe(Recipe(
            id="iron_sword",
            name="Iron Sword",
            ingredients={"iron": 5},
            result_item="iron_sword"
        ))

        assert manager_with_inventory.can_craft("iron_sword") is False

    def test_can_craft_false_locked(self, manager_with_inventory):
        """Test can_craft returns False for locked recipes."""
        assert manager_with_inventory.can_craft("locked_recipe") is False

    def test_can_craft_false_nonexistent(self, manager_with_inventory):
        """Test can_craft returns False for non-existent recipes."""
        assert manager_with_inventory.can_craft("nonexistent") is False

    def test_get_missing_ingredients(self, load_crafting, manager_with_inventory):
        """Test getting missing ingredients."""
        Recipe = load_crafting["Recipe"]

        manager_with_inventory.register_recipe(Recipe(
            id="expensive",
            name="Expensive",
            ingredients={"herb": 15, "water": 10, "gold": 5},
            result_item="expensive_item"
        ))

        missing = manager_with_inventory.get_missing_ingredients("expensive")

        assert missing["herb"] == 5  # Need 15, have 10
        assert missing["water"] == 5  # Need 10, have 5
        assert missing["gold"] == 5  # Need 5, have 0

    def test_get_missing_ingredients_none(self, manager_with_inventory):
        """Test getting missing ingredients when can craft."""
        missing = manager_with_inventory.get_missing_ingredients("health_potion")
        assert missing == {}

    def test_craft_success(self, manager_with_inventory):
        """Test successful crafting."""
        success, message, result_item = manager_with_inventory.craft("health_potion")

        assert success is True
        assert "Crafted" in message
        assert result_item == "health_potion"

        # Check inventory was updated
        inv = manager_with_inventory.get_inventory()
        assert inv["herb"] == 8  # 10 - 2
        assert inv["water"] == 4  # 5 - 1
        assert inv["health_potion"] == 1

    def test_craft_multiple_results(self, manager_with_inventory):
        """Test crafting recipe with multiple result items."""
        success, message, result_item = manager_with_inventory.craft("bandage")

        assert success is True
        assert result_item == "bandage"

        inv = manager_with_inventory.get_inventory()
        assert inv["bandage"] == 3  # result_quantity = 3
        assert inv["cloth"] == 6  # 8 - 2

    def test_craft_fail_no_recipe(self, manager_with_inventory):
        """Test craft fails for non-existent recipe."""
        success, message, result_item = manager_with_inventory.craft("nonexistent")

        assert success is False
        assert "not found" in message.lower()
        assert result_item is None

    def test_craft_fail_locked(self, manager_with_inventory):
        """Test craft fails for locked recipe."""
        success, message, result_item = manager_with_inventory.craft("locked_recipe")

        assert success is False
        assert "locked" in message.lower()
        assert result_item is None

    def test_craft_fail_no_materials(self, load_crafting, manager_with_inventory):
        """Test craft fails when materials missing."""
        Recipe = load_crafting["Recipe"]

        manager_with_inventory.register_recipe(Recipe(
            id="impossible",
            name="Impossible",
            ingredients={"unobtanium": 100},
            result_item="impossible_item"
        ))

        success, message, result_item = manager_with_inventory.craft("impossible")

        assert success is False
        assert "Missing" in message
        assert result_item is None

    def test_craft_multiple(self, manager_with_inventory):
        """Test crafting multiple times."""
        # With 10 herb and 5 water, can make 5 health potions (limited by water)
        count, message = manager_with_inventory.craft_multiple("health_potion", 3)

        assert count == 3
        assert "3" in message

        inv = manager_with_inventory.get_inventory()
        assert inv["herb"] == 4  # 10 - (2*3)
        assert inv["water"] == 2  # 5 - (1*3)
        assert inv["health_potion"] == 3

    def test_craft_multiple_limited_by_materials(self, manager_with_inventory):
        """Test craft_multiple stops when materials run out."""
        # Try to craft 10, but can only make 5 (limited by water)
        count, message = manager_with_inventory.craft_multiple("health_potion", 10)

        assert count == 5  # Limited by water (5)

        inv = manager_with_inventory.get_inventory()
        assert "water" not in inv  # All used up
        assert inv["health_potion"] == 5

    def test_get_max_craftable(self, manager_with_inventory):
        """Test getting max craftable count."""
        # 10 herb / 2 = 5, 5 water / 1 = 5, min = 5
        max_count = manager_with_inventory.get_max_craftable("health_potion")
        assert max_count == 5

    def test_get_max_craftable_limited(self, manager_with_inventory):
        """Test max craftable limited by scarcest ingredient."""
        # cloth: 8, needs 2 per craft = 4 max
        max_count = manager_with_inventory.get_max_craftable("bandage")
        assert max_count == 4

    def test_get_max_craftable_zero(self, load_crafting, manager_with_inventory):
        """Test max craftable returns 0 when cannot craft."""
        Recipe = load_crafting["Recipe"]

        manager_with_inventory.register_recipe(Recipe(
            id="no_mats",
            name="No Materials",
            ingredients={"diamond": 1},
            result_item="item"
        ))

        max_count = manager_with_inventory.get_max_craftable("no_mats")
        assert max_count == 0

    def test_get_max_craftable_locked(self, manager_with_inventory):
        """Test max craftable returns 0 for locked recipe."""
        max_count = manager_with_inventory.get_max_craftable("locked_recipe")
        assert max_count == 0

    def test_get_available_recipes(self, manager_with_inventory):
        """Test getting recipes that can be crafted."""
        available = manager_with_inventory.get_available_recipes()

        # Should have health_potion and bandage (both unlocked and have materials)
        recipe_ids = [r.id for r in available]
        assert "health_potion" in recipe_ids
        assert "bandage" in recipe_ids
        assert "locked_recipe" not in recipe_ids

    def test_get_craftable_recipes_alias(self, manager_with_inventory):
        """Test get_craftable_recipes is alias for get_available_recipes."""
        available = manager_with_inventory.get_available_recipes()
        craftable = manager_with_inventory.get_craftable_recipes()

        assert available == craftable


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def load_crafting(self, load_system):
        """Load the crafting system."""
        return load_system("crafting")

    @pytest.fixture
    def manager(self, load_crafting):
        """Create a fresh CraftingManager instance."""
        CraftingManager = load_crafting["CraftingManager"]
        return CraftingManager()

    def test_empty_ingredients(self, load_crafting, manager):
        """Test recipe with no ingredients."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="free_item",
            name="Free Item",
            ingredients={},
            result_item="free_item"
        )
        manager.register_recipe(recipe)

        # Setup minimal inventory
        inventory = {}
        manager.set_inventory_callbacks(
            lambda: inventory,
            lambda inv: inventory.update(inv),
            lambda item, qty: inventory.update({item: inventory.get(item, 0) + qty}),
            lambda item, qty: None
        )

        assert manager.can_craft("free_item") is True

    def test_recipe_overwrite(self, load_crafting, manager):
        """Test registering recipe with same ID overwrites."""
        Recipe = load_crafting["Recipe"]

        r1 = Recipe(id="same", name="Original", ingredients={}, result_item="item1")
        r2 = Recipe(id="same", name="Updated", ingredients={}, result_item="item2")

        manager.register_recipe(r1)
        manager.register_recipe(r2)

        recipe = manager.get_recipe("same")
        assert recipe.name == "Updated"
        assert recipe.result_item == "item2"

    def test_no_inventory_callbacks(self, load_crafting, manager):
        """Test operations without inventory callbacks."""
        Recipe = load_crafting["Recipe"]

        recipe = Recipe(
            id="test",
            name="Test",
            ingredients={"item": 1},
            result_item="result"
        )
        manager.register_recipe(recipe)

        # Without callbacks, get_inventory returns empty dict
        assert manager.get_inventory() == {}
        assert manager.can_craft("test") is False

    def test_callable_unlock_condition_exception(self, load_crafting, manager):
        """Test callable unlock condition that raises exception."""
        Recipe = load_crafting["Recipe"]

        def bad_condition(context):
            raise ValueError("Intentional error")

        recipe = Recipe(
            id="bad",
            name="Bad",
            ingredients={},
            result_item="item",
            unlock_condition=bad_condition
        )
        manager.register_recipe(recipe)

        # Should not raise, just not unlock
        unlocked = manager.check_unlock_conditions({})
        assert "bad" not in unlocked
        assert recipe.unlocked is False

    def test_is_recipe_unlocked_nonexistent(self, manager):
        """Test is_recipe_unlocked for non-existent recipe."""
        assert manager.is_recipe_unlocked("nonexistent") is False

    def test_get_missing_ingredients_nonexistent(self, manager):
        """Test get_missing_ingredients for non-existent recipe."""
        missing = manager.get_missing_ingredients("nonexistent")
        assert missing == {}


class TestHelperFunctions:
    """Tests for helper functions."""

    @pytest.fixture
    def load_crafting(self, load_system):
        """Load the crafting system."""
        return load_system("crafting")

    def test_get_item_name_known(self, load_crafting):
        """Test getting name for known item."""
        get_item_name = load_crafting["get_item_name"]

        assert get_item_name("health_potion") == "Health Potion"
        assert get_item_name("iron_ore") == "Iron Ore"

    def test_get_item_name_unknown(self, load_crafting):
        """Test getting name for unknown item (auto-formats ID)."""
        get_item_name = load_crafting["get_item_name"]

        # Unknown items should have underscores replaced and be title-cased
        assert get_item_name("unknown_item") == "Unknown Item"
        assert get_item_name("rare_dragon_scale") == "Rare Dragon Scale"

    def test_item_names_registry(self, load_crafting):
        """Test ITEM_NAMES registry exists with expected entries."""
        ITEM_NAMES = load_crafting["ITEM_NAMES"]

        assert isinstance(ITEM_NAMES, dict)
        assert "wood" in ITEM_NAMES
        assert "stone" in ITEM_NAMES
        assert "health_potion" in ITEM_NAMES

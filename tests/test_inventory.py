"""
Tests for the inventory system (game/inventory.rpy).

Tests cover:
- Item creation and properties
- Inventory add/remove operations
- Stack limits and quantities
- Equipment slots and equipping
- Gold management
- Filtering and sorting
"""
import pytest


class TestItemCategory:
    """Tests for ItemCategory enumeration class."""

    def test_category_values(self, load_system):
        """Test that all category values are defined."""
        ns = load_system("inventory")
        ItemCategory = ns["ItemCategory"]

        assert ItemCategory.WEAPON == "weapon"
        assert ItemCategory.ARMOR == "armor"
        assert ItemCategory.ACCESSORY == "accessory"
        assert ItemCategory.CONSUMABLE == "consumable"
        assert ItemCategory.KEY_ITEM == "key_item"
        assert ItemCategory.MISC == "misc"

    def test_get_all_categories(self, load_system):
        """Test get_all returns all categories."""
        ns = load_system("inventory")
        ItemCategory = ns["ItemCategory"]

        categories = ItemCategory.get_all()
        assert len(categories) == 6
        assert "weapon" in categories
        assert "armor" in categories
        assert "accessory" in categories
        assert "consumable" in categories
        assert "key_item" in categories
        assert "misc" in categories

    def test_get_display_name(self, load_system):
        """Test display name retrieval for categories."""
        ns = load_system("inventory")
        ItemCategory = ns["ItemCategory"]

        assert ItemCategory.get_display_name("weapon") == "Weapons"
        assert ItemCategory.get_display_name("armor") == "Armor"
        assert ItemCategory.get_display_name("consumable") == "Consumables"
        assert ItemCategory.get_display_name("key_item") == "Key Items"

    def test_get_color(self, load_system):
        """Test color retrieval for categories."""
        ns = load_system("inventory")
        ItemCategory = ns["ItemCategory"]

        assert ItemCategory.get_color("weapon") == "#ff6644"
        assert ItemCategory.get_color("armor") == "#4488ff"
        assert ItemCategory.get_color("consumable") == "#44ff66"
        # Unknown category returns white
        assert ItemCategory.get_color("unknown") == "#ffffff"


class TestItem:
    """Tests for Item class."""

    def test_item_creation_with_defaults(self, load_system):
        """Test basic item creation with default values."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        item = Item(id="test_item", name="Test Item")

        assert item.id == "test_item"
        assert item.name == "Test Item"
        assert item.description == ""
        assert item.category == ItemCategory.MISC
        assert item.value == 0
        assert item.stackable is True
        assert item.max_stack == 99
        assert item.effects == {}
        assert item.icon is None
        assert item.equip_slot is None

    def test_item_creation_with_all_parameters(self, load_system):
        """Test item creation with all parameters specified."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        item = Item(
            id="health_potion",
            name="Health Potion",
            description="Restores 50 HP",
            category=ItemCategory.CONSUMABLE,
            value=25,
            stackable=True,
            max_stack=99,
            effects={"heal_hp": 50},
            icon="potion.png"
        )

        assert item.id == "health_potion"
        assert item.name == "Health Potion"
        assert item.description == "Restores 50 HP"
        assert item.category == ItemCategory.CONSUMABLE
        assert item.value == 25
        assert item.stackable is True
        assert item.max_stack == 99
        assert item.effects == {"heal_hp": 50}
        assert item.icon == "potion.png"

    def test_weapon_auto_equip_slot(self, load_system):
        """Test that weapons automatically get weapon equip slot."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        sword = Item(
            id="sword",
            name="Sword",
            category=ItemCategory.WEAPON
        )

        assert sword.equip_slot == "weapon"
        assert sword.is_equippable() is True

    def test_armor_auto_equip_slot(self, load_system):
        """Test that armor automatically gets armor equip slot."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        armor = Item(
            id="armor",
            name="Armor",
            category=ItemCategory.ARMOR
        )

        assert armor.equip_slot == "armor"
        assert armor.is_equippable() is True

    def test_accessory_auto_equip_slot(self, load_system):
        """Test that accessories automatically get accessory equip slot."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        ring = Item(
            id="ring",
            name="Ring",
            category=ItemCategory.ACCESSORY
        )

        assert ring.equip_slot == "accessory"
        assert ring.is_equippable() is True

    def test_consumable_is_consumable(self, load_system):
        """Test that consumables are correctly identified."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        potion = Item(
            id="potion",
            name="Potion",
            category=ItemCategory.CONSUMABLE
        )

        assert potion.is_consumable() is True
        assert potion.is_equippable() is False

    def test_non_stackable_item_max_stack_is_one(self, load_system):
        """Test that non-stackable items have max_stack of 1."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        sword = Item(
            id="sword",
            name="Sword",
            category=ItemCategory.WEAPON,
            stackable=False
        )

        assert sword.stackable is False
        assert sword.max_stack == 1

    def test_get_effect(self, load_system):
        """Test getting specific effects from an item."""
        ns = load_system("inventory")
        Item = ns["Item"]

        item = Item(
            id="test",
            name="Test",
            effects={"strength": 5, "defense": 3}
        )

        assert item.get_effect("strength") == 5
        assert item.get_effect("defense") == 3
        assert item.get_effect("agility") == 0  # Non-existent effect

    def test_item_copy(self, load_system):
        """Test that item copy creates an independent copy."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        original = Item(
            id="original",
            name="Original",
            category=ItemCategory.WEAPON,
            effects={"strength": 5}
        )

        copy = original.copy()

        assert copy.id == original.id
        assert copy.name == original.name
        assert copy.effects == original.effects
        assert copy is not original
        assert copy.effects is not original.effects

    def test_item_repr(self, load_system):
        """Test item string representation."""
        ns = load_system("inventory")
        Item = ns["Item"]

        item = Item(id="test_id", name="Test Name")

        assert repr(item) == "Item(test_id, Test Name)"


class TestInventorySlot:
    """Tests for InventorySlot class."""

    def test_empty_slot(self, load_system):
        """Test that a new slot is empty."""
        ns = load_system("inventory")
        InventorySlot = ns["InventorySlot"]

        slot = InventorySlot()

        assert slot.is_empty() is True
        assert slot.item is None
        assert slot.quantity == 0

    def test_slot_with_item(self, load_system):
        """Test slot with an item."""
        ns = load_system("inventory")
        InventorySlot = ns["InventorySlot"]
        Item = ns["Item"]

        item = Item(id="test", name="Test")
        slot = InventorySlot(item=item, quantity=5)

        assert slot.is_empty() is False
        assert slot.item == item
        assert slot.quantity == 5

    def test_can_add_to_empty_slot(self, load_system):
        """Test that items can be added to an empty slot."""
        ns = load_system("inventory")
        InventorySlot = ns["InventorySlot"]
        Item = ns["Item"]

        slot = InventorySlot()
        item = Item(id="test", name="Test")

        assert slot.can_add(item) is True

    def test_can_add_same_item_stackable(self, load_system):
        """Test that same stackable items can be added."""
        ns = load_system("inventory")
        InventorySlot = ns["InventorySlot"]
        Item = ns["Item"]

        item = Item(id="test", name="Test", stackable=True, max_stack=10)
        slot = InventorySlot(item=item, quantity=5)

        assert slot.can_add(item, amount=3) is True
        assert slot.can_add(item, amount=5) is True
        assert slot.can_add(item, amount=6) is False  # Would exceed max

    def test_cannot_add_different_item(self, load_system):
        """Test that different items cannot be added to occupied slot."""
        ns = load_system("inventory")
        InventorySlot = ns["InventorySlot"]
        Item = ns["Item"]

        item1 = Item(id="item1", name="Item 1")
        item2 = Item(id="item2", name="Item 2")
        slot = InventorySlot(item=item1, quantity=5)

        assert slot.can_add(item2) is False

    def test_cannot_add_to_non_stackable(self, load_system):
        """Test that items cannot be added to non-stackable slot."""
        ns = load_system("inventory")
        InventorySlot = ns["InventorySlot"]
        Item = ns["Item"]

        item = Item(id="sword", name="Sword", stackable=False)
        slot = InventorySlot(item=item, quantity=1)

        assert slot.can_add(item) is False

    def test_slot_add(self, load_system):
        """Test adding quantity to slot."""
        ns = load_system("inventory")
        InventorySlot = ns["InventorySlot"]
        Item = ns["Item"]

        item = Item(id="test", name="Test", max_stack=10)
        slot = InventorySlot(item=item, quantity=5)

        slot.add(3)
        assert slot.quantity == 8

        slot.add(5)  # Would exceed max_stack
        assert slot.quantity == 10  # Capped at max

    def test_slot_remove(self, load_system):
        """Test removing quantity from slot."""
        ns = load_system("inventory")
        InventorySlot = ns["InventorySlot"]
        Item = ns["Item"]

        item = Item(id="test", name="Test")
        slot = InventorySlot(item=item, quantity=5)

        slot.remove(2)
        assert slot.quantity == 3
        assert slot.is_empty() is False

        slot.remove(3)
        assert slot.quantity == 0
        assert slot.is_empty() is True
        assert slot.item is None

    def test_slot_clear(self, load_system):
        """Test clearing a slot."""
        ns = load_system("inventory")
        InventorySlot = ns["InventorySlot"]
        Item = ns["Item"]

        item = Item(id="test", name="Test")
        slot = InventorySlot(item=item, quantity=5)

        slot.clear()

        assert slot.is_empty() is True
        assert slot.item is None
        assert slot.quantity == 0


class TestEquipment:
    """Tests for Equipment class."""

    def test_equipment_slots(self, load_system):
        """Test that equipment has correct slots."""
        ns = load_system("inventory")
        Equipment = ns["Equipment"]

        equipment = Equipment()

        assert "weapon" in equipment.slots
        assert "armor" in equipment.slots
        assert "accessory" in equipment.slots
        assert len(equipment.slots) == 3

    def test_equip_item(self, load_system):
        """Test equipping an item."""
        ns = load_system("inventory")
        Equipment = ns["Equipment"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        equipment = Equipment()
        sword = Item(
            id="sword",
            name="Sword",
            category=ItemCategory.WEAPON,
            effects={"strength": 5}
        )

        previous = equipment.equip(sword)

        assert previous is None
        assert equipment.get_equipped("weapon") == sword

    def test_equip_replaces_existing(self, load_system):
        """Test that equipping replaces existing item."""
        ns = load_system("inventory")
        Equipment = ns["Equipment"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        equipment = Equipment()
        sword1 = Item(id="sword1", name="Sword 1", category=ItemCategory.WEAPON)
        sword2 = Item(id="sword2", name="Sword 2", category=ItemCategory.WEAPON)

        equipment.equip(sword1)
        previous = equipment.equip(sword2)

        assert previous == sword1
        assert equipment.get_equipped("weapon") == sword2

    def test_equip_non_equippable_returns_none(self, load_system):
        """Test that equipping non-equippable item returns None."""
        ns = load_system("inventory")
        Equipment = ns["Equipment"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        equipment = Equipment()
        potion = Item(id="potion", name="Potion", category=ItemCategory.CONSUMABLE)

        result = equipment.equip(potion)

        assert result is None

    def test_unequip_item(self, load_system):
        """Test unequipping an item."""
        ns = load_system("inventory")
        Equipment = ns["Equipment"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        equipment = Equipment()
        sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)

        equipment.equip(sword)
        unequipped = equipment.unequip("weapon")

        assert unequipped == sword
        assert equipment.get_equipped("weapon") is None

    def test_unequip_empty_slot(self, load_system):
        """Test unequipping from an empty slot."""
        ns = load_system("inventory")
        Equipment = ns["Equipment"]

        equipment = Equipment()
        result = equipment.unequip("weapon")

        assert result is None

    def test_is_equipped(self, load_system):
        """Test checking if an item is equipped."""
        ns = load_system("inventory")
        Equipment = ns["Equipment"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        equipment = Equipment()
        sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)

        assert equipment.is_equipped("sword") is False

        equipment.equip(sword)

        assert equipment.is_equipped("sword") is True

    def test_get_total_effects(self, load_system):
        """Test getting combined effects from all equipment."""
        ns = load_system("inventory")
        Equipment = ns["Equipment"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        equipment = Equipment()

        sword = Item(
            id="sword",
            name="Sword",
            category=ItemCategory.WEAPON,
            effects={"strength": 5}
        )
        armor = Item(
            id="armor",
            name="Armor",
            category=ItemCategory.ARMOR,
            effects={"defense": 10, "strength": 2}
        )
        ring = Item(
            id="ring",
            name="Ring",
            category=ItemCategory.ACCESSORY,
            effects={"luck": 3}
        )

        equipment.equip(sword)
        equipment.equip(armor)
        equipment.equip(ring)

        effects = equipment.get_total_effects()

        assert effects["strength"] == 7  # 5 + 2
        assert effects["defense"] == 10
        assert effects["luck"] == 3

    def test_get_all_equipped(self, load_system):
        """Test getting list of all equipped items."""
        ns = load_system("inventory")
        Equipment = ns["Equipment"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        equipment = Equipment()
        sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)
        armor = Item(id="armor", name="Armor", category=ItemCategory.ARMOR)

        equipment.equip(sword)
        equipment.equip(armor)

        equipped = equipment.get_all_equipped()

        assert len(equipped) == 2
        assert sword in equipped
        assert armor in equipped


class TestInventory:
    """Tests for Inventory class."""

    def test_inventory_creation_default(self, load_system):
        """Test inventory creation with default slots."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()

        assert inventory.max_slots == 20
        assert len(inventory.slots) == 20
        assert inventory.gold == 0
        assert inventory.equipment is not None

    def test_inventory_creation_custom_slots(self, load_system):
        """Test inventory creation with custom slot count."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory(max_slots=30)

        assert inventory.max_slots == 30
        assert len(inventory.slots) == 30

    def test_add_item_to_empty_inventory(self, load_system):
        """Test adding item to empty inventory."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item = Item(id="test", name="Test")

        added = inventory.add_item(item)

        assert added == 1
        assert inventory.has_item("test") is True
        assert inventory.get_item_count("test") == 1

    def test_add_item_with_quantity(self, load_system):
        """Test adding multiple items at once."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item = Item(id="potion", name="Potion", stackable=True, max_stack=99)

        added = inventory.add_item(item, quantity=10)

        assert added == 10
        assert inventory.get_item_count("potion") == 10

    def test_add_item_stacking(self, load_system):
        """Test that stackable items stack properly."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item = Item(id="potion", name="Potion", stackable=True, max_stack=99)

        inventory.add_item(item, quantity=10)
        inventory.add_item(item, quantity=5)

        assert inventory.get_item_count("potion") == 15
        assert inventory.get_used_slots() == 1  # All in one slot

    def test_add_item_exceeds_stack_creates_new_slot(self, load_system):
        """Test that exceeding stack limit creates new slots."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item = Item(id="potion", name="Potion", stackable=True, max_stack=10)

        added = inventory.add_item(item, quantity=25)

        assert added == 25
        assert inventory.get_item_count("potion") == 25
        assert inventory.get_used_slots() == 3  # 10 + 10 + 5

    def test_add_item_inventory_full(self, load_system):
        """Test adding item when inventory is full."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory(max_slots=2)
        item1 = Item(id="item1", name="Item 1", stackable=False)
        item2 = Item(id="item2", name="Item 2", stackable=False)
        item3 = Item(id="item3", name="Item 3", stackable=False)

        inventory.add_item(item1)
        inventory.add_item(item2)
        added = inventory.add_item(item3)

        assert added == 0
        assert inventory.is_full() is True

    def test_remove_item(self, load_system):
        """Test removing items from inventory."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item = Item(id="potion", name="Potion")

        inventory.add_item(item, quantity=10)
        removed = inventory.remove_item("potion", quantity=3)

        assert removed == 3
        assert inventory.get_item_count("potion") == 7

    def test_remove_item_all(self, load_system):
        """Test removing all items clears the slot."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item = Item(id="potion", name="Potion")

        inventory.add_item(item, quantity=5)
        removed = inventory.remove_item("potion", quantity=5)

        assert removed == 5
        assert inventory.has_item("potion") is False
        assert inventory.get_used_slots() == 0

    def test_remove_item_more_than_available(self, load_system):
        """Test removing more items than available."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item = Item(id="potion", name="Potion")

        inventory.add_item(item, quantity=5)
        removed = inventory.remove_item("potion", quantity=10)

        assert removed == 5
        assert inventory.has_item("potion") is False

    def test_remove_nonexistent_item(self, load_system):
        """Test removing an item that doesn't exist."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()
        removed = inventory.remove_item("nonexistent")

        assert removed == 0

    def test_has_item(self, load_system):
        """Test checking if inventory has items."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item = Item(id="potion", name="Potion")

        inventory.add_item(item, quantity=5)

        assert inventory.has_item("potion") is True
        assert inventory.has_item("potion", quantity=5) is True
        assert inventory.has_item("potion", quantity=6) is False
        assert inventory.has_item("nonexistent") is False

    def test_get_item(self, load_system):
        """Test getting item reference from inventory."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item = Item(id="sword", name="Sword")

        inventory.add_item(item)
        retrieved = inventory.get_item("sword")

        assert retrieved is not None
        assert retrieved.id == "sword"

    def test_get_nonexistent_item(self, load_system):
        """Test getting item that doesn't exist."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()
        retrieved = inventory.get_item("nonexistent")

        assert retrieved is None

    def test_get_free_slots(self, load_system):
        """Test counting free slots."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory(max_slots=10)
        item = Item(id="item", name="Item", stackable=False)

        assert inventory.get_free_slots() == 10

        inventory.add_item(item)
        assert inventory.get_free_slots() == 9

    def test_is_full(self, load_system):
        """Test checking if inventory is full."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory(max_slots=2)
        item = Item(id="item", name="Item", stackable=False)

        assert inventory.is_full() is False

        inventory.add_item(item)
        inventory.add_item(item.copy())

        assert inventory.is_full() is True


class TestInventoryEquipment:
    """Tests for inventory equipment management."""

    def test_equip_item_from_inventory(self, load_system):
        """Test equipping an item from inventory."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        inventory = Inventory()
        sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)

        inventory.add_item(sword)
        result = inventory.equip_item("sword")

        assert result is True
        assert inventory.is_equipped("sword") is True
        assert inventory.has_item("sword") is False  # Removed from inventory

    def test_equip_item_replaces_existing(self, load_system):
        """Test that equipping item returns previous to inventory."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        inventory = Inventory()
        sword1 = Item(id="sword1", name="Sword 1", category=ItemCategory.WEAPON)
        sword2 = Item(id="sword2", name="Sword 2", category=ItemCategory.WEAPON)

        inventory.add_item(sword1)
        inventory.add_item(sword2)

        inventory.equip_item("sword1")
        inventory.equip_item("sword2")

        assert inventory.is_equipped("sword2") is True
        assert inventory.has_item("sword1") is True  # Returned to inventory

    def test_equip_nonexistent_item(self, load_system):
        """Test equipping item not in inventory."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()
        result = inventory.equip_item("nonexistent")

        assert result is False

    def test_unequip_item_to_inventory(self, load_system):
        """Test unequipping item returns it to inventory."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        inventory = Inventory()
        sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)

        inventory.add_item(sword)
        inventory.equip_item("sword")
        result = inventory.unequip_item("weapon")

        assert result is True
        assert inventory.is_equipped("sword") is False
        assert inventory.has_item("sword") is True

    def test_unequip_when_inventory_full(self, load_system):
        """Test unequipping when inventory is full re-equips item."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        inventory = Inventory(max_slots=1)
        sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)
        potion = Item(id="potion", name="Potion")

        inventory.add_item(sword)
        inventory.equip_item("sword")
        inventory.add_item(potion)  # Fill the only slot

        result = inventory.unequip_item("weapon")

        assert result is False
        assert inventory.is_equipped("sword") is True  # Still equipped

    def test_get_equipment_bonuses(self, load_system):
        """Test getting total equipment bonuses."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        inventory = Inventory()
        sword = Item(
            id="sword",
            name="Sword",
            category=ItemCategory.WEAPON,
            effects={"strength": 5}
        )
        armor = Item(
            id="armor",
            name="Armor",
            category=ItemCategory.ARMOR,
            effects={"defense": 10}
        )

        inventory.add_item(sword)
        inventory.add_item(armor)
        inventory.equip_item("sword")
        inventory.equip_item("armor")

        bonuses = inventory.get_equipment_bonuses()

        assert bonuses["strength"] == 5
        assert bonuses["defense"] == 10


class TestInventoryFiltering:
    """Tests for inventory filtering and sorting."""

    def test_get_items_by_category(self, load_system):
        """Test filtering items by category."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        inventory = Inventory()
        potion = Item(id="potion", name="Potion", category=ItemCategory.CONSUMABLE)
        sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)
        elixir = Item(id="elixir", name="Elixir", category=ItemCategory.CONSUMABLE)

        inventory.add_item(potion)
        inventory.add_item(sword)
        inventory.add_item(elixir)

        consumables = inventory.get_items_by_category(ItemCategory.CONSUMABLE)

        assert len(consumables) == 2
        item_ids = [item.id for item, qty in consumables]
        assert "potion" in item_ids
        assert "elixir" in item_ids

    def test_get_all_items(self, load_system):
        """Test getting all items."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        item1 = Item(id="item1", name="Item 1")
        item2 = Item(id="item2", name="Item 2")

        inventory.add_item(item1, quantity=5)
        inventory.add_item(item2, quantity=3)

        all_items = inventory.get_all_items()

        assert len(all_items) == 2
        quantities = {item.id: qty for item, qty in all_items}
        assert quantities["item1"] == 5
        assert quantities["item2"] == 3

    def test_sort_by_name(self, load_system):
        """Test sorting inventory by name."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]

        inventory = Inventory()
        inventory.add_item(Item(id="z_item", name="Zebra"))
        inventory.add_item(Item(id="a_item", name="Apple"))
        inventory.add_item(Item(id="m_item", name="Mango"))

        inventory.sort_by_name()

        all_items = inventory.get_all_items()
        names = [item.name for item, qty in all_items]

        assert names == ["Apple", "Mango", "Zebra"]

    def test_sort_by_category(self, load_system):
        """Test sorting inventory by category."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        inventory = Inventory()
        inventory.add_item(Item(id="potion", name="Potion", category=ItemCategory.CONSUMABLE))
        inventory.add_item(Item(id="sword", name="Sword", category=ItemCategory.WEAPON))
        inventory.add_item(Item(id="armor", name="Armor", category=ItemCategory.ARMOR))

        inventory.sort_by_category()

        all_items = inventory.get_all_items()
        categories = [item.category for item, qty in all_items]

        # Should be sorted by category order: weapon, armor, accessory, consumable, key_item, misc
        assert categories.index(ItemCategory.WEAPON) < categories.index(ItemCategory.ARMOR)
        assert categories.index(ItemCategory.ARMOR) < categories.index(ItemCategory.CONSUMABLE)


class TestGoldManagement:
    """Tests for gold/currency management."""

    def test_add_gold(self, load_system):
        """Test adding gold."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()
        inventory.add_gold(100)

        assert inventory.gold == 100

    def test_add_gold_cumulative(self, load_system):
        """Test that gold additions are cumulative."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()
        inventory.add_gold(50)
        inventory.add_gold(30)

        assert inventory.gold == 80

    def test_remove_gold_success(self, load_system):
        """Test removing gold when enough is available."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()
        inventory.add_gold(100)
        result = inventory.remove_gold(30)

        assert result is True
        assert inventory.gold == 70

    def test_remove_gold_insufficient(self, load_system):
        """Test removing gold when not enough is available."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()
        inventory.add_gold(50)
        result = inventory.remove_gold(100)

        assert result is False
        assert inventory.gold == 50  # Unchanged

    def test_can_afford(self, load_system):
        """Test checking if player can afford something."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()
        inventory.add_gold(100)

        assert inventory.can_afford(50) is True
        assert inventory.can_afford(100) is True
        assert inventory.can_afford(101) is False

    def test_gold_cannot_go_negative(self, load_system):
        """Test that gold cannot go below zero."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        inventory = Inventory()
        inventory.add_gold(-50)  # Negative addition

        assert inventory.gold == 0


class TestInventorySerialization:
    """Tests for inventory save/load functionality."""

    def test_to_dict(self, load_system):
        """Test converting inventory to dictionary."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        inventory = Inventory(max_slots=10)
        potion = Item(id="potion", name="Potion")
        sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)

        inventory.add_item(potion, quantity=5)
        inventory.add_item(sword)
        inventory.add_gold(100)
        inventory.equip_item("sword")

        data = inventory.to_dict()

        assert data["max_slots"] == 10
        assert data["gold"] == 100
        assert len(data["slots"]) == 1  # Only potion, sword is equipped
        assert data["slots"][0]["item_id"] == "potion"
        assert data["slots"][0]["quantity"] == 5
        assert data["equipment"]["weapon"] == "sword"

    def test_from_dict(self, load_system):
        """Test creating inventory from dictionary."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        # Create item database
        item_database = {
            "potion": Item(id="potion", name="Potion"),
            "sword": Item(id="sword", name="Sword", category=ItemCategory.WEAPON)
        }

        data = {
            "max_slots": 15,
            "gold": 200,
            "slots": [
                {"item_id": "potion", "quantity": 10}
            ],
            "equipment": {
                "weapon": "sword"
            }
        }

        inventory = Inventory.from_dict(data, item_database)

        assert inventory.max_slots == 15
        assert inventory.gold == 200
        assert inventory.has_item("potion") is True
        assert inventory.get_item_count("potion") == 10
        assert inventory.is_equipped("sword") is True


class TestItemEffects:
    """Tests for item effect application."""

    def test_apply_heal_effect(self, load_system):
        """Test applying healing effect."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        class MockPlayer:
            def __init__(self):
                self.hp = 50
                self.healed_amount = 0

            def heal(self, amount):
                self.healed_amount = amount
                self.hp += amount

        potion = Item(
            id="potion",
            name="Health Potion",
            category=ItemCategory.CONSUMABLE,
            effects={"heal_hp": 50}
        )

        player = MockPlayer()
        result = potion.apply_effects(player)

        assert result is True
        assert player.healed_amount == 50

    def test_apply_stat_effect(self, load_system):
        """Test applying stat modification effect."""
        ns = load_system("inventory")
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        class MockPlayer:
            def __init__(self):
                self.stats = {}

            def add_stat(self, stat, value):
                self.stats[stat] = self.stats.get(stat, 0) + value

        tonic = Item(
            id="tonic",
            name="Strength Tonic",
            category=ItemCategory.CONSUMABLE,
            effects={"strength": 5}
        )

        player = MockPlayer()
        result = tonic.apply_effects(player)

        assert result is True
        assert player.stats["strength"] == 5

    def test_apply_effects_no_target(self, load_system):
        """Test applying effects with no target."""
        ns = load_system("inventory")
        Item = ns["Item"]

        item = Item(id="test", name="Test", effects={"heal_hp": 50})
        result = item.apply_effects(None)

        assert result is False

    def test_apply_effects_no_effects(self, load_system):
        """Test applying effects when item has none."""
        ns = load_system("inventory")
        Item = ns["Item"]

        class MockPlayer:
            pass

        item = Item(id="test", name="Test")
        result = item.apply_effects(MockPlayer())

        assert result is False


class TestUseItem:
    """Tests for using consumable items."""

    def test_use_consumable_item(self, load_system):
        """Test using a consumable item."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        class MockPlayer:
            def __init__(self):
                self.healed = False

            def heal(self, amount):
                self.healed = True

        inventory = Inventory()
        potion = Item(
            id="potion",
            name="Potion",
            category=ItemCategory.CONSUMABLE,
            effects={"heal_hp": 50}
        )

        inventory.add_item(potion, quantity=3)
        player = MockPlayer()

        result = inventory.use_item("potion", player)

        assert result is True
        assert player.healed is True
        assert inventory.get_item_count("potion") == 2

    def test_use_non_consumable_fails(self, load_system):
        """Test that using non-consumable item fails."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]
        Item = ns["Item"]
        ItemCategory = ns["ItemCategory"]

        class MockPlayer:
            pass

        inventory = Inventory()
        sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)

        inventory.add_item(sword)

        result = inventory.use_item("sword", MockPlayer())

        assert result is False
        assert inventory.has_item("sword") is True  # Not consumed

    def test_use_nonexistent_item_fails(self, load_system):
        """Test that using nonexistent item fails."""
        ns = load_system("inventory")
        Inventory = ns["Inventory"]

        class MockPlayer:
            pass

        inventory = Inventory()
        result = inventory.use_item("nonexistent", MockPlayer())

        assert result is False

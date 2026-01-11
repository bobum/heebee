# Heebee - Inventory System
# A complete inventory and equipment system for Ren'Py visual novels
#
# ============================================================================
# USAGE EXAMPLES:
# ============================================================================
#
# Initialize inventory at game start:
#   $ inventory = Inventory(max_slots=20)
#
# Add items to inventory:
#   $ inventory.add_item(items["health_potion"])
#   $ inventory.add_item(items["health_potion"], quantity=5)
#
# Remove items from inventory:
#   $ inventory.remove_item("health_potion")
#   $ inventory.remove_item("health_potion", quantity=3)
#
# Use consumable items:
#   $ inventory.use_item("health_potion", player)
#
# Equip/Unequip items:
#   $ inventory.equip_item("iron_sword")
#   $ inventory.unequip_item("weapon")
#
# Check inventory:
#   $ count = inventory.get_item_count("health_potion")
#   $ has_key = inventory.has_item("old_key")
#
# Show inventory screen:
#   call screen inventory_screen
#
# ============================================================================

init python:

    # ========================================================================
    # ITEM CATEGORIES
    # ========================================================================

    class ItemCategory:
        """Enumeration of item categories."""
        WEAPON = "weapon"
        ARMOR = "armor"
        ACCESSORY = "accessory"
        CONSUMABLE = "consumable"
        KEY_ITEM = "key_item"
        MISC = "misc"

        @staticmethod
        def get_all():
            """Return all item categories."""
            return [
                ItemCategory.WEAPON,
                ItemCategory.ARMOR,
                ItemCategory.ACCESSORY,
                ItemCategory.CONSUMABLE,
                ItemCategory.KEY_ITEM,
                ItemCategory.MISC
            ]

        @staticmethod
        def get_display_name(category):
            """Get display name for a category."""
            names = {
                "weapon": "Weapons",
                "armor": "Armor",
                "accessory": "Accessories",
                "consumable": "Consumables",
                "key_item": "Key Items",
                "misc": "Miscellaneous"
            }
            return names.get(category, category.title())

        @staticmethod
        def get_color(category):
            """Get display color for a category."""
            colors = {
                "weapon": "#ff6644",
                "armor": "#4488ff",
                "accessory": "#ffaa44",
                "consumable": "#44ff66",
                "key_item": "#ff44ff",
                "misc": "#aaaaaa"
            }
            return colors.get(category, "#ffffff")

    # ========================================================================
    # ITEM CLASS
    # ========================================================================

    class Item:
        """
        Represents an item in the game.

        Attributes:
            id: Unique identifier for the item
            name: Display name of the item
            description: Detailed description
            category: Item category (weapon, armor, consumable, etc.)
            value: Gold/currency value
            stackable: Whether multiple items can stack in one slot
            max_stack: Maximum stack size (if stackable)
            effects: Dictionary of effects when used/equipped
            icon: Optional icon path for display
            equip_slot: For equipment, which slot it goes in
        """

        def __init__(self, id, name, description="", category=ItemCategory.MISC,
                     value=0, stackable=True, max_stack=99, effects=None,
                     icon=None, equip_slot=None):
            self.id = id
            self.name = name
            self.description = description
            self.category = category
            self.value = value
            self.stackable = stackable
            self.max_stack = max_stack if stackable else 1
            self.effects = effects or {}
            self.icon = icon
            self.equip_slot = equip_slot

            # Automatically set equip_slot based on category if not provided
            if equip_slot is None:
                if category == ItemCategory.WEAPON:
                    self.equip_slot = "weapon"
                elif category == ItemCategory.ARMOR:
                    self.equip_slot = "armor"
                elif category == ItemCategory.ACCESSORY:
                    self.equip_slot = "accessory"

        def is_equippable(self):
            """Check if this item can be equipped."""
            return self.equip_slot is not None

        def is_consumable(self):
            """Check if this item can be consumed/used."""
            return self.category == ItemCategory.CONSUMABLE

        def get_effect(self, effect_name):
            """Get a specific effect value."""
            return self.effects.get(effect_name, 0)

        def apply_effects(self, target):
            """
            Apply item effects to a target (player).
            Returns True if effects were applied, False otherwise.
            """
            if not target or not self.effects:
                return False

            applied = False

            # HP restoration
            if "heal_hp" in self.effects:
                if hasattr(target, 'heal'):
                    target.heal(self.effects["heal_hp"])
                    applied = True

            # MP restoration
            if "heal_mp" in self.effects:
                if hasattr(target, 'restore_mp'):
                    target.restore_mp(self.effects["heal_mp"])
                    applied = True

            # Stat modifications
            stat_effects = ["strength", "defense", "agility", "charisma",
                           "intelligence", "luck", "max_hp", "max_mp"]
            for stat in stat_effects:
                if stat in self.effects:
                    if hasattr(target, 'add_stat'):
                        target.add_stat(stat, self.effects[stat])
                        applied = True

            # Full restore
            if self.effects.get("full_restore", False):
                if hasattr(target, 'full_restore'):
                    target.full_restore()
                    applied = True

            # XP bonus
            if "xp" in self.effects:
                if hasattr(target, 'add_xp'):
                    target.add_xp(self.effects["xp"])
                    applied = True

            return applied

        def copy(self):
            """Create a copy of this item."""
            return Item(
                id=self.id,
                name=self.name,
                description=self.description,
                category=self.category,
                value=self.value,
                stackable=self.stackable,
                max_stack=self.max_stack,
                effects=dict(self.effects),
                icon=self.icon,
                equip_slot=self.equip_slot
            )

        def __repr__(self):
            return "Item({}, {})".format(self.id, self.name)

    # ========================================================================
    # INVENTORY SLOT CLASS
    # ========================================================================

    class InventorySlot:
        """
        Represents a slot in the inventory holding an item and quantity.
        """

        def __init__(self, item=None, quantity=0):
            self.item = item
            self.quantity = quantity

        def is_empty(self):
            """Check if slot is empty."""
            return self.item is None or self.quantity <= 0

        def can_add(self, item, amount=1):
            """Check if we can add more of this item to this slot."""
            if self.is_empty():
                return True
            if self.item.id != item.id:
                return False
            if not self.item.stackable:
                return False
            return self.quantity + amount <= self.item.max_stack

        def add(self, amount=1):
            """Add to the quantity in this slot."""
            if self.item:
                self.quantity = min(self.quantity + amount, self.item.max_stack)

        def remove(self, amount=1):
            """Remove from the quantity in this slot."""
            self.quantity = max(0, self.quantity - amount)
            if self.quantity <= 0:
                self.clear()

        def clear(self):
            """Clear this slot."""
            self.item = None
            self.quantity = 0

    # ========================================================================
    # EQUIPMENT CLASS
    # ========================================================================

    class Equipment:
        """
        Manages equipped items in various slots.
        """

        SLOTS = ["weapon", "armor", "accessory"]

        def __init__(self):
            self.slots = {slot: None for slot in self.SLOTS}

        def get_equipped(self, slot):
            """Get the item equipped in a slot."""
            return self.slots.get(slot, None)

        def equip(self, item):
            """
            Equip an item, returning the previously equipped item (or None).
            """
            if not item or not item.is_equippable():
                return None

            slot = item.equip_slot
            if slot not in self.slots:
                return None

            previous = self.slots[slot]
            self.slots[slot] = item
            return previous

        def unequip(self, slot):
            """
            Unequip an item from a slot, returning the item (or None).
            """
            if slot not in self.slots:
                return None

            item = self.slots[slot]
            self.slots[slot] = None
            return item

        def is_equipped(self, item_id):
            """Check if an item is currently equipped."""
            for slot_item in self.slots.values():
                if slot_item and slot_item.id == item_id:
                    return True
            return False

        def get_total_effects(self):
            """Get combined effects from all equipped items."""
            total = {}
            for item in self.slots.values():
                if item:
                    for effect, value in item.effects.items():
                        if effect in total:
                            total[effect] += value
                        else:
                            total[effect] = value
            return total

        def get_all_equipped(self):
            """Get list of all equipped items."""
            return [item for item in self.slots.values() if item]

    # ========================================================================
    # INVENTORY CLASS
    # ========================================================================

    class Inventory:
        """
        Main inventory class managing items and equipment.

        Attributes:
            max_slots: Maximum number of inventory slots
            slots: List of InventorySlot objects
            equipment: Equipment manager for equipped items
            gold: Currency amount
        """

        DEFAULT_MAX_SLOTS = 20

        def __init__(self, max_slots=None):
            self.max_slots = max_slots or self.DEFAULT_MAX_SLOTS
            self.slots = [InventorySlot() for _ in range(self.max_slots)]
            self.equipment = Equipment()
            self.gold = 0

        # ====================================================================
        # ITEM MANAGEMENT
        # ====================================================================

        def add_item(self, item, quantity=1):
            """
            Add an item to the inventory.
            Returns the number of items actually added.
            """
            if not item or quantity <= 0:
                return 0

            added = 0
            remaining = quantity

            # First, try to stack with existing items
            if item.stackable:
                for slot in self.slots:
                    if not slot.is_empty() and slot.item.id == item.id:
                        can_add = slot.item.max_stack - slot.quantity
                        to_add = min(remaining, can_add)
                        if to_add > 0:
                            slot.add(to_add)
                            added += to_add
                            remaining -= to_add
                        if remaining <= 0:
                            break

            # Then, use empty slots for the rest
            while remaining > 0:
                empty_slot = self._find_empty_slot()
                if empty_slot is None:
                    break  # Inventory full

                to_add = min(remaining, item.max_stack)
                empty_slot.item = item.copy()
                empty_slot.quantity = to_add
                added += to_add
                remaining -= to_add

            return added

        def remove_item(self, item_id, quantity=1):
            """
            Remove an item from the inventory by ID.
            Returns the number of items actually removed.
            """
            if quantity <= 0:
                return 0

            removed = 0
            remaining = quantity

            for slot in self.slots:
                if not slot.is_empty() and slot.item.id == item_id:
                    to_remove = min(remaining, slot.quantity)
                    slot.remove(to_remove)
                    removed += to_remove
                    remaining -= to_remove
                    if remaining <= 0:
                        break

            return removed

        def use_item(self, item_id, target):
            """
            Use a consumable item on a target.
            Returns True if the item was used, False otherwise.
            """
            slot = self._find_item_slot(item_id)
            if not slot or slot.is_empty():
                return False

            item = slot.item
            if not item.is_consumable():
                return False

            # Apply effects
            if item.apply_effects(target):
                slot.remove(1)
                return True

            return False

        def has_item(self, item_id, quantity=1):
            """Check if inventory contains at least quantity of an item."""
            return self.get_item_count(item_id) >= quantity

        def get_item_count(self, item_id):
            """Get the total count of an item in the inventory."""
            count = 0
            for slot in self.slots:
                if not slot.is_empty() and slot.item.id == item_id:
                    count += slot.quantity
            return count

        def get_item(self, item_id):
            """Get the first instance of an item (for info display)."""
            slot = self._find_item_slot(item_id)
            return slot.item if slot else None

        def _find_empty_slot(self):
            """Find the first empty slot."""
            for slot in self.slots:
                if slot.is_empty():
                    return slot
            return None

        def _find_item_slot(self, item_id):
            """Find the first slot containing an item."""
            for slot in self.slots:
                if not slot.is_empty() and slot.item.id == item_id:
                    return slot
            return None

        def get_used_slots(self):
            """Get number of used inventory slots."""
            return sum(1 for slot in self.slots if not slot.is_empty())

        def get_free_slots(self):
            """Get number of free inventory slots."""
            return self.max_slots - self.get_used_slots()

        def is_full(self):
            """Check if inventory is full."""
            return self.get_free_slots() == 0

        # ====================================================================
        # EQUIPMENT MANAGEMENT
        # ====================================================================

        def equip_item(self, item_id):
            """
            Equip an item from inventory.
            Returns True if successful, False otherwise.
            """
            slot = self._find_item_slot(item_id)
            if not slot or slot.is_empty():
                return False

            item = slot.item
            if not item.is_equippable():
                return False

            # Unequip current item in that slot
            previous = self.equipment.equip(item.copy())

            # Remove from inventory
            slot.remove(1)

            # Add previous item back to inventory
            if previous:
                self.add_item(previous)

            return True

        def unequip_item(self, slot_name):
            """
            Unequip an item from a slot back to inventory.
            Returns True if successful, False otherwise.
            """
            item = self.equipment.unequip(slot_name)
            if not item:
                return False

            # Try to add back to inventory
            added = self.add_item(item)
            if added == 0:
                # Inventory full, re-equip the item
                self.equipment.equip(item)
                return False

            return True

        def is_equipped(self, item_id):
            """Check if an item is equipped."""
            return self.equipment.is_equipped(item_id)

        def get_equipped(self, slot_name):
            """Get the item equipped in a slot."""
            return self.equipment.get_equipped(slot_name)

        def get_equipment_bonuses(self):
            """Get total stat bonuses from equipment."""
            return self.equipment.get_total_effects()

        # ====================================================================
        # FILTERING AND SORTING
        # ====================================================================

        def get_items_by_category(self, category):
            """Get all items of a specific category."""
            result = []
            for slot in self.slots:
                if not slot.is_empty() and slot.item.category == category:
                    result.append((slot.item, slot.quantity))
            return result

        def get_all_items(self):
            """Get all items in inventory as (item, quantity) tuples."""
            result = []
            for slot in self.slots:
                if not slot.is_empty():
                    result.append((slot.item, slot.quantity))
            return result

        def sort_by_category(self):
            """Sort inventory by category."""
            # Collect all items
            all_items = []
            for slot in self.slots:
                if not slot.is_empty():
                    all_items.append((slot.item, slot.quantity))
                    slot.clear()

            # Sort by category order
            category_order = ItemCategory.get_all()
            all_items.sort(key=lambda x: (
                category_order.index(x[0].category) if x[0].category in category_order else 999,
                x[0].name
            ))

            # Re-add items
            for item, qty in all_items:
                self.add_item(item, qty)

        def sort_by_name(self):
            """Sort inventory alphabetically by name."""
            all_items = []
            for slot in self.slots:
                if not slot.is_empty():
                    all_items.append((slot.item, slot.quantity))
                    slot.clear()

            all_items.sort(key=lambda x: x[0].name.lower())

            for item, qty in all_items:
                self.add_item(item, qty)

        # ====================================================================
        # GOLD MANAGEMENT
        # ====================================================================

        def add_gold(self, amount):
            """Add gold to inventory."""
            self.gold = max(0, self.gold + amount)

        def remove_gold(self, amount):
            """Remove gold from inventory. Returns True if successful."""
            if self.gold >= amount:
                self.gold -= amount
                return True
            return False

        def can_afford(self, amount):
            """Check if player can afford an amount."""
            return self.gold >= amount

        # ====================================================================
        # SAVE/LOAD SUPPORT
        # ====================================================================

        def to_dict(self):
            """Convert inventory to dictionary for saving."""
            slot_data = []
            for slot in self.slots:
                if not slot.is_empty():
                    slot_data.append({
                        "item_id": slot.item.id,
                        "quantity": slot.quantity
                    })

            equipped_data = {}
            for slot_name, item in self.equipment.slots.items():
                if item:
                    equipped_data[slot_name] = item.id

            return {
                "max_slots": self.max_slots,
                "slots": slot_data,
                "equipment": equipped_data,
                "gold": self.gold
            }

        @classmethod
        def from_dict(cls, data, item_database):
            """
            Create an Inventory from a dictionary.
            Requires an item database to look up items by ID.
            """
            inv = cls(data.get("max_slots", cls.DEFAULT_MAX_SLOTS))
            inv.gold = data.get("gold", 0)

            # Load items
            for slot_data in data.get("slots", []):
                item_id = slot_data["item_id"]
                quantity = slot_data["quantity"]
                if item_id in item_database:
                    inv.add_item(item_database[item_id], quantity)

            # Load equipment
            for slot_name, item_id in data.get("equipment", {}).items():
                if item_id in item_database:
                    inv.equipment.equip(item_database[item_id].copy())

            return inv


# ============================================================================
# EXAMPLE ITEMS DATABASE
# ============================================================================
# A dictionary of all items available in the game.
# Access items with: items["item_id"]

init python:

    # Create the items dictionary
    items = {}

    # ========================================================================
    # CONSUMABLES
    # ========================================================================

    items["health_potion"] = Item(
        id="health_potion",
        name="Health Potion",
        description="A red potion that restores 50 HP.",
        category=ItemCategory.CONSUMABLE,
        value=25,
        stackable=True,
        max_stack=99,
        effects={"heal_hp": 50}
    )

    items["mana_potion"] = Item(
        id="mana_potion",
        name="Mana Potion",
        description="A blue potion that restores 30 MP.",
        category=ItemCategory.CONSUMABLE,
        value=30,
        stackable=True,
        max_stack=99,
        effects={"heal_mp": 30}
    )

    items["elixir"] = Item(
        id="elixir",
        name="Elixir",
        description="A powerful potion that fully restores HP and MP.",
        category=ItemCategory.CONSUMABLE,
        value=200,
        stackable=True,
        max_stack=10,
        effects={"full_restore": True}
    )

    items["strength_tonic"] = Item(
        id="strength_tonic",
        name="Strength Tonic",
        description="Permanently increases Strength by 1.",
        category=ItemCategory.CONSUMABLE,
        value=500,
        stackable=True,
        max_stack=10,
        effects={"strength": 1}
    )

    items["xp_scroll"] = Item(
        id="xp_scroll",
        name="Experience Scroll",
        description="Grants 100 experience points when used.",
        category=ItemCategory.CONSUMABLE,
        value=150,
        stackable=True,
        max_stack=20,
        effects={"xp": 100}
    )

    # ========================================================================
    # WEAPONS
    # ========================================================================

    items["rusty_sword"] = Item(
        id="rusty_sword",
        name="Rusty Sword",
        description="An old sword, worn by time. Better than nothing.",
        category=ItemCategory.WEAPON,
        value=10,
        stackable=False,
        effects={"strength": 2}
    )

    items["iron_sword"] = Item(
        id="iron_sword",
        name="Iron Sword",
        description="A reliable iron sword. Standard issue for soldiers.",
        category=ItemCategory.WEAPON,
        value=100,
        stackable=False,
        effects={"strength": 5}
    )

    items["silver_blade"] = Item(
        id="silver_blade",
        name="Silver Blade",
        description="A finely crafted silver sword. Effective against dark creatures.",
        category=ItemCategory.WEAPON,
        value=500,
        stackable=False,
        effects={"strength": 10, "luck": 2}
    )

    items["enchanted_staff"] = Item(
        id="enchanted_staff",
        name="Enchanted Staff",
        description="A magical staff pulsing with arcane energy.",
        category=ItemCategory.WEAPON,
        value=400,
        stackable=False,
        effects={"intelligence": 8, "max_mp": 20}
    )

    # ========================================================================
    # ARMOR
    # ========================================================================

    items["leather_armor"] = Item(
        id="leather_armor",
        name="Leather Armor",
        description="Light armor made from tanned leather.",
        category=ItemCategory.ARMOR,
        value=50,
        stackable=False,
        effects={"defense": 3, "agility": 1}
    )

    items["chainmail"] = Item(
        id="chainmail",
        name="Chainmail",
        description="Armor made of interlocking metal rings.",
        category=ItemCategory.ARMOR,
        value=200,
        stackable=False,
        effects={"defense": 7}
    )

    items["plate_armor"] = Item(
        id="plate_armor",
        name="Plate Armor",
        description="Heavy armor offering excellent protection.",
        category=ItemCategory.ARMOR,
        value=800,
        stackable=False,
        effects={"defense": 15, "agility": -2}
    )

    items["mage_robes"] = Item(
        id="mage_robes",
        name="Mage Robes",
        description="Enchanted robes favored by spellcasters.",
        category=ItemCategory.ARMOR,
        value=350,
        stackable=False,
        effects={"defense": 2, "intelligence": 5, "max_mp": 30}
    )

    # ========================================================================
    # ACCESSORIES
    # ========================================================================

    items["lucky_charm"] = Item(
        id="lucky_charm",
        name="Lucky Charm",
        description="A small trinket said to bring good fortune.",
        category=ItemCategory.ACCESSORY,
        value=75,
        stackable=False,
        effects={"luck": 5}
    )

    items["power_ring"] = Item(
        id="power_ring",
        name="Ring of Power",
        description="A ring that enhances physical abilities.",
        category=ItemCategory.ACCESSORY,
        value=300,
        stackable=False,
        effects={"strength": 3, "defense": 2}
    )

    items["amulet_wisdom"] = Item(
        id="amulet_wisdom",
        name="Amulet of Wisdom",
        description="An ancient amulet that sharpens the mind.",
        category=ItemCategory.ACCESSORY,
        value=400,
        stackable=False,
        effects={"intelligence": 5, "charisma": 3}
    )

    items["speed_boots_charm"] = Item(
        id="speed_boots_charm",
        name="Swift Anklet",
        description="A magical anklet that enhances speed.",
        category=ItemCategory.ACCESSORY,
        value=250,
        stackable=False,
        effects={"agility": 7}
    )

    # ========================================================================
    # KEY ITEMS
    # ========================================================================

    items["old_key"] = Item(
        id="old_key",
        name="Old Key",
        description="A rusty key. It might open something in the library.",
        category=ItemCategory.KEY_ITEM,
        value=0,
        stackable=False
    )

    items["ancient_map"] = Item(
        id="ancient_map",
        name="Ancient Map",
        description="A faded map showing the location of a hidden treasure.",
        category=ItemCategory.KEY_ITEM,
        value=0,
        stackable=False
    )

    items["elena_journal"] = Item(
        id="elena_journal",
        name="Elena's Journal",
        description="Elena's research journal, filled with notes on local legends.",
        category=ItemCategory.KEY_ITEM,
        value=0,
        stackable=False
    )

    # ========================================================================
    # MISCELLANEOUS
    # ========================================================================

    items["gold_coin"] = Item(
        id="gold_coin",
        name="Gold Coin",
        description="A shiny gold coin. Can be sold for gold.",
        category=ItemCategory.MISC,
        value=10,
        stackable=True,
        max_stack=999
    )

    items["monster_fang"] = Item(
        id="monster_fang",
        name="Monster Fang",
        description="A sharp fang from a defeated monster. Crafting material.",
        category=ItemCategory.MISC,
        value=15,
        stackable=True,
        max_stack=99
    )

    items["magic_crystal"] = Item(
        id="magic_crystal",
        name="Magic Crystal",
        description="A glowing crystal infused with magical energy.",
        category=ItemCategory.MISC,
        value=50,
        stackable=True,
        max_stack=50
    )


# ============================================================================
# DEFAULT INVENTORY VARIABLE
# ============================================================================
# This creates a default inventory that will be saved with the game.
# Initialize at game start with:
#   $ inventory = Inventory(max_slots=20)

default inventory = None


# ============================================================================
# INVENTORY SCREEN UI
# ============================================================================
# Display inventory with: call screen inventory_screen
# Or as overlay: show screen inventory_screen

screen inventory_screen():
    tag menu
    modal True

    # Background overlay
    add Solid("#000000cc")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 30
        ypadding 20
        xminimum 800
        yminimum 500
        background Solid("#1a1a2e")

        vbox:
            spacing 15

            # Header
            hbox:
                xfill True

                text "Inventory" size 32 color "#ffffff"

                hbox:
                    xalign 1.0
                    spacing 20

                    if inventory:
                        text "Gold: [inventory.gold]" size 20 color "#ffdd44"
                        text "[inventory.get_used_slots()]/[inventory.max_slots] slots" size 18 color "#aaaaaa"

            null height 5

            hbox:
                spacing 20

                # Left panel - Equipment
                frame:
                    xsize 250
                    yminimum 400
                    background Solid("#2a2a4e")
                    padding (15, 15, 15, 15)

                    vbox:
                        spacing 10

                        text "Equipment" size 22 color "#66aaff" xalign 0.5

                        null height 10

                        # Equipment slots
                        for slot_name in ["weapon", "armor", "accessory"]:
                            $ slot_item = inventory.get_equipped(slot_name) if inventory else None
                            $ slot_display = slot_name.title()

                            frame:
                                xfill True
                                background Solid("#3a3a5e")
                                padding (10, 8, 10, 8)

                                hbox:
                                    spacing 10

                                    text "[slot_display]:" size 16 color "#aaaaaa" min_width 80

                                    if slot_item:
                                        textbutton slot_item.name:
                                            text_size 16
                                            text_color ItemCategory.get_color(slot_item.category)
                                            text_hover_color "#ffffff"
                                            action Show("item_detail_screen", item=slot_item, equipped=True, slot=slot_name)
                                    else:
                                        text "Empty" size 16 color "#666666"

                        null height 20

                        # Equipment stat bonuses
                        if inventory:
                            $ bonuses = inventory.get_equipment_bonuses()
                            if bonuses:
                                text "Bonuses:" size 18 color "#88ff88"
                                for stat, value in bonuses.items():
                                    $ sign = "+" if value >= 0 else ""
                                    text "  [stat.title()]: [sign][value]" size 14 color "#aaffaa"

                # Right panel - Items list
                frame:
                    xsize 480
                    yminimum 400
                    background Solid("#2a2a4e")
                    padding (15, 15, 15, 15)

                    vbox:
                        spacing 10

                        # Category filter tabs
                        hbox:
                            spacing 5
                            textbutton "All" action SetScreenVariable("filter_category", None) text_size 14
                            for cat in ItemCategory.get_all():
                                $ cat_name = ItemCategory.get_display_name(cat)[:4]
                                textbutton cat_name action SetScreenVariable("filter_category", cat) text_size 14

                        null height 5

                        # Items viewport
                        viewport:
                            scrollbars "vertical"
                            mousewheel True
                            ysize 320

                            vbox:
                                spacing 5

                                if inventory:
                                    $ all_items = inventory.get_all_items()
                                    $ current_filter = globals().get("filter_category", None)

                                    for item, qty in all_items:
                                        if current_filter is None or item.category == current_filter:
                                            $ item_color = ItemCategory.get_color(item.category)

                                            button:
                                                xfill True
                                                background Solid("#3a3a5e")
                                                hover_background Solid("#4a4a7e")
                                                padding (10, 8, 10, 8)
                                                action Show("item_detail_screen", item=item, equipped=False, slot=None)

                                                hbox:
                                                    spacing 10

                                                    text item.name size 16 color item_color min_width 200

                                                    if item.stackable:
                                                        text "x[qty]" size 14 color "#aaaaaa"

                                                    text ItemCategory.get_display_name(item.category)[:4] size 12 color "#666666" xalign 1.0
                                else:
                                    text "No inventory initialized." size 18 color "#ff6666" xalign 0.5

            # Sort and Close buttons
            hbox:
                xfill True
                spacing 20

                hbox:
                    spacing 10
                    if inventory:
                        textbutton "Sort by Name" action Function(inventory.sort_by_name) text_size 16
                        textbutton "Sort by Type" action Function(inventory.sort_by_category) text_size 16

                textbutton "Close" action Return() xalign 1.0 text_size 20


# Default filter category
default filter_category = None


# ============================================================================
# ITEM DETAIL SCREEN
# ============================================================================
# Shows detailed information about an item

screen item_detail_screen(item, equipped=False, slot=None):
    modal True

    # Background overlay
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 25
        ypadding 20
        xminimum 400
        background Solid("#2a2a4e")

        vbox:
            spacing 12

            # Item name with category color
            $ item_color = ItemCategory.get_color(item.category)
            text item.name size 28 color item_color

            # Category
            text ItemCategory.get_display_name(item.category) size 16 color "#aaaaaa"

            null height 5

            # Description
            text item.description size 16 color "#cccccc" xmaximum 350

            null height 10

            # Value
            text "Value: [item.value] gold" size 14 color "#ffdd44"

            # Effects
            if item.effects:
                null height 5
                text "Effects:" size 16 color "#88ff88"
                for effect, value in item.effects.items():
                    $ sign = "+" if isinstance(value, int) and value >= 0 else ""
                    if effect == "full_restore" and value:
                        text "  Full HP/MP Restore" size 14 color "#aaffaa"
                    elif effect == "heal_hp":
                        text "  Restore [value] HP" size 14 color "#aaffaa"
                    elif effect == "heal_mp":
                        text "  Restore [value] MP" size 14 color "#aaffaa"
                    elif effect == "xp":
                        text "  Grant [value] XP" size 14 color "#aaffaa"
                    else:
                        text "  [effect.title()]: [sign][value]" size 14 color "#aaffaa"

            null height 15

            # Action buttons
            hbox:
                spacing 15
                xalign 0.5

                if equipped:
                    textbutton "Unequip" action [Function(inventory.unequip_item, slot), Hide("item_detail_screen")] text_size 18
                else:
                    if item.is_consumable() and player:
                        textbutton "Use" action [Function(inventory.use_item, item.id, player), Hide("item_detail_screen")] text_size 18

                    if item.is_equippable():
                        textbutton "Equip" action [Function(inventory.equip_item, item.id), Hide("item_detail_screen")] text_size 18

                    textbutton "Drop" action [Function(inventory.remove_item, item.id, 1), Hide("item_detail_screen")] text_size 18

                textbutton "Cancel" action Hide("item_detail_screen") text_size 18


# ============================================================================
# COMPACT INVENTORY HUD
# ============================================================================
# Shows key items and gold. Use with:
#   show screen inventory_hud
#   hide screen inventory_hud

screen inventory_hud():
    tag inventory_hud
    zorder 100

    frame:
        xalign 1.0
        yalign 0.0
        xoffset -10
        yoffset 10
        xpadding 15
        ypadding 10
        background "#00000088"

        vbox:
            spacing 5

            if inventory:
                text "Gold: [inventory.gold]" size 14 color "#ffdd44"

                $ key_items = inventory.get_items_by_category(ItemCategory.KEY_ITEM)
                if key_items:
                    text "Key Items:" size 12 color "#ff44ff"
                    for item, qty in key_items[:3]:  # Show max 3
                        text "  [item.name]" size 11 color "#ffaaff"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

init python:

    def give_item(item_id, quantity=1):
        """Convenience function to add an item to player inventory."""
        if inventory and item_id in items:
            return inventory.add_item(items[item_id], quantity)
        return 0

    def take_item(item_id, quantity=1):
        """Convenience function to remove an item from player inventory."""
        if inventory:
            return inventory.remove_item(item_id, quantity)
        return 0

    def has_item(item_id, quantity=1):
        """Convenience function to check if player has an item."""
        if inventory:
            return inventory.has_item(item_id, quantity)
        return False

    def give_gold(amount):
        """Convenience function to add gold."""
        if inventory:
            inventory.add_gold(amount)

    def take_gold(amount):
        """Convenience function to remove gold."""
        if inventory:
            return inventory.remove_gold(amount)
        return False

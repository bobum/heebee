# Inventory System for Ren'Py
# Provides item management, equipment slots, and inventory UI

init python:
    import json

    # =========================================================================
    # ITEM CLASS
    # =========================================================================

    class Item:
        """Represents an item in the game."""

        def __init__(self, id, name, description, item_type="misc", value=0,
                     stackable=True, max_stack=99, effects=None, icon=None):
            self.id = id
            self.name = name
            self.description = description
            self.item_type = item_type  # weapon, armor, accessory, consumable, key_item, misc
            self.value = value  # Base sell/buy price
            self.stackable = stackable
            self.max_stack = max_stack if stackable else 1
            self.effects = effects or {}  # {"hp": 50, "mp": 20, "strength": 5}
            self.icon = icon  # Path to icon image

            # Equipment stats (for weapons/armor)
            self.attack = 0
            self.defense = 0
            self.magic = 0
            self.speed = 0

        def use(self, target=None):
            """Use the item. Override for specific behavior."""
            if self.item_type == "consumable" and self.effects:
                return self.effects.copy()
            return None

        def can_equip(self):
            """Check if item can be equipped."""
            return self.item_type in ["weapon", "armor", "accessory"]

        def __repr__(self):
            return f"Item({self.id}: {self.name})"

    # =========================================================================
    # INVENTORY CLASS
    # =========================================================================

    class Inventory:
        """Manages player's inventory."""

        def __init__(self, max_slots=50):
            self.max_slots = max_slots
            self.items = {}  # {item_id: quantity}
            self.equipment = {
                "weapon": None,
                "armor": None,
                "accessory": None
            }

        def add_item(self, item_id, quantity=1):
            """Add item(s) to inventory. Returns actual amount added."""
            if item_id not in ITEM_DATABASE:
                return 0

            item = ITEM_DATABASE[item_id]

            if item_id in self.items:
                current = self.items[item_id]
                max_add = item.max_stack - current
                actual_add = min(quantity, max_add)
                self.items[item_id] += actual_add
                return actual_add
            else:
                if len(self.items) >= self.max_slots:
                    return 0
                actual_add = min(quantity, item.max_stack)
                self.items[item_id] = actual_add
                return actual_add

        def remove_item(self, item_id, quantity=1):
            """Remove item(s) from inventory. Returns actual amount removed."""
            if item_id not in self.items:
                return 0

            current = self.items[item_id]
            actual_remove = min(quantity, current)
            self.items[item_id] -= actual_remove

            if self.items[item_id] <= 0:
                del self.items[item_id]

            return actual_remove

        def get_item_count(self, item_id):
            """Get quantity of an item."""
            return self.items.get(item_id, 0)

        def has_item(self, item_id, quantity=1):
            """Check if inventory has enough of an item."""
            return self.get_item_count(item_id) >= quantity

        def use_item(self, item_id, target=None):
            """Use a consumable item."""
            if not self.has_item(item_id):
                return None

            item = ITEM_DATABASE.get(item_id)
            if not item or item.item_type != "consumable":
                return None

            effects = item.use(target)
            if effects:
                self.remove_item(item_id, 1)
            return effects

        def equip_item(self, item_id):
            """Equip an item. Returns previously equipped item or None."""
            if not self.has_item(item_id):
                return None

            item = ITEM_DATABASE.get(item_id)
            if not item or not item.can_equip():
                return None

            slot = item.item_type
            previous = self.equipment[slot]

            # Unequip current
            if previous:
                self.add_item(previous, 1)

            # Equip new
            self.remove_item(item_id, 1)
            self.equipment[slot] = item_id

            return previous

        def unequip_item(self, slot):
            """Unequip item from slot."""
            if slot not in self.equipment or not self.equipment[slot]:
                return None

            item_id = self.equipment[slot]
            added = self.add_item(item_id, 1)

            if added > 0:
                self.equipment[slot] = None
                return item_id
            return None

        def get_equipped(self, slot):
            """Get equipped item in slot."""
            item_id = self.equipment.get(slot)
            if item_id:
                return ITEM_DATABASE.get(item_id)
            return None

        def get_equipment_bonus(self, stat):
            """Get total equipment bonus for a stat."""
            total = 0
            for slot, item_id in self.equipment.items():
                if item_id:
                    item = ITEM_DATABASE.get(item_id)
                    if item:
                        total += getattr(item, stat, 0)
            return total

        def get_items_by_type(self, item_type):
            """Get all items of a specific type."""
            result = []
            for item_id, qty in self.items.items():
                item = ITEM_DATABASE.get(item_id)
                if item and item.item_type == item_type:
                    result.append((item, qty))
            return result

        def get_all_items(self):
            """Get all items with their quantities."""
            result = []
            for item_id, qty in self.items.items():
                item = ITEM_DATABASE.get(item_id)
                if item:
                    result.append((item, qty))
            return result

        def is_full(self):
            """Check if inventory is full."""
            return len(self.items) >= self.max_slots

        def slots_used(self):
            """Get number of slots used."""
            return len(self.items)

        def to_dict(self):
            """Convert to dictionary for saving."""
            return {
                "items": self.items.copy(),
                "equipment": self.equipment.copy(),
                "max_slots": self.max_slots
            }

        def from_dict(self, data):
            """Load from dictionary."""
            self.items = data.get("items", {})
            self.equipment = data.get("equipment", {
                "weapon": None, "armor": None, "accessory": None
            })
            self.max_slots = data.get("max_slots", 50)

# =============================================================================
# ITEM DATABASE - Define all game items here
# =============================================================================

init python:
    ITEM_DATABASE = {}

    def register_item(item):
        """Register an item in the database."""
        ITEM_DATABASE[item.id] = item
        return item

# Define items
init python:
    # Consumables
    health_potion = Item(
        id="health_potion",
        name="Health Potion",
        description="Restores 50 HP.",
        item_type="consumable",
        value=25,
        effects={"hp": 50}
    )
    register_item(health_potion)

    mana_potion = Item(
        id="mana_potion",
        name="Mana Potion",
        description="Restores 30 MP.",
        item_type="consumable",
        value=30,
        effects={"mp": 30}
    )
    register_item(mana_potion)

    full_restore = Item(
        id="full_restore",
        name="Full Restore",
        description="Fully restores HP and MP.",
        item_type="consumable",
        value=200,
        effects={"hp": 9999, "mp": 9999}
    )
    register_item(full_restore)

    antidote = Item(
        id="antidote",
        name="Antidote",
        description="Cures poison status.",
        item_type="consumable",
        value=15,
        effects={"cure": "poison"}
    )
    register_item(antidote)

    # Weapons
    rusty_sword = Item(
        id="rusty_sword",
        name="Rusty Sword",
        description="An old, worn blade. Better than nothing.",
        item_type="weapon",
        value=50,
        stackable=False
    )
    rusty_sword.attack = 5
    register_item(rusty_sword)

    iron_sword = Item(
        id="iron_sword",
        name="Iron Sword",
        description="A sturdy iron blade.",
        item_type="weapon",
        value=150,
        stackable=False
    )
    iron_sword.attack = 12
    register_item(iron_sword)

    magic_staff = Item(
        id="magic_staff",
        name="Magic Staff",
        description="A staff imbued with magical energy.",
        item_type="weapon",
        value=200,
        stackable=False
    )
    magic_staff.attack = 5
    magic_staff.magic = 15
    register_item(magic_staff)

    # Armor
    leather_armor = Item(
        id="leather_armor",
        name="Leather Armor",
        description="Basic protection made of leather.",
        item_type="armor",
        value=100,
        stackable=False
    )
    leather_armor.defense = 8
    register_item(leather_armor)

    chainmail = Item(
        id="chainmail",
        name="Chainmail",
        description="Interlocking metal rings provide good defense.",
        item_type="armor",
        value=300,
        stackable=False
    )
    chainmail.defense = 15
    chainmail.speed = -2
    register_item(chainmail)

    # Accessories
    silver_ring = Item(
        id="silver_ring",
        name="Silver Ring",
        description="A simple silver ring. Slightly boosts magic.",
        item_type="accessory",
        value=75,
        stackable=False
    )
    silver_ring.magic = 3
    register_item(silver_ring)

    speed_boots = Item(
        id="speed_boots",
        name="Speed Boots",
        description="Enchanted boots that increase agility.",
        item_type="accessory",
        value=250,
        stackable=False
    )
    speed_boots.speed = 10
    register_item(speed_boots)

    # Key Items
    old_key = Item(
        id="old_key",
        name="Old Key",
        description="An ornate key. Might open something important.",
        item_type="key_item",
        value=0,
        stackable=False
    )
    register_item(old_key)

    ancient_map = Item(
        id="ancient_map",
        name="Ancient Map",
        description="A weathered map showing mysterious locations.",
        item_type="key_item",
        value=0,
        stackable=False
    )
    register_item(ancient_map)

    # Misc
    gold_nugget = Item(
        id="gold_nugget",
        name="Gold Nugget",
        description="A small chunk of gold. Can be sold for a good price.",
        item_type="misc",
        value=100
    )
    register_item(gold_nugget)

    monster_fang = Item(
        id="monster_fang",
        name="Monster Fang",
        description="A sharp fang from a defeated monster.",
        item_type="misc",
        value=25
    )
    register_item(monster_fang)

# =============================================================================
# PLAYER INVENTORY INSTANCE
# =============================================================================

default player_inventory = Inventory(max_slots=50)

# =============================================================================
# INVENTORY SCREENS
# =============================================================================

screen inventory_screen():
    tag menu
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 900
        ysize 600
        background Solid("#1a1a2e")
        padding (20, 20)

        vbox:
            spacing 10

            # Header
            hbox:
                text "Inventory" size 32 color "#66aaff"
                xfill True
                text "[player_inventory.slots_used()]/[player_inventory.max_slots] slots" size 20 color "#aaa" xalign 1.0

            null height 10

            # Category tabs
            hbox:
                spacing 10
                textbutton "All" action SetScreenVariable("inv_filter", None)
                textbutton "Weapons" action SetScreenVariable("inv_filter", "weapon")
                textbutton "Armor" action SetScreenVariable("inv_filter", "armor")
                textbutton "Consumables" action SetScreenVariable("inv_filter", "consumable")
                textbutton "Key Items" action SetScreenVariable("inv_filter", "key_item")
                textbutton "Misc" action SetScreenVariable("inv_filter", "misc")

            null height 10

            # Equipment slots
            frame:
                background Solid("#2a2a4e")
                padding (10, 10)
                xfill True

                hbox:
                    spacing 30

                    vbox:
                        text "Weapon:" size 16 color "#888"
                        if player_inventory.equipment["weapon"]:
                            $ eq_weapon = ITEM_DATABASE.get(player_inventory.equipment["weapon"])
                            textbutton eq_weapon.name action Function(player_inventory.unequip_item, "weapon")
                        else:
                            text "Empty" size 14 color "#555"

                    vbox:
                        text "Armor:" size 16 color "#888"
                        if player_inventory.equipment["armor"]:
                            $ eq_armor = ITEM_DATABASE.get(player_inventory.equipment["armor"])
                            textbutton eq_armor.name action Function(player_inventory.unequip_item, "armor")
                        else:
                            text "Empty" size 14 color "#555"

                    vbox:
                        text "Accessory:" size 16 color "#888"
                        if player_inventory.equipment["accessory"]:
                            $ eq_acc = ITEM_DATABASE.get(player_inventory.equipment["accessory"])
                            textbutton eq_acc.name action Function(player_inventory.unequip_item, "accessory")
                        else:
                            text "Empty" size 14 color "#555"

            null height 10

            # Item list
            default inv_filter = None

            viewport:
                scrollbars "vertical"
                mousewheel True
                ysize 300
                xfill True

                vbox:
                    spacing 5

                    for item, qty in player_inventory.get_all_items():
                        if inv_filter is None or item.item_type == inv_filter:
                            frame:
                                background Solid("#333355")
                                hover_background Solid("#4444aa")
                                padding (10, 5)
                                xfill True

                                hbox:
                                    spacing 15

                                    text item.name size 18 color "#fff" yalign 0.5 xsize 200
                                    text "x[qty]" size 16 color "#aaa" yalign 0.5 xsize 50
                                    text item.description size 14 color "#888" yalign 0.5

                                    hbox:
                                        xalign 1.0
                                        spacing 5

                                        if item.item_type == "consumable":
                                            textbutton "Use" action Function(player_inventory.use_item, item.id) yalign 0.5

                                        if item.can_equip():
                                            textbutton "Equip" action Function(player_inventory.equip_item, item.id) yalign 0.5

            # Close button
            hbox:
                xalign 0.5
                textbutton "Close" action Hide("inventory_screen")

style inventory_button:
    background Solid("#444466")
    hover_background Solid("#5555aa")
    padding (10, 5)

style inventory_button_text:
    size 14
    color "#ccc"
    hover_color "#fff"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

init python:
    def give_item(item_id, quantity=1):
        """Give item to player. Shows notification."""
        added = player_inventory.add_item(item_id, quantity)
        if added > 0:
            item = ITEM_DATABASE.get(item_id)
            renpy.notify(f"Obtained {item.name} x{added}")
        return added

    def take_item(item_id, quantity=1):
        """Remove item from player."""
        return player_inventory.remove_item(item_id, quantity)

    def has_item(item_id, quantity=1):
        """Check if player has item."""
        return player_inventory.has_item(item_id, quantity)

    def save_inventory():
        """Save inventory to persistent data."""
        persistent.inventory_data = player_inventory.to_dict()

    def load_inventory():
        """Load inventory from persistent data."""
        if hasattr(persistent, 'inventory_data') and persistent.inventory_data:
            player_inventory.from_dict(persistent.inventory_data)

# =============================================================================
# EXAMPLE USAGE (in script.rpy):
# =============================================================================
#
# # Give items
# $ give_item("health_potion", 5)
# $ give_item("rusty_sword")
#
# # Check items
# if has_item("old_key"):
#     "You have the key!"
#
# # Show inventory
# call screen inventory_screen
#
# # Equip item
# $ player_inventory.equip_item("iron_sword")
#
# # Get equipment bonus
# $ total_attack = player_inventory.get_equipment_bonus("attack")

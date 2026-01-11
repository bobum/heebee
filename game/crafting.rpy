# Crafting System for Ren'Py Visual Novel
# This module provides a comprehensive crafting system with recipes,
# material management, recipe discovery/unlocking, and crafting UI.

init python:

    # =========================================================================
    # RECIPE CLASS - Defines a craftable item recipe
    # =========================================================================

    class Recipe:
        """
        Represents a crafting recipe.

        Attributes:
            id (str): Unique identifier for the recipe
            name (str): Display name of the recipe
            ingredients (dict): Dictionary of item_id: quantity required
            result_item (str): ID of the item produced
            result_quantity (int): Number of items produced
            unlock_condition (str or callable): Condition for recipe availability
            description (str): Description of the recipe
            category (str): Category for organization (e.g., "weapons", "potions")
            unlocked (bool): Whether the recipe has been discovered/unlocked
        """

        def __init__(self, id, name, ingredients, result_item, result_quantity=1,
                     unlock_condition=None, description="", category="misc"):
            self.id = id
            self.name = name
            self.ingredients = ingredients  # {item_id: quantity, ...}
            self.result_item = result_item
            self.result_quantity = result_quantity
            self.unlock_condition = unlock_condition
            self.description = description
            self.category = category
            self.unlocked = unlock_condition is None  # Auto-unlock if no condition

        def get_ingredients_list(self):
            """Return ingredients as a list of tuples (item_id, quantity)."""
            return list(self.ingredients.items())

        def __repr__(self):
            return f"Recipe(id={self.id!r}, name={self.name!r})"

    # =========================================================================
    # CRAFTING MANAGER CLASS - Central manager for all crafting operations
    # =========================================================================

    class CraftingManager:
        """
        Central manager for the crafting system.

        Handles recipe registration, material checking, crafting operations,
        and recipe discovery/unlocking.

        Attributes:
            recipes (dict): Dictionary of recipe_id: Recipe objects
            inventory_getter (callable): Function to get player inventory
            inventory_setter (callable): Function to modify player inventory
        """

        def __init__(self):
            self.recipes = {}
            self._inventory_getter = None
            self._inventory_setter = None
            self._item_adder = None
            self._item_remover = None

        # ---------------------------------------------------------------------
        # Inventory Integration
        # ---------------------------------------------------------------------

        def set_inventory_callbacks(self, getter, setter=None, adder=None, remover=None):
            """
            Set callbacks for inventory integration.

            Args:
                getter (callable): Function that returns inventory dict {item_id: quantity}
                setter (callable): Function to set entire inventory (optional)
                adder (callable): Function to add items: adder(item_id, quantity)
                remover (callable): Function to remove items: remover(item_id, quantity)
            """
            self._inventory_getter = getter
            self._inventory_setter = setter
            self._item_adder = adder
            self._item_remover = remover

        def get_inventory(self):
            """Get the current player inventory."""
            if self._inventory_getter:
                return self._inventory_getter()
            return {}

        def add_item(self, item_id, quantity):
            """Add items to player inventory."""
            if self._item_adder:
                self._item_adder(item_id, quantity)
                return True
            elif self._inventory_setter:
                inv = self.get_inventory()
                inv[item_id] = inv.get(item_id, 0) + quantity
                self._inventory_setter(inv)
                return True
            return False

        def remove_item(self, item_id, quantity):
            """Remove items from player inventory."""
            if self._item_remover:
                self._item_remover(item_id, quantity)
                return True
            elif self._inventory_setter:
                inv = self.get_inventory()
                current = inv.get(item_id, 0)
                if current >= quantity:
                    inv[item_id] = current - quantity
                    if inv[item_id] == 0:
                        del inv[item_id]
                    self._inventory_setter(inv)
                    return True
            return False

        # ---------------------------------------------------------------------
        # Recipe Management
        # ---------------------------------------------------------------------

        def register_recipe(self, recipe):
            """
            Register a new recipe in the crafting system.

            Args:
                recipe (Recipe): The recipe to register

            Returns:
                Recipe: The registered recipe
            """
            self.recipes[recipe.id] = recipe
            return recipe

        def register_recipes(self, recipes):
            """
            Register multiple recipes at once.

            Args:
                recipes (list): List of Recipe objects

            Returns:
                list: List of registered recipes
            """
            for recipe in recipes:
                self.register_recipe(recipe)
            return recipes

        def get_recipe(self, recipe_id):
            """
            Get a recipe by its ID.

            Args:
                recipe_id (str): The recipe identifier

            Returns:
                Recipe: The recipe or None if not found
            """
            return self.recipes.get(recipe_id)

        def remove_recipe(self, recipe_id):
            """
            Remove a recipe from the system.

            Args:
                recipe_id (str): The recipe identifier

            Returns:
                bool: True if removed, False if not found
            """
            if recipe_id in self.recipes:
                del self.recipes[recipe_id]
                return True
            return False

        def get_all_recipes(self):
            """Get all registered recipes."""
            return list(self.recipes.values())

        def get_recipes_by_category(self, category):
            """
            Get all recipes in a specific category.

            Args:
                category (str): The category to filter by

            Returns:
                list: List of recipes in the category
            """
            return [r for r in self.recipes.values() if r.category == category]

        def get_categories(self):
            """Get all unique recipe categories."""
            return list(set(r.category for r in self.recipes.values()))

        # ---------------------------------------------------------------------
        # Recipe Unlocking/Discovery
        # ---------------------------------------------------------------------

        def unlock_recipe(self, recipe_id):
            """
            Unlock a recipe for the player.

            Args:
                recipe_id (str): The recipe identifier

            Returns:
                bool: True if unlocked, False if not found or already unlocked
            """
            recipe = self.get_recipe(recipe_id)
            if recipe and not recipe.unlocked:
                recipe.unlocked = True
                return True
            return False

        def lock_recipe(self, recipe_id):
            """
            Lock a recipe (hide it from the player).

            Args:
                recipe_id (str): The recipe identifier

            Returns:
                bool: True if locked, False if not found
            """
            recipe = self.get_recipe(recipe_id)
            if recipe:
                recipe.unlocked = False
                return True
            return False

        def is_recipe_unlocked(self, recipe_id):
            """
            Check if a recipe is unlocked.

            Args:
                recipe_id (str): The recipe identifier

            Returns:
                bool: True if unlocked, False otherwise
            """
            recipe = self.get_recipe(recipe_id)
            return recipe.unlocked if recipe else False

        def check_unlock_conditions(self, context=None):
            """
            Check all recipe unlock conditions and unlock eligible recipes.

            Args:
                context (dict): Optional context for condition evaluation

            Returns:
                list: List of newly unlocked recipe IDs
            """
            newly_unlocked = []
            for recipe in self.recipes.values():
                if not recipe.unlocked and recipe.unlock_condition:
                    should_unlock = False

                    if callable(recipe.unlock_condition):
                        try:
                            should_unlock = recipe.unlock_condition(context)
                        except Exception:
                            should_unlock = False
                    elif isinstance(recipe.unlock_condition, str):
                        # String conditions are evaluated as simple flags
                        if context and recipe.unlock_condition in context:
                            should_unlock = bool(context[recipe.unlock_condition])

                    if should_unlock:
                        recipe.unlocked = True
                        newly_unlocked.append(recipe.id)

            return newly_unlocked

        def get_unlocked_recipes(self):
            """Get all unlocked recipes."""
            return [r for r in self.recipes.values() if r.unlocked]

        def get_locked_recipes(self):
            """Get all locked recipes."""
            return [r for r in self.recipes.values() if not r.unlocked]

        # ---------------------------------------------------------------------
        # Crafting Operations
        # ---------------------------------------------------------------------

        def can_craft(self, recipe_id):
            """
            Check if the player can craft a recipe (has all materials).

            Args:
                recipe_id (str): The recipe identifier

            Returns:
                bool: True if player has all required materials
            """
            recipe = self.get_recipe(recipe_id)
            if not recipe or not recipe.unlocked:
                return False

            inventory = self.get_inventory()
            for item_id, required_qty in recipe.ingredients.items():
                if inventory.get(item_id, 0) < required_qty:
                    return False
            return True

        def get_missing_ingredients(self, recipe_id):
            """
            Get a list of missing ingredients for a recipe.

            Args:
                recipe_id (str): The recipe identifier

            Returns:
                dict: Dictionary of {item_id: missing_quantity} or empty if can craft
            """
            recipe = self.get_recipe(recipe_id)
            if not recipe:
                return {}

            inventory = self.get_inventory()
            missing = {}
            for item_id, required_qty in recipe.ingredients.items():
                have = inventory.get(item_id, 0)
                if have < required_qty:
                    missing[item_id] = required_qty - have
            return missing

        def craft(self, recipe_id):
            """
            Craft an item using a recipe.

            Consumes the required materials and produces the result item.

            Args:
                recipe_id (str): The recipe identifier

            Returns:
                tuple: (success: bool, message: str, result_item: str or None)
            """
            recipe = self.get_recipe(recipe_id)
            if not recipe:
                return False, "Recipe not found.", None

            if not recipe.unlocked:
                return False, "Recipe is locked.", None

            if not self.can_craft(recipe_id):
                missing = self.get_missing_ingredients(recipe_id)
                missing_str = ", ".join([f"{k}: {v}" for k, v in missing.items()])
                return False, f"Missing materials: {missing_str}", None

            # Consume ingredients
            for item_id, quantity in recipe.ingredients.items():
                self.remove_item(item_id, quantity)

            # Produce result
            self.add_item(recipe.result_item, recipe.result_quantity)

            return True, f"Crafted {recipe.result_quantity}x {recipe.name}!", recipe.result_item

        def craft_multiple(self, recipe_id, count):
            """
            Craft multiple instances of a recipe.

            Args:
                recipe_id (str): The recipe identifier
                count (int): Number of times to craft

            Returns:
                tuple: (success_count: int, message: str)
            """
            success_count = 0
            for _ in range(count):
                success, _, _ = self.craft(recipe_id)
                if success:
                    success_count += 1
                else:
                    break
            return success_count, f"Crafted {success_count} times."

        def get_max_craftable(self, recipe_id):
            """
            Get the maximum number of times a recipe can be crafted.

            Args:
                recipe_id (str): The recipe identifier

            Returns:
                int: Maximum craft count (0 if cannot craft)
            """
            recipe = self.get_recipe(recipe_id)
            if not recipe or not recipe.unlocked:
                return 0

            inventory = self.get_inventory()
            max_count = float('inf')

            for item_id, required_qty in recipe.ingredients.items():
                have = inventory.get(item_id, 0)
                possible = have // required_qty
                max_count = min(max_count, possible)

            return int(max_count) if max_count != float('inf') else 0

        def get_available_recipes(self):
            """
            Get all recipes that are unlocked and can be crafted.

            Returns:
                list: List of recipes that can currently be crafted
            """
            return [r for r in self.recipes.values()
                    if r.unlocked and self.can_craft(r.id)]

        def get_craftable_recipes(self):
            """
            Alias for get_available_recipes.

            Returns:
                list: List of recipes that can currently be crafted
            """
            return self.get_available_recipes()


# =============================================================================
# GLOBAL CRAFTING MANAGER INSTANCE
# =============================================================================

default crafting_manager = CraftingManager()

# =============================================================================
# SIMPLE INVENTORY SYSTEM (for standalone use)
# =============================================================================

default player_inventory = {}

init python:
    def get_player_inventory():
        """Get the player inventory dictionary."""
        return store.player_inventory

    def set_player_inventory(inv):
        """Set the player inventory dictionary."""
        store.player_inventory = inv

    def add_to_inventory(item_id, quantity=1):
        """Add items to player inventory."""
        store.player_inventory[item_id] = store.player_inventory.get(item_id, 0) + quantity

    def remove_from_inventory(item_id, quantity=1):
        """Remove items from player inventory."""
        current = store.player_inventory.get(item_id, 0)
        if current >= quantity:
            store.player_inventory[item_id] = current - quantity
            if store.player_inventory[item_id] == 0:
                del store.player_inventory[item_id]
            return True
        return False

    def setup_crafting_inventory():
        """Connect the crafting manager to the inventory system."""
        crafting_manager.set_inventory_callbacks(
            getter=get_player_inventory,
            setter=set_player_inventory,
            adder=add_to_inventory,
            remover=remove_from_inventory
        )

# =============================================================================
# ITEM NAME REGISTRY (for display purposes)
# =============================================================================

init python:
    # Simple item name registry - can be expanded or replaced
    ITEM_NAMES = {
        # Raw materials
        "wood": "Wood",
        "stone": "Stone",
        "iron_ore": "Iron Ore",
        "gold_ore": "Gold Ore",
        "leather": "Leather",
        "cloth": "Cloth",
        "herb": "Herb",
        "flower": "Flower",
        "water": "Water",
        "coal": "Coal",

        # Processed materials
        "iron_ingot": "Iron Ingot",
        "gold_ingot": "Gold Ingot",
        "plank": "Wooden Plank",
        "refined_leather": "Refined Leather",

        # Crafted items
        "health_potion": "Health Potion",
        "mana_potion": "Mana Potion",
        "iron_sword": "Iron Sword",
        "iron_shield": "Iron Shield",
        "wooden_bow": "Wooden Bow",
        "leather_armor": "Leather Armor",
        "torch": "Torch",
        "rope": "Rope",
        "bandage": "Bandage",
        "antidote": "Antidote",
    }

    def get_item_name(item_id):
        """Get display name for an item."""
        return ITEM_NAMES.get(item_id, item_id.replace("_", " ").title())

# =============================================================================
# EXAMPLE RECIPE DEFINITIONS
# =============================================================================

init python:
    def setup_example_recipes():
        """Initialize example recipes for the crafting system."""

        # Setup inventory integration
        setup_crafting_inventory()

        # Basic recipes (always unlocked)
        crafting_manager.register_recipe(Recipe(
            id="health_potion",
            name="Health Potion",
            ingredients={"herb": 2, "water": 1},
            result_item="health_potion",
            result_quantity=1,
            unlock_condition=None,
            description="A basic healing potion that restores health.",
            category="potions"
        ))

        crafting_manager.register_recipe(Recipe(
            id="bandage",
            name="Bandage",
            ingredients={"cloth": 2},
            result_item="bandage",
            result_quantity=3,
            unlock_condition=None,
            description="Simple bandages for treating wounds.",
            category="consumables"
        ))

        crafting_manager.register_recipe(Recipe(
            id="torch",
            name="Torch",
            ingredients={"wood": 1, "cloth": 1},
            result_item="torch",
            result_quantity=2,
            unlock_condition=None,
            description="A simple torch to light dark areas.",
            category="tools"
        ))

        crafting_manager.register_recipe(Recipe(
            id="rope",
            name="Rope",
            ingredients={"cloth": 3},
            result_item="rope",
            result_quantity=1,
            unlock_condition=None,
            description="A sturdy rope for various uses.",
            category="tools"
        ))

        # Intermediate recipes (require unlocking)
        crafting_manager.register_recipe(Recipe(
            id="iron_ingot",
            name="Iron Ingot",
            ingredients={"iron_ore": 2, "coal": 1},
            result_item="iron_ingot",
            result_quantity=1,
            unlock_condition="learned_smelting",
            description="Smelt iron ore into usable ingots.",
            category="materials"
        ))

        crafting_manager.register_recipe(Recipe(
            id="iron_sword",
            name="Iron Sword",
            ingredients={"iron_ingot": 3, "wood": 1, "leather": 1},
            result_item="iron_sword",
            result_quantity=1,
            unlock_condition="learned_smithing",
            description="A reliable iron sword for combat.",
            category="weapons"
        ))

        crafting_manager.register_recipe(Recipe(
            id="iron_shield",
            name="Iron Shield",
            ingredients={"iron_ingot": 4, "leather": 2},
            result_item="iron_shield",
            result_quantity=1,
            unlock_condition="learned_smithing",
            description="A sturdy iron shield for defense.",
            category="armor"
        ))

        crafting_manager.register_recipe(Recipe(
            id="leather_armor",
            name="Leather Armor",
            ingredients={"leather": 5, "cloth": 2},
            result_item="leather_armor",
            result_quantity=1,
            unlock_condition="learned_tailoring",
            description="Light armor made from leather.",
            category="armor"
        ))

        crafting_manager.register_recipe(Recipe(
            id="mana_potion",
            name="Mana Potion",
            ingredients={"flower": 2, "water": 1, "herb": 1},
            result_item="mana_potion",
            result_quantity=1,
            unlock_condition="learned_alchemy",
            description="A mystical potion that restores magical energy.",
            category="potions"
        ))

        crafting_manager.register_recipe(Recipe(
            id="antidote",
            name="Antidote",
            ingredients={"herb": 3, "water": 2},
            result_item="antidote",
            result_quantity=1,
            unlock_condition="learned_alchemy",
            description="Cures poison and other ailments.",
            category="potions"
        ))

        crafting_manager.register_recipe(Recipe(
            id="wooden_bow",
            name="Wooden Bow",
            ingredients={"wood": 3, "cloth": 2},
            result_item="wooden_bow",
            result_quantity=1,
            unlock_condition="learned_woodworking",
            description="A basic bow for ranged combat.",
            category="weapons"
        ))

# Initialize recipes when game starts
label crafting_init:
    $ setup_example_recipes()
    return

# =============================================================================
# CRAFTING UI SCREENS
# =============================================================================

# Selected recipe for detail view
default selected_recipe = None

screen crafting_menu():
    tag menu

    use game_menu(_("Crafting"), scroll="viewport"):

        style_prefix "crafting"

        vbox:
            spacing 20

            # Category filter buttons
            hbox:
                spacing 10
                text "Categories:" size 18 color "#aaaaaa" yalign 0.5

                textbutton "All" action SetVariable("crafting_category_filter", None):
                    style "crafting_category_button"

                for cat in crafting_manager.get_categories():
                    textbutton cat.title() action SetVariable("crafting_category_filter", cat):
                        style "crafting_category_button"

            null height 10

            # Main content area
            hbox:
                spacing 20

                # Recipe list (left side)
                frame:
                    xsize 350
                    ysize 500
                    background "#2a2a2a"
                    padding (15, 15)

                    vbox:
                        spacing 5

                        text "Available Recipes" size 22 color "#ffffff"
                        null height 10

                        viewport:
                            ysize 420
                            scrollbars "vertical"
                            mousewheel True

                            vbox:
                                spacing 8

                                for recipe in crafting_manager.get_unlocked_recipes():
                                    if not defined("crafting_category_filter") or crafting_category_filter is None or recipe.category == crafting_category_filter:
                                        $ can_craft = crafting_manager.can_craft(recipe.id)
                                        $ btn_color = "#3a5a3a" if can_craft else "#3a3a3a"
                                        $ text_color = "#ffffff" if can_craft else "#888888"

                                        button:
                                            xfill True
                                            background btn_color
                                            hover_background "#4a6a4a" if can_craft else "#4a4a4a"
                                            padding (10, 8)
                                            action SetVariable("selected_recipe", recipe.id)

                                            hbox:
                                                spacing 10
                                                text recipe.name size 16 color text_color
                                                if can_craft:
                                                    text "(Ready)" size 14 color "#88ff88" xalign 1.0

                # Recipe details (right side)
                frame:
                    xsize 400
                    ysize 500
                    background "#2a2a2a"
                    padding (20, 20)

                    if selected_recipe:
                        $ recipe = crafting_manager.get_recipe(selected_recipe)
                        if recipe:
                            vbox:
                                spacing 15

                                # Recipe name and category
                                text recipe.name size 26 color "#ffffff"
                                text "[" + recipe.category.title() + "]" size 14 color "#888888"

                                null height 5

                                # Description
                                text recipe.description size 16 color "#cccccc"

                                null height 10

                                # Ingredients section
                                text "Ingredients:" size 18 color "#ffcc66"

                                frame:
                                    xfill True
                                    background "#1a1a1a"
                                    padding (15, 10)

                                    vbox:
                                        spacing 5
                                        for item_id, qty in recipe.ingredients.items():
                                            $ have = crafting_manager.get_inventory().get(item_id, 0)
                                            $ has_enough = have >= qty
                                            $ color = "#88ff88" if has_enough else "#ff8888"

                                            hbox:
                                                text get_item_name(item_id) size 16 color "#ffffff" min_width 150
                                                text "[have]/[qty]" size 16 color color

                                null height 10

                                # Result section
                                text "Result:" size 18 color "#66ccff"

                                frame:
                                    xfill True
                                    background "#1a1a1a"
                                    padding (15, 10)

                                    hbox:
                                        text get_item_name(recipe.result_item) size 16 color "#ffffff"
                                        text " x[recipe.result_quantity]" size 16 color "#aaaaaa"

                                null height 15

                                # Craft button
                                $ can_craft = crafting_manager.can_craft(recipe.id)
                                $ max_craft = crafting_manager.get_max_craftable(recipe.id)

                                hbox:
                                    spacing 15

                                    textbutton "Craft" action Function(do_craft, recipe.id):
                                        sensitive can_craft
                                        style "crafting_craft_button"

                                    if max_craft > 1:
                                        textbutton "Craft All ([max_craft])" action Function(do_craft_all, recipe.id):
                                            sensitive can_craft
                                            style "crafting_craft_button"

                    else:
                        vbox:
                            yalign 0.5
                            xalign 0.5
                            text "Select a recipe" size 20 color "#666666"
                            text "to view details" size 16 color "#444444"

# =============================================================================
# CRAFTING UI HELPER FUNCTIONS
# =============================================================================

init python:
    def do_craft(recipe_id):
        """Execute crafting and show notification."""
        success, message, _ = crafting_manager.craft(recipe_id)
        renpy.notify(message)

    def do_craft_all(recipe_id):
        """Craft as many as possible and show notification."""
        count, message = crafting_manager.craft_multiple(
            recipe_id,
            crafting_manager.get_max_craftable(recipe_id)
        )
        renpy.notify(message)

# Filter variable for category
default crafting_category_filter = None

# =============================================================================
# INVENTORY DISPLAY SCREEN
# =============================================================================

screen inventory_screen():
    tag menu

    use game_menu(_("Inventory"), scroll="viewport"):

        style_prefix "inventory"

        vbox:
            spacing 15

            text "Your Items" size 28 color "#ffffff"

            null height 10

            if player_inventory:
                for item_id, quantity in player_inventory.items():
                    frame:
                        xfill True
                        background "#333333"
                        padding (15, 10)

                        hbox:
                            text get_item_name(item_id) size 18 color "#ffffff" min_width 200
                            text "x[quantity]" size 18 color "#aaaaaa"
            else:
                text "Your inventory is empty." size 16 color "#888888"

# =============================================================================
# STYLES FOR CRAFTING SCREENS
# =============================================================================

style crafting_vbox:
    xfill True
    spacing 10

style crafting_category_button:
    background "#404040"
    hover_background "#505050"
    padding (15, 8)

style crafting_category_button_text:
    size 14
    color "#cccccc"
    hover_color "#ffffff"

style crafting_craft_button:
    background "#2a5a2a"
    hover_background "#3a7a3a"
    insensitive_background "#2a2a2a"
    padding (20, 12)

style crafting_craft_button_text:
    size 18
    color "#ffffff"
    hover_color "#ffffff"
    insensitive_color "#666666"

style inventory_vbox:
    xfill True
    spacing 10

# =============================================================================
# HELPER LABELS FOR CRAFTING OPERATIONS
# =============================================================================

# Open crafting menu
label open_crafting:
    $ setup_crafting_inventory()
    call screen crafting_menu
    return

# Unlock a recipe with notification
label unlock_recipe(recipe_id, notify=True):
    $ success = crafting_manager.unlock_recipe(recipe_id)
    if success and notify:
        $ recipe = crafting_manager.get_recipe(recipe_id)
        if recipe:
            $ renpy.notify("New recipe unlocked: [recipe.name]")
    return

# Give items to player
label give_item(item_id, quantity=1, notify=True):
    $ add_to_inventory(item_id, quantity)
    if notify:
        $ item_name = get_item_name(item_id)
        $ renpy.notify("Received [quantity]x [item_name]")
    return

# =============================================================================
# EXAMPLE USAGE IN GAME SCRIPT
# =============================================================================

# Example label showing crafting system usage:
#
# label example_crafting:
#     "You found some materials!"
#     call give_item("herb", 5)
#     call give_item("water", 3)
#     call give_item("cloth", 4)
#
#     "The herbalist taught you alchemy."
#     call unlock_recipe("mana_potion")
#     call unlock_recipe("antidote")
#
#     "Let's see what we can craft."
#     call open_crafting
#
#     return
#
# To check if player can craft something:
#     if crafting_manager.can_craft("health_potion"):
#         "You can make a health potion!"
#
# To craft programmatically:
#     $ success, msg, item = crafting_manager.craft("health_potion")

# Relationship Meters System for Ren'Py Visual Novel
# This module provides a comprehensive relationship tracking system with
# affection, trust, respect meters, relationship tiers, and faction reputation.

init python:
    import math

    # =========================================================================
    # RELATIONSHIP TIERS - Define thresholds for relationship progression
    # =========================================================================

    RELATIONSHIP_TIERS = {
        "stranger": {"min": 0, "max": 19, "label": "Stranger"},
        "acquaintance": {"min": 20, "max": 39, "label": "Acquaintance"},
        "friend": {"min": 40, "max": 59, "label": "Friend"},
        "close_friend": {"min": 60, "max": 79, "label": "Close Friend"},
        "best_friend": {"min": 80, "max": 99, "label": "Best Friend"},
        "romantic": {"min": 100, "max": 150, "label": "Romantic Partner"}
    }

    # =========================================================================
    # DIALOGUE/EVENT UNLOCKS - Content unlocked at specific relationship levels
    # =========================================================================

    RELATIONSHIP_UNLOCKS = {
        20: "casual_conversation",      # Acquaintance - can have casual talks
        40: "personal_story",           # Friend - shares personal stories
        60: "secret_sharing",           # Close Friend - shares secrets
        80: "deep_bond_event",          # Best Friend - special bonding event
        100: "romance_confession",      # Romantic - confession scene available
        120: "romance_date",            # Romantic+ - date events available
        150: "romance_ending"           # Max Romance - special ending unlocked
    }

    # =========================================================================
    # CHARACTER CLASS - Represents an NPC with relationship meters
    # =========================================================================

    class Character:
        """
        Represents an NPC character with relationship tracking.

        Attributes:
            name (str): Display name of the character
            id (str): Unique identifier for the character
            affection (int): How much the character likes the player (0-150)
            trust (int): How much the character trusts the player (0-100)
            respect (int): How much the character respects the player (0-100)
            romance_available (bool): Whether romance path is available
            portrait (str): Path to character portrait image
            faction (str): Faction/group the character belongs to
            unlocked_events (list): List of unlocked event IDs
            relationship_history (list): Log of relationship changes
        """

        def __init__(self, name, id, affection=0, trust=0, respect=0,
                     romance_available=False, portrait=None, faction=None):
            self.name = name
            self.id = id
            self.affection = max(0, min(150, affection))
            self.trust = max(0, min(100, trust))
            self.respect = max(0, min(100, respect))
            self.romance_available = romance_available
            self.portrait = portrait
            self.faction = faction
            self.unlocked_events = []
            self.relationship_history = []

        def get_combined_score(self):
            """Calculate combined relationship score (weighted average)."""
            # Affection weighted more heavily, trust and respect equal
            return int((self.affection * 0.5) + (self.trust * 0.25) + (self.respect * 0.25))

        def get_tier(self):
            """Get current relationship tier based on combined score."""
            score = self.get_combined_score()
            for tier_id, tier_data in RELATIONSHIP_TIERS.items():
                if tier_data["min"] <= score <= tier_data["max"]:
                    return tier_id, tier_data["label"]
            return "stranger", "Stranger"

        def get_tier_label(self):
            """Get displayable tier label."""
            return self.get_tier()[1]

        def check_unlocks(self):
            """Check and unlock events based on current affection level."""
            unlocked = []
            for threshold, event_id in RELATIONSHIP_UNLOCKS.items():
                if self.affection >= threshold and event_id not in self.unlocked_events:
                    self.unlocked_events.append(event_id)
                    unlocked.append(event_id)
            return unlocked

        def is_event_unlocked(self, event_id):
            """Check if a specific event is unlocked."""
            return event_id in self.unlocked_events

        def can_romance(self):
            """Check if romance path is available and conditions are met."""
            return (self.romance_available and
                    self.affection >= 80 and
                    self.trust >= 60)

        def log_change(self, change_type, amount, reason=""):
            """Log a relationship change for history tracking."""
            self.relationship_history.append({
                "type": change_type,
                "amount": amount,
                "reason": reason,
                "new_value": getattr(self, change_type, 0)
            })

    # =========================================================================
    # FACTION CLASS - Represents a group/organization with reputation
    # =========================================================================

    class Faction:
        """
        Represents a faction or group with reputation tracking.

        Attributes:
            name (str): Display name of the faction
            id (str): Unique identifier
            reputation (int): Player's standing with faction (-100 to 100)
            description (str): Faction description
            icon (str): Path to faction icon
        """

        REPUTATION_LEVELS = {
            (-100, -60): ("Hated", "#ff0000"),
            (-59, -20): ("Hostile", "#ff6600"),
            (-19, 19): ("Neutral", "#808080"),
            (20, 59): ("Friendly", "#66cc00"),
            (60, 100): ("Allied", "#00ff00")
        }

        def __init__(self, name, id, reputation=0, description="", icon=None):
            self.name = name
            self.id = id
            self.reputation = max(-100, min(100, reputation))
            self.description = description
            self.icon = icon

        def get_reputation_level(self):
            """Get reputation level name and color."""
            for (min_val, max_val), (level, color) in self.REPUTATION_LEVELS.items():
                if min_val <= self.reputation <= max_val:
                    return level, color
            return "Neutral", "#808080"

        def change_reputation(self, amount):
            """Change faction reputation by amount."""
            old_rep = self.reputation
            self.reputation = max(-100, min(100, self.reputation + amount))
            return self.reputation - old_rep

    # =========================================================================
    # RELATIONSHIP MANAGER - Central manager for all relationships
    # =========================================================================

    class RelationshipManager:
        """
        Central manager for tracking all NPC relationships and faction standings.

        This class provides methods to modify relationships, query status,
        and manage the overall relationship system.
        """

        def __init__(self):
            self.characters = {}
            self.factions = {}

        # ---------------------------------------------------------------------
        # Character Management
        # ---------------------------------------------------------------------

        def add_character(self, character):
            """Add a character to the relationship system."""
            self.characters[character.id] = character
            return character

        def get_character(self, char_id):
            """Get a character by ID."""
            return self.characters.get(char_id, None)

        def remove_character(self, char_id):
            """Remove a character from the system."""
            if char_id in self.characters:
                del self.characters[char_id]
                return True
            return False

        # ---------------------------------------------------------------------
        # Relationship Modification Methods
        # ---------------------------------------------------------------------

        def change_affection(self, char_id, amount, reason=""):
            """
            Change a character's affection value.

            Args:
                char_id (str): Character identifier
                amount (int): Amount to change (positive or negative)
                reason (str): Optional reason for the change

            Returns:
                tuple: (new_value, unlocked_events) or (None, []) if not found
            """
            char = self.get_character(char_id)
            if char:
                char.affection = max(0, min(150, char.affection + amount))
                char.log_change("affection", amount, reason)
                unlocked = char.check_unlocks()

                # Update faction reputation if character has a faction
                if char.faction and char.faction in self.factions:
                    faction_change = amount // 4  # 25% of affection change
                    self.change_faction_reputation(char.faction, faction_change)

                return char.affection, unlocked
            return None, []

        def change_trust(self, char_id, amount, reason=""):
            """
            Change a character's trust value.

            Args:
                char_id (str): Character identifier
                amount (int): Amount to change (positive or negative)
                reason (str): Optional reason for the change

            Returns:
                int: New trust value or None if character not found
            """
            char = self.get_character(char_id)
            if char:
                char.trust = max(0, min(100, char.trust + amount))
                char.log_change("trust", amount, reason)
                return char.trust
            return None

        def change_respect(self, char_id, amount, reason=""):
            """
            Change a character's respect value.

            Args:
                char_id (str): Character identifier
                amount (int): Amount to change (positive or negative)
                reason (str): Optional reason for the change

            Returns:
                int: New respect value or None if character not found
            """
            char = self.get_character(char_id)
            if char:
                char.respect = max(0, min(100, char.respect + amount))
                char.log_change("respect", amount, reason)
                return char.respect
            return None

        def change_all(self, char_id, affection=0, trust=0, respect=0, reason=""):
            """Change all relationship values at once."""
            self.change_affection(char_id, affection, reason)
            self.change_trust(char_id, trust, reason)
            self.change_respect(char_id, respect, reason)

        # ---------------------------------------------------------------------
        # Query Methods
        # ---------------------------------------------------------------------

        def get_relationship_level(self, char_id):
            """
            Get a character's relationship tier.

            Args:
                char_id (str): Character identifier

            Returns:
                tuple: (tier_id, tier_label) or (None, None) if not found
            """
            char = self.get_character(char_id)
            if char:
                return char.get_tier()
            return None, None

        def get_all_characters(self):
            """Get list of all tracked characters."""
            return list(self.characters.values())

        def get_characters_by_tier(self, tier_id):
            """Get all characters at a specific relationship tier."""
            return [c for c in self.characters.values()
                    if c.get_tier()[0] == tier_id]

        def get_romanceable_characters(self):
            """Get all characters eligible for romance."""
            return [c for c in self.characters.values() if c.can_romance()]

        # ---------------------------------------------------------------------
        # Faction Management
        # ---------------------------------------------------------------------

        def add_faction(self, faction):
            """Add a faction to the system."""
            self.factions[faction.id] = faction
            return faction

        def get_faction(self, faction_id):
            """Get a faction by ID."""
            return self.factions.get(faction_id, None)

        def change_faction_reputation(self, faction_id, amount):
            """Change a faction's reputation."""
            faction = self.get_faction(faction_id)
            if faction:
                return faction.change_reputation(amount)
            return 0

        def get_all_factions(self):
            """Get list of all factions."""
            return list(self.factions.values())

        def get_faction_members(self, faction_id):
            """Get all characters belonging to a faction."""
            return [c for c in self.characters.values()
                    if c.faction == faction_id]

# =============================================================================
# GLOBAL RELATIONSHIP MANAGER INSTANCE
# =============================================================================

default relationship_manager = RelationshipManager()

# =============================================================================
# EXAMPLE NPC DEFINITIONS
# =============================================================================

init python:
    def setup_example_npcs():
        """Initialize example NPCs for the relationship system."""

        # Create example factions
        merchant_guild = Faction(
            name="Merchant's Guild",
            id="merchant_guild",
            reputation=0,
            description="A powerful guild of traders and merchants."
        )

        noble_house = Faction(
            name="House Valdoria",
            id="noble_house",
            reputation=0,
            description="An ancient noble house with great influence."
        )

        adventurer_guild = Faction(
            name="Adventurer's Guild",
            id="adventurer_guild",
            reputation=10,
            description="A guild for brave souls seeking fortune and glory."
        )

        # Add factions to manager
        relationship_manager.add_faction(merchant_guild)
        relationship_manager.add_faction(noble_house)
        relationship_manager.add_faction(adventurer_guild)

        # Create example characters
        elena = Character(
            name="Elena Brightwood",
            id="elena",
            affection=10,
            trust=5,
            respect=10,
            romance_available=True,
            portrait="images/characters/elena.png",
            faction="adventurer_guild"
        )

        marcus = Character(
            name="Marcus Sterling",
            id="marcus",
            affection=5,
            trust=15,
            respect=20,
            romance_available=True,
            portrait="images/characters/marcus.png",
            faction="merchant_guild"
        )

        lady_victoria = Character(
            name="Lady Victoria Valdoria",
            id="victoria",
            affection=0,
            trust=0,
            respect=5,
            romance_available=True,
            portrait="images/characters/victoria.png",
            faction="noble_house"
        )

        old_sage = Character(
            name="Sage Aldric",
            id="aldric",
            affection=15,
            trust=10,
            respect=25,
            romance_available=False,
            portrait="images/characters/aldric.png",
            faction=None
        )

        rival = Character(
            name="Rex Thornwood",
            id="rex",
            affection=0,
            trust=0,
            respect=10,
            romance_available=False,
            portrait="images/characters/rex.png",
            faction="adventurer_guild"
        )

        # Add characters to manager
        relationship_manager.add_character(elena)
        relationship_manager.add_character(marcus)
        relationship_manager.add_character(lady_victoria)
        relationship_manager.add_character(old_sage)
        relationship_manager.add_character(rival)

# Initialize example NPCs when game starts
label after_load:
    $ setup_example_npcs()
    return

label splashscreen:
    $ setup_example_npcs()
    return

# =============================================================================
# RELATIONSHIP SCREEN UI
# =============================================================================

screen relationship_screen():
    tag menu

    use game_menu(_("Relationships"), scroll="viewport"):

        style_prefix "relationship"

        vbox:
            spacing 20

            # Section: Character Relationships
            text "Character Relationships" size 36 color "#ffffff"

            null height 10

            for char in relationship_manager.get_all_characters():
                frame:
                    xfill True
                    padding (20, 15)
                    background "#333333"

                    hbox:
                        spacing 20

                        # Character portrait placeholder
                        frame:
                            xysize (80, 80)
                            background "#555555"
                            if char.portrait:
                                add char.portrait fit "contain"
                            else:
                                text char.name[0] align (0.5, 0.5) size 40

                        vbox:
                            spacing 8
                            xfill True

                            # Character name and tier
                            hbox:
                                text char.name size 24 color "#ffffff"
                                null width 20
                                text "[" + char.get_tier_label() + "]" size 18 color "#aaaaaa"

                                if char.romance_available:
                                    null width 10
                                    if char.can_romance():
                                        text "{color=#ff69b4}[heart]{/color}" size 18
                                    else:
                                        text "{color=#666666}[heart]{/color}" size 18

                            # Affection meter
                            hbox:
                                spacing 10
                                text "Affection:" size 16 color "#ff6699" min_width 80
                                bar value char.affection range 150 xsize 200 left_bar "#ff6699" right_bar "#444444"
                                text "[char.affection]/150" size 14 color "#aaaaaa"

                            # Trust meter
                            hbox:
                                spacing 10
                                text "Trust:" size 16 color "#66ccff" min_width 80
                                bar value char.trust range 100 xsize 200 left_bar "#66ccff" right_bar "#444444"
                                text "[char.trust]/100" size 14 color "#aaaaaa"

                            # Respect meter
                            hbox:
                                spacing 10
                                text "Respect:" size 16 color "#ffcc66" min_width 80
                                bar value char.respect range 100 xsize 200 left_bar "#ffcc66" right_bar "#444444"
                                text "[char.respect]/100" size 14 color "#aaaaaa"

                            # Faction affiliation
                            if char.faction:
                                $ faction = relationship_manager.get_faction(char.faction)
                                if faction:
                                    text "Faction: [faction.name]" size 14 color "#888888"

            null height 30

            # Section: Faction Reputation
            text "Faction Reputation" size 36 color "#ffffff"

            null height 10

            for faction in relationship_manager.get_all_factions():
                $ rep_level, rep_color = faction.get_reputation_level()

                frame:
                    xfill True
                    padding (20, 15)
                    background "#333333"

                    vbox:
                        spacing 8

                        # Faction name and reputation level
                        hbox:
                            text faction.name size 22 color "#ffffff"
                            null width 20
                            text rep_level size 18 color rep_color

                        # Reputation description
                        text faction.description size 14 color "#888888"

                        # Reputation bar (-100 to 100, centered at 0)
                        hbox:
                            spacing 10
                            text "Reputation:" size 16 color "#aaaaaa" min_width 100

                            # Custom bar showing negative to positive
                            frame:
                                xsize 250
                                ysize 20
                                background "#444444"

                                # Calculate bar position (0 is center)
                                $ bar_width = int((faction.reputation + 100) / 200.0 * 250)
                                $ bar_color = rep_color

                                if faction.reputation >= 0:
                                    frame:
                                        pos (125, 0)
                                        xsize max(0, bar_width - 125)
                                        ysize 20
                                        background bar_color
                                else:
                                    frame:
                                        pos (bar_width, 0)
                                        xsize max(0, 125 - bar_width)
                                        ysize 20
                                        background bar_color

                            text "[faction.reputation]" size 14 color "#aaaaaa"

                        # Faction members
                        $ members = relationship_manager.get_faction_members(faction.id)
                        if members:
                            $ member_names = ", ".join([m.name for m in members])
                            text "Members: [member_names]" size 12 color "#666666"

# =============================================================================
# STYLES FOR RELATIONSHIP SCREEN
# =============================================================================

style relationship_vbox:
    xfill True
    spacing 10

style relationship_frame:
    background "#2a2a2a"
    padding (20, 20)

style relationship_text:
    color "#ffffff"

style relationship_bar:
    xsize 200
    ysize 18
    left_bar Frame("gui/bar/left.png", 4, 4)
    right_bar Frame("gui/bar/right.png", 4, 4)

# =============================================================================
# HELPER LABELS FOR EASY RELATIONSHIP CHANGES
# =============================================================================

# Change affection with notification
label change_affection(char_id, amount, reason="", notify=True):
    $ new_val, unlocks = relationship_manager.change_affection(char_id, amount, reason)
    if notify and new_val is not None:
        $ char = relationship_manager.get_character(char_id)
        if amount > 0:
            $ renpy.notify("[char.name]: Affection +[amount]")
        elif amount < 0:
            $ renpy.notify("[char.name]: Affection [amount]")

        # Notify about unlocked events
        for event in unlocks:
            $ renpy.notify("New event unlocked: [event]")
    return

# Change trust with notification
label change_trust(char_id, amount, reason="", notify=True):
    $ new_val = relationship_manager.change_trust(char_id, amount, reason)
    if notify and new_val is not None:
        $ char = relationship_manager.get_character(char_id)
        if amount > 0:
            $ renpy.notify("[char.name]: Trust +[amount]")
        elif amount < 0:
            $ renpy.notify("[char.name]: Trust [amount]")
    return

# Change respect with notification
label change_respect(char_id, amount, reason="", notify=True):
    $ new_val = relationship_manager.change_respect(char_id, amount, reason)
    if notify and new_val is not None:
        $ char = relationship_manager.get_character(char_id)
        if amount > 0:
            $ renpy.notify("[char.name]: Respect +[amount]")
        elif amount < 0:
            $ renpy.notify("[char.name]: Respect [amount]")
    return

# Change all relationship values
label change_relationship(char_id, affection=0, trust=0, respect=0, reason="", notify=True):
    if affection != 0:
        call change_affection(char_id, affection, reason, notify)
    if trust != 0:
        call change_trust(char_id, trust, reason, notify)
    if respect != 0:
        call change_respect(char_id, respect, reason, notify)
    return

# Change faction reputation with notification
label change_faction_rep(faction_id, amount, notify=True):
    $ change = relationship_manager.change_faction_reputation(faction_id, amount)
    if notify and change != 0:
        $ faction = relationship_manager.get_faction(faction_id)
        if amount > 0:
            $ renpy.notify("[faction.name]: Reputation +[amount]")
        elif amount < 0:
            $ renpy.notify("[faction.name]: Reputation [amount]")
    return

# =============================================================================
# EXAMPLE USAGE IN GAME SCRIPT
# =============================================================================

# Example label showing relationship system usage:
#
# label example_conversation:
#     "You helped Elena with her quest."
#     call change_affection("elena", 15, "Helped with quest")
#     call change_trust("elena", 10, "Proved reliability")
#
#     if relationship_manager.get_character("elena").can_romance():
#         "Elena looks at you with warm eyes..."
#         # Romance content here
#
#     return
#
# To open the relationship screen:
#     call screen relationship_screen
#
# To check relationship tier:
#     $ tier_id, tier_label = relationship_manager.get_relationship_level("elena")
#     if tier_id == "close_friend":
#         "Elena considers you a close friend."

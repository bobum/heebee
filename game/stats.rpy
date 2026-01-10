# Heebee - Attributes/Stats System
# A complete RPG-style stats system for Ren'Py visual novels
#
# ============================================================================
# USAGE EXAMPLES:
# ============================================================================
#
# Initialize player at game start:
#   $ player = Player("Hero")
#
# Modify stats:
#   $ player.add_stat("strength", 5)
#   $ player.subtract_stat("hp", 10)
#   $ player.set_stat("charisma", 15)
#
# Add experience and level up:
#   $ player.add_xp(100)
#
# Check stats in conditions:
#   if player.strength >= 10:
#       "You are strong enough to lift the boulder."
#
# Show stats screen:
#   call screen stats_screen
#
# Save/Load stats (automatic with Ren'Py save system)
#   Stats are saved automatically when the game is saved.
#
# ============================================================================

init python:
    import math

    class Player:
        """
        Player class containing all character attributes and stats.
        Includes HP, MP, core stats, XP tracking, and leveling system.
        """

        # Constants for stat bounds
        MIN_STAT = 0
        MAX_STAT = 999
        MIN_LEVEL = 1
        MAX_LEVEL = 100

        def __init__(self, name="Player"):
            """Initialize a new player with default stats."""
            self.name = name

            # Level and Experience
            self.level = 1
            self.xp = 0
            self.xp_to_next_level = 100

            # Vital Stats
            self.max_hp = 100
            self.hp = 100
            self.max_mp = 50
            self.mp = 50

            # Core Attributes (Base values)
            self.strength = 10      # Physical power, affects damage
            self.defense = 10       # Damage reduction
            self.agility = 10       # Speed, evasion, turn order
            self.charisma = 10      # Dialogue options, NPC reactions
            self.intelligence = 10  # Magic power, puzzle solving
            self.luck = 10          # Critical hits, item drops, random events

            # Stat abbreviations for display
            self._stat_names = {
                "hp": "HP",
                "mp": "MP",
                "max_hp": "Max HP",
                "max_mp": "Max MP",
                "strength": "STR",
                "defense": "DEF",
                "agility": "AGI",
                "charisma": "CHA",
                "intelligence": "INT",
                "luck": "LCK"
            }

        # ====================================================================
        # STAT MODIFICATION METHODS
        # ====================================================================

        def _clamp(self, value, min_val, max_val):
            """Clamp a value between min and max bounds."""
            return max(min_val, min(value, max_val))

        def get_stat(self, stat_name):
            """Get the current value of a stat."""
            stat_name = stat_name.lower()
            if hasattr(self, stat_name):
                return getattr(self, stat_name)
            return None

        def set_stat(self, stat_name, value):
            """Set a stat to a specific value, respecting bounds."""
            stat_name = stat_name.lower()
            if not hasattr(self, stat_name):
                return False

            # Determine appropriate bounds
            if stat_name in ["hp", "mp"]:
                max_val = getattr(self, "max_" + stat_name)
                value = self._clamp(value, 0, max_val)
            elif stat_name in ["max_hp", "max_mp"]:
                value = self._clamp(value, 1, self.MAX_STAT)
            elif stat_name == "level":
                value = self._clamp(value, self.MIN_LEVEL, self.MAX_LEVEL)
            else:
                value = self._clamp(value, self.MIN_STAT, self.MAX_STAT)

            setattr(self, stat_name, value)
            return True

        def add_stat(self, stat_name, amount):
            """Add to a stat value, respecting bounds."""
            current = self.get_stat(stat_name)
            if current is not None:
                return self.set_stat(stat_name, current + amount)
            return False

        def subtract_stat(self, stat_name, amount):
            """Subtract from a stat value, respecting bounds."""
            return self.add_stat(stat_name, -amount)

        def heal(self, amount):
            """Restore HP up to max_hp."""
            self.add_stat("hp", amount)

        def restore_mp(self, amount):
            """Restore MP up to max_mp."""
            self.add_stat("mp", amount)

        def take_damage(self, amount):
            """Reduce HP by damage amount (considers defense)."""
            # Simple damage formula: damage - (defense / 2)
            actual_damage = max(1, amount - (self.defense // 2))
            self.subtract_stat("hp", actual_damage)
            return actual_damage

        def is_alive(self):
            """Check if player HP is above 0."""
            return self.hp > 0

        def full_restore(self):
            """Fully restore HP and MP."""
            self.hp = self.max_hp
            self.mp = self.max_mp

        # ====================================================================
        # EXPERIENCE AND LEVELING SYSTEM
        # ====================================================================

        def calculate_xp_needed(self, level):
            """Calculate XP needed for a specific level."""
            # Formula: 100 * level^1.5 (exponential growth)
            return int(100 * math.pow(level, 1.5))

        def add_xp(self, amount):
            """
            Add experience points and handle level ups.
            Returns the number of levels gained.
            """
            self.xp += amount
            levels_gained = 0

            while self.xp >= self.xp_to_next_level and self.level < self.MAX_LEVEL:
                self.xp -= self.xp_to_next_level
                self.level_up()
                levels_gained += 1

            return levels_gained

        def level_up(self):
            """
            Increase level and improve stats.
            Called automatically when XP threshold is reached.
            """
            if self.level >= self.MAX_LEVEL:
                return False

            self.level += 1
            self.xp_to_next_level = self.calculate_xp_needed(self.level)

            # Stat increases on level up
            self.max_hp += 10
            self.max_mp += 5
            self.hp = self.max_hp  # Full heal on level up
            self.mp = self.max_mp

            # Small boost to all core stats
            self.strength += 1
            self.defense += 1
            self.agility += 1
            self.charisma += 1
            self.intelligence += 1
            self.luck += 1

            return True

        def get_xp_progress(self):
            """Get XP progress as a percentage (0.0 to 1.0)."""
            if self.xp_to_next_level <= 0:
                return 1.0
            return float(self.xp) / float(self.xp_to_next_level)

        # ====================================================================
        # STAT DISPLAY HELPERS
        # ====================================================================

        def get_stat_display_name(self, stat_name):
            """Get the display abbreviation for a stat."""
            return self._stat_names.get(stat_name.lower(), stat_name.upper())

        def get_all_stats(self):
            """Return a dictionary of all displayable stats."""
            return {
                "level": self.level,
                "xp": self.xp,
                "xp_to_next": self.xp_to_next_level,
                "hp": self.hp,
                "max_hp": self.max_hp,
                "mp": self.mp,
                "max_mp": self.max_mp,
                "strength": self.strength,
                "defense": self.defense,
                "agility": self.agility,
                "charisma": self.charisma,
                "intelligence": self.intelligence,
                "luck": self.luck
            }

        # ====================================================================
        # SAVE/LOAD SUPPORT
        # ====================================================================

        def to_dict(self):
            """Convert player stats to a dictionary for saving."""
            return {
                "name": self.name,
                "level": self.level,
                "xp": self.xp,
                "xp_to_next_level": self.xp_to_next_level,
                "hp": self.hp,
                "max_hp": self.max_hp,
                "mp": self.mp,
                "max_mp": self.max_mp,
                "strength": self.strength,
                "defense": self.defense,
                "agility": self.agility,
                "charisma": self.charisma,
                "intelligence": self.intelligence,
                "luck": self.luck
            }

        @classmethod
        def from_dict(cls, data):
            """Create a Player instance from a dictionary (for loading)."""
            player = cls(data.get("name", "Player"))
            player.level = data.get("level", 1)
            player.xp = data.get("xp", 0)
            player.xp_to_next_level = data.get("xp_to_next_level", 100)
            player.hp = data.get("hp", 100)
            player.max_hp = data.get("max_hp", 100)
            player.mp = data.get("mp", 50)
            player.max_mp = data.get("max_mp", 50)
            player.strength = data.get("strength", 10)
            player.defense = data.get("defense", 10)
            player.agility = data.get("agility", 10)
            player.charisma = data.get("charisma", 10)
            player.intelligence = data.get("intelligence", 10)
            player.luck = data.get("luck", 10)
            return player

    # ========================================================================
    # HELPER FUNCTIONS (Global scope for easy access in Ren'Py)
    # ========================================================================

    def save_player_stats(player, slot="stats"):
        """
        Save player stats to persistent data.
        Note: Ren'Py's default save system handles this automatically,
        but this provides manual control if needed.
        """
        if player:
            persistent_data = player.to_dict()
            renpy.store.persistent.__setattr__(slot, persistent_data)
            return True
        return False

    def load_player_stats(slot="stats"):
        """
        Load player stats from persistent data.
        Returns a new Player instance or None if no save exists.
        """
        data = getattr(renpy.store.persistent, slot, None)
        if data:
            return Player.from_dict(data)
        return None

    def create_new_player(name="Hero"):
        """Create and return a new player with default stats."""
        return Player(name)


# ============================================================================
# DEFAULT PLAYER VARIABLE
# ============================================================================
# This creates a default player variable that will be saved with the game.
# You can initialize this at the start of your game with:
#   $ player = Player("YourHeroName")

default player = None


# ============================================================================
# STATS DISPLAY SCREEN
# ============================================================================
# A screen to display player stats. Call with:
#   call screen stats_screen
# Or show as overlay:
#   show screen stats_screen

screen stats_screen():
    tag menu
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 40
        ypadding 30
        xminimum 500

        vbox:
            spacing 15

            # Title
            text "Character Stats" size 36 xalign 0.5 color "#ffffff"

            null height 10

            if player:
                # Name and Level
                hbox:
                    spacing 20
                    text "[player.name]" size 28 color "#ffdd44"
                    text "Level [player.level]" size 24 color "#aaaaaa"

                null height 5

                # XP Bar
                vbox:
                    spacing 5
                    text "Experience" size 18 color "#aaaaaa"
                    bar value player.xp range player.xp_to_next_level xmaximum 420 ysize 20
                    text "[player.xp] / [player.xp_to_next_level] XP" size 14 color "#888888"

                null height 10

                # HP and MP Bars
                hbox:
                    spacing 30

                    vbox:
                        spacing 5
                        text "HP" size 20 color "#ff6666"
                        bar value player.hp range player.max_hp xmaximum 180 ysize 18 left_bar "#ff4444" right_bar "#442222"
                        text "[player.hp] / [player.max_hp]" size 14 color "#888888"

                    vbox:
                        spacing 5
                        text "MP" size 20 color "#6666ff"
                        bar value player.mp range player.max_mp xmaximum 180 ysize 18 left_bar "#4444ff" right_bar "#222244"
                        text "[player.mp] / [player.max_mp]" size 14 color "#888888"

                null height 15

                # Core Stats Grid
                text "Attributes" size 22 color "#ffffff"
                null height 5

                grid 2 3:
                    spacing 20
                    xalign 0.5

                    # Row 1
                    hbox:
                        spacing 10
                        text "STR" size 18 color "#ff9944" min_width 50
                        text "[player.strength]" size 18 color "#ffffff"

                    hbox:
                        spacing 10
                        text "DEF" size 18 color "#44aaff" min_width 50
                        text "[player.defense]" size 18 color "#ffffff"

                    # Row 2
                    hbox:
                        spacing 10
                        text "AGI" size 18 color "#44ff44" min_width 50
                        text "[player.agility]" size 18 color "#ffffff"

                    hbox:
                        spacing 10
                        text "CHA" size 18 color "#ff44ff" min_width 50
                        text "[player.charisma]" size 18 color "#ffffff"

                    # Row 3
                    hbox:
                        spacing 10
                        text "INT" size 18 color "#44ffff" min_width 50
                        text "[player.intelligence]" size 18 color "#ffffff"

                    hbox:
                        spacing 10
                        text "LCK" size 18 color "#ffff44" min_width 50
                        text "[player.luck]" size 18 color "#ffffff"

            else:
                text "No player data available." size 20 color "#ff4444" xalign 0.5

            null height 20

            # Close Button
            textbutton "Close" action Return() xalign 0.5 text_size 22


# ============================================================================
# COMPACT STATS HUD (Optional overlay)
# ============================================================================
# A minimal HUD showing HP/MP. Use with:
#   show screen stats_hud
#   hide screen stats_hud

screen stats_hud():
    tag stats_hud
    zorder 100

    frame:
        xalign 0.0
        yalign 0.0
        xoffset 10
        yoffset 10
        xpadding 15
        ypadding 10
        background "#00000088"

        vbox:
            spacing 5

            if player:
                text "[player.name] Lv.[player.level]" size 14 color "#ffffff"

                hbox:
                    spacing 10
                    text "HP" size 12 color "#ff6666"
                    bar value player.hp range player.max_hp xmaximum 100 ysize 10 left_bar "#ff4444" right_bar "#442222"
                    text "[player.hp]" size 12 color "#ffffff"

                hbox:
                    spacing 10
                    text "MP" size 12 color "#6666ff"
                    bar value player.mp range player.max_mp xmaximum 100 ysize 10 left_bar "#4444ff" right_bar "#222244"
                    text "[player.mp]" size 12 color "#ffffff"

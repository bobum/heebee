# Turn-Based Combat System for Ren'Py
# Provides enemies, combat mechanics, and battle UI

init python:
    import random

    # =========================================================================
    # STATUS EFFECTS
    # =========================================================================

    class StatusEffect:
        """Represents a status effect on a combatant."""

        def __init__(self, name, duration, effect_type, value=0):
            self.name = name
            self.duration = duration  # Turns remaining
            self.effect_type = effect_type  # poison, stun, buff, debuff
            self.value = value

        def tick(self):
            """Called each turn. Returns damage/healing or None."""
            self.duration -= 1
            if self.effect_type == "poison":
                return -self.value  # Damage
            return None

        def is_expired(self):
            return self.duration <= 0

    # =========================================================================
    # COMBATANT BASE CLASS
    # =========================================================================

    class Combatant:
        """Base class for anything that can fight."""

        def __init__(self, name, hp, mp, attack, defense, speed, magic=0):
            self.name = name
            self.max_hp = hp
            self.hp = hp
            self.max_mp = mp
            self.mp = mp
            self.attack = attack
            self.defense = defense
            self.speed = speed
            self.magic = magic
            self.status_effects = []
            self.is_defending = False

        def take_damage(self, amount):
            """Take damage, returns actual damage taken."""
            defense_mod = self.defense
            if self.is_defending:
                defense_mod *= 2

            actual_damage = max(1, amount - defense_mod // 2)
            self.hp = max(0, self.hp - actual_damage)
            return actual_damage

        def heal(self, amount):
            """Heal HP."""
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + amount)
            return self.hp - old_hp

        def use_mp(self, amount):
            """Use MP. Returns True if successful."""
            if self.mp >= amount:
                self.mp -= amount
                return True
            return False

        def add_status(self, effect):
            """Add a status effect."""
            # Remove existing effect of same type
            self.status_effects = [e for e in self.status_effects if e.name != effect.name]
            self.status_effects.append(effect)

        def process_status_effects(self):
            """Process all status effects. Returns total damage/healing."""
            total = 0
            for effect in self.status_effects[:]:
                result = effect.tick()
                if result:
                    if result < 0:
                        self.hp = max(0, self.hp + result)
                    else:
                        self.heal(result)
                    total += result
                if effect.is_expired():
                    self.status_effects.remove(effect)
            return total

        def has_status(self, name):
            """Check if has a status effect."""
            return any(e.name == name for e in self.status_effects)

        def is_alive(self):
            return self.hp > 0

        def is_stunned(self):
            return self.has_status("Stun")

    # =========================================================================
    # ENEMY CLASS
    # =========================================================================

    class Enemy(Combatant):
        """An enemy combatant with AI behavior."""

        def __init__(self, name, hp, mp, attack, defense, speed, magic=0,
                     xp_reward=10, gold_reward=5, drops=None):
            super().__init__(name, hp, mp, attack, defense, speed, magic)
            self.xp_reward = xp_reward
            self.gold_reward = gold_reward
            self.drops = drops or []  # [(item_id, drop_chance), ...]
            self.skills = []  # [(skill_name, mp_cost, damage_mult, effect), ...]

        def choose_action(self, player):
            """AI decides what to do. Returns (action_type, target, data)."""
            # Priority 1: Heal if low HP (if has healing skill)
            if self.hp < self.max_hp * 0.3:
                for skill in self.skills:
                    if "heal" in skill[0].lower() and self.mp >= skill[1]:
                        return ("skill", self, skill)

            # Priority 2: Use offensive skill if MP available (30% chance)
            if self.skills and self.mp >= 5:
                if random.random() < 0.3:  # 30% chance to use skill
                    skill = random.choice(self.skills)
                    if self.mp >= skill[1]:
                        return ("skill", player, skill)

            return ("attack", player, None)

        def get_drops(self):
            """Roll for item drops."""
            dropped = []
            for item_id, chance in self.drops:
                if random.random() < chance:
                    dropped.append(item_id)
            return dropped

    # =========================================================================
    # COMBAT MANAGER
    # =========================================================================

    class CombatManager:
        """Manages a combat encounter."""

        def __init__(self):
            self.player = None
            self.enemies = []
            self.turn_order = []
            self.current_turn = 0
            self.battle_log = []
            self.state = "inactive"  # inactive, player_turn, enemy_turn, victory, defeat
            self.selected_action = None
            self.selected_target = None

        def start_battle(self, player_combatant, enemies):
            """Start a new battle."""
            self.player = player_combatant
            self.enemies = enemies if isinstance(enemies, list) else [enemies]
            self.battle_log = []
            self.state = "active"
            self.current_turn = 0

            # Determine turn order by speed
            self.calculate_turn_order()
            self.log(f"Battle started!")

            # Start first turn
            self.next_turn()

        def calculate_turn_order(self):
            """Calculate turn order based on speed."""
            all_combatants = [self.player] + self.enemies
            self.turn_order = sorted(all_combatants, key=lambda c: c.speed, reverse=True)

        def get_current_combatant(self):
            """Get who's turn it is."""
            if not self.turn_order:
                return None
            return self.turn_order[self.current_turn % len(self.turn_order)]

        def next_turn(self):
            """Move to next turn."""
            # Remove dead combatants
            self.turn_order = [c for c in self.turn_order if c.is_alive()]
            self.enemies = [e for e in self.enemies if e.is_alive()]

            # Check win/lose
            if not self.player.is_alive():
                self.state = "defeat"
                self.log("You have been defeated...")
                return

            if not self.enemies:
                self.state = "victory"
                self.log("Victory!")
                return

            current = self.get_current_combatant()
            if not current:
                return

            # Process status effects
            current.is_defending = False
            status_dmg = current.process_status_effects()
            if status_dmg:
                self.log(f"{current.name} {'takes' if status_dmg < 0 else 'heals'} {abs(status_dmg)} from status effects!")

            # Check if stunned
            if current.is_stunned():
                self.log(f"{current.name} is stunned and cannot act!")
                self.current_turn += 1
                self.next_turn()
                return

            if current == self.player:
                self.state = "player_turn"
            else:
                self.state = "enemy_turn"
                self.process_enemy_turn(current)

        def process_enemy_turn(self, enemy):
            """Process an enemy's turn."""
            action, target, data = enemy.choose_action(self.player)

            if action == "attack":
                damage = self.calculate_damage(enemy, target)
                actual = target.take_damage(damage)
                self.log(f"{enemy.name} attacks {target.name} for {actual} damage!")

            elif action == "skill":
                skill_name, mp_cost, dmg_mult, effect = data
                enemy.use_mp(mp_cost)

                if effect == "heal":
                    heal_amount = int(enemy.magic * dmg_mult)
                    enemy.heal(heal_amount)
                    self.log(f"{enemy.name} uses {skill_name} and heals for {heal_amount}!")
                else:
                    damage = self.calculate_damage(enemy, target, dmg_mult)
                    actual = target.take_damage(damage)
                    self.log(f"{enemy.name} uses {skill_name} for {actual} damage!")

            self.current_turn += 1
            renpy.restart_interaction()
            self.next_turn()

        def player_attack(self, target):
            """Player attacks a target."""
            if self.state != "player_turn":
                return

            damage = self.calculate_damage(self.player, target)

            # Critical hit chance
            if random.random() < 0.1:
                damage = int(damage * 1.5)
                self.log(f"Critical hit!")

            actual = target.take_damage(damage)
            self.log(f"You attack {target.name} for {actual} damage!")

            self.current_turn += 1
            self.next_turn()

        def player_defend(self):
            """Player defends."""
            if self.state != "player_turn":
                return

            self.player.is_defending = True
            self.log("You take a defensive stance!")

            self.current_turn += 1
            self.next_turn()

        def player_skill(self, skill_name, mp_cost, damage_mult, target):
            """Player uses a skill."""
            if self.state != "player_turn":
                return

            if not self.player.use_mp(mp_cost):
                self.log("Not enough MP!")
                return

            damage = self.calculate_damage(self.player, target, damage_mult, use_magic=True)
            actual = target.take_damage(damage)
            self.log(f"You use {skill_name} for {actual} damage!")

            self.current_turn += 1
            self.next_turn()

        def player_flee(self):
            """Attempt to flee."""
            if self.state != "player_turn":
                return

            # 50% base flee chance, modified by speed
            avg_enemy_speed = sum(e.speed for e in self.enemies) / len(self.enemies)
            flee_chance = 0.5 + (self.player.speed - avg_enemy_speed) * 0.02
            flee_chance = max(0.1, min(0.9, flee_chance))

            if random.random() < flee_chance:
                self.state = "fled"
                self.log("You escaped!")
            else:
                self.log("Couldn't escape!")
                self.current_turn += 1
                self.next_turn()

        def player_use_item(self, item_id):
            """Player uses an item in combat."""
            if self.state != "player_turn":
                return

            # This would integrate with inventory system
            self.log(f"Used item!")
            self.current_turn += 1
            self.next_turn()

        def calculate_damage(self, attacker, defender, multiplier=1.0, use_magic=False):
            """Calculate damage dealt."""
            if use_magic:
                base = attacker.magic
            else:
                base = attacker.attack

            damage = int(base * multiplier * (1 + random.random() * 0.2))
            return max(1, damage)

        def get_rewards(self):
            """Calculate battle rewards."""
            total_xp = 0
            total_gold = 0
            items = []

            for enemy in self.enemies:
                total_xp += enemy.xp_reward
                total_gold += enemy.gold_reward
                items.extend(enemy.get_drops())

            return total_xp, total_gold, items

        def log(self, message):
            """Add message to battle log."""
            self.battle_log.append(message)
            if len(self.battle_log) > 10:
                self.battle_log.pop(0)

# =============================================================================
# ENEMY DATABASE
# =============================================================================

init python:
    ENEMY_DATABASE = {}

    def create_enemy(enemy_id):
        """Create a new enemy instance from database."""
        template = ENEMY_DATABASE.get(enemy_id)
        if template:
            enemy = Enemy(
                template["name"],
                template["hp"],
                template["mp"],
                template["attack"],
                template["defense"],
                template["speed"],
                template.get("magic", 0),
                template.get("xp", 10),
                template.get("gold", 5),
                template.get("drops", [])
            )
            enemy.skills = template.get("skills", [])
            return enemy
        return None

# Define enemies
init python:
    ENEMY_DATABASE["slime"] = {
        "name": "Slime",
        "hp": 30,
        "mp": 0,
        "attack": 5,
        "defense": 2,
        "speed": 3,
        "xp": 10,
        "gold": 5,
        "drops": [("health_potion", 0.2)]
    }

    ENEMY_DATABASE["goblin"] = {
        "name": "Goblin",
        "hp": 50,
        "mp": 10,
        "attack": 12,
        "defense": 5,
        "speed": 8,
        "xp": 25,
        "gold": 15,
        "drops": [("gold_nugget", 0.3), ("rusty_sword", 0.1)]
    }

    ENEMY_DATABASE["wolf"] = {
        "name": "Wolf",
        "hp": 45,
        "mp": 0,
        "attack": 15,
        "defense": 3,
        "speed": 12,
        "xp": 20,
        "gold": 8,
        "drops": [("monster_fang", 0.5)]
    }

    ENEMY_DATABASE["dark_mage"] = {
        "name": "Dark Mage",
        "hp": 40,
        "mp": 50,
        "attack": 5,
        "defense": 4,
        "speed": 7,
        "magic": 20,
        "xp": 50,
        "gold": 30,
        "drops": [("mana_potion", 0.4), ("magic_staff", 0.05)],
        "skills": [
            ("Dark Bolt", 10, 1.5, "damage"),
            ("Shadow Heal", 15, 1.0, "heal")
        ]
    }

    ENEMY_DATABASE["boss_dragon"] = {
        "name": "Ancient Dragon",
        "hp": 500,
        "mp": 100,
        "attack": 35,
        "defense": 20,
        "speed": 10,
        "magic": 30,
        "xp": 500,
        "gold": 300,
        "drops": [("full_restore", 1.0)],
        "skills": [
            ("Fire Breath", 20, 2.0, "damage"),
            ("Tail Swipe", 5, 1.2, "damage")
        ]
    }

# =============================================================================
# COMBAT INSTANCE
# =============================================================================

default combat = CombatManager()

# =============================================================================
# COMBAT SCREEN
# =============================================================================

screen combat_screen():
    tag menu
    modal True

    frame:
        xfill True
        yfill True
        background Solid("#1a1a2e")

        vbox:
            spacing 10

            # Enemy area
            frame:
                xfill True
                ysize 200
                background Solid("#2a2a4e")
                padding (20, 20)

                hbox:
                    spacing 50
                    xalign 0.5

                    for enemy in combat.enemies:
                        vbox:
                            spacing 5

                            text enemy.name size 20 color "#ff6666" xalign 0.5

                            # HP Bar
                            frame:
                                xsize 150
                                ysize 20
                                background Solid("#333")

                                frame:
                                    xsize int(150 * enemy.hp / enemy.max_hp)
                                    ysize 20
                                    background Solid("#cc3333")

                            text "[enemy.hp]/[enemy.max_hp]" size 14 color "#aaa" xalign 0.5

                            if combat.state == "player_turn":
                                textbutton "Target" action Function(combat.player_attack, enemy) xalign 0.5

            # Battle log
            frame:
                xfill True
                ysize 150
                background Solid("#111122")
                padding (10, 10)

                viewport:
                    scrollbars None
                    mousewheel True
                    yinitial 1.0

                    vbox:
                        for msg in combat.battle_log:
                            text msg size 16 color "#aaaaaa"

            # Player stats
            frame:
                xfill True
                ysize 100
                background Solid("#2a2a4e")
                padding (20, 10)

                hbox:
                    spacing 50

                    vbox:
                        text combat.player.name size 24 color "#66ff66"

                        hbox:
                            spacing 20

                            # HP Bar
                            vbox:
                                text "HP" size 14 color "#888"
                                frame:
                                    xsize 200
                                    ysize 20
                                    background Solid("#333")

                                    frame:
                                        xsize int(200 * combat.player.hp / combat.player.max_hp)
                                        ysize 20
                                        background Solid("#33cc33")
                                text "[combat.player.hp]/[combat.player.max_hp]" size 14 color "#aaa"

                            # MP Bar
                            vbox:
                                text "MP" size 14 color "#888"
                                frame:
                                    xsize 150
                                    ysize 20
                                    background Solid("#333")

                                    frame:
                                        xsize int(150 * combat.player.mp / max(1, combat.player.max_mp))
                                        ysize 20
                                        background Solid("#3333cc")
                                text "[combat.player.mp]/[combat.player.max_mp]" size 14 color "#aaa"

            # Action buttons
            if combat.state == "player_turn":
                frame:
                    xfill True
                    background Solid("#333355")
                    padding (20, 15)

                    hbox:
                        spacing 20
                        xalign 0.5

                        textbutton "Attack" action NullAction() # Target selection above
                        textbutton "Defend" action Function(combat.player_defend)
                        textbutton "Skills" action Show("combat_skills_screen")
                        textbutton "Items" action Show("combat_items_screen")
                        textbutton "Flee" action Function(combat.player_flee)

            elif combat.state == "victory":
                frame:
                    xfill True
                    background Solid("#335533")
                    padding (20, 15)

                    vbox:
                        xalign 0.5
                        spacing 10

                        text "VICTORY!" size 32 color "#66ff66" xalign 0.5

                        $ xp, gold, items = combat.get_rewards()
                        text "Gained [xp] XP and [gold] Gold!" size 20 color "#fff" xalign 0.5

                        textbutton "Continue" action Return(("victory", xp, gold, items)) xalign 0.5

            elif combat.state == "defeat":
                frame:
                    xfill True
                    background Solid("#553333")
                    padding (20, 15)

                    vbox:
                        xalign 0.5
                        spacing 10

                        text "DEFEAT" size 32 color "#ff6666" xalign 0.5
                        textbutton "Continue" action Return(("defeat", 0, 0, [])) xalign 0.5

            elif combat.state == "fled":
                frame:
                    xfill True
                    background Solid("#555533")
                    padding (20, 15)

                    vbox:
                        xalign 0.5
                        text "Escaped!" size 24 color "#ffff66" xalign 0.5
                        textbutton "Continue" action Return(("fled", 0, 0, [])) xalign 0.5

            else:
                # Enemy turn - show waiting message
                frame:
                    xfill True
                    background Solid("#333355")
                    padding (20, 15)

                    text "Enemy turn..." size 20 color "#aaa" xalign 0.5

screen combat_skills_screen():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 400
        ysize 300
        background Solid("#2a2a4e")
        padding (20, 20)

        vbox:
            spacing 10

            text "Skills" size 24 color "#66aaff"

            # Example skills - integrate with skill tree system
            textbutton "Fire Bolt (10 MP)" action [Hide("combat_skills_screen"), Function(combat.player_skill, "Fire Bolt", 10, 1.5, combat.enemies[0] if combat.enemies else None)]
            textbutton "Heal (15 MP)" action NullAction()

            null height 20
            textbutton "Back" action Hide("combat_skills_screen") xalign 0.5

screen combat_items_screen():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 400
        ysize 300
        background Solid("#2a2a4e")
        padding (20, 20)

        vbox:
            spacing 10

            text "Items" size 24 color "#66aaff"

            # Would integrate with inventory system
            text "No usable items" size 16 color "#888"

            null height 20
            textbutton "Back" action Hide("combat_items_screen") xalign 0.5

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

init python:
    def start_combat(enemy_ids):
        """Start combat with specified enemies."""
        # Create player combatant from stats system (integrate with stats.rpy)
        player_combatant = Combatant("Player", 100, 50, 15, 10, 10, 8)

        # Create enemies
        enemies = []
        if isinstance(enemy_ids, str):
            enemy_ids = [enemy_ids]

        for eid in enemy_ids:
            enemy = create_enemy(eid)
            if enemy:
                enemies.append(enemy)

        if enemies:
            combat.start_battle(player_combatant, enemies)
            return True
        return False

# =============================================================================
# EXAMPLE USAGE (in script.rpy):
# =============================================================================
#
# # Start a battle
# $ start_combat("goblin")
# $ result = renpy.call_screen("combat_screen")
#
# if result[0] == "victory":
#     $ xp, gold, items = result[1], result[2], result[3]
#     "You won! Gained [xp] XP and [gold] gold!"
#
# elif result[0] == "defeat":
#     "Game Over..."
#     jump game_over
#
# # Battle multiple enemies
# $ start_combat(["goblin", "goblin", "wolf"])
# call screen combat_screen

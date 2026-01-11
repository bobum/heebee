# Skill Tree System for Ren'Py
# Provides skill trees, unlockable abilities, and skill management

init python:
    # =========================================================================
    # SKILL CLASS
    # =========================================================================

    class Skill:
        """Represents a single skill in the skill tree."""

        def __init__(self, id, name, description, branch, cost=1,
                     prerequisites=None, max_level=1, skill_type="active"):
            self.id = id
            self.name = name
            self.description = description
            self.branch = branch  # combat, magic, social, utility
            self.cost = cost  # Skill points to unlock
            self.prerequisites = prerequisites or []  # List of skill IDs required
            self.max_level = max_level
            self.skill_type = skill_type  # active, passive

            # Effects at each level
            self.effects = {}  # {level: {effect_type: value}}

            # For active skills
            self.mp_cost = 0
            self.cooldown = 0
            self.target_type = "enemy"  # enemy, self, ally, all_enemies

        def set_effects(self, level_effects):
            """Set effects for each level. {1: {"damage": 10}, 2: {"damage": 15}}"""
            self.effects = level_effects

        def get_effect(self, effect_type, level=1):
            """Get effect value at specified level."""
            if level in self.effects:
                return self.effects[level].get(effect_type, 0)
            return 0

        def __repr__(self):
            return f"Skill({self.id}: {self.name})"

    # =========================================================================
    # SKILL TREE CLASS
    # =========================================================================

    class SkillTree:
        """Manages all skills and player's progression."""

        BRANCHES = ["combat", "magic", "social", "utility"]

        def __init__(self):
            self.skill_points = 0
            self.unlocked_skills = {}  # {skill_id: current_level}
            self.active_skills = []  # Skills equipped for combat (max 4)
            self.max_active_skills = 4

        def add_skill_points(self, points):
            """Add skill points."""
            self.skill_points += points

        def can_unlock(self, skill_id):
            """Check if a skill can be unlocked."""
            skill = SKILL_DATABASE.get(skill_id)
            if not skill:
                return False

            # Already at max level?
            current_level = self.unlocked_skills.get(skill_id, 0)
            if current_level >= skill.max_level:
                return False

            # Have enough points?
            if self.skill_points < skill.cost:
                return False

            # Prerequisites met?
            for prereq_id in skill.prerequisites:
                if prereq_id not in self.unlocked_skills:
                    return False

            return True

        def unlock_skill(self, skill_id):
            """Unlock or upgrade a skill."""
            if not self.can_unlock(skill_id):
                return False

            skill = SKILL_DATABASE[skill_id]
            self.skill_points -= skill.cost

            current_level = self.unlocked_skills.get(skill_id, 0)
            self.unlocked_skills[skill_id] = current_level + 1

            return True

        def get_skill_level(self, skill_id):
            """Get current level of a skill."""
            return self.unlocked_skills.get(skill_id, 0)

        def has_skill(self, skill_id, min_level=1):
            """Check if player has skill at minimum level."""
            return self.get_skill_level(skill_id) >= min_level

        def equip_active_skill(self, skill_id):
            """Equip an active skill for combat."""
            if skill_id not in self.unlocked_skills:
                return False

            skill = SKILL_DATABASE.get(skill_id)
            if not skill or skill.skill_type != "active":
                return False

            if skill_id in self.active_skills:
                return True

            if len(self.active_skills) >= self.max_active_skills:
                return False

            self.active_skills.append(skill_id)
            return True

        def unequip_active_skill(self, skill_id):
            """Unequip an active skill."""
            if skill_id in self.active_skills:
                self.active_skills.remove(skill_id)
                return True
            return False

        def get_equipped_skills(self):
            """Get list of equipped active skills."""
            return [SKILL_DATABASE[sid] for sid in self.active_skills if sid in SKILL_DATABASE]

        def get_skills_by_branch(self, branch):
            """Get all skills in a branch."""
            return [s for s in SKILL_DATABASE.values() if s.branch == branch]

        def get_unlocked_by_branch(self, branch):
            """Get unlocked skills in a branch."""
            return [(SKILL_DATABASE[sid], level) for sid, level in self.unlocked_skills.items()
                    if SKILL_DATABASE.get(sid) and SKILL_DATABASE[sid].branch == branch]

        def get_passive_bonuses(self):
            """Calculate total bonuses from all passive skills."""
            bonuses = {}

            for skill_id, level in self.unlocked_skills.items():
                skill = SKILL_DATABASE.get(skill_id)
                if skill and skill.skill_type == "passive":
                    for effect_type, value in skill.effects.get(level, {}).items():
                        bonuses[effect_type] = bonuses.get(effect_type, 0) + value

            return bonuses

        def to_dict(self):
            """Convert to dictionary for saving."""
            return {
                "skill_points": self.skill_points,
                "unlocked_skills": self.unlocked_skills.copy(),
                "active_skills": self.active_skills.copy()
            }

        def from_dict(self, data):
            """Load from dictionary."""
            self.skill_points = data.get("skill_points", 0)
            self.unlocked_skills = data.get("unlocked_skills", {})
            self.active_skills = data.get("active_skills", [])

# =============================================================================
# SKILL DATABASE
# =============================================================================

init python:
    SKILL_DATABASE = {}

    def register_skill(skill):
        """Register a skill in the database."""
        SKILL_DATABASE[skill.id] = skill
        return skill

# Define skills
init python:
    # === COMBAT BRANCH ===

    # Tier 1
    power_strike = Skill(
        id="power_strike",
        name="Power Strike",
        description="A powerful melee attack dealing increased damage.",
        branch="combat",
        cost=1,
        max_level=3,
        skill_type="active"
    )
    power_strike.mp_cost = 5
    power_strike.set_effects({
        1: {"damage_mult": 1.5},
        2: {"damage_mult": 1.8},
        3: {"damage_mult": 2.2}
    })
    register_skill(power_strike)

    toughness = Skill(
        id="toughness",
        name="Toughness",
        description="Permanently increases maximum HP.",
        branch="combat",
        cost=1,
        max_level=5,
        skill_type="passive"
    )
    toughness.set_effects({
        1: {"max_hp": 10},
        2: {"max_hp": 25},
        3: {"max_hp": 45},
        4: {"max_hp": 70},
        5: {"max_hp": 100}
    })
    register_skill(toughness)

    # Tier 2
    double_strike = Skill(
        id="double_strike",
        name="Double Strike",
        description="Attack twice in rapid succession.",
        branch="combat",
        cost=2,
        prerequisites=["power_strike"],
        max_level=2,
        skill_type="active"
    )
    double_strike.mp_cost = 12
    double_strike.set_effects({
        1: {"hits": 2, "damage_mult": 0.7},
        2: {"hits": 2, "damage_mult": 0.85}
    })
    register_skill(double_strike)

    armor_mastery = Skill(
        id="armor_mastery",
        name="Armor Mastery",
        description="Increases defense from equipped armor.",
        branch="combat",
        cost=2,
        prerequisites=["toughness"],
        max_level=3,
        skill_type="passive"
    )
    armor_mastery.set_effects({
        1: {"armor_mult": 1.1},
        2: {"armor_mult": 1.2},
        3: {"armor_mult": 1.35}
    })
    register_skill(armor_mastery)

    # Tier 3
    berserker_rage = Skill(
        id="berserker_rage",
        name="Berserker Rage",
        description="Enter a rage, greatly increasing attack but lowering defense.",
        branch="combat",
        cost=3,
        prerequisites=["double_strike", "armor_mastery"],
        max_level=1,
        skill_type="active"
    )
    berserker_rage.mp_cost = 25
    berserker_rage.set_effects({
        1: {"attack_buff": 50, "defense_debuff": 20, "duration": 3}
    })
    register_skill(berserker_rage)

    # === MAGIC BRANCH ===

    # Tier 1
    fire_bolt = Skill(
        id="fire_bolt",
        name="Fire Bolt",
        description="Launch a bolt of fire at an enemy.",
        branch="magic",
        cost=1,
        max_level=3,
        skill_type="active"
    )
    fire_bolt.mp_cost = 8
    fire_bolt.set_effects({
        1: {"magic_damage": 15},
        2: {"magic_damage": 25},
        3: {"magic_damage": 40}
    })
    register_skill(fire_bolt)

    mana_well = Skill(
        id="mana_well",
        name="Mana Well",
        description="Increases maximum MP.",
        branch="magic",
        cost=1,
        max_level=5,
        skill_type="passive"
    )
    mana_well.set_effects({
        1: {"max_mp": 10},
        2: {"max_mp": 25},
        3: {"max_mp": 45},
        4: {"max_mp": 70},
        5: {"max_mp": 100}
    })
    register_skill(mana_well)

    # Tier 2
    ice_shard = Skill(
        id="ice_shard",
        name="Ice Shard",
        description="Hurl a shard of ice that may slow the enemy.",
        branch="magic",
        cost=2,
        prerequisites=["fire_bolt"],
        max_level=2,
        skill_type="active"
    )
    ice_shard.mp_cost = 12
    ice_shard.set_effects({
        1: {"magic_damage": 20, "slow_chance": 0.3},
        2: {"magic_damage": 35, "slow_chance": 0.5}
    })
    register_skill(ice_shard)

    healing_light = Skill(
        id="healing_light",
        name="Healing Light",
        description="Restore HP to yourself or an ally.",
        branch="magic",
        cost=2,
        prerequisites=["mana_well"],
        max_level=3,
        skill_type="active"
    )
    healing_light.mp_cost = 15
    healing_light.target_type = "ally"
    healing_light.set_effects({
        1: {"heal": 30},
        2: {"heal": 50},
        3: {"heal": 80}
    })
    register_skill(healing_light)

    # Tier 3
    thunderstorm = Skill(
        id="thunderstorm",
        name="Thunderstorm",
        description="Call down lightning on all enemies.",
        branch="magic",
        cost=3,
        prerequisites=["ice_shard"],
        max_level=1,
        skill_type="active"
    )
    thunderstorm.mp_cost = 35
    thunderstorm.target_type = "all_enemies"
    thunderstorm.set_effects({
        1: {"magic_damage": 45, "stun_chance": 0.2}
    })
    register_skill(thunderstorm)

    # === SOCIAL BRANCH ===

    # Tier 1
    silver_tongue = Skill(
        id="silver_tongue",
        name="Silver Tongue",
        description="Improves prices when buying and selling.",
        branch="social",
        cost=1,
        max_level=3,
        skill_type="passive"
    )
    silver_tongue.set_effects({
        1: {"price_modifier": 0.05},
        2: {"price_modifier": 0.10},
        3: {"price_modifier": 0.15}
    })
    register_skill(silver_tongue)

    keen_eye = Skill(
        id="keen_eye",
        name="Keen Eye",
        description="Increases chance of finding hidden items.",
        branch="social",
        cost=1,
        max_level=3,
        skill_type="passive"
    )
    keen_eye.set_effects({
        1: {"discovery_chance": 0.1},
        2: {"discovery_chance": 0.2},
        3: {"discovery_chance": 0.35}
    })
    register_skill(keen_eye)

    # Tier 2
    intimidate = Skill(
        id="intimidate",
        name="Intimidate",
        description="Frighten enemies, potentially making them flee.",
        branch="social",
        cost=2,
        prerequisites=["silver_tongue"],
        max_level=2,
        skill_type="active"
    )
    intimidate.mp_cost = 10
    intimidate.set_effects({
        1: {"flee_chance": 0.2, "defense_debuff": 5},
        2: {"flee_chance": 0.35, "defense_debuff": 10}
    })
    register_skill(intimidate)

    charm = Skill(
        id="charm",
        name="Charm",
        description="Unlock special dialogue options with NPCs.",
        branch="social",
        cost=2,
        prerequisites=["silver_tongue"],
        max_level=1,
        skill_type="passive"
    )
    charm.set_effects({
        1: {"unlock_dialogue": True}
    })
    register_skill(charm)

    # === UTILITY BRANCH ===

    # Tier 1
    quick_feet = Skill(
        id="quick_feet",
        name="Quick Feet",
        description="Increases speed and flee chance.",
        branch="utility",
        cost=1,
        max_level=3,
        skill_type="passive"
    )
    quick_feet.set_effects({
        1: {"speed": 3, "flee_bonus": 0.1},
        2: {"speed": 6, "flee_bonus": 0.2},
        3: {"speed": 10, "flee_bonus": 0.3}
    })
    register_skill(quick_feet)

    lucky_star = Skill(
        id="lucky_star",
        name="Lucky Star",
        description="Increases critical hit chance and item drop rates.",
        branch="utility",
        cost=1,
        max_level=3,
        skill_type="passive"
    )
    lucky_star.set_effects({
        1: {"crit_chance": 0.05, "drop_bonus": 0.1},
        2: {"crit_chance": 0.10, "drop_bonus": 0.2},
        3: {"crit_chance": 0.15, "drop_bonus": 0.35}
    })
    register_skill(lucky_star)

    # Tier 2
    treasure_hunter = Skill(
        id="treasure_hunter",
        name="Treasure Hunter",
        description="Find extra gold after battles.",
        branch="utility",
        cost=2,
        prerequisites=["lucky_star"],
        max_level=2,
        skill_type="passive"
    )
    treasure_hunter.set_effects({
        1: {"gold_bonus": 0.15},
        2: {"gold_bonus": 0.30}
    })
    register_skill(treasure_hunter)

    survivalist = Skill(
        id="survivalist",
        name="Survivalist",
        description="Reduces damage taken when HP is low.",
        branch="utility",
        cost=2,
        prerequisites=["quick_feet"],
        max_level=2,
        skill_type="passive"
    )
    survivalist.set_effects({
        1: {"low_hp_defense": 0.15, "threshold": 0.25},
        2: {"low_hp_defense": 0.30, "threshold": 0.30}
    })
    register_skill(survivalist)

# =============================================================================
# PLAYER SKILL TREE INSTANCE
# =============================================================================

default player_skills = SkillTree()

# =============================================================================
# SKILL TREE SCREEN
# =============================================================================

screen skill_tree_screen():
    tag menu
    modal True

    frame:
        xfill True
        yfill True
        background Solid("#1a1a2e")
        padding (20, 20)

        vbox:
            spacing 10

            # Header
            hbox:
                text "Skill Tree" size 32 color "#66aaff"
                xfill True
                text "Skill Points: [player_skills.skill_points]" size 24 color "#ffcc66" xalign 1.0

            null height 10

            # Branch tabs
            default current_branch = "combat"

            hbox:
                spacing 10

                for branch in SkillTree.BRANCHES:
                    textbutton branch.capitalize():
                        action SetScreenVariable("current_branch", branch)
                        style "skill_tab_button"
                        selected current_branch == branch

            null height 20

            # Skills in current branch
            viewport:
                scrollbars "vertical"
                mousewheel True
                xfill True
                ysize 400

                vbox:
                    spacing 15

                    for skill in player_skills.get_skills_by_branch(current_branch):
                        $ current_level = player_skills.get_skill_level(skill.id)
                        $ can_unlock = player_skills.can_unlock(skill.id)
                        $ is_unlocked = current_level > 0

                        frame:
                            xfill True
                            padding (15, 10)

                            if is_unlocked:
                                background Solid("#2a4a2a")
                            elif can_unlock:
                                background Solid("#4a4a2a")
                            else:
                                background Solid("#2a2a3e")

                            hbox:
                                spacing 15

                                # Skill info
                                vbox:
                                    xsize 500

                                    hbox:
                                        text skill.name size 20 color "#fff"
                                        text " ([skill.skill_type])" size 16 color "#888"

                                    text skill.description size 14 color "#aaa"

                                    if skill.prerequisites:
                                        $ prereq_names = [SKILL_DATABASE[p].name for p in skill.prerequisites if p in SKILL_DATABASE]
                                        text "Requires: [', '.join(prereq_names)]" size 12 color "#ff9966"

                                # Level and unlock
                                vbox:
                                    xalign 1.0

                                    text "Level: [current_level]/[skill.max_level]" size 16 color "#aaa"
                                    text "Cost: [skill.cost] SP" size 14 color "#ffcc66"

                                    if can_unlock:
                                        textbutton "Unlock":
                                            action Function(player_skills.unlock_skill, skill.id)
                                            style "skill_unlock_button"
                                    elif current_level >= skill.max_level:
                                        text "MAXED" size 14 color "#66ff66"

            # Active skills section
            null height 20

            frame:
                xfill True
                background Solid("#2a2a4e")
                padding (15, 10)

                vbox:
                    text "Equipped Active Skills ([len(player_skills.active_skills)]/[player_skills.max_active_skills])" size 18 color "#66aaff"

                    hbox:
                        spacing 10

                        for skill in player_skills.get_equipped_skills():
                            frame:
                                background Solid("#445566")
                                padding (10, 5)

                                hbox:
                                    text skill.name size 14 color "#fff"
                                    textbutton "X":
                                        action Function(player_skills.unequip_active_skill, skill.id)
                                        text_size 12

            # Close button
            hbox:
                xalign 0.5
                textbutton "Close" action Hide("skill_tree_screen")

style skill_tab_button:
    background Solid("#333355")
    hover_background Solid("#4444aa")
    selected_background Solid("#5555cc")
    padding (15, 8)

style skill_tab_button_text:
    size 18
    color "#aaa"
    hover_color "#fff"
    selected_color "#fff"

style skill_unlock_button:
    background Solid("#446644")
    hover_background Solid("#55aa55")
    padding (10, 5)

style skill_unlock_button_text:
    size 14
    color "#fff"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

init python:
    def grant_skill_points(amount):
        """Give player skill points."""
        player_skills.add_skill_points(amount)
        renpy.notify(f"Gained {amount} skill point(s)!")

    def has_skill(skill_id, min_level=1):
        """Check if player has a skill."""
        return player_skills.has_skill(skill_id, min_level)

    def get_passive_bonus(bonus_type):
        """Get total passive bonus of a type."""
        return player_skills.get_passive_bonuses().get(bonus_type, 0)

# =============================================================================
# EXAMPLE USAGE (in script.rpy):
# =============================================================================
#
# # Give skill points on level up
# $ grant_skill_points(1)
#
# # Show skill tree
# call screen skill_tree_screen
#
# # Check if player has a skill for dialogue
# if has_skill("charm"):
#     "You use your charm to convince the guard."
#
# # Get passive bonuses
# $ price_mod = get_passive_bonus("price_modifier")
# $ final_price = int(base_price * (1 - price_mod))

# Skill Tree System for Ren'Py Visual Novel
# Provides a complete skill tree with multiple branches, prerequisites, and UI

init python:

    # ============================================================================
    # SKILL CLASS
    # ============================================================================

    class Skill:
        """
        Represents a single skill in the skill tree.

        Attributes:
            id: Unique identifier for the skill
            name: Display name of the skill
            description: Detailed description of what the skill does
            cost: Skill points required to unlock/upgrade
            prerequisites: List of skill IDs that must be unlocked first
            effects: Dictionary of effects the skill provides
            level: Current level of the skill (0 = locked)
            max_level: Maximum level the skill can reach
            skill_type: "active" or "passive"
            branch: Which branch this skill belongs to
            icon: Optional icon path for display
        """

        def __init__(self, id, name, description, cost=1, prerequisites=None,
                     effects=None, max_level=1, skill_type="passive", branch="combat", icon=None):
            self.id = id
            self.name = name
            self.description = description
            self.cost = cost
            self.prerequisites = prerequisites if prerequisites else []
            self.effects = effects if effects else {}
            self.level = 0
            self.max_level = max_level
            self.skill_type = skill_type
            self.branch = branch
            self.icon = icon

        @property
        def is_unlocked(self):
            """Check if the skill has been unlocked (level > 0)."""
            return self.level > 0

        @property
        def is_maxed(self):
            """Check if the skill is at maximum level."""
            return self.level >= self.max_level

        @property
        def is_active(self):
            """Check if this is an active skill."""
            return self.skill_type == "active"

        @property
        def is_passive(self):
            """Check if this is a passive skill."""
            return self.skill_type == "passive"

        def get_current_effect(self, effect_name):
            """Get the current value of an effect based on skill level."""
            if effect_name not in self.effects:
                return 0
            base_value = self.effects[effect_name]
            return base_value * self.level

        def get_next_level_effect(self, effect_name):
            """Get the value of an effect at the next level."""
            if effect_name not in self.effects:
                return 0
            base_value = self.effects[effect_name]
            return base_value * (self.level + 1)

        def unlock(self):
            """Unlock the skill (set level to 1)."""
            if self.level == 0:
                self.level = 1
                return True
            return False

        def upgrade(self):
            """Upgrade the skill by one level."""
            if self.level < self.max_level:
                self.level += 1
                return True
            return False

        def __repr__(self):
            return f"Skill({self.id}, level={self.level}/{self.max_level})"


    # ============================================================================
    # SKILL TREE CLASS
    # ============================================================================

    class SkillTree:
        """
        Manages the entire skill tree system with multiple branches.

        Branches:
            - Combat: Physical fighting abilities
            - Magic: Magical spells and abilities
            - Social: Dialogue and relationship skills
            - Utility: General purpose skills and bonuses
        """

        BRANCHES = ["combat", "magic", "social", "utility"]

        def __init__(self):
            self.skills = {}
            self.skill_points = 0
            self.total_points_earned = 0
            self._initialize_skills()

        def _initialize_skills(self):
            """Initialize all skills in the skill tree."""

            # ====================================================================
            # COMBAT BRANCH
            # ====================================================================

            # Tier 1 - Base combat skills
            self.add_skill(Skill(
                id="power_strike",
                name="Power Strike",
                description="A powerful melee attack that deals increased damage.",
                cost=1,
                prerequisites=[],
                effects={"damage_bonus": 10, "crit_chance": 5},
                max_level=5,
                skill_type="active",
                branch="combat"
            ))

            self.add_skill(Skill(
                id="defensive_stance",
                name="Defensive Stance",
                description="Adopt a defensive posture, reducing incoming damage.",
                cost=1,
                prerequisites=[],
                effects={"damage_reduction": 5, "block_chance": 10},
                max_level=3,
                skill_type="active",
                branch="combat"
            ))

            # Tier 2 - Requires tier 1
            self.add_skill(Skill(
                id="critical_mastery",
                name="Critical Mastery",
                description="Increases critical hit chance and damage.",
                cost=2,
                prerequisites=["power_strike"],
                effects={"crit_chance": 8, "crit_damage": 15},
                max_level=3,
                skill_type="passive",
                branch="combat"
            ))

            self.add_skill(Skill(
                id="iron_skin",
                name="Iron Skin",
                description="Permanently increases your defense.",
                cost=2,
                prerequisites=["defensive_stance"],
                effects={"defense": 10, "health": 20},
                max_level=5,
                skill_type="passive",
                branch="combat"
            ))

            # Tier 3 - Ultimate combat
            self.add_skill(Skill(
                id="berserker_rage",
                name="Berserker Rage",
                description="Enter a powerful rage, greatly increasing attack power but reducing defense.",
                cost=3,
                prerequisites=["critical_mastery", "power_strike"],
                effects={"damage_bonus": 25, "attack_speed": 20},
                max_level=3,
                skill_type="active",
                branch="combat"
            ))

            # ====================================================================
            # MAGIC BRANCH
            # ====================================================================

            # Tier 1 - Base magic skills
            self.add_skill(Skill(
                id="mana_bolt",
                name="Mana Bolt",
                description="A basic magical projectile that deals arcane damage.",
                cost=1,
                prerequisites=[],
                effects={"magic_damage": 15, "mana_cost": -5},
                max_level=5,
                skill_type="active",
                branch="magic"
            ))

            self.add_skill(Skill(
                id="arcane_shield",
                name="Arcane Shield",
                description="Create a magical barrier that absorbs damage.",
                cost=1,
                prerequisites=[],
                effects={"shield_strength": 20, "duration": 2},
                max_level=3,
                skill_type="active",
                branch="magic"
            ))

            # Tier 2 - Elemental magic
            self.add_skill(Skill(
                id="fire_mastery",
                name="Fire Mastery",
                description="Increases fire damage and unlocks fire spells.",
                cost=2,
                prerequisites=["mana_bolt"],
                effects={"fire_damage": 20, "burn_chance": 15},
                max_level=3,
                skill_type="passive",
                branch="magic"
            ))

            self.add_skill(Skill(
                id="mana_regeneration",
                name="Mana Regeneration",
                description="Passively regenerate mana over time.",
                cost=2,
                prerequisites=["arcane_shield"],
                effects={"mana_regen": 5, "max_mana": 25},
                max_level=5,
                skill_type="passive",
                branch="magic"
            ))

            # Tier 3 - Ultimate magic
            self.add_skill(Skill(
                id="meteor_storm",
                name="Meteor Storm",
                description="Call down a devastating storm of meteors.",
                cost=3,
                prerequisites=["fire_mastery", "mana_bolt"],
                effects={"aoe_damage": 50, "stun_chance": 25},
                max_level=3,
                skill_type="active",
                branch="magic"
            ))

            # ====================================================================
            # SOCIAL BRANCH
            # ====================================================================

            # Tier 1 - Base social skills
            self.add_skill(Skill(
                id="persuasion",
                name="Persuasion",
                description="Increases your ability to convince others in dialogue.",
                cost=1,
                prerequisites=[],
                effects={"persuade_bonus": 15, "unlock_options": 1},
                max_level=5,
                skill_type="passive",
                branch="social"
            ))

            self.add_skill(Skill(
                id="empathy",
                name="Empathy",
                description="Better understand the emotions and motivations of others.",
                cost=1,
                prerequisites=[],
                effects={"insight_bonus": 10, "relationship_gain": 10},
                max_level=3,
                skill_type="passive",
                branch="social"
            ))

            # Tier 2 - Advanced social
            self.add_skill(Skill(
                id="silver_tongue",
                name="Silver Tongue",
                description="Master the art of speech, unlocking special dialogue options.",
                cost=2,
                prerequisites=["persuasion"],
                effects={"special_dialogue": 1, "price_reduction": 10},
                max_level=3,
                skill_type="passive",
                branch="social"
            ))

            self.add_skill(Skill(
                id="emotional_intelligence",
                name="Emotional Intelligence",
                description="Gain deeper insights into character relationships.",
                cost=2,
                prerequisites=["empathy"],
                effects={"relationship_speed": 20, "hidden_info": 1},
                max_level=3,
                skill_type="passive",
                branch="social"
            ))

            # Tier 3 - Ultimate social
            self.add_skill(Skill(
                id="master_manipulator",
                name="Master Manipulator",
                description="Bend others to your will with masterful social skills.",
                cost=3,
                prerequisites=["silver_tongue", "emotional_intelligence"],
                effects={"mind_control_chance": 20, "all_social": 25},
                max_level=3,
                skill_type="active",
                branch="social"
            ))

            # ====================================================================
            # UTILITY BRANCH
            # ====================================================================

            # Tier 1 - Base utility skills
            self.add_skill(Skill(
                id="quick_learner",
                name="Quick Learner",
                description="Gain bonus experience from all sources.",
                cost=1,
                prerequisites=[],
                effects={"exp_bonus": 10},
                max_level=5,
                skill_type="passive",
                branch="utility"
            ))

            self.add_skill(Skill(
                id="treasure_hunter",
                name="Treasure Hunter",
                description="Find more gold and better items.",
                cost=1,
                prerequisites=[],
                effects={"gold_bonus": 15, "item_quality": 10},
                max_level=3,
                skill_type="passive",
                branch="utility"
            ))

            # Tier 2 - Advanced utility
            self.add_skill(Skill(
                id="efficient_training",
                name="Efficient Training",
                description="Reduce the cost of learning new skills.",
                cost=2,
                prerequisites=["quick_learner"],
                effects={"skill_cost_reduction": 1},
                max_level=2,
                skill_type="passive",
                branch="utility"
            ))

            self.add_skill(Skill(
                id="lucky_star",
                name="Lucky Star",
                description="Increase your luck in all random events.",
                cost=2,
                prerequisites=["treasure_hunter"],
                effects={"luck": 15, "rare_find": 10},
                max_level=3,
                skill_type="passive",
                branch="utility"
            ))

            # Tier 3 - Ultimate utility
            self.add_skill(Skill(
                id="jack_of_all_trades",
                name="Jack of All Trades",
                description="Gain a bonus to all stats and abilities.",
                cost=3,
                prerequisites=["efficient_training", "lucky_star"],
                effects={"all_stats": 10, "versatility": 15},
                max_level=3,
                skill_type="passive",
                branch="utility"
            ))

        def add_skill(self, skill):
            """Add a skill to the skill tree."""
            self.skills[skill.id] = skill

        def get_skill(self, skill_id):
            """Get a skill by its ID."""
            return self.skills.get(skill_id)

        def get_branch_skills(self, branch):
            """Get all skills in a specific branch."""
            return [s for s in self.skills.values() if s.branch == branch]

        def check_prerequisites(self, skill_id):
            """
            Check if all prerequisites for a skill are met.
            Returns True if all prerequisites are unlocked.
            """
            skill = self.get_skill(skill_id)
            if not skill:
                return False

            for prereq_id in skill.prerequisites:
                prereq = self.get_skill(prereq_id)
                if not prereq or not prereq.is_unlocked:
                    return False
            return True

        def can_unlock_skill(self, skill_id):
            """Check if a skill can be unlocked."""
            skill = self.get_skill(skill_id)
            if not skill:
                return False

            # Check if already unlocked
            if skill.is_unlocked:
                return False

            # Check prerequisites
            if not self.check_prerequisites(skill_id):
                return False

            # Check skill points (accounting for cost reduction from efficient_training)
            actual_cost = self.get_skill_cost(skill_id)
            if self.skill_points < actual_cost:
                return False

            return True

        def can_upgrade_skill(self, skill_id):
            """Check if a skill can be upgraded."""
            skill = self.get_skill(skill_id)
            if not skill:
                return False

            # Must be unlocked first
            if not skill.is_unlocked:
                return False

            # Check if at max level
            if skill.is_maxed:
                return False

            # Check skill points
            actual_cost = self.get_skill_cost(skill_id)
            if self.skill_points < actual_cost:
                return False

            return True

        def get_skill_cost(self, skill_id):
            """Get the actual cost of a skill, accounting for cost reduction."""
            skill = self.get_skill(skill_id)
            if not skill:
                return 0

            base_cost = skill.cost

            # Apply cost reduction from efficient_training
            efficient = self.get_skill("efficient_training")
            if efficient and efficient.is_unlocked:
                reduction = efficient.get_current_effect("skill_cost_reduction")
                base_cost = max(1, base_cost - reduction)

            return base_cost

        def unlock_skill(self, skill_id):
            """
            Attempt to unlock a skill.
            Returns True if successful, False otherwise.
            """
            if not self.can_unlock_skill(skill_id):
                return False

            skill = self.get_skill(skill_id)
            cost = self.get_skill_cost(skill_id)

            self.skill_points -= cost
            skill.unlock()
            return True

        def upgrade_skill(self, skill_id):
            """
            Attempt to upgrade a skill.
            Returns True if successful, False otherwise.
            """
            if not self.can_upgrade_skill(skill_id):
                return False

            skill = self.get_skill(skill_id)
            cost = self.get_skill_cost(skill_id)

            self.skill_points -= cost
            skill.upgrade()
            return True

        def add_skill_points(self, amount):
            """Add skill points (usually from leveling up)."""
            self.skill_points += amount
            self.total_points_earned += amount

        def on_level_up(self, new_level):
            """Called when the player levels up. Awards skill points."""
            # Award 2 skill points per level, plus 1 bonus every 5 levels
            points = 2
            if new_level % 5 == 0:
                points += 1

            # Apply quick_learner bonus
            quick = self.get_skill("quick_learner")
            if quick and quick.is_unlocked:
                bonus_chance = quick.get_current_effect("exp_bonus")
                # 10% bonus per level means occasional extra point
                if renpy.random.randint(1, 100) <= bonus_chance:
                    points += 1

            self.add_skill_points(points)
            return points

        def get_unlocked_skills(self):
            """Get all unlocked skills."""
            return [s for s in self.skills.values() if s.is_unlocked]

        def get_active_skills(self):
            """Get all unlocked active skills."""
            return [s for s in self.skills.values() if s.is_unlocked and s.is_active]

        def get_passive_skills(self):
            """Get all unlocked passive skills."""
            return [s for s in self.skills.values() if s.is_unlocked and s.is_passive]

        def get_total_effect(self, effect_name):
            """Get the total value of an effect from all unlocked skills."""
            total = 0
            for skill in self.get_unlocked_skills():
                total += skill.get_current_effect(effect_name)
            return total

        def reset_all_skills(self):
            """Reset all skills and refund skill points."""
            refund = 0
            for skill in self.skills.values():
                if skill.is_unlocked:
                    # Refund based on current level
                    refund += skill.cost * skill.level
                    skill.level = 0
            self.skill_points += refund
            return refund

        def reset_branch(self, branch):
            """Reset all skills in a branch and refund skill points."""
            refund = 0
            for skill in self.get_branch_skills(branch):
                if skill.is_unlocked:
                    refund += skill.cost * skill.level
                    skill.level = 0
            self.skill_points += refund
            return refund


# ============================================================================
# GLOBAL SKILL TREE INSTANCE
# ============================================================================

default skill_tree = SkillTree()


# ============================================================================
# SKILL TREE SCREEN UI
# ============================================================================

style skill_tree_frame:
    background "#1a1a2e"
    padding (20, 20)

style skill_branch_frame:
    background "#16213e"
    padding (15, 15)
    margin (5, 5)

style skill_button:
    background "#0f3460"
    hover_background "#e94560"
    padding (10, 10)
    minimum (120, 80)

style skill_button_locked:
    background "#333333"
    padding (10, 10)
    minimum (120, 80)

style skill_button_maxed:
    background "#1e5631"
    padding (10, 10)
    minimum (120, 80)

style skill_name_text:
    color "#ffffff"
    size 14
    text_align 0.5

style skill_level_text:
    color "#aaaaaa"
    size 12
    text_align 0.5

style skill_points_text:
    color "#ffd700"
    size 18
    text_align 0.5

style branch_title_text:
    color "#e94560"
    size 20
    text_align 0.5


screen skill_tree_screen():
    tag menu
    modal True

    frame:
        style "skill_tree_frame"
        xfill True
        yfill True

        vbox:
            spacing 10

            # Header
            hbox:
                xfill True

                text "Skill Tree" size 28 color "#ffffff"

                null width 50

                text "Skill Points: [skill_tree.skill_points]" style "skill_points_text"

                null width 50

                textbutton "Close" action Return() xalign 1.0

            null height 20

            # Branch tabs
            hbox:
                spacing 10
                xalign 0.5

                for branch in SkillTree.BRANCHES:
                    textbutton branch.capitalize():
                        action SetScreenVariable("current_branch", branch)
                        style "skill_button"

            null height 10

            # Default to combat branch
            default current_branch = "combat"

            # Skill display area
            frame:
                style "skill_branch_frame"
                xfill True
                yfill True

                viewport:
                    scrollbars "vertical"
                    mousewheel True

                    vbox:
                        spacing 15

                        text "[current_branch.capitalize()] Skills" style "branch_title_text" xalign 0.5

                        null height 10

                        # Display skills in tiers
                        python:
                            branch_skills = skill_tree.get_branch_skills(current_branch)
                            # Sort by number of prerequisites (tier)
                            tier_0 = [s for s in branch_skills if len(s.prerequisites) == 0]
                            tier_1 = [s for s in branch_skills if len(s.prerequisites) == 1]
                            tier_2 = [s for s in branch_skills if len(s.prerequisites) >= 2]

                        # Tier labels and skills
                        if tier_0:
                            text "Tier 1 - Basic" color "#888888" size 14 xalign 0.5
                            hbox:
                                spacing 20
                                xalign 0.5
                                for skill in tier_0:
                                    use skill_display(skill)

                        if tier_1:
                            null height 20
                            text "Tier 2 - Advanced" color "#888888" size 14 xalign 0.5
                            hbox:
                                spacing 20
                                xalign 0.5
                                for skill in tier_1:
                                    use skill_display(skill)

                        if tier_2:
                            null height 20
                            text "Tier 3 - Ultimate" color "#888888" size 14 xalign 0.5
                            hbox:
                                spacing 20
                                xalign 0.5
                                for skill in tier_2:
                                    use skill_display(skill)


screen skill_display(skill):
    $ can_unlock = skill_tree.can_unlock_skill(skill.id)
    $ can_upgrade = skill_tree.can_upgrade_skill(skill.id)
    $ prereqs_met = skill_tree.check_prerequisites(skill.id)
    $ cost = skill_tree.get_skill_cost(skill.id)

    vbox:
        spacing 5

        # Skill button with appropriate style
        if skill.is_maxed:
            button:
                style "skill_button_maxed"
                action NullAction()

                vbox:
                    xalign 0.5
                    text skill.name style "skill_name_text"
                    text "MAXED" color "#90ee90" size 12 xalign 0.5
                    text "[skill.level]/[skill.max_level]" style "skill_level_text"
                    if skill.is_active:
                        text "(Active)" color "#ffcc00" size 10 xalign 0.5

        elif skill.is_unlocked:
            button:
                style "skill_button"
                action Function(skill_tree.upgrade_skill, skill.id)
                sensitive can_upgrade

                vbox:
                    xalign 0.5
                    text skill.name style "skill_name_text"
                    text "[skill.level]/[skill.max_level]" style "skill_level_text"
                    if can_upgrade:
                        text "Upgrade: [cost] pts" color "#90ee90" size 10 xalign 0.5
                    if skill.is_active:
                        text "(Active)" color "#ffcc00" size 10 xalign 0.5

        elif prereqs_met:
            button:
                style "skill_button"
                action Function(skill_tree.unlock_skill, skill.id)
                sensitive can_unlock

                vbox:
                    xalign 0.5
                    text skill.name style "skill_name_text"
                    text "Locked" color "#ff6666" size 12 xalign 0.5
                    text "Cost: [cost] pts" color "#aaaaaa" size 10 xalign 0.5
                    if skill.is_active:
                        text "(Active)" color "#888888" size 10 xalign 0.5

        else:
            button:
                style "skill_button_locked"
                action NullAction()

                vbox:
                    xalign 0.5
                    text skill.name style "skill_name_text" color "#666666"
                    text "Requires:" color "#ff6666" size 10 xalign 0.5
                    for prereq_id in skill.prerequisites:
                        $ prereq = skill_tree.get_skill(prereq_id)
                        if prereq and not prereq.is_unlocked:
                            text prereq.name color "#ff6666" size 9 xalign 0.5

        # Tooltip on hover
        if GetTooltip() == skill.id:
            frame:
                background "#000000cc"
                padding (10, 10)

                vbox:
                    text skill.name color "#ffffff" size 16
                    text skill.description color "#cccccc" size 12
                    null height 5
                    text "Type: [skill.skill_type.capitalize()]" color "#aaaaaa" size 11
                    if skill.effects:
                        text "Effects:" color "#90ee90" size 11
                        for effect, value in skill.effects.items():
                            $ effect_display = effect.replace("_", " ").title()
                            text "  [effect_display]: +[value] per level" color "#88cc88" size 10


# ============================================================================
# SKILL TOOLTIP SCREEN
# ============================================================================

screen skill_tooltip(skill):
    frame:
        background "#000000dd"
        padding (15, 15)

        vbox:
            spacing 5

            text skill.name color "#ffffff" size 18 bold True

            null height 5

            text skill.description color "#cccccc" size 13

            null height 10

            hbox:
                text "Type: " color "#888888" size 12
                if skill.is_active:
                    text "Active" color "#ffcc00" size 12
                else:
                    text "Passive" color "#66ccff" size 12

            hbox:
                text "Level: " color "#888888" size 12
                text "[skill.level]/[skill.max_level]" color "#ffffff" size 12

            if skill.effects:
                null height 5
                text "Effects:" color "#90ee90" size 12
                for effect_name, value in skill.effects.items():
                    $ effect_display = effect_name.replace("_", " ").title()
                    if skill.is_unlocked:
                        $ current = skill.get_current_effect(effect_name)
                        text "  [effect_display]: +[current]" color "#88cc88" size 11
                    else:
                        text "  [effect_display]: +[value]/level" color "#888888" size 11

            if skill.prerequisites:
                null height 5
                text "Prerequisites:" color "#ff9999" size 12
                for prereq_id in skill.prerequisites:
                    $ prereq = skill_tree.get_skill(prereq_id)
                    if prereq:
                        if prereq.is_unlocked:
                            text "  [prereq.name] (unlocked)" color "#90ee90" size 11
                        else:
                            text "  [prereq.name] (locked)" color "#ff6666" size 11


# ============================================================================
# HELPER LABELS FOR INTEGRATION
# ============================================================================

label open_skill_tree:
    call screen skill_tree_screen
    return

label give_skill_points(amount=1):
    $ skill_tree.add_skill_points(amount)
    "You gained [amount] skill point(s)!"
    return

label player_level_up(new_level):
    $ points_gained = skill_tree.on_level_up(new_level)
    "Level Up! You are now level [new_level]!"
    "You gained [points_gained] skill point(s)!"
    return

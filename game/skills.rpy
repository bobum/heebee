# Heebee - Skill Tree System
# A comprehensive skill tree system for Ren'Py visual novels
#
# ============================================================================
# USAGE EXAMPLES:
# ============================================================================
#
# Initialize skill manager at game start:
#   $ skill_manager = SkillManager()
#   $ skill_manager.add_skill_points(5)  # Give player starting points
#
# Create skills with prerequisites:
#   $ fireball = Skill("fireball", "Fireball", "Cast a ball of fire",
#                      cost=1, category="magic")
#   $ inferno = Skill("inferno", "Inferno", "Massive fire explosion",
#                     cost=3, category="magic", prerequisites=["fireball"])
#
# Unlock skills:
#   $ skill_manager.unlock_skill("fireball")  # Returns True if successful
#
# Check if skill is available:
#   if skill_manager.is_unlocked("fireball"):
#       "You cast Fireball!"
#
# Refund skill points:
#   $ skill_manager.refund_skill("fireball")  # Returns points and re-locks
#
# Reset all skills:
#   $ skill_manager.reset_all()  # Refunds all points
#
# ============================================================================

init python:

    class Skill:
        """
        Represents a single skill in the skill tree.

        Attributes:
            skill_id: Unique identifier for the skill
            name: Display name
            description: Description text
            cost: Skill points required to unlock
            category: Category/branch of the skill tree
            prerequisites: List of skill_ids that must be unlocked first
            effects: Dict of stat bonuses or effects when unlocked
            unlocked: Whether the skill is currently unlocked
        """

        def __init__(self, skill_id, name, description, cost=1, category="general",
                     prerequisites=None, effects=None):
            """Initialize a new skill."""
            self.skill_id = skill_id
            self.name = name
            self.description = description
            self.cost = max(1, cost)  # Minimum cost of 1
            self.category = category
            self.prerequisites = prerequisites or []
            self.effects = effects or {}
            self.unlocked = False

        def can_unlock(self, unlocked_skills):
            """
            Check if this skill can be unlocked given a set of unlocked skill IDs.

            Args:
                unlocked_skills: Set or list of skill_ids that are already unlocked

            Returns:
                True if all prerequisites are met, False otherwise
            """
            if self.unlocked:
                return False  # Already unlocked

            for prereq in self.prerequisites:
                if prereq not in unlocked_skills:
                    return False
            return True

        def unlock(self):
            """Mark this skill as unlocked."""
            self.unlocked = True

        def lock(self):
            """Mark this skill as locked."""
            self.unlocked = False

        def get_missing_prerequisites(self, unlocked_skills):
            """
            Get list of prerequisites that are not yet unlocked.

            Args:
                unlocked_skills: Set or list of skill_ids that are already unlocked

            Returns:
                List of missing prerequisite skill_ids
            """
            missing = []
            for prereq in self.prerequisites:
                if prereq not in unlocked_skills:
                    missing.append(prereq)
            return missing

        def to_dict(self):
            """Convert skill to dictionary for serialization."""
            return {
                "skill_id": self.skill_id,
                "name": self.name,
                "description": self.description,
                "cost": self.cost,
                "category": self.category,
                "prerequisites": self.prerequisites.copy(),
                "effects": self.effects.copy(),
                "unlocked": self.unlocked
            }

        @classmethod
        def from_dict(cls, data):
            """Create a Skill instance from a dictionary."""
            skill = cls(
                skill_id=data["skill_id"],
                name=data["name"],
                description=data["description"],
                cost=data.get("cost", 1),
                category=data.get("category", "general"),
                prerequisites=data.get("prerequisites", []),
                effects=data.get("effects", {})
            )
            skill.unlocked = data.get("unlocked", False)
            return skill

        def __repr__(self):
            status = "unlocked" if self.unlocked else "locked"
            return f"Skill({self.skill_id!r}, {self.name!r}, {status})"


    class SkillTree:
        """
        Represents a branch/category of skills in a tree structure.

        Attributes:
            name: Display name of the skill tree branch
            category: Category identifier
            skills: Dictionary of skill_id -> Skill objects
            description: Description of this skill tree branch
        """

        def __init__(self, name, category, description=""):
            """Initialize a new skill tree branch."""
            self.name = name
            self.category = category
            self.description = description
            self.skills = {}

        def add_skill(self, skill):
            """
            Add a skill to this tree branch.

            Args:
                skill: Skill object to add

            Returns:
                True if added successfully, False if skill_id already exists
            """
            if skill.skill_id in self.skills:
                return False

            # Ensure skill has matching category
            skill.category = self.category
            self.skills[skill.skill_id] = skill
            return True

        def remove_skill(self, skill_id):
            """
            Remove a skill from this tree branch.

            Args:
                skill_id: ID of skill to remove

            Returns:
                The removed Skill object, or None if not found
            """
            return self.skills.pop(skill_id, None)

        def get_skill(self, skill_id):
            """
            Get a skill by ID.

            Args:
                skill_id: ID of skill to retrieve

            Returns:
                Skill object or None if not found
            """
            return self.skills.get(skill_id)

        def get_unlocked_skills(self):
            """
            Get all unlocked skills in this branch.

            Returns:
                List of unlocked Skill objects
            """
            return [s for s in self.skills.values() if s.unlocked]

        def get_available_skills(self, all_unlocked_ids):
            """
            Get skills that can be unlocked (prerequisites met, not yet unlocked).

            Args:
                all_unlocked_ids: Set of all unlocked skill_ids across all trees

            Returns:
                List of Skill objects that can be unlocked
            """
            available = []
            for skill in self.skills.values():
                if skill.can_unlock(all_unlocked_ids):
                    available.append(skill)
            return available

        def get_total_points_spent(self):
            """
            Calculate total skill points spent in this branch.

            Returns:
                Sum of costs of all unlocked skills
            """
            return sum(s.cost for s in self.skills.values() if s.unlocked)

        def get_skill_count(self):
            """Get total number of skills in this branch."""
            return len(self.skills)

        def get_unlocked_count(self):
            """Get number of unlocked skills in this branch."""
            return len(self.get_unlocked_skills())

        def to_dict(self):
            """Convert skill tree branch to dictionary for serialization."""
            return {
                "name": self.name,
                "category": self.category,
                "description": self.description,
                "skills": {sid: s.to_dict() for sid, s in self.skills.items()}
            }

        @classmethod
        def from_dict(cls, data):
            """Create a SkillTree instance from a dictionary."""
            tree = cls(
                name=data["name"],
                category=data["category"],
                description=data.get("description", "")
            )
            for skill_data in data.get("skills", {}).values():
                skill = Skill.from_dict(skill_data)
                tree.skills[skill.skill_id] = skill
            return tree

        def __repr__(self):
            return f"SkillTree({self.name!r}, {self.get_unlocked_count()}/{self.get_skill_count()} unlocked)"


    class SkillManager:
        """
        Central manager for all skill trees and skill points.

        Handles:
        - Skill point allocation and tracking
        - Unlocking and refunding skills
        - Managing multiple skill tree branches
        - Applying skill effects
        """

        def __init__(self):
            """Initialize the skill manager."""
            self.skill_points = 0
            self.total_points_earned = 0
            self.skill_trees = {}  # category -> SkillTree
            self._all_skills = {}  # skill_id -> Skill (flat lookup)

        # ====================================================================
        # SKILL TREE MANAGEMENT
        # ====================================================================

        def add_skill_tree(self, skill_tree):
            """
            Add a skill tree branch to the manager.

            Args:
                skill_tree: SkillTree object to add

            Returns:
                True if added, False if category already exists
            """
            if skill_tree.category in self.skill_trees:
                return False

            self.skill_trees[skill_tree.category] = skill_tree

            # Update flat skill lookup
            for skill_id, skill in skill_tree.skills.items():
                self._all_skills[skill_id] = skill

            return True

        def create_skill_tree(self, name, category, description=""):
            """
            Create and add a new skill tree branch.

            Args:
                name: Display name
                category: Category identifier
                description: Description text

            Returns:
                The created SkillTree, or None if category exists
            """
            if category in self.skill_trees:
                return None

            tree = SkillTree(name, category, description)
            self.skill_trees[category] = tree
            return tree

        def get_skill_tree(self, category):
            """Get a skill tree by category."""
            return self.skill_trees.get(category)

        def get_all_trees(self):
            """Get list of all skill trees."""
            return list(self.skill_trees.values())

        # ====================================================================
        # SKILL REGISTRATION
        # ====================================================================

        def register_skill(self, skill, category=None):
            """
            Register a skill with the manager.

            If category is provided, adds to that skill tree (creates if needed).
            Otherwise uses the skill's category.

            Args:
                skill: Skill object to register
                category: Optional category override

            Returns:
                True if registered successfully
            """
            cat = category or skill.category

            # Create tree if it doesn't exist
            if cat not in self.skill_trees:
                self.create_skill_tree(cat.title(), cat)

            tree = self.skill_trees[cat]
            if tree.add_skill(skill):
                self._all_skills[skill.skill_id] = skill
                return True
            return False

        def get_skill(self, skill_id):
            """Get a skill by ID from any tree."""
            return self._all_skills.get(skill_id)

        # ====================================================================
        # SKILL POINTS
        # ====================================================================

        def add_skill_points(self, amount):
            """
            Add skill points to the player's pool.

            Args:
                amount: Number of points to add (must be positive)

            Returns:
                New total skill points
            """
            if amount > 0:
                self.skill_points += amount
                self.total_points_earned += amount
            return self.skill_points

        def get_skill_points(self):
            """Get current available skill points."""
            return self.skill_points

        def get_total_points_spent(self):
            """Get total skill points spent across all trees."""
            return sum(tree.get_total_points_spent() for tree in self.skill_trees.values())

        # ====================================================================
        # UNLOCKING SKILLS
        # ====================================================================

        def get_unlocked_skill_ids(self):
            """Get set of all unlocked skill IDs."""
            return {sid for sid, skill in self._all_skills.items() if skill.unlocked}

        def is_unlocked(self, skill_id):
            """Check if a skill is unlocked."""
            skill = self.get_skill(skill_id)
            return skill.unlocked if skill else False

        def can_unlock(self, skill_id):
            """
            Check if a skill can be unlocked.

            Verifies:
            - Skill exists
            - Skill is not already unlocked
            - All prerequisites are met
            - Player has enough skill points

            Args:
                skill_id: ID of skill to check

            Returns:
                True if skill can be unlocked
            """
            skill = self.get_skill(skill_id)
            if not skill:
                return False

            if skill.unlocked:
                return False

            if self.skill_points < skill.cost:
                return False

            unlocked_ids = self.get_unlocked_skill_ids()
            return skill.can_unlock(unlocked_ids)

        def unlock_skill(self, skill_id):
            """
            Attempt to unlock a skill.

            Args:
                skill_id: ID of skill to unlock

            Returns:
                True if unlocked successfully, False otherwise
            """
            if not self.can_unlock(skill_id):
                return False

            skill = self.get_skill(skill_id)
            skill.unlock()
            self.skill_points -= skill.cost
            return True

        def get_available_skills(self, category=None):
            """
            Get all skills that can currently be unlocked.

            Args:
                category: Optional category filter

            Returns:
                List of Skill objects that can be unlocked
            """
            unlocked_ids = self.get_unlocked_skill_ids()
            available = []

            trees = [self.skill_trees[category]] if category else self.skill_trees.values()

            for tree in trees:
                if tree:
                    for skill in tree.get_available_skills(unlocked_ids):
                        if self.skill_points >= skill.cost:
                            available.append(skill)

            return available

        # ====================================================================
        # REFUNDING SKILLS
        # ====================================================================

        def can_refund(self, skill_id):
            """
            Check if a skill can be refunded.

            A skill can only be refunded if no other unlocked skills
            depend on it as a prerequisite.

            Args:
                skill_id: ID of skill to check

            Returns:
                True if skill can be refunded
            """
            skill = self.get_skill(skill_id)
            if not skill or not skill.unlocked:
                return False

            # Check if any unlocked skill has this as a prerequisite
            for other_skill in self._all_skills.values():
                if other_skill.unlocked and skill_id in other_skill.prerequisites:
                    return False

            return True

        def refund_skill(self, skill_id):
            """
            Refund a skill and return its points.

            Args:
                skill_id: ID of skill to refund

            Returns:
                Number of points refunded, or 0 if refund failed
            """
            if not self.can_refund(skill_id):
                return 0

            skill = self.get_skill(skill_id)
            skill.lock()
            self.skill_points += skill.cost
            return skill.cost

        def get_dependent_skills(self, skill_id):
            """
            Get skills that depend on this skill as a prerequisite.

            Args:
                skill_id: ID of skill to check

            Returns:
                List of Skill objects that have this skill as prerequisite
            """
            dependents = []
            for skill in self._all_skills.values():
                if skill_id in skill.prerequisites:
                    dependents.append(skill)
            return dependents

        # ====================================================================
        # RESET AND RESPEC
        # ====================================================================

        def reset_all(self):
            """
            Reset all skills and refund all points.

            Returns:
                Total points refunded
            """
            total_refunded = 0

            for skill in self._all_skills.values():
                if skill.unlocked:
                    total_refunded += skill.cost
                    skill.lock()

            self.skill_points += total_refunded
            return total_refunded

        def reset_tree(self, category):
            """
            Reset all skills in a specific tree and refund points.

            Args:
                category: Category of tree to reset

            Returns:
                Total points refunded from that tree
            """
            tree = self.get_skill_tree(category)
            if not tree:
                return 0

            total_refunded = 0
            for skill in tree.skills.values():
                if skill.unlocked:
                    total_refunded += skill.cost
                    skill.lock()

            self.skill_points += total_refunded
            return total_refunded

        # ====================================================================
        # SKILL EFFECTS
        # ====================================================================

        def get_total_effects(self):
            """
            Calculate combined effects from all unlocked skills.

            Returns:
                Dictionary of effect_name -> total_value
            """
            effects = {}

            for skill in self._all_skills.values():
                if skill.unlocked:
                    for effect_name, value in skill.effects.items():
                        effects[effect_name] = effects.get(effect_name, 0) + value

            return effects

        def get_effect(self, effect_name):
            """
            Get the total value of a specific effect.

            Args:
                effect_name: Name of the effect to look up

            Returns:
                Total value from all unlocked skills, or 0
            """
            return self.get_total_effects().get(effect_name, 0)

        def apply_effects_to_player(self, player):
            """
            Apply skill effects to a player's stats.

            Assumes effects are named like stat bonuses: "strength_bonus", etc.

            Args:
                player: Player object with add_stat method

            Returns:
                Dictionary of applied effects
            """
            effects = self.get_total_effects()

            for effect_name, value in effects.items():
                if effect_name.endswith("_bonus"):
                    stat_name = effect_name[:-6]  # Remove "_bonus"
                    if hasattr(player, 'add_stat'):
                        player.add_stat(stat_name, value)

            return effects

        # ====================================================================
        # SAVE/LOAD
        # ====================================================================

        def to_dict(self):
            """Convert manager state to dictionary for saving."""
            return {
                "skill_points": self.skill_points,
                "total_points_earned": self.total_points_earned,
                "skill_trees": {cat: tree.to_dict() for cat, tree in self.skill_trees.items()}
            }

        @classmethod
        def from_dict(cls, data):
            """Create a SkillManager from saved data."""
            manager = cls()
            manager.skill_points = data.get("skill_points", 0)
            manager.total_points_earned = data.get("total_points_earned", 0)

            for tree_data in data.get("skill_trees", {}).values():
                tree = SkillTree.from_dict(tree_data)
                manager.skill_trees[tree.category] = tree
                for skill_id, skill in tree.skills.items():
                    manager._all_skills[skill_id] = skill

            return manager

        # ====================================================================
        # UTILITY METHODS
        # ====================================================================

        def get_statistics(self):
            """
            Get overall statistics about skill progression.

            Returns:
                Dictionary with various statistics
            """
            total_skills = len(self._all_skills)
            unlocked_skills = len(self.get_unlocked_skill_ids())

            return {
                "total_skills": total_skills,
                "unlocked_skills": unlocked_skills,
                "locked_skills": total_skills - unlocked_skills,
                "completion_percent": (unlocked_skills / total_skills * 100) if total_skills > 0 else 0,
                "skill_points": self.skill_points,
                "total_points_earned": self.total_points_earned,
                "total_points_spent": self.get_total_points_spent(),
                "tree_count": len(self.skill_trees)
            }

        def __repr__(self):
            unlocked = len(self.get_unlocked_skill_ids())
            total = len(self._all_skills)
            return f"SkillManager({unlocked}/{total} skills, {self.skill_points} points)"


    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================

    def create_default_skill_trees():
        """
        Create a default set of skill trees for a typical RPG.

        Returns:
            SkillManager with pre-configured skill trees
        """
        manager = SkillManager()

        # Combat tree
        manager.create_skill_tree("Combat", "combat", "Physical combat abilities")
        manager.register_skill(Skill("power_strike", "Power Strike", "Deal extra damage",
                               cost=1, category="combat", effects={"strength_bonus": 2}))
        manager.register_skill(Skill("shield_bash", "Shield Bash", "Stun enemies briefly",
                               cost=1, category="combat"))
        manager.register_skill(Skill("berserker", "Berserker", "Increased damage at low HP",
                               cost=2, category="combat", prerequisites=["power_strike"],
                               effects={"strength_bonus": 5}))
        manager.register_skill(Skill("whirlwind", "Whirlwind", "Attack all nearby enemies",
                               cost=3, category="combat", prerequisites=["berserker", "shield_bash"]))

        # Magic tree
        manager.create_skill_tree("Magic", "magic", "Arcane abilities")
        manager.register_skill(Skill("fireball", "Fireball", "Cast a ball of fire",
                              cost=1, category="magic", effects={"intelligence_bonus": 2}))
        manager.register_skill(Skill("ice_shard", "Ice Shard", "Throw sharp ice",
                              cost=1, category="magic"))
        manager.register_skill(Skill("inferno", "Inferno", "Massive fire explosion",
                              cost=3, category="magic", prerequisites=["fireball"],
                              effects={"intelligence_bonus": 5}))
        manager.register_skill(Skill("blizzard", "Blizzard", "Freeze all enemies",
                              cost=3, category="magic", prerequisites=["ice_shard"]))
        manager.register_skill(Skill("elemental_mastery", "Elemental Mastery", "Master of elements",
                              cost=5, category="magic", prerequisites=["inferno", "blizzard"],
                              effects={"intelligence_bonus": 10}))

        # Stealth tree
        manager.create_skill_tree("Stealth", "stealth", "Sneaky abilities")
        manager.register_skill(Skill("sneak", "Sneak", "Move quietly",
                                cost=1, category="stealth", effects={"agility_bonus": 2}))
        manager.register_skill(Skill("pickpocket", "Pickpocket", "Steal from NPCs",
                                cost=2, category="stealth", prerequisites=["sneak"]))
        manager.register_skill(Skill("backstab", "Backstab", "Critical hit from behind",
                                cost=2, category="stealth", prerequisites=["sneak"],
                                effects={"agility_bonus": 3}))
        manager.register_skill(Skill("shadow_step", "Shadow Step", "Teleport behind enemies",
                                cost=4, category="stealth", prerequisites=["backstab"],
                                effects={"agility_bonus": 5}))

        return manager


# ============================================================================
# DEFAULT SKILL MANAGER
# ============================================================================

default skill_manager = None


# ============================================================================
# SKILL TREE SCREEN
# ============================================================================

screen skill_tree_screen():
    tag menu
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 40
        ypadding 30
        xminimum 700

        vbox:
            spacing 15

            # Title and Points
            hbox:
                spacing 20
                text "Skill Trees" size 36 color "#ffffff"
                text "Points: [skill_manager.skill_points]" size 24 color "#ffdd44" yalign 1.0

            null height 10

            if skill_manager:
                # Tree tabs
                hbox:
                    spacing 10
                    for tree in skill_manager.get_all_trees():
                        textbutton tree.name action SetScreenVariable("selected_tree", tree.category)

                null height 15

                # Skills in selected tree
                $ selected = getattr(renpy.store, "selected_tree", None) or (skill_manager.get_all_trees()[0].category if skill_manager.get_all_trees() else None)
                $ current_tree = skill_manager.get_skill_tree(selected) if selected else None

                if current_tree:
                    text current_tree.description size 16 color "#aaaaaa"

                    null height 10

                    viewport:
                        scrollbars "vertical"
                        ymaximum 400

                        vbox:
                            spacing 8
                            for skill in current_tree.skills.values():
                                $ can_unlock = skill_manager.can_unlock(skill.skill_id)
                                $ is_unlocked = skill.unlocked

                                frame:
                                    xfill True
                                    background "#333333" if is_unlocked else ("#444444" if can_unlock else "#222222")
                                    padding (15, 10)

                                    hbox:
                                        spacing 15

                                        vbox:
                                            xmaximum 400
                                            text skill.name size 20 color ("#44ff44" if is_unlocked else ("#ffffff" if can_unlock else "#666666"))
                                            text skill.description size 14 color "#888888"
                                            if skill.prerequisites:
                                                text "Requires: [', '.join(skill.prerequisites)]" size 12 color "#ff8844"

                                        null width 20

                                        vbox:
                                            yalign 0.5
                                            text "Cost: [skill.cost]" size 16 color "#ffdd44"

                                            if not is_unlocked and can_unlock:
                                                textbutton "Unlock" action Function(skill_manager.unlock_skill, skill.skill_id) text_size 14
                                            elif is_unlocked and skill_manager.can_refund(skill.skill_id):
                                                textbutton "Refund" action Function(skill_manager.refund_skill, skill.skill_id) text_size 14

            else:
                text "No skill manager initialized." size 20 color "#ff4444" xalign 0.5

            null height 20

            # Bottom buttons
            hbox:
                spacing 20
                xalign 0.5

                textbutton "Reset All" action Function(skill_manager.reset_all) text_size 18 sensitive (skill_manager and skill_manager.get_total_points_spent() > 0)
                textbutton "Close" action Return() text_size 22

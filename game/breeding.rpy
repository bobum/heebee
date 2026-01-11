# breeding.rpy - Fantasy Creature Breeding System
# A comprehensive system for collecting, raising, and breeding fantasy creatures

init python:
    import random

    # =========================================================================
    # CREATURE RARITY - Enum-style class for rarity levels
    # =========================================================================

    class CreatureRarity:
        """Enumeration of creature rarity levels."""
        COMMON = "common"
        UNCOMMON = "uncommon"
        RARE = "rare"
        EPIC = "epic"
        LEGENDARY = "legendary"
        MYTHIC = "mythic"

        @staticmethod
        def get_all():
            """Return all rarity levels in order."""
            return [
                CreatureRarity.COMMON,
                CreatureRarity.UNCOMMON,
                CreatureRarity.RARE,
                CreatureRarity.EPIC,
                CreatureRarity.LEGENDARY,
                CreatureRarity.MYTHIC
            ]

        @staticmethod
        def get_display_name(rarity):
            """Get display name for a rarity."""
            names = {
                "common": "Common",
                "uncommon": "Uncommon",
                "rare": "Rare",
                "epic": "Epic",
                "legendary": "Legendary",
                "mythic": "Mythic"
            }
            return names.get(rarity, rarity.title())

        @staticmethod
        def get_color(rarity):
            """Get display color for a rarity."""
            colors = {
                "common": "#aaaaaa",
                "uncommon": "#44ff44",
                "rare": "#4488ff",
                "epic": "#aa44ff",
                "legendary": "#ffaa00",
                "mythic": "#ff44aa"
            }
            return colors.get(rarity, "#ffffff")

        @staticmethod
        def get_value_multiplier(rarity):
            """Get value multiplier for economy integration."""
            multipliers = {
                "common": 1.0,
                "uncommon": 2.0,
                "rare": 5.0,
                "epic": 15.0,
                "legendary": 50.0,
                "mythic": 200.0
            }
            return multipliers.get(rarity, 1.0)

    # =========================================================================
    # CREATURE TRAIT - Heritable traits for creatures
    # =========================================================================

    class CreatureTrait:
        """
        Represents a heritable trait for creatures.

        Attributes:
            id: Unique identifier
            name: Display name
            description: What the trait does
            stat_modifiers: Dict of stat_name to modifier value
            inheritance_weight: How likely to be passed to offspring (0-100)
            dominant: If True, always shows when present
            visual_effect: Optional visual modification (e.g., "color:blue")
            rarity_modifier: Modifies creature rarity calculation
        """

        def __init__(self, id, name, description="",
                     stat_modifiers=None, inheritance_weight=50,
                     dominant=False, visual_effect=None,
                     rarity_modifier=0):
            self.id = id
            self.name = name
            self.description = description
            self.stat_modifiers = stat_modifiers or {}
            self.inheritance_weight = inheritance_weight
            self.dominant = dominant
            self.visual_effect = visual_effect
            self.rarity_modifier = rarity_modifier

        def apply_modifiers(self, stats):
            """Apply this trait's modifiers to a stats dictionary."""
            result = dict(stats)
            for stat, modifier in self.stat_modifiers.items():
                if stat in result:
                    result[stat] = max(0, result[stat] + modifier)
            return result

        def __repr__(self):
            return f"CreatureTrait({self.id}, {self.name})"

    # =========================================================================
    # CREATURE SPECIES - Template for creature types
    # =========================================================================

    class CreatureSpecies:
        """
        Template definition for a creature species.

        Attributes:
            id: Unique identifier (e.g., "fire_dragon", "water_slime")
            name: Display name of the species
            description: Lore/description text
            base_stats: Dict of starting stat values
            growth_rates: Dict of stat growth per age
            possible_traits: List of traits this species can have
            trait_weights: Dict of trait_id to probability weight
            compatible_species: List of species IDs that can breed with this one
            gestation_periods: Number of time periods for egg incubation
            maturity_age: Age when creature can breed (in days)
            lifespan: Maximum age in days (0 for immortal)
            rarity_weights: Dict of rarity to spawn weight
            icon: Path to species icon
            egg_image: Path to egg sprite
        """

        def __init__(self, id, name, description="",
                     base_stats=None, growth_rates=None,
                     possible_traits=None, trait_weights=None,
                     compatible_species=None, gestation_periods=4,
                     maturity_age=7, lifespan=0, rarity_weights=None,
                     icon=None, egg_image=None):
            self.id = id
            self.name = name
            self.description = description
            self.base_stats = base_stats or {
                "max_health": 100,
                "hunger": 100,
                "happiness": 50,
                "energy": 100
            }
            self.growth_rates = growth_rates or {
                "max_health": 5,
                "hunger": 0,
                "happiness": 0,
                "energy": 2
            }
            self.possible_traits = possible_traits or []
            self.trait_weights = trait_weights or {}
            self.compatible_species = compatible_species or [id]
            self.gestation_periods = gestation_periods
            self.maturity_age = maturity_age
            self.lifespan = lifespan
            self.rarity_weights = rarity_weights or {
                "common": 60,
                "uncommon": 25,
                "rare": 10,
                "epic": 4,
                "legendary": 1,
                "mythic": 0
            }
            self.icon = icon
            self.egg_image = egg_image

        def can_breed_with(self, other_species_id):
            """Check if this species can breed with another."""
            return other_species_id in self.compatible_species

        def get_random_rarity(self):
            """Get a random rarity based on weights."""
            choices = []
            for rarity, weight in self.rarity_weights.items():
                choices.extend([rarity] * weight)
            if not choices:
                return CreatureRarity.COMMON
            return random.choice(choices)

        def __repr__(self):
            return f"CreatureSpecies({self.id}, {self.name})"

    # =========================================================================
    # CREATURE - Individual creature instance
    # =========================================================================

    class Creature:
        """
        Represents an individual creature instance.

        Stats are bounded similar to the Player class pattern.
        Bond system follows the Relationship class pattern.
        """

        MIN_STAT = 0
        MAX_STAT = 100
        MAX_BOND = 100

        def __init__(self, id, name, species_id, generation=0,
                     rarity=None, traits=None, parent1_id=None,
                     parent2_id=None, birth_day=0, appearance=None):
            self.id = id
            self.name = name
            self.species_id = species_id
            self.generation = generation
            self.rarity = rarity or CreatureRarity.COMMON
            self.traits = traits or []
            self.parent1_id = parent1_id
            self.parent2_id = parent2_id
            self.birth_day = birth_day
            self.appearance = appearance or {}

            # Stats
            self.max_health = 100
            self.health = 100
            self.hunger = 100
            self.happiness = 50
            self.energy = 100

            # Bond system (like Relationship)
            self.bond_level = 0
            self.bond_history = []

            # Age
            self.age_days = 0
            self.is_mature = False

            # Egg state
            self.is_egg = False
            self.hatch_time_remaining = 0

        def _clamp(self, value, min_val, max_val):
            """Clamp value between bounds."""
            return max(min_val, min(value, max_val))

        def get_stat(self, stat_name):
            """Get a stat value."""
            stat_name = stat_name.lower()
            if hasattr(self, stat_name):
                return getattr(self, stat_name)
            return None

        def set_stat(self, stat_name, value):
            """Set a stat with bounds checking."""
            stat_name = stat_name.lower()
            if not hasattr(self, stat_name):
                return False

            if stat_name == "health":
                value = self._clamp(value, 0, self.max_health)
            elif stat_name == "max_health":
                value = self._clamp(value, 1, 999)
            elif stat_name in ["hunger", "happiness", "energy", "bond_level"]:
                value = self._clamp(value, self.MIN_STAT, self.MAX_STAT)

            setattr(self, stat_name, value)
            return True

        def add_stat(self, stat_name, amount):
            """Add to a stat value."""
            current = self.get_stat(stat_name)
            if current is not None:
                return self.set_stat(stat_name, current + amount)
            return False

        def modify_bond(self, amount, reason=""):
            """Modify bond level with history tracking."""
            old_val = self.bond_level
            self.bond_level = self._clamp(self.bond_level + amount, 0, self.MAX_BOND)
            if reason:
                self.bond_history.append((reason, amount))
            return self.bond_level - old_val

        def get_bond_status(self):
            """Get descriptive bond status."""
            if self.bond_level >= 90:
                return "Soulbound"
            elif self.bond_level >= 75:
                return "Devoted"
            elif self.bond_level >= 60:
                return "Loyal"
            elif self.bond_level >= 45:
                return "Friendly"
            elif self.bond_level >= 30:
                return "Familiar"
            elif self.bond_level >= 15:
                return "Wary"
            else:
                return "Stranger"

        def get_health_status(self):
            """Get descriptive health status."""
            pct = (self.health / self.max_health) * 100 if self.max_health > 0 else 0
            if pct >= 80:
                return "Healthy"
            elif pct >= 50:
                return "Fair"
            elif pct >= 20:
                return "Weak"
            else:
                return "Critical"

        def get_mood(self):
            """Get descriptive mood based on happiness."""
            if self.happiness >= 80:
                return "Joyful"
            elif self.happiness >= 60:
                return "Content"
            elif self.happiness >= 40:
                return "Neutral"
            elif self.happiness >= 20:
                return "Sad"
            else:
                return "Miserable"

        def age_one_day(self, species_registry):
            """Age the creature by one day."""
            self.age_days += 1
            species = species_registry.get(self.species_id)
            if species and not self.is_mature:
                if self.age_days >= species.maturity_age:
                    self.is_mature = True
            # Daily stat decay
            self.add_stat("hunger", -10)
            self.add_stat("happiness", -5)
            self.add_stat("energy", 20)

        def can_breed(self, species_registry):
            """Check if creature can breed."""
            return (
                self.is_mature and
                not self.is_egg and
                self.health > 30 and
                self.hunger > 20 and
                self.happiness > 20 and
                self.energy > 40
            )

        def feed(self, nutrition_value=30):
            """Feed the creature."""
            self.add_stat("hunger", nutrition_value)
            self.modify_bond(2, "Fed")
            return True

        def play(self):
            """Play with the creature."""
            if self.energy < 10:
                return False
            self.add_stat("happiness", 15)
            self.add_stat("energy", -10)
            self.modify_bond(5, "Played together")
            return True

        def rest(self):
            """Let creature rest."""
            self.add_stat("energy", 30)
            self.add_stat("happiness", 5)
            return True

        def pet(self):
            """Pet the creature for bonding."""
            self.add_stat("happiness", 5)
            self.modify_bond(3, "Petted")
            return True

        def to_dict(self):
            """Convert creature to dictionary for saving."""
            return {
                "id": self.id,
                "name": self.name,
                "species_id": self.species_id,
                "generation": self.generation,
                "rarity": self.rarity,
                "traits": list(self.traits),
                "parent1_id": self.parent1_id,
                "parent2_id": self.parent2_id,
                "birth_day": self.birth_day,
                "appearance": dict(self.appearance),
                "max_health": self.max_health,
                "health": self.health,
                "hunger": self.hunger,
                "happiness": self.happiness,
                "energy": self.energy,
                "bond_level": self.bond_level,
                "bond_history": list(self.bond_history),
                "age_days": self.age_days,
                "is_mature": self.is_mature,
                "is_egg": self.is_egg,
                "hatch_time_remaining": self.hatch_time_remaining
            }

        @classmethod
        def from_dict(cls, data):
            """Create creature from dictionary."""
            creature = cls(
                id=data["id"],
                name=data["name"],
                species_id=data["species_id"],
                generation=data.get("generation", 0),
                rarity=data.get("rarity", CreatureRarity.COMMON),
                traits=data.get("traits", []),
                parent1_id=data.get("parent1_id"),
                parent2_id=data.get("parent2_id"),
                birth_day=data.get("birth_day", 0),
                appearance=data.get("appearance", {})
            )
            creature.max_health = data.get("max_health", 100)
            creature.health = data.get("health", 100)
            creature.hunger = data.get("hunger", 100)
            creature.happiness = data.get("happiness", 50)
            creature.energy = data.get("energy", 100)
            creature.bond_level = data.get("bond_level", 0)
            creature.bond_history = data.get("bond_history", [])
            creature.age_days = data.get("age_days", 0)
            creature.is_mature = data.get("is_mature", False)
            creature.is_egg = data.get("is_egg", False)
            creature.hatch_time_remaining = data.get("hatch_time_remaining", 0)
            return creature

        def __repr__(self):
            return f"Creature({self.id}, {self.name}, {self.species_id})"

    # =========================================================================
    # BREEDING PAIR - Tracks active breeding attempts
    # =========================================================================

    class BreedingPair:
        """
        Represents an active breeding pair.

        Attributes:
            id: Unique identifier for this breeding attempt
            creature1_id: First parent creature ID
            creature2_id: Second parent creature ID
            started_day: Game day when breeding started
            started_period: Time period when started
            gestation_remaining: Periods until egg is ready
            egg_id: ID of resulting egg creature (once created)
            completed: Whether breeding has produced an egg
        """

        def __init__(self, id, creature1_id, creature2_id,
                     started_day=0, started_period=0, gestation_periods=4):
            self.id = id
            self.creature1_id = creature1_id
            self.creature2_id = creature2_id
            self.started_day = started_day
            self.started_period = started_period
            self.gestation_remaining = gestation_periods
            self.egg_id = None
            self.completed = False

        def advance_time(self, periods=1):
            """Advance breeding timer. Returns True if ready."""
            if self.completed:
                return False
            self.gestation_remaining = max(0, self.gestation_remaining - periods)
            return self.gestation_remaining <= 0

        def to_dict(self):
            return {
                "id": self.id,
                "creature1_id": self.creature1_id,
                "creature2_id": self.creature2_id,
                "started_day": self.started_day,
                "started_period": self.started_period,
                "gestation_remaining": self.gestation_remaining,
                "egg_id": self.egg_id,
                "completed": self.completed
            }

        @classmethod
        def from_dict(cls, data):
            pair = cls(
                id=data["id"],
                creature1_id=data["creature1_id"],
                creature2_id=data["creature2_id"],
                started_day=data.get("started_day", 0),
                started_period=data.get("started_period", 0),
                gestation_periods=data.get("gestation_remaining", 4)
            )
            pair.egg_id = data.get("egg_id")
            pair.completed = data.get("completed", False)
            return pair

    # =========================================================================
    # BREEDING MANAGER - Central manager for the breeding system
    # =========================================================================

    class BreedingManager:
        """
        Central manager for the creature breeding system.

        Handles creature registration, breeding operations, time integration,
        and save/load functionality.
        """

        def __init__(self):
            self.species = {}
            self.traits = {}
            self.creatures = {}
            self.breeding_pairs = {}

            self._next_creature_id = 1
            self._next_pair_id = 1

            self.notification_queue = []

        # === Species & Trait Registration ===

        def register_species(self, species):
            """Register a creature species."""
            self.species[species.id] = species
            return species

        def register_trait(self, trait):
            """Register a creature trait."""
            self.traits[trait.id] = trait
            return trait

        def get_species(self, species_id):
            """Get a species by ID."""
            return self.species.get(species_id)

        def get_trait(self, trait_id):
            """Get a trait by ID."""
            return self.traits.get(trait_id)

        def get_all_species(self):
            """Get all registered species."""
            return list(self.species.values())

        # === Creature Management ===

        def _generate_creature_id(self):
            """Generate unique creature ID."""
            id = f"creature_{self._next_creature_id}"
            self._next_creature_id += 1
            return id

        def add_creature(self, creature):
            """Add a creature to the registry."""
            self.creatures[creature.id] = creature
            return creature

        def remove_creature(self, creature_id):
            """Remove a creature from the registry."""
            if creature_id in self.creatures:
                del self.creatures[creature_id]
                return True
            return False

        def get_creature(self, creature_id):
            """Get a creature by ID."""
            return self.creatures.get(creature_id)

        def get_all_creatures(self):
            """Get all creatures."""
            return list(self.creatures.values())

        def get_creatures_by_species(self, species_id):
            """Get all creatures of a species."""
            return [c for c in self.creatures.values() if c.species_id == species_id]

        def get_creatures_by_rarity(self, rarity):
            """Get all creatures of a rarity."""
            return [c for c in self.creatures.values() if c.rarity == rarity]

        def get_mature_creatures(self):
            """Get all creatures that can breed."""
            return [c for c in self.creatures.values()
                    if c.can_breed(self.species)]

        def get_eggs(self):
            """Get all creatures that are eggs."""
            return [c for c in self.creatures.values() if c.is_egg]

        def get_hatched_creatures(self):
            """Get all non-egg creatures."""
            return [c for c in self.creatures.values() if not c.is_egg]

        # === Creature Creation ===

        def create_creature(self, species_id, name=None, rarity=None,
                            traits=None, generation=0, current_day=0,
                            is_mature=False):
            """
            Create a new creature.

            Args:
                species_id: Species ID
                name: Custom name (auto-generated if None)
                rarity: Rarity level (random from species if None)
                traits: List of trait IDs (random from species if None)
                generation: Breeding generation
                current_day: Current game day for birth_day
                is_mature: Whether creature starts mature

            Returns:
                Creature: The created creature
            """
            species = self.get_species(species_id)
            if not species:
                return None

            creature_id = self._generate_creature_id()

            if not name:
                name = f"{species.name} #{self._next_creature_id - 1}"

            if not rarity:
                rarity = species.get_random_rarity()

            if traits is None:
                traits = self._select_random_traits(species)

            appearance = self._generate_appearance(species, traits)

            creature = Creature(
                id=creature_id,
                name=name,
                species_id=species_id,
                generation=generation,
                rarity=rarity,
                traits=traits,
                birth_day=current_day,
                appearance=appearance
            )

            # Apply species base stats
            creature.max_health = species.base_stats.get("max_health", 100)
            creature.health = creature.max_health
            creature.hunger = species.base_stats.get("hunger", 100)
            creature.happiness = species.base_stats.get("happiness", 50)
            creature.energy = species.base_stats.get("energy", 100)

            # Apply trait modifiers
            for trait_id in traits:
                trait = self.get_trait(trait_id)
                if trait:
                    for stat, mod in trait.stat_modifiers.items():
                        creature.add_stat(stat, mod)

            # Set maturity
            if is_mature:
                creature.is_mature = True
                creature.age_days = species.maturity_age

            self.add_creature(creature)
            return creature

        def _select_random_traits(self, species, count=2):
            """Select random traits for a species."""
            if not species.possible_traits:
                return []

            available = list(species.possible_traits)
            selected = []

            while len(selected) < count and available:
                if species.trait_weights:
                    weighted = []
                    for t in available:
                        weight = species.trait_weights.get(t, 10)
                        weighted.extend([t] * weight)
                    if weighted:
                        trait = random.choice(weighted)
                    else:
                        trait = random.choice(available)
                else:
                    trait = random.choice(available)

                selected.append(trait)
                available.remove(trait)

            return selected

        def _generate_appearance(self, species, traits):
            """Generate appearance data based on species and traits."""
            appearance = {
                "primary_color": "default",
                "secondary_color": "default",
                "pattern": "none",
                "size": "medium"
            }
            for trait_id in traits:
                trait = self.get_trait(trait_id)
                if trait and trait.visual_effect:
                    parts = trait.visual_effect.split(":")
                    if len(parts) == 2:
                        appearance[parts[0]] = parts[1]
            return appearance

        # === Breeding Mechanics ===

        def can_breed(self, creature1_id, creature2_id):
            """
            Check if two creatures can breed.

            Returns:
                tuple: (can_breed: bool, reason: str)
            """
            c1 = self.get_creature(creature1_id)
            c2 = self.get_creature(creature2_id)

            if not c1 or not c2:
                return False, "Creature not found"

            if c1.id == c2.id:
                return False, "Cannot breed with self"

            if c1.is_egg or c2.is_egg:
                return False, "Eggs cannot breed"

            if not c1.is_mature or not c2.is_mature:
                return False, "Creatures must be mature"

            s1 = self.get_species(c1.species_id)
            s2 = self.get_species(c2.species_id)

            if not s1 or not s2:
                return False, "Unknown species"

            if not s1.can_breed_with(s2.id) and not s2.can_breed_with(s1.id):
                return False, "Species are not compatible"

            if not c1.can_breed(self.species):
                return False, f"{c1.name} is not ready"

            if not c2.can_breed(self.species):
                return False, f"{c2.name} is not ready"

            for pair in self.breeding_pairs.values():
                if not pair.completed:
                    if creature1_id in [pair.creature1_id, pair.creature2_id]:
                        return False, f"{c1.name} is already breeding"
                    if creature2_id in [pair.creature1_id, pair.creature2_id]:
                        return False, f"{c2.name} is already breeding"

            return True, "Ready to breed"

        def start_breeding(self, creature1_id, creature2_id, current_day=0, current_period=0):
            """
            Start a breeding pair.

            Returns:
                tuple: (success: bool, message: str, pair_id: str or None)
            """
            can_breed, reason = self.can_breed(creature1_id, creature2_id)
            if not can_breed:
                return False, reason, None

            c1 = self.get_creature(creature1_id)
            c2 = self.get_creature(creature2_id)
            s1 = self.get_species(c1.species_id)
            s2 = self.get_species(c2.species_id)

            gestation = (s1.gestation_periods + s2.gestation_periods) // 2

            pair_id = f"pair_{self._next_pair_id}"
            self._next_pair_id += 1

            pair = BreedingPair(
                id=pair_id,
                creature1_id=creature1_id,
                creature2_id=creature2_id,
                started_day=current_day,
                started_period=current_period,
                gestation_periods=gestation
            )

            self.breeding_pairs[pair_id] = pair

            c1.add_stat("energy", -30)
            c2.add_stat("energy", -30)

            return True, f"Breeding started! Egg ready in {gestation} periods.", pair_id

        def advance_breeding_time(self, periods=1):
            """Advance time for all breeding pairs."""
            completed = []
            for pair_id, pair in self.breeding_pairs.items():
                if not pair.completed and pair.advance_time(periods):
                    completed.append(pair_id)
            return completed

        def complete_breeding(self, pair_id, current_day=0):
            """
            Complete a breeding and create the egg.

            Returns:
                tuple: (success: bool, message: str, egg: Creature or None)
            """
            pair = self.breeding_pairs.get(pair_id)
            if not pair:
                return False, "Breeding pair not found", None

            if pair.completed:
                return False, "Breeding already completed", None

            if pair.gestation_remaining > 0:
                return False, f"Not ready ({pair.gestation_remaining} periods left)", None

            c1 = self.get_creature(pair.creature1_id)
            c2 = self.get_creature(pair.creature2_id)

            if not c1 or not c2:
                return False, "Parent creature not found", None

            egg = self._create_offspring(c1, c2, current_day)

            pair.egg_id = egg.id
            pair.completed = True

            self.notification_queue.append({
                "type": "egg_created",
                "creature": egg,
                "parents": [c1.name, c2.name]
            })

            return True, f"A new egg has appeared!", egg

        def _create_offspring(self, parent1, parent2, current_day):
            """Create offspring from two parents."""
            s1 = self.get_species(parent1.species_id)
            s2 = self.get_species(parent2.species_id)

            offspring_species_id = random.choice([parent1.species_id, parent2.species_id])
            offspring_species = self.get_species(offspring_species_id)

            traits = self._inherit_traits(parent1, parent2, offspring_species)
            rarity = self._calculate_offspring_rarity(parent1, parent2, offspring_species, traits)
            generation = max(parent1.generation, parent2.generation) + 1

            creature_id = self._generate_creature_id()
            egg = Creature(
                id=creature_id,
                name=f"Egg #{self._next_creature_id - 1}",
                species_id=offspring_species_id,
                generation=generation,
                rarity=rarity,
                traits=traits,
                parent1_id=parent1.id,
                parent2_id=parent2.id,
                birth_day=current_day
            )

            egg.max_health = self._average_stat(
                parent1.max_health, parent2.max_health,
                offspring_species.base_stats.get("max_health", 100)
            )
            egg.health = egg.max_health

            egg.is_egg = True
            egg.hatch_time_remaining = offspring_species.gestation_periods

            egg.appearance = self._mix_appearance(
                parent1.appearance, parent2.appearance, traits
            )

            self.add_creature(egg)
            return egg

        def _inherit_traits(self, parent1, parent2, offspring_species):
            """Inherit traits from parents."""
            inherited = []
            all_parent_traits = parent1.traits + parent2.traits

            for trait_id in set(all_parent_traits):
                trait = self.get_trait(trait_id)
                if trait and trait_id in offspring_species.possible_traits:
                    if trait.dominant:
                        inherited.append(trait_id)
                    elif random.randint(1, 100) <= trait.inheritance_weight:
                        inherited.append(trait_id)

            # 10% mutation chance
            if random.randint(1, 100) <= 10:
                possible_new = [t for t in offspring_species.possible_traits
                               if t not in inherited]
                if possible_new:
                    inherited.append(random.choice(possible_new))

            return inherited[:4]

        def _calculate_offspring_rarity(self, parent1, parent2, species, traits):
            """Calculate offspring rarity."""
            base_rarity = species.get_random_rarity()
            rarity_order = CreatureRarity.get_all()
            base_index = rarity_order.index(base_rarity)

            p1_index = rarity_order.index(parent1.rarity)
            p2_index = rarity_order.index(parent2.rarity)
            parent_avg = (p1_index + p2_index) / 2

            trait_bonus = sum(
                self.get_trait(t).rarity_modifier
                for t in traits if self.get_trait(t)
            )

            final_index = base_index
            if parent_avg > base_index:
                if random.randint(1, 100) <= 30:
                    final_index = min(int(parent_avg), base_index + 1)

            final_index = min(len(rarity_order) - 1, final_index + trait_bonus)
            final_index = max(0, final_index)

            return rarity_order[final_index]

        def _average_stat(self, stat1, stat2, base_stat, variation=0.1):
            """Average two stats with variation."""
            avg = (stat1 + stat2 + base_stat) / 3
            min_val = avg * (1 - variation)
            max_val = avg * (1 + variation)
            return int(random.uniform(min_val, max_val))

        def _mix_appearance(self, app1, app2, traits):
            """Mix appearance from two parents."""
            result = {}
            for key in set(list(app1.keys()) + list(app2.keys())):
                if key in app1 and key in app2:
                    result[key] = random.choice([app1[key], app2[key]])
                elif key in app1:
                    result[key] = app1[key]
                else:
                    result[key] = app2[key]
            return result

        # === Egg Hatching ===

        def hatch_egg(self, creature_id):
            """
            Hatch an egg creature.

            Returns:
                tuple: (success: bool, message: str)
            """
            creature = self.get_creature(creature_id)
            if not creature:
                return False, "Creature not found"

            if not creature.is_egg:
                return False, "This is not an egg"

            if creature.hatch_time_remaining > 0:
                return False, f"Not ready ({creature.hatch_time_remaining} periods left)"

            creature.is_egg = False
            creature.age_days = 0

            if creature.name.startswith("Egg #"):
                species = self.get_species(creature.species_id)
                if species:
                    creature.name = f"Baby {species.name}"

            self.notification_queue.append({
                "type": "hatched",
                "creature": creature
            })

            return True, f"{creature.name} has hatched!"

        def advance_egg_time(self, periods=1):
            """Advance time for all eggs."""
            ready = []
            for creature in self.creatures.values():
                if creature.is_egg:
                    creature.hatch_time_remaining = max(
                        0, creature.hatch_time_remaining - periods
                    )
                    if creature.hatch_time_remaining <= 0:
                        ready.append(creature.id)
            return ready

        # === Time Integration ===

        def daily_update(self, current_day):
            """Called once per game day for creature aging and stat decay."""
            for creature in self.creatures.values():
                if not creature.is_egg:
                    creature.age_one_day(self.species)

        def on_time_advance(self, periods=1, current_day=0):
            """
            Called when time advances.

            Returns:
                dict: Events that occurred
            """
            events = {
                "eggs_ready": [],
                "breeding_complete": []
            }

            completed_pairs = self.advance_breeding_time(periods)
            for pair_id in completed_pairs:
                success, msg, egg = self.complete_breeding(pair_id, current_day)
                if success:
                    events["breeding_complete"].append(pair_id)

            events["eggs_ready"] = self.advance_egg_time(periods)

            return events

        # === Economy Integration ===

        def get_creature_value(self, creature_id):
            """Calculate the value of a creature for selling."""
            creature = self.get_creature(creature_id)
            if not creature:
                return 0

            base_value = 100
            rarity_mult = CreatureRarity.get_value_multiplier(creature.rarity)
            trait_bonus = len(creature.traits) * 25
            bond_bonus = creature.bond_level * 2
            gen_bonus = creature.generation * 50

            return int((base_value + trait_bonus + bond_bonus + gen_bonus) * rarity_mult)

        def sell_creature(self, creature_id, wallet):
            """
            Sell a creature.

            Returns:
                tuple: (success: bool, message: str, amount: int)
            """
            creature = self.get_creature(creature_id)
            if not creature:
                return False, "Creature not found", 0

            value = self.get_creature_value(creature_id)
            wallet.add("gold", value)
            name = creature.name
            self.remove_creature(creature_id)

            return True, f"Sold {name} for {value} gold", value

        # === Notifications ===

        def has_pending_notifications(self):
            """Check for pending notifications."""
            return len(self.notification_queue) > 0

        def get_pending_notification(self):
            """Get next notification."""
            if self.notification_queue:
                return self.notification_queue.pop(0)
            return None

        def clear_notifications(self):
            """Clear all notifications."""
            self.notification_queue = []

        # === Save/Load ===

        def to_dict(self):
            """Serialize manager state for saving."""
            return {
                "creatures": {k: v.to_dict() for k, v in self.creatures.items()},
                "breeding_pairs": {k: v.to_dict() for k, v in self.breeding_pairs.items()},
                "next_creature_id": self._next_creature_id,
                "next_pair_id": self._next_pair_id
            }

        def from_dict(self, data):
            """Restore manager state from save."""
            self._next_creature_id = data.get("next_creature_id", 1)
            self._next_pair_id = data.get("next_pair_id", 1)

            self.creatures = {}
            for k, v in data.get("creatures", {}).items():
                self.creatures[k] = Creature.from_dict(v)

            self.breeding_pairs = {}
            for k, v in data.get("breeding_pairs", {}).items():
                self.breeding_pairs[k] = BreedingPair.from_dict(v)

    # =========================================================================
    # SPECIES AND TRAITS SETUP
    # =========================================================================

    def setup_creature_species(manager):
        """Initialize creature species and traits."""

        # === TRAITS ===

        manager.register_trait(CreatureTrait(
            id="flame_aura",
            name="Flame Aura",
            description="Radiates gentle warmth.",
            stat_modifiers={"happiness": 10, "energy": -5},
            inheritance_weight=60,
            visual_effect="aura:fire"
        ))

        manager.register_trait(CreatureTrait(
            id="thick_scales",
            name="Thick Scales",
            description="Extra tough scales provide protection.",
            stat_modifiers={"max_health": 20},
            inheritance_weight=50,
            dominant=True,
            rarity_modifier=1
        ))

        manager.register_trait(CreatureTrait(
            id="fire_breath",
            name="Fire Breath",
            description="Can breathe small flames.",
            stat_modifiers={"energy": -10},
            inheritance_weight=40,
            rarity_modifier=1
        ))

        manager.register_trait(CreatureTrait(
            id="quick_learner",
            name="Quick Learner",
            description="Bonds faster with its caretaker.",
            stat_modifiers={"happiness": 5},
            inheritance_weight=55
        ))

        manager.register_trait(CreatureTrait(
            id="calm",
            name="Calm",
            description="A peaceful temperament.",
            stat_modifiers={"happiness": 15},
            inheritance_weight=65
        ))

        manager.register_trait(CreatureTrait(
            id="aggressive",
            name="Aggressive",
            description="Feisty and energetic.",
            stat_modifiers={"energy": 10, "happiness": -5},
            inheritance_weight=50
        ))

        manager.register_trait(CreatureTrait(
            id="regeneration",
            name="Regeneration",
            description="Slowly regenerates health over time.",
            stat_modifiers={"max_health": 15},
            inheritance_weight=70,
            rarity_modifier=1
        ))

        manager.register_trait(CreatureTrait(
            id="bouncy",
            name="Bouncy",
            description="Extra springy and playful.",
            stat_modifiers={"happiness": 10, "energy": 10},
            inheritance_weight=60,
            visual_effect="size:small"
        ))

        manager.register_trait(CreatureTrait(
            id="transparent",
            name="Transparent",
            description="Partially see-through body.",
            stat_modifiers={},
            inheritance_weight=45,
            visual_effect="pattern:transparent",
            rarity_modifier=1
        ))

        manager.register_trait(CreatureTrait(
            id="sticky",
            name="Sticky",
            description="Leaves a slight residue.",
            stat_modifiers={"energy": -5},
            inheritance_weight=50
        ))

        manager.register_trait(CreatureTrait(
            id="photosynthesis",
            name="Photosynthesis",
            description="Gains energy from light.",
            stat_modifiers={"energy": 20, "hunger": 10},
            inheritance_weight=55
        ))

        manager.register_trait(CreatureTrait(
            id="camouflage",
            name="Camouflage",
            description="Can blend with surroundings.",
            stat_modifiers={},
            inheritance_weight=40,
            rarity_modifier=1
        ))

        manager.register_trait(CreatureTrait(
            id="healing_touch",
            name="Healing Touch",
            description="Has a soothing presence.",
            stat_modifiers={"happiness": 10},
            inheritance_weight=35,
            rarity_modifier=2
        ))

        manager.register_trait(CreatureTrait(
            id="ancient_wisdom",
            name="Ancient Wisdom",
            description="Carries knowledge of ages past.",
            stat_modifiers={"happiness": 5},
            inheritance_weight=25,
            dominant=True,
            rarity_modifier=2
        ))

        manager.register_trait(CreatureTrait(
            id="frost_aura",
            name="Frost Aura",
            description="Radiates cold air.",
            stat_modifiers={"energy": 5},
            inheritance_weight=60,
            visual_effect="aura:ice"
        ))

        manager.register_trait(CreatureTrait(
            id="storm_charged",
            name="Storm Charged",
            description="Crackles with electric energy.",
            stat_modifiers={"energy": 15},
            inheritance_weight=50,
            visual_effect="aura:lightning",
            rarity_modifier=1
        ))

        # === SPECIES ===

        manager.register_species(CreatureSpecies(
            id="fire_dragon",
            name="Fire Dragon",
            description="A majestic dragon wreathed in eternal flames.",
            base_stats={"max_health": 150, "hunger": 80, "happiness": 40, "energy": 100},
            growth_rates={"max_health": 10, "energy": 5},
            possible_traits=["flame_aura", "thick_scales", "quick_learner",
                            "aggressive", "calm", "fire_breath"],
            trait_weights={"flame_aura": 30, "thick_scales": 20, "aggressive": 25,
                          "fire_breath": 15, "calm": 10},
            compatible_species=["fire_dragon", "ice_dragon", "storm_dragon"],
            gestation_periods=8,
            maturity_age=14,
            rarity_weights={"common": 40, "uncommon": 30, "rare": 20,
                           "epic": 8, "legendary": 2}
        ))

        manager.register_species(CreatureSpecies(
            id="ice_dragon",
            name="Ice Dragon",
            description="A crystalline dragon of frost and snow.",
            base_stats={"max_health": 140, "hunger": 70, "happiness": 45, "energy": 110},
            growth_rates={"max_health": 8, "energy": 6},
            possible_traits=["frost_aura", "thick_scales", "quick_learner",
                            "calm", "regeneration"],
            trait_weights={"frost_aura": 35, "thick_scales": 20, "calm": 25},
            compatible_species=["ice_dragon", "fire_dragon", "storm_dragon"],
            gestation_periods=8,
            maturity_age=14,
            rarity_weights={"common": 35, "uncommon": 30, "rare": 22,
                           "epic": 10, "legendary": 3}
        ))

        manager.register_species(CreatureSpecies(
            id="storm_dragon",
            name="Storm Dragon",
            description="A fierce dragon crackling with lightning.",
            base_stats={"max_health": 130, "hunger": 90, "happiness": 35, "energy": 120},
            growth_rates={"max_health": 7, "energy": 8},
            possible_traits=["storm_charged", "thick_scales", "aggressive",
                            "quick_learner"],
            trait_weights={"storm_charged": 40, "aggressive": 30, "thick_scales": 15},
            compatible_species=["storm_dragon", "fire_dragon", "ice_dragon"],
            gestation_periods=7,
            maturity_age=12,
            rarity_weights={"common": 30, "uncommon": 35, "rare": 22,
                           "epic": 10, "legendary": 3}
        ))

        manager.register_species(CreatureSpecies(
            id="water_slime",
            name="Water Slime",
            description="A playful, gelatinous creature made of living water.",
            base_stats={"max_health": 60, "hunger": 100, "happiness": 70, "energy": 80},
            growth_rates={"max_health": 3, "happiness": 2},
            possible_traits=["regeneration", "transparent", "sticky", "bouncy"],
            trait_weights={"regeneration": 40, "bouncy": 35, "transparent": 15},
            compatible_species=["water_slime", "fire_slime", "earth_slime"],
            gestation_periods=3,
            maturity_age=5,
            rarity_weights={"common": 60, "uncommon": 25, "rare": 10,
                           "epic": 4, "legendary": 1}
        ))

        manager.register_species(CreatureSpecies(
            id="fire_slime",
            name="Fire Slime",
            description="A warm blob that glows with inner flame.",
            base_stats={"max_health": 50, "hunger": 90, "happiness": 65, "energy": 90},
            growth_rates={"max_health": 2, "energy": 3},
            possible_traits=["flame_aura", "transparent", "bouncy", "aggressive"],
            trait_weights={"flame_aura": 45, "bouncy": 25, "aggressive": 20},
            compatible_species=["fire_slime", "water_slime", "earth_slime"],
            gestation_periods=3,
            maturity_age=5,
            rarity_weights={"common": 55, "uncommon": 28, "rare": 12,
                           "epic": 4, "legendary": 1}
        ))

        manager.register_species(CreatureSpecies(
            id="earth_slime",
            name="Earth Slime",
            description="A sturdy slime mixed with soil and stone.",
            base_stats={"max_health": 80, "hunger": 100, "happiness": 60, "energy": 70},
            growth_rates={"max_health": 5, "happiness": 1},
            possible_traits=["regeneration", "sticky", "calm", "thick_scales"],
            trait_weights={"regeneration": 30, "calm": 35, "sticky": 20},
            compatible_species=["earth_slime", "water_slime", "fire_slime"],
            gestation_periods=4,
            maturity_age=6,
            rarity_weights={"common": 60, "uncommon": 25, "rare": 10,
                           "epic": 4, "legendary": 1}
        ))

        manager.register_species(CreatureSpecies(
            id="forest_spirit",
            name="Forest Spirit",
            description="An ethereal being born from ancient trees.",
            base_stats={"max_health": 80, "hunger": 50, "happiness": 60, "energy": 120},
            growth_rates={"max_health": 5, "energy": 8},
            possible_traits=["photosynthesis", "camouflage", "healing_touch",
                            "ancient_wisdom", "calm"],
            trait_weights={"photosynthesis": 35, "calm": 25, "camouflage": 20,
                          "healing_touch": 15, "ancient_wisdom": 5},
            compatible_species=["forest_spirit", "mountain_spirit"],
            gestation_periods=6,
            maturity_age=10,
            rarity_weights={"common": 30, "uncommon": 35, "rare": 25,
                           "epic": 8, "legendary": 2}
        ))

        manager.register_species(CreatureSpecies(
            id="mountain_spirit",
            name="Mountain Spirit",
            description="A powerful spirit of stone and earth.",
            base_stats={"max_health": 120, "hunger": 40, "happiness": 50, "energy": 90},
            growth_rates={"max_health": 8, "energy": 4},
            possible_traits=["thick_scales", "ancient_wisdom", "calm",
                            "regeneration", "camouflage"],
            trait_weights={"thick_scales": 35, "calm": 25, "ancient_wisdom": 15,
                          "regeneration": 15, "camouflage": 10},
            compatible_species=["mountain_spirit", "forest_spirit"],
            gestation_periods=7,
            maturity_age=12,
            rarity_weights={"common": 25, "uncommon": 35, "rare": 25,
                           "epic": 12, "legendary": 3}
        ))


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

default breeding_manager = BreedingManager()

default breeding_parent1 = None
default breeding_parent2 = None
default creature_filter = None
default selected_creature = None


# =============================================================================
# UI SCREENS
# =============================================================================

screen creature_collection_screen():
    modal True

    $ creature_count = len(breeding_manager.creatures)

    add Solid("#000000cc")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 30
        ypadding 20
        xsize 900
        ysize 650
        background Solid("#1a1a2e")

        vbox:
            spacing 15

            # Header
            hbox:
                xfill True
                text "Creature Collection" size 28 color "#ffffff"

                hbox:
                    xalign 1.0
                    spacing 15
                    text "[creature_count] creatures" size 16 color "#aaaaaa"
                    textbutton "X" action Return(("back", None)) text_color "#ff6666" text_size 20

            # Filter tabs
            hbox:
                spacing 10
                textbutton "All" action SetVariable("creature_filter", None) text_size 14
                for species in breeding_manager.get_all_species():
                    textbutton species.name action SetVariable("creature_filter", species.id) text_size 14

            # Creature list
            $ filtered_creatures = [c for c in breeding_manager.get_all_creatures() if creature_filter is None or c.species_id == creature_filter]
            $ fc_count = len(filtered_creatures)

            text "Creatures: [fc_count]" size 12 color "#666666"

            vbox:
                spacing 5
                ysize 400

                for creature in filtered_creatures:
                    $ c_rarity_color = CreatureRarity.get_color(creature.rarity)
                    $ c_species = breeding_manager.get_species(creature.species_id)
                    $ c_species_name = c_species.name if c_species else "Unknown"

                    textbutton "[creature.name] ([c_species_name])" action Return(("view", creature.id)) text_color c_rarity_color text_size 16

            # Bottom buttons
            hbox:
                spacing 20
                xalign 0.5
                textbutton "Breeding" action Return(("breeding", None)) text_size 18
                textbutton "Nursery" action Return(("nursery", None)) text_size 18
                textbutton "Back" action Return(("back", None)) text_size 18


screen creature_card(creature):
    $ rarity_color = CreatureRarity.get_color(creature.rarity)
    $ species = breeding_manager.get_species(creature.species_id)

    button:
        xsize 200
        ysize 180
        background Solid("#2a2a4e")
        hover_background Solid("#3a3a6e")
        action Show("creature_detail_screen", creature_id=creature.id)

        vbox:
            spacing 5
            xalign 0.5
            yalign 0.5

            if creature.is_egg:
                text "Egg" size 40 xalign 0.5 color "#ffdd88"
                text "[creature.hatch_time_remaining] periods" size 12 color "#aaaaaa" xalign 0.5
            else:
                $ creature_icon = species.name[:1] if species else "?"
                text creature_icon size 40 xalign 0.5 color rarity_color

            text creature.name size 14 color rarity_color xalign 0.5 text_align 0.5

            if species:
                text species.name size 12 color "#888888" xalign 0.5

            if not creature.is_egg:
                vbox:
                    spacing 2
                    xalign 0.5
                    bar value creature.health range creature.max_health xsize 150 ysize 8 left_bar Solid("#ff4444") right_bar Solid("#333333")
                    bar value creature.hunger range 100 xsize 150 ysize 8 left_bar Solid("#ffaa44") right_bar Solid("#333333")
                    bar value creature.happiness range 100 xsize 150 ysize 8 left_bar Solid("#44ff44") right_bar Solid("#333333")


screen creature_detail_screen(creature_id):
    modal True

    $ creature = breeding_manager.get_creature(creature_id)
    $ species = breeding_manager.get_species(creature.species_id) if creature else None
    $ rarity_color = CreatureRarity.get_color(creature.rarity) if creature else "#ffffff"

    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 30
        ypadding 25
        xsize 550
        ysize 650
        background Solid("#1a1a2e")

        if creature:
            vbox:
                spacing 12

                # Header
                hbox:
                    xfill True
                    vbox:
                        text creature.name size 26 color rarity_color
                        text CreatureRarity.get_display_name(creature.rarity) size 14 color rarity_color
                    textbutton "X" action Return("close") xalign 1.0 text_color "#ff6666"

                if species:
                    text species.name size 16 color "#aaaaaa"
                    text species.description size 12 color "#666666"

                null height 5

                # Info row
                hbox:
                    spacing 20
                    text "Gen [creature.generation]" size 14 color "#88aaff"
                    text "Age: [creature.age_days] days" size 14 color "#aaaaaa"
                    if creature.is_mature:
                        text "Mature" size 14 color "#44ff44"
                    else:
                        text "Young" size 14 color "#ffaa44"

                null height 5

                # Stats section
                text "Stats" size 18 color "#ffcc66"

                grid 2 2:
                    spacing 15
                    xfill True

                    vbox:
                        text "Health" size 14 color "#ff6666"
                        bar value creature.health range creature.max_health xsize 200 ysize 15 left_bar Solid("#ff4444") right_bar Solid("#333333")
                        text "[creature.health]/[creature.max_health]" size 12 color "#888888"

                    vbox:
                        text "Hunger" size 14 color "#ffaa44"
                        bar value creature.hunger range 100 xsize 200 ysize 15 left_bar Solid("#ffaa44") right_bar Solid("#333333")
                        text "[creature.hunger]/100" size 12 color "#888888"

                    vbox:
                        text "Happiness" size 14 color "#44ff44"
                        bar value creature.happiness range 100 xsize 200 ysize 15 left_bar Solid("#44ff44") right_bar Solid("#333333")
                        text "[creature.happiness]/100 ([creature.get_mood()])" size 12 color "#888888"

                    vbox:
                        text "Energy" size 14 color "#44aaff"
                        bar value creature.energy range 100 xsize 200 ysize 15 left_bar Solid("#44aaff") right_bar Solid("#333333")
                        text "[creature.energy]/100" size 12 color "#888888"

                null height 5

                # Bond
                text "Bond: [creature.get_bond_status()]" size 16 color "#ff88ff"
                bar value creature.bond_level range 100 xsize 450 ysize 12 left_bar Solid("#ff44ff") right_bar Solid("#333333")

                null height 5

                # Traits
                if creature.traits:
                    text "Traits" size 18 color "#ffcc66"
                    hbox:
                        spacing 10
                        for trait_id in creature.traits:
                            $ trait = breeding_manager.get_trait(trait_id)
                            if trait:
                                frame:
                                    background Solid("#3a3a5e")
                                    padding (10, 5)
                                    text trait.name size 12 color "#aaffaa"

                null height 10

                # Actions - return "stay" to keep screen open
                hbox:
                    spacing 15
                    xalign 0.5

                    if not creature.is_egg:
                        textbutton "Feed" action [Function(creature.feed), Return("stay")] text_size 16
                        textbutton "Play" action [Function(creature.play), Return("stay")] text_size 16
                        textbutton "Pet" action [Function(creature.pet), Return("stay")] text_size 16
                        textbutton "Rest" action [Function(creature.rest), Return("stay")] text_size 16

                        if creature.is_mature:
                            textbutton "Breed" action [
                                SetVariable("breeding_parent1", creature_id),
                                Return("breed")
                            ] text_size 16
                    else:
                        if creature.hatch_time_remaining <= 0:
                            textbutton "Hatch!" action [
                                Function(breeding_manager.hatch_egg, creature_id),
                                Return("stay")
                            ] text_size 18


screen breeding_selection_screen():
    modal True

    add Solid("#000000cc")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 30
        ypadding 20
        xsize 800
        ysize 550
        background Solid("#1a1a2e")

        vbox:
            spacing 15

            hbox:
                xfill True
                text "Select Breeding Pair" size 24 color "#ff88ff"
                textbutton "X" action Return() xalign 1.0 text_color "#ff6666"

            hbox:
                spacing 30

                # Parent 1
                vbox:
                    xsize 350
                    text "First Parent" size 16 color "#aaaaaa"

                    vbox:
                        spacing 5
                        ysize 350

                        for creature in breeding_manager.get_hatched_creatures():
                            if creature.is_mature:
                                $ selected = (breeding_parent1 == creature.id)
                                $ rcolor = CreatureRarity.get_color(creature.rarity)
                                $ btn_text = "> " + creature.name if selected else creature.name

                                textbutton btn_text action SetVariable("breeding_parent1", creature.id) text_color rcolor text_size 14

                # Parent 2
                vbox:
                    xsize 350
                    text "Second Parent" size 16 color "#aaaaaa"

                    vbox:
                        spacing 5
                        ysize 350

                        for creature in breeding_manager.get_hatched_creatures():
                            if creature.is_mature and creature.id != breeding_parent1:
                                $ can_breed_result = breeding_manager.can_breed(breeding_parent1, creature.id) if breeding_parent1 else (False, "Select first")
                                $ can_breed_flag = can_breed_result[0]
                                $ color = CreatureRarity.get_color(creature.rarity) if can_breed_flag else "#666666"
                                $ selected = (breeding_parent2 == creature.id)
                                $ btn_text = "> " + creature.name if selected else creature.name
                                $ btn_action = SetVariable("breeding_parent2", creature.id) if can_breed_flag else NullAction()

                                textbutton btn_text action btn_action text_color color text_size 14

            # Breed button
            hbox:
                xalign 0.5
                spacing 20

                if breeding_parent1 and breeding_parent2:
                    $ final_check = breeding_manager.can_breed(breeding_parent1, breeding_parent2)
                    if final_check[0]:
                        textbutton "Start Breeding!" action [
                            Function(breeding_manager.start_breeding, breeding_parent1, breeding_parent2, 0, 0),
                            SetVariable("breeding_parent1", None),
                            SetVariable("breeding_parent2", None),
                            Return()
                        ] text_size 18
                    else:
                        text final_check[1] color "#ff4444" size 14

                textbutton "Cancel" action [
                    SetVariable("breeding_parent1", None),
                    SetVariable("breeding_parent2", None),
                    Return()
                ] text_size 16


screen nursery_screen():
    modal True

    add Solid("#000000cc")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 30
        ypadding 20
        xsize 700
        ysize 500
        background Solid("#1a1a2e")

        vbox:
            spacing 15

            hbox:
                xfill True
                text "Nursery" size 24 color "#ffcc66"
                textbutton "X" action Return() xalign 1.0 text_color "#ff6666"

            # Start new breeding button
            textbutton "Start New Breeding..." action Return("breeding") text_size 16 text_color "#ff88ff"

            null height 5

            # Active breeding
            text "Active Breeding" size 18 color "#ff88ff"

            vbox:
                spacing 5
                ysize 120

                $ active_pairs = [(pid, p) for pid, p in breeding_manager.breeding_pairs.items() if not p.completed]

                if active_pairs:
                    for pair_id, pair in active_pairs:
                        $ c1 = breeding_manager.get_creature(pair.creature1_id)
                        $ c2 = breeding_manager.get_creature(pair.creature2_id)

                        if c1 and c2:
                            $ pair_text = c1.name + " + " + c2.name + " (" + str(pair.gestation_remaining) + " periods left)"
                            text pair_text size 14 color "#ffffff"
                else:
                    text "No active breeding pairs" size 14 color "#666666"

            null height 10

            # Eggs
            text "Eggs" size 18 color "#ffcc66"

            vbox:
                spacing 5
                ysize 200

                $ eggs = breeding_manager.get_eggs()

                if eggs:
                    for egg in eggs:
                        $ species = breeding_manager.get_species(egg.species_id)
                        $ species_name = species.name if species else "Unknown"
                        $ ready = egg.hatch_time_remaining <= 0
                        $ rcolor = CreatureRarity.get_color(egg.rarity)
                        $ rarity_name = CreatureRarity.get_display_name(egg.rarity)

                        if ready:
                            $ egg_text = species_name + " Egg (" + rarity_name + ") - READY TO HATCH!"
                            textbutton egg_text action Function(breeding_manager.hatch_egg, egg.id) text_color "#44ff44" text_size 14
                        else:
                            $ egg_text = species_name + " Egg (" + rarity_name + ") - " + str(egg.hatch_time_remaining) + " periods"
                            text egg_text size 14 color rcolor
                else:
                    text "No eggs in nursery" size 14 color "#666666"


# =============================================================================
# DEMO LABEL
# =============================================================================

label breeding_demo:
    "Welcome to the Creature Breeding Demo!"

    python:
        # Clear any existing creatures for a fresh demo
        breeding_manager.creatures.clear()
        breeding_manager.breeding_pairs.clear()
        breeding_manager._next_creature_id = 1
        breeding_manager._next_pair_id = 1

        # Setup species and traits (safe to call multiple times)
        setup_creature_species(breeding_manager)

        # Create some starter creatures
        breeding_manager.create_creature("fire_dragon", "Ember", is_mature=True)
        breeding_manager.create_creature("fire_dragon", "Blaze", is_mature=True)
        breeding_manager.create_creature("water_slime", "Droplet", is_mature=True)
        breeding_manager.create_creature("water_slime", "Splash", is_mature=True)
        breeding_manager.create_creature("forest_spirit", "Willow", is_mature=True)

    $ num_creatures = len(breeding_manager.creatures)
    "You've been given [num_creatures] starter creatures to begin breeding!"

label breeding_demo_menu:
    menu:
        "What would you like to do?"

        "View Collection":
            jump breeding_collection_loop

        "Nursery (Breeding & Eggs)":
            call screen nursery_screen
            if _return == "breeding":
                call screen breeding_selection_screen
            jump breeding_demo_menu

        "Advance Time (1 period)":
            python:
                events = breeding_manager.on_time_advance(1, 0)
                eggs_ready = len(events.get("eggs_ready", []))
                breeding_done = len(events.get("breeding_complete", []))
            if eggs_ready > 0:
                "[eggs_ready] egg(s) are ready to hatch!"
            if breeding_done > 0:
                "[breeding_done] breeding pair(s) produced eggs!"
            if eggs_ready == 0 and breeding_done == 0:
                "Time advanced. Nothing hatched yet."
            jump breeding_demo_menu

        "Exit Breeding Demo":
            "Thanks for trying the breeding system!"
            return

label breeding_collection_loop:
    call screen creature_collection_screen
    $ _action = _return[0] if _return else "back"
    $ _data = _return[1] if _return else None

    if _action == "view" and _data:
        $ _viewing_creature = _data
        jump creature_detail_loop

    if _action == "breeding":
        call screen breeding_selection_screen
        jump breeding_collection_loop

    if _action == "nursery":
        call screen nursery_screen
        if _return == "breeding":
            call screen breeding_selection_screen
        jump breeding_collection_loop

    # "back" or anything else returns to menu
    jump breeding_demo_menu

label creature_detail_loop:
    call screen creature_detail_screen(creature_id=_viewing_creature)

    # "stay" means action button was clicked - loop back to show updated stats
    if _return == "stay":
        jump creature_detail_loop

    # "breed" means open breeding screen then return to collection
    if _return == "breed":
        call screen breeding_selection_screen
        jump breeding_collection_loop

    # "close" or anything else returns to collection
    jump breeding_collection_loop


label breeding_init:
    python:
        setup_creature_species(breeding_manager)
    return

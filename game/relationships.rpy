# Relationship Meters System for Heebee
# Tracks affection, trust, respect, and faction reputation

init python:
    import math

    class Relationship:
        """Tracks relationship with a single NPC"""
        def __init__(self, name, initial_affection=50, initial_trust=50, initial_respect=50):
            self.name = name
            self.affection = initial_affection  # 0-100, romantic interest
            self.trust = initial_trust          # 0-100, reliability
            self.respect = initial_respect      # 0-100, admiration
            self.history = []                   # Track significant events
            self.unlocked_events = []           # Special events unlocked
            self.met = False
            self.romance_available = False
            self.romance_active = False

        def modify_affection(self, amount, reason=""):
            old_val = self.affection
            self.affection = max(0, min(100, self.affection + amount))
            if reason:
                self.history.append(("affection", amount, reason))
            self._check_milestones()
            return self.affection - old_val

        def modify_trust(self, amount, reason=""):
            old_val = self.trust
            self.trust = max(0, min(100, self.trust + amount))
            if reason:
                self.history.append(("trust", amount, reason))
            self._check_milestones()
            return self.trust - old_val

        def modify_respect(self, amount, reason=""):
            old_val = self.respect
            self.respect = max(0, min(100, self.respect + amount))
            if reason:
                self.history.append(("respect", amount, reason))
            self._check_milestones()
            return self.respect - old_val

        def modify_all(self, amount, reason=""):
            """Modify all relationship stats at once"""
            self.modify_affection(amount, reason)
            self.modify_trust(amount, reason)
            self.modify_respect(amount, reason)

        def get_overall(self):
            """Calculate overall relationship score"""
            return int((self.affection + self.trust + self.respect) / 3)

        def get_status(self):
            """Get relationship status text"""
            overall = self.get_overall()
            if overall >= 90:
                return "Soulmate" if self.romance_active else "Best Friend"
            elif overall >= 75:
                return "Lover" if self.romance_active else "Close Friend"
            elif overall >= 60:
                return "Dating" if self.romance_active else "Good Friend"
            elif overall >= 45:
                return "Friend"
            elif overall >= 30:
                return "Acquaintance"
            elif overall >= 15:
                return "Distant"
            else:
                return "Stranger"

        def _check_milestones(self):
            """Check for relationship milestones"""
            overall = self.get_overall()

            # Unlock romance option at 60+ affection and 50+ trust
            if self.affection >= 60 and self.trust >= 50 and not self.romance_available:
                self.romance_available = True
                if "romance_unlocked" not in self.unlocked_events:
                    self.unlocked_events.append("romance_unlocked")

            # Special events at milestones
            if overall >= 75 and "milestone_75" not in self.unlocked_events:
                self.unlocked_events.append("milestone_75")
            if overall >= 90 and "milestone_90" not in self.unlocked_events:
                self.unlocked_events.append("milestone_90")

        def start_romance(self):
            """Begin romantic relationship"""
            if self.romance_available:
                self.romance_active = True
                return True
            return False

        def end_romance(self):
            """End romantic relationship"""
            self.romance_active = False
            self.modify_affection(-20, "Breakup")
            self.modify_trust(-10, "Breakup")

    class Faction:
        """Tracks reputation with a faction/organization"""
        def __init__(self, name, initial_rep=0):
            self.name = name
            self.reputation = initial_rep  # -100 to 100
            self.rank = "Neutral"
            self.perks_unlocked = []

        def modify_reputation(self, amount, reason=""):
            old_val = self.reputation
            self.reputation = max(-100, min(100, self.reputation + amount))
            self._update_rank()
            return self.reputation - old_val

        def _update_rank(self):
            """Update rank based on reputation"""
            if self.reputation >= 80:
                self.rank = "Exalted"
            elif self.reputation >= 60:
                self.rank = "Revered"
            elif self.reputation >= 40:
                self.rank = "Honored"
            elif self.reputation >= 20:
                self.rank = "Friendly"
            elif self.reputation >= -20:
                self.rank = "Neutral"
            elif self.reputation >= -40:
                self.rank = "Unfriendly"
            elif self.reputation >= -60:
                self.rank = "Hostile"
            else:
                self.rank = "Hated"

            # Unlock perks at certain ranks
            if self.reputation >= 40 and "discount_10" not in self.perks_unlocked:
                self.perks_unlocked.append("discount_10")
            if self.reputation >= 60 and "discount_20" not in self.perks_unlocked:
                self.perks_unlocked.append("discount_20")
            if self.reputation >= 80 and "exclusive_items" not in self.perks_unlocked:
                self.perks_unlocked.append("exclusive_items")

        def get_discount(self):
            """Get shop discount based on reputation"""
            if "discount_20" in self.perks_unlocked:
                return 0.20
            elif "discount_10" in self.perks_unlocked:
                return 0.10
            return 0.0

    class RelationshipManager:
        """Manages all character relationships and factions"""
        def __init__(self):
            self.relationships = {}
            self.factions = {}

        def add_character(self, char_id, name, **kwargs):
            """Add a new character relationship"""
            self.relationships[char_id] = Relationship(name, **kwargs)

        def add_faction(self, faction_id, name, initial_rep=0):
            """Add a new faction"""
            self.factions[faction_id] = Faction(name, initial_rep)

        def get_relationship(self, char_id):
            """Get relationship with a character"""
            return self.relationships.get(char_id)

        def get_faction(self, faction_id):
            """Get faction by ID"""
            return self.factions.get(faction_id)

        def meet_character(self, char_id):
            """Mark character as met"""
            if char_id in self.relationships:
                self.relationships[char_id].met = True

        def get_met_characters(self):
            """Get list of met characters"""
            return [r for r in self.relationships.values() if r.met]

        def get_romance_options(self):
            """Get characters available for romance"""
            return [r for r in self.relationships.values()
                    if r.romance_available and not r.romance_active]

        def get_active_romances(self):
            """Get characters in active romance"""
            return [r for r in self.relationships.values() if r.romance_active]

# Initialize relationship system
default relationship_manager = RelationshipManager()

# Initialize example NPCs
init python:
    def setup_relationships():
        rm = relationship_manager

        # Add main characters
        rm.add_character("elena", "Elena", initial_affection=55, initial_trust=50, initial_respect=45)
        rm.add_character("marcus", "Marcus", initial_affection=40, initial_trust=60, initial_respect=55)
        rm.add_character("sophia", "Sophia", initial_affection=45, initial_trust=45, initial_respect=50)
        rm.add_character("kai", "Kai", initial_affection=50, initial_trust=40, initial_respect=60)

        # Add factions
        rm.add_faction("guild", "Adventurer's Guild", 10)
        rm.add_faction("merchants", "Merchant Coalition", 0)
        rm.add_faction("nobles", "Noble Houses", -10)
        rm.add_faction("underground", "The Underground", 5)

# Relationship display screen
screen relationship_screen():
    tag menu
    use game_menu(_("Relationships"), scroll="viewport"):
        style_prefix "relationship"

        vbox:
            spacing 20

            # Character relationships
            text "Characters" size 28

            for char_id, rel in relationship_manager.relationships.items():
                if rel.met:
                    frame:
                        padding (15, 10)
                        vbox:
                            spacing 5

                            hbox:
                                text rel.name size 22 bold True
                                text " - [rel.get_status()]" size 18
                                if rel.romance_active:
                                    text " ♥" color "#ff6b9d" size 22

                            # Affection bar
                            hbox:
                                text "Affection: " size 14
                                bar value rel.affection range 100 xmaximum 200
                                text " [rel.affection]%" size 14

                            # Trust bar
                            hbox:
                                text "Trust: " size 14
                                bar value rel.trust range 100 xmaximum 200
                                text " [rel.trust]%" size 14

                            # Respect bar
                            hbox:
                                text "Respect: " size 14
                                bar value rel.respect range 100 xmaximum 200
                                text " [rel.respect]%" size 14

            null height 20

            # Faction reputation
            text "Factions" size 28

            for faction_id, faction in relationship_manager.factions.items():
                frame:
                    padding (15, 10)
                    vbox:
                        spacing 5

                        hbox:
                            text faction.name size 20 bold True
                            text " - [faction.rank]" size 16

                        hbox:
                            text "Reputation: " size 14
                            bar value (faction.reputation + 100) range 200 xmaximum 200
                            text " [faction.reputation]" size 14

style relationship_vbox:
    xfill True

style relationship_frame:
    xfill True
    background Frame("gui/frame.png", 4, 4, 4, 4)

# Relationship change notification screen
screen relationship_change(character_name, stat, amount):
    timer 2.0 action Hide("relationship_change")

    frame:
        xalign 0.5
        yalign 0.1
        padding (20, 10)

        hbox:
            spacing 10
            text character_name bold True
            if amount > 0:
                text "+[amount] [stat]" color "#4CAF50"
            else:
                text "[amount] [stat]" color "#f44336"

# Helper label to show relationship change
label show_relationship_change(char_id, stat, amount, reason=""):
    python:
        rel = relationship_manager.get_relationship(char_id)
        if rel:
            if stat == "affection":
                rel.modify_affection(amount, reason)
            elif stat == "trust":
                rel.modify_trust(amount, reason)
            elif stat == "respect":
                rel.modify_respect(amount, reason)
            elif stat == "all":
                rel.modify_all(amount, reason)
            renpy.show_screen("relationship_change", rel.name, stat, amount)
    return

# Example usage in dialogue
label relationship_demo:
    call setup_relationships_label from _call_setup_relationships_label

    "Welcome to the relationship system demo!"

    # Meet Elena
    python:
        relationship_manager.meet_character("elena")

    "You've met Elena!"

    menu:
        "How should you respond to Elena?"

        "Compliment her":
            call show_relationship_change("elena", "affection", 10, "Gave a compliment") from _call_show_relationship_change
            "Elena smiles warmly at you."

        "Offer to help":
            call show_relationship_change("elena", "trust", 10, "Offered help") from _call_show_relationship_change_1
            "Elena seems to appreciate your offer."

        "Show your skills":
            call show_relationship_change("elena", "respect", 10, "Impressed with skills") from _call_show_relationship_change_2
            "Elena looks impressed."

        "Be rude":
            call show_relationship_change("elena", "all", -15, "Was rude") from _call_show_relationship_change_3
            "Elena frowns and steps back."

    "Press R to view relationships."

    call screen relationship_screen

    return

label setup_relationships_label:
    python:
        setup_relationships()
    return

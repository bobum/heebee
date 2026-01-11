# Quest/Mission Log System for Ren'Py Visual Novel
# This module provides a comprehensive quest tracking system with
# objectives, rewards, categories, and status management.

init python:

    # =========================================================================
    # QUEST STATUS CONSTANTS
    # =========================================================================

    QUEST_STATUS_AVAILABLE = "available"  # Quest can be started
    QUEST_STATUS_ACTIVE = "active"        # Quest is in progress
    QUEST_STATUS_COMPLETED = "completed"  # Quest successfully finished
    QUEST_STATUS_FAILED = "failed"        # Quest failed

    # =========================================================================
    # QUEST CATEGORY CONSTANTS
    # =========================================================================

    QUEST_CATEGORY_MAIN = "main"          # Main story quests
    QUEST_CATEGORY_SIDE = "side"          # Optional side quests

    # =========================================================================
    # QUEST OBJECTIVE CLASS
    # =========================================================================

    class QuestObjective:
        """
        Represents a single objective within a quest.

        Attributes:
            description (str): Description of what needs to be done
            completed (bool): Whether this objective has been completed
            optional (bool): Whether this objective is optional for quest completion
        """

        def __init__(self, description, completed=False, optional=False):
            self.description = description
            self.completed = completed
            self.optional = optional

        def complete(self):
            """Mark this objective as completed."""
            self.completed = True

        def reset(self):
            """Reset this objective to incomplete."""
            self.completed = False

        def __repr__(self):
            status = "done" if self.completed else "pending"
            opt = " (optional)" if self.optional else ""
            return f"QuestObjective({self.description!r}, {status}{opt})"

    # =========================================================================
    # QUEST REWARDS CLASS
    # =========================================================================

    class QuestRewards:
        """
        Represents rewards for completing a quest.

        Attributes:
            gold (int): Amount of gold/currency rewarded
            xp (int): Amount of experience points rewarded
            items (list): List of item IDs or tuples (item_id, quantity)
        """

        def __init__(self, gold=0, xp=0, items=None):
            self.gold = gold
            self.xp = xp
            self.items = items if items is not None else []

        def has_rewards(self):
            """Check if there are any rewards."""
            return self.gold > 0 or self.xp > 0 or len(self.items) > 0

        def __repr__(self):
            return f"QuestRewards(gold={self.gold}, xp={self.xp}, items={self.items})"

    # =========================================================================
    # QUEST CLASS
    # =========================================================================

    class Quest:
        """
        Represents a quest/mission in the game.

        Attributes:
            id (str): Unique identifier for the quest
            name (str): Display name of the quest
            description (str): Full description of the quest
            objectives (list): List of QuestObjective instances
            rewards (QuestRewards): Rewards for completing the quest
            status (str): Current status (available/active/completed/failed)
            category (str): Quest category (main/side)
        """

        def __init__(self, id, name, description, objectives=None, rewards=None,
                     status=QUEST_STATUS_AVAILABLE, category=QUEST_CATEGORY_SIDE):
            self.id = id
            self.name = name
            self.description = description
            self.objectives = objectives if objectives is not None else []
            self.rewards = rewards if rewards is not None else QuestRewards()
            self.status = status
            self.category = category

        def add_objective(self, description, optional=False):
            """Add a new objective to the quest."""
            objective = QuestObjective(description, optional=optional)
            self.objectives.append(objective)
            return objective

        def complete_objective(self, index):
            """
            Mark an objective as completed by index.

            Args:
                index (int): Index of the objective to complete

            Returns:
                bool: True if objective was completed, False if index invalid
            """
            if 0 <= index < len(self.objectives):
                self.objectives[index].complete()
                return True
            return False

        def get_required_objectives(self):
            """Get list of non-optional objectives."""
            return [obj for obj in self.objectives if not obj.optional]

        def get_optional_objectives(self):
            """Get list of optional objectives."""
            return [obj for obj in self.objectives if obj.optional]

        def get_completed_objectives(self):
            """Get list of completed objectives."""
            return [obj for obj in self.objectives if obj.completed]

        def get_incomplete_objectives(self):
            """Get list of incomplete objectives."""
            return [obj for obj in self.objectives if not obj.completed]

        def are_required_objectives_complete(self):
            """Check if all required (non-optional) objectives are complete."""
            required = self.get_required_objectives()
            if not required:
                return True
            return all(obj.completed for obj in required)

        def get_progress(self):
            """
            Get quest completion progress.

            Returns:
                tuple: (completed_count, total_count, percentage)
            """
            if not self.objectives:
                return (0, 0, 100.0)

            required = self.get_required_objectives()
            if not required:
                # If all objectives are optional, count all
                total = len(self.objectives)
                completed = len(self.get_completed_objectives())
            else:
                # Only count required objectives for progress
                total = len(required)
                completed = len([o for o in required if o.completed])

            percentage = (completed / total * 100.0) if total > 0 else 100.0
            return (completed, total, percentage)

        def is_main_quest(self):
            """Check if this is a main story quest."""
            return self.category == QUEST_CATEGORY_MAIN

        def is_side_quest(self):
            """Check if this is a side quest."""
            return self.category == QUEST_CATEGORY_SIDE

        def is_active(self):
            """Check if quest is currently active."""
            return self.status == QUEST_STATUS_ACTIVE

        def is_completed(self):
            """Check if quest is completed."""
            return self.status == QUEST_STATUS_COMPLETED

        def is_failed(self):
            """Check if quest has failed."""
            return self.status == QUEST_STATUS_FAILED

        def is_available(self):
            """Check if quest is available to start."""
            return self.status == QUEST_STATUS_AVAILABLE

        def __repr__(self):
            return f"Quest({self.id!r}, {self.name!r}, status={self.status})"

    # =========================================================================
    # QUEST MANAGER CLASS
    # =========================================================================

    class QuestManager:
        """
        Central manager for all quests in the game.

        This class provides methods to add, start, complete, and track quests.
        """

        def __init__(self):
            self.quests = {}  # quest_id -> Quest
            self._on_quest_complete_callbacks = []
            self._on_quest_fail_callbacks = []

        # ---------------------------------------------------------------------
        # Quest Registration
        # ---------------------------------------------------------------------

        def add_quest(self, quest):
            """
            Add a quest to the manager.

            Args:
                quest (Quest): The quest to add

            Returns:
                Quest: The added quest
            """
            self.quests[quest.id] = quest
            return quest

        def create_quest(self, id, name, description, category=QUEST_CATEGORY_SIDE,
                         rewards=None):
            """
            Create and add a new quest.

            Args:
                id (str): Unique quest identifier
                name (str): Display name
                description (str): Quest description
                category (str): Quest category (main/side)
                rewards (QuestRewards): Optional rewards

            Returns:
                Quest: The newly created quest
            """
            quest = Quest(
                id=id,
                name=name,
                description=description,
                category=category,
                rewards=rewards
            )
            return self.add_quest(quest)

        def remove_quest(self, quest_id):
            """
            Remove a quest from the manager.

            Args:
                quest_id (str): ID of quest to remove

            Returns:
                bool: True if removed, False if not found
            """
            if quest_id in self.quests:
                del self.quests[quest_id]
                return True
            return False

        # ---------------------------------------------------------------------
        # Quest Retrieval
        # ---------------------------------------------------------------------

        def get_quest(self, quest_id):
            """
            Get a quest by ID.

            Args:
                quest_id (str): Quest identifier

            Returns:
                Quest: The quest or None if not found
            """
            return self.quests.get(quest_id)

        def get_all_quests(self):
            """Get list of all quests."""
            return list(self.quests.values())

        def get_quests_by_status(self, status):
            """Get all quests with a specific status."""
            return [q for q in self.quests.values() if q.status == status]

        def get_quests_by_category(self, category):
            """Get all quests in a specific category."""
            return [q for q in self.quests.values() if q.category == category]

        def get_active_quests(self):
            """Get all currently active quests."""
            return self.get_quests_by_status(QUEST_STATUS_ACTIVE)

        def get_completed_quests(self):
            """Get all completed quests."""
            return self.get_quests_by_status(QUEST_STATUS_COMPLETED)

        def get_failed_quests(self):
            """Get all failed quests."""
            return self.get_quests_by_status(QUEST_STATUS_FAILED)

        def get_available_quests(self):
            """Get all available (not yet started) quests."""
            return self.get_quests_by_status(QUEST_STATUS_AVAILABLE)

        def get_main_quests(self):
            """Get all main story quests."""
            return self.get_quests_by_category(QUEST_CATEGORY_MAIN)

        def get_side_quests(self):
            """Get all side quests."""
            return self.get_quests_by_category(QUEST_CATEGORY_SIDE)

        def get_active_main_quests(self):
            """Get active main story quests."""
            return [q for q in self.get_active_quests() if q.is_main_quest()]

        def get_active_side_quests(self):
            """Get active side quests."""
            return [q for q in self.get_active_quests() if q.is_side_quest()]

        # ---------------------------------------------------------------------
        # Quest State Management
        # ---------------------------------------------------------------------

        def start_quest(self, quest_id):
            """
            Start a quest (change status from available to active).

            Args:
                quest_id (str): ID of quest to start

            Returns:
                bool: True if started, False if not found or not available
            """
            quest = self.get_quest(quest_id)
            if quest and quest.status == QUEST_STATUS_AVAILABLE:
                quest.status = QUEST_STATUS_ACTIVE
                return True
            return False

        def complete_quest(self, quest_id):
            """
            Complete a quest (change status to completed).

            Args:
                quest_id (str): ID of quest to complete

            Returns:
                QuestRewards: The rewards if completed, None otherwise
            """
            quest = self.get_quest(quest_id)
            if quest and quest.status == QUEST_STATUS_ACTIVE:
                quest.status = QUEST_STATUS_COMPLETED
                # Trigger callbacks
                for callback in self._on_quest_complete_callbacks:
                    callback(quest)
                return quest.rewards
            return None

        def fail_quest(self, quest_id):
            """
            Fail a quest (change status to failed).

            Args:
                quest_id (str): ID of quest to fail

            Returns:
                bool: True if failed, False if not found or not active
            """
            quest = self.get_quest(quest_id)
            if quest and quest.status == QUEST_STATUS_ACTIVE:
                quest.status = QUEST_STATUS_FAILED
                # Trigger callbacks
                for callback in self._on_quest_fail_callbacks:
                    callback(quest)
                return True
            return False

        def reset_quest(self, quest_id):
            """
            Reset a quest back to available status.

            Args:
                quest_id (str): ID of quest to reset

            Returns:
                bool: True if reset, False if not found
            """
            quest = self.get_quest(quest_id)
            if quest:
                quest.status = QUEST_STATUS_AVAILABLE
                # Reset all objectives
                for obj in quest.objectives:
                    obj.reset()
                return True
            return False

        # ---------------------------------------------------------------------
        # Objective Management
        # ---------------------------------------------------------------------

        def complete_objective(self, quest_id, objective_index):
            """
            Complete a specific objective in a quest.

            Args:
                quest_id (str): ID of the quest
                objective_index (int): Index of the objective

            Returns:
                bool: True if completed, False otherwise
            """
            quest = self.get_quest(quest_id)
            if quest and quest.is_active():
                return quest.complete_objective(objective_index)
            return False

        def add_objective(self, quest_id, description, optional=False):
            """
            Add an objective to an existing quest.

            Args:
                quest_id (str): ID of the quest
                description (str): Objective description
                optional (bool): Whether objective is optional

            Returns:
                QuestObjective: The new objective or None if quest not found
            """
            quest = self.get_quest(quest_id)
            if quest:
                return quest.add_objective(description, optional)
            return None

        def get_quest_progress(self, quest_id):
            """
            Get progress for a specific quest.

            Args:
                quest_id (str): ID of the quest

            Returns:
                tuple: (completed, total, percentage) or None if not found
            """
            quest = self.get_quest(quest_id)
            if quest:
                return quest.get_progress()
            return None

        def check_quest_completable(self, quest_id):
            """
            Check if a quest can be completed (all required objectives done).

            Args:
                quest_id (str): ID of the quest

            Returns:
                bool: True if completable, False otherwise
            """
            quest = self.get_quest(quest_id)
            if quest and quest.is_active():
                return quest.are_required_objectives_complete()
            return False

        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        def get_stats(self):
            """
            Get quest statistics.

            Returns:
                dict: Statistics including counts by status and category
            """
            return {
                "total": len(self.quests),
                "active": len(self.get_active_quests()),
                "completed": len(self.get_completed_quests()),
                "failed": len(self.get_failed_quests()),
                "available": len(self.get_available_quests()),
                "main_quests": len(self.get_main_quests()),
                "side_quests": len(self.get_side_quests()),
            }

        # ---------------------------------------------------------------------
        # Callbacks
        # ---------------------------------------------------------------------

        def on_quest_complete(self, callback):
            """Register a callback for when quests are completed."""
            self._on_quest_complete_callbacks.append(callback)

        def on_quest_fail(self, callback):
            """Register a callback for when quests fail."""
            self._on_quest_fail_callbacks.append(callback)

# =============================================================================
# GLOBAL QUEST MANAGER INSTANCE
# =============================================================================

default quest_manager = QuestManager()

# =============================================================================
# SELECTED QUEST FOR UI
# =============================================================================

default selected_quest_id = None

# =============================================================================
# EXAMPLE QUEST DEFINITIONS
# =============================================================================

init python:
    def setup_example_quests():
        """Initialize example quests for the quest system."""

        # Main Quest 1: The Beginning
        main_quest_1 = Quest(
            id="main_01_beginning",
            name="The Beginning",
            description="Start your journey by meeting with the village elder and learning about the ancient prophecy.",
            category=QUEST_CATEGORY_MAIN,
            rewards=QuestRewards(gold=50, xp=100)
        )
        main_quest_1.add_objective("Speak with the village elder")
        main_quest_1.add_objective("Listen to the prophecy")
        main_quest_1.add_objective("Decide your path")
        main_quest_1.add_objective("Explore the old ruins", optional=True)

        # Main Quest 2: Gathering Allies
        main_quest_2 = Quest(
            id="main_02_allies",
            name="Gathering Allies",
            description="You cannot face this challenge alone. Find companions who will join your cause.",
            category=QUEST_CATEGORY_MAIN,
            rewards=QuestRewards(gold=100, xp=200, items=["companion_token"])
        )
        main_quest_2.add_objective("Meet Elena at the tavern")
        main_quest_2.add_objective("Help Elena with her problem")
        main_quest_2.add_objective("Convince Elena to join you")
        main_quest_2.add_objective("Find Marcus at the market", optional=True)

        # Side Quest 1: Lost Heirloom
        side_quest_1 = Quest(
            id="side_01_heirloom",
            name="Lost Heirloom",
            description="A villager has lost a precious family heirloom in the forest. Help them find it.",
            category=QUEST_CATEGORY_SIDE,
            rewards=QuestRewards(gold=25, xp=50, items=["minor_potion"])
        )
        side_quest_1.add_objective("Search the forest clearing")
        side_quest_1.add_objective("Return the heirloom to the villager")

        # Side Quest 2: Merchant's Request
        side_quest_2 = Quest(
            id="side_02_merchant",
            name="Merchant's Request",
            description="The local merchant needs rare herbs for their potions. Gather them from the mountain.",
            category=QUEST_CATEGORY_SIDE,
            rewards=QuestRewards(gold=40, xp=75, items=["herb_bundle", "discount_voucher"])
        )
        side_quest_2.add_objective("Travel to the mountain")
        side_quest_2.add_objective("Collect moonflowers (0/5)")
        side_quest_2.add_objective("Collect starleaf herbs (0/3)")
        side_quest_2.add_objective("Return to the merchant")
        side_quest_2.add_objective("Find the rare glowmoss", optional=True)

        # Add quests to manager
        quest_manager.add_quest(main_quest_1)
        quest_manager.add_quest(main_quest_2)
        quest_manager.add_quest(side_quest_1)
        quest_manager.add_quest(side_quest_2)

        # Start the first main quest automatically
        quest_manager.start_quest("main_01_beginning")

# =============================================================================
# QUEST LOG SCREEN UI
# =============================================================================

screen quest_log_screen():
    tag menu

    default current_category = "all"

    frame:
        xfill True
        yfill True
        background "#1a1a1a"
        padding (40, 40)

        vbox:
            spacing 20
            xfill True
            yfill True

            # Title bar with close button
            hbox:
                xfill True
                text _("Quest Log") size 36 color "#ffffff"
                textbutton _("Return") action Return() align (1.0, 0.5)

            style_prefix "quest_log"

            hbox:
                spacing 20
                xfill True
                yfill True

                # Left panel: Quest list
                frame:
                    xsize 350
                    yfill True
                    background "#2a2a2a"
                    padding (15, 15)

                    vbox:
                        spacing 10

                        # Category tabs
                        hbox:
                            spacing 5
                            xfill True

                            textbutton "All" action SetScreenVariable("current_category", "all"):
                                style "quest_tab_button"
                                selected current_category == "all"

                            textbutton "Main" action SetScreenVariable("current_category", "main"):
                                style "quest_tab_button"
                                selected current_category == "main"

                            textbutton "Side" action SetScreenVariable("current_category", "side"):
                                style "quest_tab_button"
                                selected current_category == "side"

                        null height 10

                        # Quest list with scrolling
                        viewport:
                            scrollbars "vertical"
                            mousewheel True
                            yfill True
                            xfill True

                            vbox:
                                spacing 5

                                # Active quests section
                                if current_category == "all" or current_category == "main":
                                    for quest in quest_manager.get_active_main_quests():
                                        use quest_list_item(quest)

                                if current_category == "all" or current_category == "side":
                                    for quest in quest_manager.get_active_side_quests():
                                        use quest_list_item(quest)

                                # Available quests section
                                $ available = quest_manager.get_available_quests()
                                if available:
                                    null height 15
                                    text "Available" size 14 color "#888888"
                                    null height 5

                                    for quest in available:
                                        if current_category == "all" or quest.category == current_category:
                                            use quest_list_item(quest)

                                # Completed quests section
                                $ completed = quest_manager.get_completed_quests()
                                if completed:
                                    null height 15
                                    text "Completed" size 14 color "#888888"
                                    null height 5

                                    for quest in completed:
                                        if current_category == "all" or quest.category == current_category:
                                            use quest_list_item(quest)

                                # Failed quests section
                                $ failed = quest_manager.get_failed_quests()
                                if failed:
                                    null height 15
                                    text "Failed" size 14 color "#888888"
                                    null height 5

                                    for quest in failed:
                                        if current_category == "all" or quest.category == current_category:
                                            use quest_list_item(quest)

                # Right panel: Quest details
                frame:
                    xfill True
                    yfill True
                    background "#333333"
                    padding (20, 20)

                    if selected_quest_id:
                        $ quest = quest_manager.get_quest(selected_quest_id)
                        if quest:
                            use quest_detail_view(quest)
                        else:
                            text "Quest not found" align (0.5, 0.5) color "#666666"
                    else:
                        text "Select a quest to view details" align (0.5, 0.5) color "#666666"

# Quest list item component
screen quest_list_item(quest):
    button:
        action SetVariable("selected_quest_id", quest.id)
        xfill True
        padding (10, 8)

        if selected_quest_id == quest.id:
            background "#4a4a6a"
        else:
            background "#3a3a3a"
            hover_background "#454545"

        hbox:
            spacing 10
            xfill True

            # Status indicator
            frame:
                xysize (12, 12)
                yalign 0.5
                if quest.is_completed():
                    background "#00cc00"
                elif quest.is_active():
                    background "#ffcc00"
                elif quest.is_failed():
                    background "#cc0000"
                else:
                    background "#666666"

            # Category indicator
            $ cat_text = "[" + ("M" if quest.is_main_quest() else "S") + "]"
            $ cat_color = "#ffaa00" if quest.is_main_quest() else "#888888"
            text cat_text:
                size 12
                color cat_color
                yalign 0.5

            # Quest name
            $ name_color = "#ffffff" if quest.is_active() else "#aaaaaa"
            text quest.name:
                size 16
                color name_color
                yalign 0.5

# Quest detail view component
screen quest_detail_view(quest):
    viewport:
        scrollbars "vertical"
        mousewheel True
        xfill True
        yfill True

        vbox:
            spacing 15
            xfill True

            # Quest header
            hbox:
                spacing 15

                # Category badge
                frame:
                    padding (8, 4)
                    if quest.is_main_quest():
                        background "#cc8800"
                        text "MAIN QUEST" size 12 color "#ffffff"
                    else:
                        background "#555555"
                        text "SIDE QUEST" size 12 color "#ffffff"

                # Status badge
                frame:
                    padding (8, 4)
                    if quest.is_completed():
                        background "#006600"
                        text "COMPLETED" size 12 color "#ffffff"
                    elif quest.is_active():
                        background "#005588"
                        text "ACTIVE" size 12 color "#ffffff"
                    elif quest.is_failed():
                        background "#880000"
                        text "FAILED" size 12 color "#ffffff"
                    else:
                        background "#444444"
                        text "AVAILABLE" size 12 color "#ffffff"

            # Quest name
            text quest.name size 28 color "#ffffff"

            # Quest description
            text quest.description size 16 color "#cccccc"

            null height 10

            # Objectives section
            if quest.objectives:
                text "Objectives" size 20 color "#ffffff"

                null height 5

                for i, obj in enumerate(quest.objectives):
                    hbox:
                        spacing 10
                        xfill True

                        # Checkbox
                        frame:
                            xysize (20, 20)
                            yalign 0.0
                            background "#444444"
                            if obj.completed:
                                text "X" align (0.5, 0.5) size 14 color "#00cc00"

                        # Objective text
                        vbox:
                            $ obj_color = "#00cc00" if obj.completed else "#ffffff"
                            if obj.optional:
                                text "(Optional) " + obj.description:
                                    size 15
                                    color obj_color
                                    strikethrough obj.completed
                            else:
                                text obj.description:
                                    size 15
                                    color obj_color
                                    strikethrough obj.completed

                # Progress bar
                $ completed_count, total_count, percentage = quest.get_progress()
                null height 10

                hbox:
                    spacing 10
                    text "Progress:" size 14 color "#888888"
                    bar value percentage range 100 xsize 200 left_bar "#00cc00" right_bar "#444444"
                    text "[completed_count]/[total_count]" size 14 color "#888888"

            null height 15

            # Rewards section
            if quest.rewards and quest.rewards.has_rewards():
                text "Rewards" size 20 color "#ffffff"

                null height 5

                hbox:
                    spacing 20

                    if quest.rewards.gold > 0:
                        hbox:
                            spacing 5
                            text "Gold:" size 14 color "#ffcc00"
                            text str(quest.rewards.gold) size 14 color "#ffffff"

                    if quest.rewards.xp > 0:
                        hbox:
                            spacing 5
                            text "XP:" size 14 color "#66ccff"
                            text str(quest.rewards.xp) size 14 color "#ffffff"

                if quest.rewards.items:
                    null height 5
                    hbox:
                        spacing 5
                        text "Items:" size 14 color "#cc66ff"
                        $ items_str = ", ".join(str(item) for item in quest.rewards.items)
                        text items_str size 14 color "#ffffff"

# =============================================================================
# STYLES FOR QUEST LOG SCREEN
# =============================================================================

style quest_log_hbox:
    spacing 20

style quest_log_frame:
    background "#2a2a2a"
    padding (15, 15)

style quest_tab_button:
    padding (10, 5)
    background "#3a3a3a"
    hover_background "#4a4a4a"
    selected_background "#5a5a8a"

style quest_tab_button_text:
    size 14
    color "#aaaaaa"
    hover_color "#ffffff"
    selected_color "#ffffff"

# =============================================================================
# HELPER LABELS FOR QUEST MANAGEMENT
# =============================================================================

# Start a quest with notification
label start_quest(quest_id, notify=True):
    $ success = quest_manager.start_quest(quest_id)
    if notify and success:
        $ quest = quest_manager.get_quest(quest_id)
        $ renpy.notify("Quest Started: " + quest.name)
    return

# Complete a quest with notification
label complete_quest(quest_id, notify=True):
    $ rewards = quest_manager.complete_quest(quest_id)
    if notify and rewards:
        $ quest = quest_manager.get_quest(quest_id)
        $ renpy.notify("Quest Completed: " + quest.name)
        if rewards.gold > 0:
            $ renpy.notify("Received " + str(rewards.gold) + " gold")
        if rewards.xp > 0:
            $ renpy.notify("Received " + str(rewards.xp) + " XP")
    return

# Fail a quest with notification
label fail_quest(quest_id, notify=True):
    $ success = quest_manager.fail_quest(quest_id)
    if notify and success:
        $ quest = quest_manager.get_quest(quest_id)
        $ renpy.notify("Quest Failed: " + quest.name)
    return

# Complete an objective with notification
label complete_objective(quest_id, objective_index, notify=True):
    $ success = quest_manager.complete_objective(quest_id, objective_index)
    if notify and success:
        $ quest = quest_manager.get_quest(quest_id)
        $ obj = quest.objectives[objective_index]
        $ renpy.notify("Objective Complete: " + obj.description)
    return

# =============================================================================
# EXAMPLE USAGE IN GAME SCRIPT
# =============================================================================

# Example label showing quest system usage:
#
# label start_game:
#     call setup_example_quests
#
#     "Your adventure begins..."
#     call start_quest("main_01_beginning")
#
#     "You meet the village elder."
#     call complete_objective("main_01_beginning", 0)
#
#     "The elder tells you about the prophecy."
#     call complete_objective("main_01_beginning", 1)
#
#     menu:
#         "Choose the path of light":
#             call complete_objective("main_01_beginning", 2)
#             $ quest_manager.check_quest_completable("main_01_beginning")
#             call complete_quest("main_01_beginning")
#         "Choose the path of shadow":
#             call complete_objective("main_01_beginning", 2)
#             call complete_quest("main_01_beginning")
#
#     # Open quest log:
#     call screen quest_log_screen
#
#     return

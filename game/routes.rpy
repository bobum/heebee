# Character Route System for Ren'Py Visual Novel
# This module provides a comprehensive route management system with
# route requirements, lock-in mechanics, compatibility checks, and route-specific content.

init python:

    # =========================================================================
    # ROUTE CLASS - Represents a character route/path
    # =========================================================================

    class Route:
        """
        Represents a character route in the visual novel.

        Attributes:
            id (str): Unique identifier for the route
            character_name (str): Display name of the character for this route
            description (str): Description of the route
            locked_in (bool): Whether the player is locked into this route
            requirements (dict): Relationship thresholds needed to access the route
                Format: {"affection": int, "trust": int, "respect": int}
            incompatible_routes (list): List of route IDs that cannot be accessed if this is locked
            content_flags (set): Set of content flags enabled for this route
            icon (str): Path to route icon image
            priority (int): Priority for display ordering (lower = higher priority)
        """

        def __init__(self, id, character_name, description="",
                     requirements=None, incompatible_routes=None,
                     icon=None, priority=100):
            self.id = id
            self.character_name = character_name
            self.description = description
            self.locked_in = False
            self.requirements = requirements or {"affection": 0, "trust": 0, "respect": 0}
            self.incompatible_routes = incompatible_routes or []
            self.content_flags = set()
            self.icon = icon
            self.priority = priority
            self._lock_in_point = None  # Label where lock-in occurred

        def set_requirement(self, stat, value):
            """Set a specific requirement threshold."""
            if stat in ["affection", "trust", "respect"]:
                self.requirements[stat] = value

        def add_incompatible_route(self, route_id):
            """Add a route that becomes incompatible when this is locked."""
            if route_id not in self.incompatible_routes:
                self.incompatible_routes.append(route_id)

        def remove_incompatible_route(self, route_id):
            """Remove a route from the incompatible list."""
            if route_id in self.incompatible_routes:
                self.incompatible_routes.remove(route_id)

        def add_content_flag(self, flag):
            """Add a content flag for route-specific content."""
            self.content_flags.add(flag)

        def remove_content_flag(self, flag):
            """Remove a content flag."""
            self.content_flags.discard(flag)

        def has_content_flag(self, flag):
            """Check if a content flag is set."""
            return flag in self.content_flags

        def lock(self, lock_point=None):
            """Lock into this route."""
            self.locked_in = True
            self._lock_in_point = lock_point

        def unlock(self):
            """Unlock from this route (for debugging/special cases)."""
            self.locked_in = False
            self._lock_in_point = None

        def get_lock_point(self):
            """Get the label/point where lock-in occurred."""
            return self._lock_in_point

        def __repr__(self):
            return f"Route(id='{self.id}', character='{self.character_name}', locked_in={self.locked_in})"


    # =========================================================================
    # ROUTE MANAGER CLASS - Central manager for all routes
    # =========================================================================

    class RouteManager:
        """
        Central manager for handling character routes.

        This class provides methods to register routes, check availability,
        lock into routes, and manage route-specific content.
        """

        def __init__(self):
            self.routes = {}
            self._current_route = None
            self._route_history = []
            self._available_routes_cache = None
            self._cache_valid = False

        # ---------------------------------------------------------------------
        # Route Registration
        # ---------------------------------------------------------------------

        def register_route(self, route):
            """
            Register a route with the manager.

            Args:
                route (Route): The route to register

            Returns:
                Route: The registered route
            """
            self.routes[route.id] = route
            self._invalidate_cache()
            return route

        def unregister_route(self, route_id):
            """
            Remove a route from the manager.

            Args:
                route_id (str): ID of the route to remove

            Returns:
                bool: True if route was removed, False if not found
            """
            if route_id in self.routes:
                del self.routes[route_id]
                self._invalidate_cache()
                return True
            return False

        def get_route(self, route_id):
            """
            Get a route by its ID.

            Args:
                route_id (str): ID of the route

            Returns:
                Route or None: The route if found, None otherwise
            """
            return self.routes.get(route_id)

        def get_all_routes(self):
            """Get list of all registered routes, sorted by priority."""
            return sorted(self.routes.values(), key=lambda r: r.priority)

        # ---------------------------------------------------------------------
        # Route Availability Checking
        # ---------------------------------------------------------------------

        def check_requirements(self, route_id, relationship_manager):
            """
            Check if route requirements are met based on character relationships.

            Args:
                route_id (str): ID of the route to check
                relationship_manager: The RelationshipManager instance

            Returns:
                bool: True if all requirements are met
            """
            route = self.get_route(route_id)
            if not route:
                return False

            # Get the character associated with this route
            char = relationship_manager.get_character(route_id)
            if not char:
                # Try to find by matching character name or use route_id as char_id
                return False

            # Check each requirement
            reqs = route.requirements
            if char.affection < reqs.get("affection", 0):
                return False
            if char.trust < reqs.get("trust", 0):
                return False
            if char.respect < reqs.get("respect", 0):
                return False

            return True

        def check_requirements_with_char(self, route_id, character):
            """
            Check if route requirements are met with a character object directly.

            Args:
                route_id (str): ID of the route to check
                character: Character object with affection, trust, respect attributes

            Returns:
                bool: True if all requirements are met
            """
            route = self.get_route(route_id)
            if not route or not character:
                return False

            reqs = route.requirements
            if character.affection < reqs.get("affection", 0):
                return False
            if character.trust < reqs.get("trust", 0):
                return False
            if character.respect < reqs.get("respect", 0):
                return False

            return True

        def is_route_available(self, route_id, relationship_manager):
            """
            Check if a route is available (requirements met and not blocked).

            Args:
                route_id (str): ID of the route to check
                relationship_manager: The RelationshipManager instance

            Returns:
                bool: True if route is available
            """
            route = self.get_route(route_id)
            if not route:
                return False

            # If already locked into a different route, check compatibility
            if self._current_route and self._current_route != route_id:
                current = self.get_route(self._current_route)
                if current and route_id in current.incompatible_routes:
                    return False

            # Check if this route is blocked by any locked incompatible route
            for other_id, other_route in self.routes.items():
                if other_route.locked_in and route_id in other_route.incompatible_routes:
                    return False

            return self.check_requirements(route_id, relationship_manager)

        def get_available_routes(self, relationship_manager):
            """
            Get list of all currently available routes.

            Args:
                relationship_manager: The RelationshipManager instance

            Returns:
                list: List of available Route objects
            """
            available = []
            for route_id in self.routes:
                if self.is_route_available(route_id, relationship_manager):
                    available.append(self.routes[route_id])
            return sorted(available, key=lambda r: r.priority)

        # ---------------------------------------------------------------------
        # Route Lock-In
        # ---------------------------------------------------------------------

        def lock_into_route(self, route_id, lock_point=None):
            """
            Lock the player into a specific route.

            Args:
                route_id (str): ID of the route to lock into
                lock_point (str): Optional label/identifier for where lock occurred

            Returns:
                bool: True if successfully locked in
            """
            route = self.get_route(route_id)
            if not route:
                return False

            # Lock the route
            route.lock(lock_point)
            self._current_route = route_id
            self._route_history.append({
                "route_id": route_id,
                "lock_point": lock_point,
                "action": "locked_in"
            })
            self._invalidate_cache()

            # Add default content flags for locked routes
            route.add_content_flag(f"route_{route_id}_locked")
            route.add_content_flag(f"route_{route_id}_content")

            return True

        def unlock_route(self, route_id):
            """
            Unlock a route (for debugging or special game mechanics).

            Args:
                route_id (str): ID of the route to unlock

            Returns:
                bool: True if successfully unlocked
            """
            route = self.get_route(route_id)
            if not route:
                return False

            route.unlock()
            if self._current_route == route_id:
                self._current_route = None
            self._invalidate_cache()

            # Remove lock-specific flags
            route.remove_content_flag(f"route_{route_id}_locked")

            return True

        # ---------------------------------------------------------------------
        # Current Route Management
        # ---------------------------------------------------------------------

        def get_current_route(self):
            """
            Get the currently locked route.

            Returns:
                Route or None: The current route if locked in, None otherwise
            """
            if self._current_route:
                return self.get_route(self._current_route)
            return None

        def get_current_route_id(self):
            """Get the ID of the currently locked route."""
            return self._current_route

        def is_locked_in(self):
            """Check if player is locked into any route."""
            return self._current_route is not None

        def get_route_history(self):
            """Get the history of route changes."""
            return list(self._route_history)

        # ---------------------------------------------------------------------
        # Route Compatibility
        # ---------------------------------------------------------------------

        def check_compatibility(self, route_id_a, route_id_b):
            """
            Check if two routes are compatible (can both be accessed).

            Args:
                route_id_a (str): First route ID
                route_id_b (str): Second route ID

            Returns:
                bool: True if routes are compatible
            """
            route_a = self.get_route(route_id_a)
            route_b = self.get_route(route_id_b)

            if not route_a or not route_b:
                return False

            # Check if either route blocks the other
            if route_id_b in route_a.incompatible_routes:
                return False
            if route_id_a in route_b.incompatible_routes:
                return False

            return True

        def get_blocked_routes(self, route_id=None):
            """
            Get list of routes that are currently blocked.

            Args:
                route_id (str): Optional - if provided, get routes blocked by this route
                               If None, get all currently blocked routes

            Returns:
                list: List of blocked route IDs
            """
            blocked = set()

            if route_id:
                route = self.get_route(route_id)
                if route:
                    blocked.update(route.incompatible_routes)
            else:
                # Get all blocked routes from locked routes
                for r_id, route in self.routes.items():
                    if route.locked_in:
                        blocked.update(route.incompatible_routes)

            return list(blocked)

        # ---------------------------------------------------------------------
        # Content Flags
        # ---------------------------------------------------------------------

        def has_route_flag(self, flag):
            """
            Check if any locked route has a specific content flag.

            Args:
                flag (str): The content flag to check

            Returns:
                bool: True if the flag is set on any locked route
            """
            for route in self.routes.values():
                if route.locked_in and route.has_content_flag(flag):
                    return True
            return False

        def get_active_content_flags(self):
            """
            Get all active content flags from locked routes.

            Returns:
                set: Set of all active content flags
            """
            flags = set()
            for route in self.routes.values():
                if route.locked_in:
                    flags.update(route.content_flags)
            return flags

        def set_route_content_flag(self, route_id, flag):
            """
            Set a content flag on a specific route.

            Args:
                route_id (str): ID of the route
                flag (str): The content flag to set

            Returns:
                bool: True if flag was set
            """
            route = self.get_route(route_id)
            if route:
                route.add_content_flag(flag)
                return True
            return False

        # ---------------------------------------------------------------------
        # Utility Methods
        # ---------------------------------------------------------------------

        def reset(self):
            """Reset all routes to unlocked state."""
            for route in self.routes.values():
                route.unlock()
                route.content_flags.clear()
            self._current_route = None
            self._route_history.clear()
            self._invalidate_cache()

        def _invalidate_cache(self):
            """Invalidate the available routes cache."""
            self._cache_valid = False
            self._available_routes_cache = None

        def get_route_status(self, route_id, relationship_manager):
            """
            Get detailed status information for a route.

            Args:
                route_id (str): ID of the route
                relationship_manager: The RelationshipManager instance

            Returns:
                dict: Status information including availability, requirements met, etc.
            """
            route = self.get_route(route_id)
            if not route:
                return None

            status = {
                "id": route_id,
                "character_name": route.character_name,
                "locked_in": route.locked_in,
                "is_current": self._current_route == route_id,
                "available": self.is_route_available(route_id, relationship_manager),
                "requirements_met": self.check_requirements(route_id, relationship_manager),
                "blocked_by": [],
                "blocks": list(route.incompatible_routes),
                "content_flags": list(route.content_flags)
            }

            # Find what routes are blocking this one
            for other_id, other_route in self.routes.items():
                if other_route.locked_in and route_id in other_route.incompatible_routes:
                    status["blocked_by"].append(other_id)

            return status


# =============================================================================
# GLOBAL ROUTE MANAGER INSTANCE
# =============================================================================

default route_manager = RouteManager()


# =============================================================================
# EXAMPLE ROUTE DEFINITIONS
# =============================================================================

init python:
    def setup_example_routes():
        """Initialize example routes for the route system."""

        # Elena's Route - Adventurous romance
        elena_route = Route(
            id="elena",
            character_name="Elena Brightwood",
            description="A bold adventure awaits with the guild's rising star.",
            requirements={"affection": 60, "trust": 40, "respect": 30},
            incompatible_routes=["victoria"],  # Can't romance both nobles/commoners
            icon="images/routes/elena_icon.png",
            priority=1
        )

        # Marcus's Route - Merchant intrigue
        marcus_route = Route(
            id="marcus",
            character_name="Marcus Sterling",
            description="Discover the secrets of trade and the heart.",
            requirements={"affection": 50, "trust": 50, "respect": 40},
            incompatible_routes=[],
            icon="images/routes/marcus_icon.png",
            priority=2
        )

        # Victoria's Route - Noble politics
        victoria_route = Route(
            id="victoria",
            character_name="Lady Victoria Valdoria",
            description="Enter the world of nobility and forbidden love.",
            requirements={"affection": 70, "trust": 30, "respect": 60},
            incompatible_routes=["elena"],  # Can't romance both
            icon="images/routes/victoria_icon.png",
            priority=3
        )

        # Register routes
        route_manager.register_route(elena_route)
        route_manager.register_route(marcus_route)
        route_manager.register_route(victoria_route)


# =============================================================================
# ROUTE SYSTEM UI SCREENS
# =============================================================================

# -----------------------------------------------------------------------------
# Route Selection Screen - Shown when multiple routes are available
# -----------------------------------------------------------------------------

screen route_selection_screen(available_routes=None):
    # Screen for selecting a route when multiple are available.

    modal True
    zorder 200

    default selected_route = None

    # Semi-transparent background
    add Solid("#000000bb")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 800
        padding (40, 40)
        background "#1a1a2e"

        vbox:
            spacing 25
            xfill True

            # Title
            text "Choose Your Path" xalign 0.5 size 42 color "#ffffff"

            null height 10

            text "Your relationships have opened multiple paths forward." xalign 0.5 size 20 color "#aaaaaa"
            text "Choose wisely - this decision may close other doors." xalign 0.5 size 18 color "#888888"

            null height 20

            # Route options
            if available_routes:
                for route in available_routes:
                    $ route_bg = "#2a2a4e" if selected_route != route.id else "#4a4a8e"
                    button:
                        xfill True
                        padding (20, 15)
                        background route_bg
                        hover_background "#3a3a6e"
                        action SetScreenVariable("selected_route", route.id)

                        hbox:
                            spacing 20

                            # Route icon placeholder
                            frame:
                                xysize (60, 60)
                                background "#444466"
                                if route.icon:
                                    add route.icon fit "contain"
                                else:
                                    text route.character_name[0] align (0.5, 0.5) size 30 color "#ffffff"

                            vbox:
                                spacing 5
                                xfill True

                                text route.character_name size 24 color "#ffffff"
                                text route.description size 16 color "#aaaaaa"

                                # Show incompatibilities warning
                                if route.incompatible_routes:
                                    $ blocked_names = []
                                    python:
                                        for blocked_id in route.incompatible_routes:
                                            blocked_route = route_manager.get_route(blocked_id)
                                            if blocked_route:
                                                blocked_names.append(blocked_route.character_name)
                                    if blocked_names:
                                        $ warning_text = "Blocks: " + ", ".join(blocked_names)
                                        text warning_text size 14 color "#ff6666"

            null height 20

            # Action buttons
            hbox:
                xalign 0.5
                spacing 30

                textbutton "Cancel":
                    padding (30, 10)
                    background "#444444"
                    hover_background "#555555"
                    action Return(None)

                $ confirm_bg = "#2255aa" if selected_route else "#333333"
                $ confirm_hover = "#3366cc" if selected_route else "#333333"
                textbutton "Confirm Selection":
                    padding (30, 10)
                    background confirm_bg
                    hover_background confirm_hover
                    sensitive selected_route is not None
                    action Return(selected_route)


# -----------------------------------------------------------------------------
# Route Indicator Screen - Shows current route status
# -----------------------------------------------------------------------------

screen route_indicator():
    # Persistent indicator showing current route status.

    zorder 50

    if route_manager.is_locked_in():
        $ current = route_manager.get_current_route()

        frame:
            xalign 1.0
            yalign 0.0
            xoffset -10
            yoffset 10
            padding (15, 8)
            background "#2a2a4ecc"

            hbox:
                spacing 10

                # Route icon
                if current.icon:
                    add current.icon xysize (24, 24)
                else:
                    frame:
                        xysize (24, 24)
                        background "#4a4a8e"
                        text current.character_name[0] align (0.5, 0.5) size 14 color "#ffffff"

                vbox:
                    spacing 2
                    text current.character_name size 16 color "#ffffff"
                    text "Route Active" size 12 color "#66aaff"


# -----------------------------------------------------------------------------
# Route Lock-In Confirmation Screen
# -----------------------------------------------------------------------------

screen route_lockin_confirmation(route_id):
    # Confirmation screen before locking into a route.

    modal True
    zorder 200

    $ route = route_manager.get_route(route_id)

    # Semi-transparent background
    add Solid("#000000cc")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 700
        padding (40, 40)
        background "#1a1a2e"

        if route:
            vbox:
                spacing 20
                xfill True

                # Warning icon/header
                text "Point of No Return" xalign 0.5 size 36 color "#ffcc00"

                null height 10

                # Route info
                hbox:
                    xalign 0.5
                    spacing 20

                    frame:
                        xysize (80, 80)
                        background "#444466"
                        if route.icon:
                            add route.icon fit "contain"
                        else:
                            text route.character_name[0] align (0.5, 0.5) size 40 color "#ffffff"

                    vbox:
                        spacing 5
                        text route.character_name size 28 color "#ffffff"
                        text route.description size 16 color "#aaaaaa"

                null height 10

                # Warning message
                frame:
                    xfill True
                    padding (20, 15)
                    background "#332222"

                    vbox:
                        spacing 10

                        text "Are you sure you want to commit to this path?" xalign 0.5 size 18 color "#ffffff"

                        if route.incompatible_routes:
                            $ blocked_names = []
                            python:
                                for blocked_id in route.incompatible_routes:
                                    blocked_route = route_manager.get_route(blocked_id)
                                    if blocked_route:
                                        blocked_names.append(blocked_route.character_name)
                            if blocked_names:
                                $ warning = "This will permanently close the following paths: " + ", ".join(blocked_names)
                                text warning xalign 0.5 size 16 color "#ff6666"

                null height 20

                # Confirmation buttons
                hbox:
                    xalign 0.5
                    spacing 40

                    textbutton "Go Back":
                        padding (40, 12)
                        background "#444444"
                        hover_background "#555555"
                        action Return(False)

                    textbutton "Commit to [route.character_name]":
                        padding (40, 12)
                        background "#aa3333"
                        hover_background "#cc4444"
                        action Return(True)

        else:
            text "Route not found!" xalign 0.5 color "#ff0000"
            textbutton "Close" xalign 0.5 action Return(False)


# -----------------------------------------------------------------------------
# Route Status Screen - Shows all routes and their status
# -----------------------------------------------------------------------------

screen route_status_screen():
    # Full screen showing all routes and their current status.

    tag menu
    modal True

    frame:
        xfill True
        yfill True
        background "#1a1a2e"
        padding (40, 40)

        vbox:
            spacing 15

            # Header with title and close button
            hbox:
                xfill True
                text "Routes" size 36 color "#aaaaff"
                textbutton "Return" action Return() xalign 1.0

            style_prefix "route_status"

            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True
                ysize 500

                vbox:
                    spacing 20

                    # Current route section
                    if route_manager.is_locked_in():
                        $ current = route_manager.get_current_route()

                        text "Current Route" size 32 color "#66aaff"

                        frame:
                            xfill True
                            padding (25, 20)
                            background "#2a4a2a"

                            hbox:
                                spacing 20

                                frame:
                                    xysize (80, 80)
                                    background "#3a6a3a"
                                    if current.icon:
                                        add current.icon fit "contain"
                                    else:
                                        text current.character_name[0] align (0.5, 0.5) size 40 color "#ffffff"

                                vbox:
                                    spacing 8
                                    text current.character_name size 26 color "#ffffff"
                                    text current.description size 16 color "#aaddaa"
                                    text "Locked In" size 14 color "#88ff88"

                        null height 20

                    # Available routes section
                    text "All Routes" size 32 color "#ffffff"

                    null height 10

                    for route in route_manager.get_all_routes():
                        $ is_current = route_manager.get_current_route_id() == route.id
                        $ is_blocked = route.id in route_manager.get_blocked_routes()

                        if is_current:
                            $ frame_bg = "#2a4a2a"
                        elif is_blocked:
                            $ frame_bg = "#4a2a2a"
                        elif route.locked_in:
                            $ frame_bg = "#2a2a4a"
                        else:
                            $ frame_bg = "#333333"

                        frame:
                            xfill True
                            padding (20, 15)
                            background frame_bg

                            hbox:
                                spacing 20

                                # Route icon
                                $ icon_bg = "#553333" if is_blocked else "#555555"
                                frame:
                                    xysize (60, 60)
                                    background icon_bg

                                    if route.icon:
                                        add route.icon fit "contain"
                                    else:
                                        text route.character_name[0] align (0.5, 0.5) size 30 color "#ffffff"

                                vbox:
                                    spacing 5
                                    xfill True

                                    # Name and status
                                    hbox:
                                        text route.character_name size 22 color "#ffffff"
                                        null width 15

                                        if is_current:
                                            text "[ACTIVE]" size 16 color "#88ff88"
                                        elif is_blocked:
                                            text "[BLOCKED]" size 16 color "#ff6666"
                                        elif route.locked_in:
                                            text "[LOCKED]" size 16 color "#6688ff"

                                    text route.description size 15 color "#aaaaaa"

                                    # Requirements display
                                    $ reqs = route.requirements
                                    hbox:
                                        spacing 15
                                        text "Required:" size 13 color "#888888"
                                        text "Affection: [reqs['affection']]" size 13 color "#ff6699"
                                        text "Trust: [reqs['trust']]" size 13 color "#66ccff"
                                        text "Respect: [reqs['respect']]" size 13 color "#ffcc66"


# =============================================================================
# STYLES FOR ROUTE SCREENS
# =============================================================================

style route_status_vbox:
    xfill True
    spacing 10

style route_status_text:
    color "#ffffff"


# =============================================================================
# HELPER LABELS FOR ROUTE MANAGEMENT
# =============================================================================

# Show route selection and return chosen route
label show_route_selection():
    $ available = route_manager.get_available_routes(relationship_manager)
    if len(available) > 1:
        call screen route_selection_screen(available)
        $ selected = _return
        if selected:
            return selected
    elif len(available) == 1:
        $ selected = available[0].id
        return selected
    return None

# Lock into a route with confirmation
label lock_into_route(route_id, skip_confirmation=False):
    if not skip_confirmation:
        call screen route_lockin_confirmation(route_id)
        $ confirmed = _return
        if not confirmed:
            return False

    $ success = route_manager.lock_into_route(route_id, renpy.get_return_stack()[-1] if renpy.get_return_stack() else "unknown")
    if success:
        $ route = route_manager.get_route(route_id)
        $ renpy.notify("Locked into [route.character_name]'s route!")
    return success

# Check if content should be shown based on route
label check_route_content(route_id=None, flag=None):
    # Check if route-specific content should be shown.
    #
    # Usage:
    #     call check_route_content("elena")  # Check if on Elena's route
    #     call check_route_content(flag="romance_scene")  # Check for flag
    if route_id:
        $ result = route_manager.get_current_route_id() == route_id
        return result
    if flag:
        $ result = route_manager.has_route_flag(flag)
        return result
    return False


# =============================================================================
# INITIALIZATION
# =============================================================================

# Initialize example routes when appropriate
# Note: Call setup_example_routes() from your main after_load or splashscreen label
label routes_init:
    if not route_manager.routes:
        $ setup_example_routes()
    return


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

# Example usage in game script:
#
# label chapter_3_decision:
#     "A crucial moment approaches..."
#
#     # Check if player qualifies for any routes
#     $ available_routes = route_manager.get_available_routes(relationship_manager)
#
#     if len(available_routes) == 0:
#         "You haven't built strong enough bonds with anyone yet."
#         jump bad_ending
#
#     elif len(available_routes) == 1:
#         $ chosen_route = available_routes[0].id
#         "Your bond with [available_routes[0].character_name] has grown strong."
#         call lock_into_route(chosen_route)
#
#     else:
#         "Multiple paths are open to you..."
#         call show_route_selection
#         $ chosen_route = _return
#         if chosen_route:
#             call lock_into_route(chosen_route)
#
#     # Later, show route-specific content
#     if route_manager.get_current_route_id() == "elena":
#         jump elena_chapter_4
#     elif route_manager.get_current_route_id() == "marcus":
#         jump marcus_chapter_4
#     # etc.
#
# To show the route indicator during gameplay:
#     show screen route_indicator
#
# To view all route statuses:
#     call screen route_status_screen

# mods.rpy
# Mod Support Framework for Heebee Visual Novel
# Provides discovery, loading, and management of game mods

init python:
    import json
    import os

    class Mod:
        """
        Represents a single mod with its metadata and state.

        Attributes:
            id: Unique identifier for the mod
            name: Human-readable mod name
            version: Mod version string
            author: Mod author name
            description: Description of what the mod does
            enabled: Whether the mod is currently enabled
            path: Filesystem path to the mod directory
            dependencies: List of mod IDs this mod depends on
            conflicts: List of mod IDs this mod conflicts with
            priority: Load order priority (lower = loads first)
        """

        def __init__(self, id, name, version="1.0.0", author="Unknown",
                     description="", enabled=False, path=None,
                     dependencies=None, conflicts=None, priority=100):
            self.id = id
            self.name = name
            self.version = version
            self.author = author
            self.description = description
            self.enabled = enabled
            self.path = path
            self.dependencies = dependencies if dependencies is not None else []
            self.conflicts = conflicts if conflicts is not None else []
            self.priority = priority
            self._loaded = False
            self._error = None

        def __repr__(self):
            return f"Mod(id={self.id!r}, name={self.name!r}, version={self.version!r}, enabled={self.enabled})"

        def __eq__(self, other):
            if not isinstance(other, Mod):
                return False
            return self.id == other.id

        def __hash__(self):
            return hash(self.id)

        @classmethod
        def from_manifest(cls, manifest_path):
            """
            Create a Mod instance from a mod.json manifest file.

            Args:
                manifest_path: Path to the mod.json file

            Returns:
                Mod instance or None if parsing fails
            """
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                mod_dir = os.path.dirname(manifest_path)

                return cls(
                    id=data.get('id', os.path.basename(mod_dir)),
                    name=data.get('name', os.path.basename(mod_dir)),
                    version=data.get('version', '1.0.0'),
                    author=data.get('author', 'Unknown'),
                    description=data.get('description', ''),
                    enabled=data.get('enabled', False),
                    path=mod_dir,
                    dependencies=data.get('dependencies', []),
                    conflicts=data.get('conflicts', []),
                    priority=data.get('priority', 100)
                )
            except (json.JSONDecodeError, IOError, KeyError) as e:
                return None

        def to_dict(self):
            """Convert mod to dictionary for serialization."""
            return {
                'id': self.id,
                'name': self.name,
                'version': self.version,
                'author': self.author,
                'description': self.description,
                'enabled': self.enabled,
                'path': self.path,
                'dependencies': self.dependencies,
                'conflicts': self.conflicts,
                'priority': self.priority
            }

        def validate(self):
            """
            Validate the mod's metadata.

            Returns:
                Tuple of (is_valid, error_message)
            """
            if not self.id:
                return False, "Mod ID is required"
            if not self.name:
                return False, "Mod name is required"
            if not isinstance(self.priority, (int, float)):
                return False, "Priority must be a number"
            return True, None


    class ModManager:
        """
        Manages mod discovery, loading, and state.

        Handles:
        - Discovering mods in the mods/ directory
        - Loading and unloading mods
        - Enabling and disabling mods
        - Managing load order
        - Detecting conflicts
        """

        def __init__(self, mods_directory=None):
            """
            Initialize the ModManager.

            Args:
                mods_directory: Path to the mods folder. Defaults to game/mods/
            """
            if mods_directory is None:
                # Default to game/mods directory
                game_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else config.gamedir
                self.mods_directory = os.path.join(game_dir, 'mods')
            else:
                self.mods_directory = mods_directory

            self._mods = {}  # id -> Mod
            self._load_order = []  # List of mod IDs in load order
            self._loaded_mods = set()  # Set of currently loaded mod IDs
            self._state_file = os.path.join(self.mods_directory, '.mod_state.json')

        @property
        def mods(self):
            """Get dictionary of all discovered mods."""
            return self._mods.copy()

        def discover_mods(self):
            """
            Scan the mods directory for available mods.

            Looks for mod.json manifest files in subdirectories.

            Returns:
                List of discovered Mod objects
            """
            self._mods.clear()

            if not os.path.exists(self.mods_directory):
                return []

            discovered = []

            for entry in os.listdir(self.mods_directory):
                mod_path = os.path.join(self.mods_directory, entry)

                if not os.path.isdir(mod_path):
                    continue

                # Skip hidden directories
                if entry.startswith('.'):
                    continue

                manifest_path = os.path.join(mod_path, 'mod.json')

                if os.path.exists(manifest_path):
                    mod = Mod.from_manifest(manifest_path)
                    if mod:
                        self._mods[mod.id] = mod
                        discovered.append(mod)
                else:
                    # Create a basic mod entry from directory name
                    mod = Mod(
                        id=entry,
                        name=entry,
                        path=mod_path
                    )
                    self._mods[mod.id] = mod
                    discovered.append(mod)

            # Restore saved state
            self._load_state()

            # Update load order
            self._update_load_order()

            return discovered

        def get_mod(self, mod_id):
            """
            Get a mod by its ID.

            Args:
                mod_id: The unique mod identifier

            Returns:
                Mod instance or None if not found
            """
            return self._mods.get(mod_id)

        def get_mod_list(self):
            """
            Get list of all mods sorted by load order.

            Returns:
                List of Mod objects in load order
            """
            return [self._mods[mid] for mid in self._load_order if mid in self._mods]

        def get_enabled_mods(self):
            """
            Get list of enabled mods in load order.

            Returns:
                List of enabled Mod objects
            """
            return [m for m in self.get_mod_list() if m.enabled]

        def enable_mod(self, mod_id):
            """
            Enable a mod.

            Args:
                mod_id: The mod ID to enable

            Returns:
                Tuple of (success, error_message)
            """
            mod = self._mods.get(mod_id)
            if not mod:
                return False, f"Mod '{mod_id}' not found"

            # Check for conflicts
            conflict_error = self._check_conflicts(mod)
            if conflict_error:
                return False, conflict_error

            # Check dependencies
            dep_error = self._check_dependencies(mod)
            if dep_error:
                return False, dep_error

            mod.enabled = True
            self._save_state()
            return True, None

        def disable_mod(self, mod_id):
            """
            Disable a mod.

            Args:
                mod_id: The mod ID to disable

            Returns:
                Tuple of (success, error_message)
            """
            mod = self._mods.get(mod_id)
            if not mod:
                return False, f"Mod '{mod_id}' not found"

            # Check if other enabled mods depend on this one
            for other_id, other_mod in self._mods.items():
                if other_mod.enabled and mod_id in other_mod.dependencies:
                    return False, f"Cannot disable: '{other_mod.name}' depends on this mod"

            mod.enabled = False
            self._save_state()
            return True, None

        def load_mod(self, mod_id):
            """
            Load a mod's content into the game.

            Args:
                mod_id: The mod ID to load

            Returns:
                Tuple of (success, error_message)
            """
            mod = self._mods.get(mod_id)
            if not mod:
                return False, f"Mod '{mod_id}' not found"

            if not mod.enabled:
                return False, f"Mod '{mod_id}' is not enabled"

            if mod_id in self._loaded_mods:
                return True, None  # Already loaded

            try:
                # Load the mod's init.rpy if it exists
                init_path = os.path.join(mod.path, 'init.rpy')
                if os.path.exists(init_path):
                    # In a real Ren'Py environment, this would use renpy.load_module
                    # For now, we just mark it as loaded
                    pass

                self._loaded_mods.add(mod_id)
                mod._loaded = True
                return True, None

            except Exception as e:
                mod._error = str(e)
                return False, f"Failed to load mod: {e}"

        def unload_mod(self, mod_id):
            """
            Unload a mod's content from the game.

            Note: Full unloading may require a game restart.

            Args:
                mod_id: The mod ID to unload

            Returns:
                Tuple of (success, error_message)
            """
            mod = self._mods.get(mod_id)
            if not mod:
                return False, f"Mod '{mod_id}' not found"

            if mod_id not in self._loaded_mods:
                return True, None  # Already unloaded

            # Mark as unloaded
            self._loaded_mods.discard(mod_id)
            mod._loaded = False

            return True, "Mod unloaded. Some changes may require restart."

        def load_enabled_mods(self):
            """
            Load all enabled mods in order.

            Returns:
                List of (mod_id, success, error) tuples
            """
            results = []
            for mod in self.get_enabled_mods():
                success, error = self.load_mod(mod.id)
                results.append((mod.id, success, error))
            return results

        def set_load_order(self, mod_ids):
            """
            Set the mod load order.

            Args:
                mod_ids: List of mod IDs in desired load order

            Returns:
                Tuple of (success, error_message)
            """
            # Validate all IDs exist
            for mid in mod_ids:
                if mid not in self._mods:
                    return False, f"Unknown mod ID: {mid}"

            # Ensure all mods are represented
            missing = set(self._mods.keys()) - set(mod_ids)
            if missing:
                # Add missing mods to end
                mod_ids = list(mod_ids) + list(missing)

            self._load_order = list(mod_ids)

            # Update priorities based on order
            for i, mid in enumerate(self._load_order):
                if mid in self._mods:
                    self._mods[mid].priority = i

            self._save_state()
            return True, None

        def move_mod_up(self, mod_id):
            """
            Move a mod earlier in the load order.

            Args:
                mod_id: The mod ID to move

            Returns:
                Tuple of (success, error_message)
            """
            if mod_id not in self._load_order:
                return False, f"Mod '{mod_id}' not found"

            idx = self._load_order.index(mod_id)
            if idx == 0:
                return True, None  # Already first

            self._load_order[idx], self._load_order[idx - 1] = \
                self._load_order[idx - 1], self._load_order[idx]

            self._update_priorities()
            self._save_state()
            return True, None

        def move_mod_down(self, mod_id):
            """
            Move a mod later in the load order.

            Args:
                mod_id: The mod ID to move

            Returns:
                Tuple of (success, error_message)
            """
            if mod_id not in self._load_order:
                return False, f"Mod '{mod_id}' not found"

            idx = self._load_order.index(mod_id)
            if idx >= len(self._load_order) - 1:
                return True, None  # Already last

            self._load_order[idx], self._load_order[idx + 1] = \
                self._load_order[idx + 1], self._load_order[idx]

            self._update_priorities()
            self._save_state()
            return True, None

        def detect_conflicts(self):
            """
            Detect conflicts between enabled mods.

            Returns:
                List of (mod1_id, mod2_id, reason) tuples describing conflicts
            """
            conflicts = []
            enabled = self.get_enabled_mods()

            for i, mod1 in enumerate(enabled):
                for mod2 in enabled[i + 1:]:
                    # Check explicit conflicts
                    if mod2.id in mod1.conflicts:
                        conflicts.append((mod1.id, mod2.id, f"'{mod1.name}' conflicts with '{mod2.name}'"))
                    elif mod1.id in mod2.conflicts:
                        conflicts.append((mod1.id, mod2.id, f"'{mod2.name}' conflicts with '{mod1.name}'"))

            return conflicts

        def _check_conflicts(self, mod):
            """Check if enabling a mod would cause conflicts."""
            for other_id, other_mod in self._mods.items():
                if not other_mod.enabled:
                    continue
                if other_id in mod.conflicts:
                    return f"Conflicts with enabled mod '{other_mod.name}'"
                if mod.id in other_mod.conflicts:
                    return f"Enabled mod '{other_mod.name}' conflicts with this mod"
            return None

        def _check_dependencies(self, mod):
            """Check if all dependencies are satisfied."""
            for dep_id in mod.dependencies:
                dep = self._mods.get(dep_id)
                if not dep:
                    return f"Missing dependency: '{dep_id}'"
                if not dep.enabled:
                    return f"Dependency '{dep.name}' is not enabled"
            return None

        def _update_load_order(self):
            """Update load order based on mod priorities."""
            # Sort by priority, then by name for stability
            sorted_mods = sorted(
                self._mods.values(),
                key=lambda m: (m.priority, m.name)
            )
            self._load_order = [m.id for m in sorted_mods]

        def _update_priorities(self):
            """Update mod priorities based on current load order."""
            for i, mid in enumerate(self._load_order):
                if mid in self._mods:
                    self._mods[mid].priority = i

        def _save_state(self):
            """Save mod enabled states and load order to disk."""
            state = {
                'enabled': {mid: mod.enabled for mid, mod in self._mods.items()},
                'load_order': self._load_order
            }
            try:
                os.makedirs(os.path.dirname(self._state_file), exist_ok=True)
                with open(self._state_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2)
            except IOError:
                pass  # Silently fail if we can't save state

        def _load_state(self):
            """Load saved mod states from disk."""
            if not os.path.exists(self._state_file):
                return

            try:
                with open(self._state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                # Restore enabled states
                enabled = state.get('enabled', {})
                for mid, is_enabled in enabled.items():
                    if mid in self._mods:
                        self._mods[mid].enabled = is_enabled

                # Restore load order
                saved_order = state.get('load_order', [])
                if saved_order:
                    # Only keep IDs that still exist
                    self._load_order = [mid for mid in saved_order if mid in self._mods]
                    # Add any new mods not in saved order
                    for mid in self._mods:
                        if mid not in self._load_order:
                            self._load_order.append(mid)
                    # Update priorities to match restored load order
                    for i, mid in enumerate(self._load_order):
                        if mid in self._mods:
                            self._mods[mid].priority = i

            except (json.JSONDecodeError, IOError):
                pass  # Use defaults if state file is invalid


# Global mod manager instance
default mod_manager = None

init python:
    # Initialize mod manager after game initialization
    def init_mod_manager():
        global mod_manager
        if mod_manager is None:
            mod_manager = ModManager()
            mod_manager.discover_mods()


# ============================================================================
# MOD MANAGER UI SCREENS
# ============================================================================

screen mod_manager():
    """Main mod manager screen."""
    tag menu
    modal True

    add Solid("#1a1a2e")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 900
        ysize 600
        padding (20, 20, 20, 20)
        background Solid("#2a2a4e")

        vbox:
            spacing 15

            # Header
            hbox:
                xfill True
                text "Mod Manager" size 32 color "#66aaff"
                textbutton "X" action Hide("mod_manager") xalign 1.0 text_size 24

            # Mod count info
            python:
                if mod_manager:
                    total_mods = len(mod_manager.mods)
                    enabled_count = len(mod_manager.get_enabled_mods())
                else:
                    total_mods = 0
                    enabled_count = 0

            text "[enabled_count] of [total_mods] mods enabled" size 16 color "#aaaaaa"

            null height 10

            # Mod list
            viewport:
                xfill True
                ysize 400
                scrollbars "vertical"
                mousewheel True
                draggable True

                vbox:
                    spacing 8
                    xfill True

                    if mod_manager:
                        for mod in mod_manager.get_mod_list():
                            use mod_list_item(mod)
                    else:
                        text "No mod manager initialized" color "#ff6666"

            null height 10

            # Bottom buttons
            hbox:
                xfill True
                spacing 10

                textbutton "Refresh" action Function(mod_manager.discover_mods) style "mod_button"
                textbutton "Enable All" action Function(enable_all_mods) style "mod_button"
                textbutton "Disable All" action Function(disable_all_mods) style "mod_button"


screen mod_list_item(mod):
    """Individual mod item in the list."""
    button:
        xfill True
        padding (15, 10, 15, 10)
        background Solid("#3a3a5e") if mod.enabled else Solid("#2d2d4a")
        hover_background Solid("#4a4a6e")
        action Show("mod_details", mod=mod)

        hbox:
            spacing 15
            xfill True

            # Enable/disable toggle
            textbutton ("[X]" if mod.enabled else "[ ]"):
                action ToggleModEnabled(mod.id)
                text_size 18
                text_color "#66ff66" if mod.enabled else "#aaaaaa"

            # Mod info
            vbox:
                spacing 3
                xsize 500
                text mod.name size 18 color "#ffffff"
                text "v[mod.version] by [mod.author]" size 14 color "#888888"

            # Load order controls
            hbox:
                xalign 1.0
                spacing 5
                textbutton "^" action Function(mod_manager.move_mod_up, mod.id) text_size 16
                textbutton "v" action Function(mod_manager.move_mod_down, mod.id) text_size 16


screen mod_details(mod):
    """Detailed view of a single mod."""
    tag menu
    modal True

    add Solid("#1a1a2ecc")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 700
        ysize 500
        padding (25, 25, 25, 25)
        background Solid("#2a2a4e")

        vbox:
            spacing 15

            # Header
            hbox:
                xfill True
                text mod.name size 28 color "#66aaff"
                textbutton "X" action Hide("mod_details") xalign 1.0 text_size 24

            # Mod metadata
            grid 2 4:
                spacing 10
                xfill True

                text "ID:" color "#888888"
                text mod.id color "#ffffff"

                text "Version:" color "#888888"
                text mod.version color "#ffffff"

                text "Author:" color "#888888"
                text mod.author color "#ffffff"

                text "Status:" color "#888888"
                text ("Enabled" if mod.enabled else "Disabled") color ("#66ff66" if mod.enabled else "#ff6666")

            null height 10

            # Description
            text "Description" size 18 color "#aaaaaa"
            frame:
                xfill True
                ysize 150
                padding (10, 10, 10, 10)
                background Solid("#1a1a2e")

                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    text (mod.description if mod.description else "No description available.") color "#cccccc" size 16

            null height 10

            # Dependencies and conflicts
            if mod.dependencies:
                text "Dependencies: [', '.join(mod.dependencies)]" size 14 color "#ffaa66"

            if mod.conflicts:
                text "Conflicts: [', '.join(mod.conflicts)]" size 14 color "#ff6666"

            # Action buttons
            hbox:
                xfill True
                spacing 10
                xalign 0.5

                if mod.enabled:
                    textbutton "Disable Mod" action [ToggleModEnabled(mod.id), Hide("mod_details")] style "mod_button"
                else:
                    textbutton "Enable Mod" action [ToggleModEnabled(mod.id), Hide("mod_details")] style "mod_button"

                textbutton "Close" action Hide("mod_details") style "mod_button"


# ============================================================================
# MOD MANAGER ACTIONS
# ============================================================================

init python:
    class ToggleModEnabled(Action):
        """Action to toggle a mod's enabled state."""

        def __init__(self, mod_id):
            self.mod_id = mod_id

        def __call__(self):
            if mod_manager:
                mod = mod_manager.get_mod(self.mod_id)
                if mod:
                    if mod.enabled:
                        success, error = mod_manager.disable_mod(self.mod_id)
                    else:
                        success, error = mod_manager.enable_mod(self.mod_id)

                    if not success and error:
                        renpy.notify(error)
                    renpy.restart_interaction()

        def get_sensitive(self):
            return mod_manager is not None

    def enable_all_mods():
        """Enable all discovered mods."""
        if mod_manager:
            for mod_id in mod_manager.mods:
                mod_manager.enable_mod(mod_id)
            renpy.restart_interaction()

    def disable_all_mods():
        """Disable all mods."""
        if mod_manager:
            for mod_id in list(mod_manager.mods.keys()):
                mod_manager.disable_mod(mod_id)
            renpy.restart_interaction()


# ============================================================================
# MOD MANAGER STYLES
# ============================================================================

style mod_button:
    background Solid("#444466")
    hover_background Solid("#5555aa")
    padding (15, 8, 15, 8)

style mod_button_text:
    color "#cccccc"
    hover_color "#ffffff"
    size 16

"""
Tests for the Mod Support Framework.

Tests cover:
- Mod class functionality
- ModManager discovery, loading, and state management
- Load order management
- Conflict detection
- Enable/disable functionality
"""
import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(__file__))
from conftest import load_rpy_classes, GAME_DIR


@pytest.fixture
def mods_namespace():
    """Load the mods module from mods.rpy."""
    rpy_path = GAME_DIR / "mods.rpy"
    if not rpy_path.exists():
        pytest.skip("mods.rpy not found")
    return load_rpy_classes(rpy_path)


@pytest.fixture
def Mod(mods_namespace):
    """Get the Mod class."""
    return mods_namespace['Mod']


@pytest.fixture
def ModManager(mods_namespace):
    """Get the ModManager class."""
    return mods_namespace['ModManager']


@pytest.fixture
def temp_mods_dir():
    """Create a temporary mods directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_mod_dir(temp_mods_dir):
    """Create a sample mod directory with manifest."""
    mod_path = os.path.join(temp_mods_dir, "test_mod")
    os.makedirs(mod_path)

    manifest = {
        "id": "test_mod",
        "name": "Test Mod",
        "version": "1.0.0",
        "author": "Test Author",
        "description": "A test mod for testing",
        "dependencies": [],
        "conflicts": [],
        "priority": 50
    }

    with open(os.path.join(mod_path, "mod.json"), 'w') as f:
        json.dump(manifest, f)

    return mod_path


class TestModClass:
    """Tests for the Mod class."""

    def test_mod_creation_with_defaults(self, Mod):
        """Test creating a Mod with default values."""
        mod = Mod(id="test", name="Test Mod")

        assert mod.id == "test"
        assert mod.name == "Test Mod"
        assert mod.version == "1.0.0"
        assert mod.author == "Unknown"
        assert mod.description == ""
        assert mod.enabled is False
        assert mod.path is None
        assert mod.dependencies == []
        assert mod.conflicts == []
        assert mod.priority == 100

    def test_mod_creation_with_all_params(self, Mod):
        """Test creating a Mod with all parameters."""
        mod = Mod(
            id="full_mod",
            name="Full Mod",
            version="2.0.0",
            author="Test Author",
            description="A fully configured mod",
            enabled=True,
            path="/path/to/mod",
            dependencies=["base_mod"],
            conflicts=["incompatible_mod"],
            priority=10
        )

        assert mod.id == "full_mod"
        assert mod.name == "Full Mod"
        assert mod.version == "2.0.0"
        assert mod.author == "Test Author"
        assert mod.description == "A fully configured mod"
        assert mod.enabled is True
        assert mod.path == "/path/to/mod"
        assert mod.dependencies == ["base_mod"]
        assert mod.conflicts == ["incompatible_mod"]
        assert mod.priority == 10

    def test_mod_repr(self, Mod):
        """Test Mod string representation."""
        mod = Mod(id="test", name="Test", version="1.0", enabled=True)
        repr_str = repr(mod)

        assert "test" in repr_str
        assert "Test" in repr_str
        assert "1.0" in repr_str
        assert "True" in repr_str

    def test_mod_equality(self, Mod):
        """Test Mod equality comparison."""
        mod1 = Mod(id="test", name="Test 1")
        mod2 = Mod(id="test", name="Test 2")
        mod3 = Mod(id="different", name="Different")

        assert mod1 == mod2
        assert mod1 != mod3

    def test_mod_hash(self, Mod):
        """Test Mod hashing."""
        mod1 = Mod(id="test", name="Test 1")
        mod2 = Mod(id="test", name="Test 2")

        # Same ID should produce same hash
        assert hash(mod1) == hash(mod2)

        # Can be used in sets
        mod_set = {mod1, mod2}
        assert len(mod_set) == 1

    def test_mod_from_manifest(self, Mod, sample_mod_dir):
        """Test creating a Mod from a manifest file."""
        manifest_path = os.path.join(sample_mod_dir, "mod.json")
        mod = Mod.from_manifest(manifest_path)

        assert mod is not None
        assert mod.id == "test_mod"
        assert mod.name == "Test Mod"
        assert mod.version == "1.0.0"
        assert mod.author == "Test Author"
        assert mod.description == "A test mod for testing"
        assert mod.path == sample_mod_dir

    def test_mod_from_manifest_missing_file(self, Mod):
        """Test that from_manifest returns None for missing file."""
        mod = Mod.from_manifest("/nonexistent/path/mod.json")
        assert mod is None

    def test_mod_from_manifest_invalid_json(self, Mod, temp_mods_dir):
        """Test that from_manifest returns None for invalid JSON."""
        mod_path = os.path.join(temp_mods_dir, "invalid_mod")
        os.makedirs(mod_path)

        with open(os.path.join(mod_path, "mod.json"), 'w') as f:
            f.write("{ invalid json }")

        mod = Mod.from_manifest(os.path.join(mod_path, "mod.json"))
        assert mod is None

    def test_mod_to_dict(self, Mod):
        """Test converting Mod to dictionary."""
        mod = Mod(
            id="test",
            name="Test",
            version="1.0.0",
            author="Author",
            description="Description",
            enabled=True,
            path="/path",
            dependencies=["dep1"],
            conflicts=["conf1"],
            priority=50
        )

        data = mod.to_dict()

        assert data['id'] == "test"
        assert data['name'] == "Test"
        assert data['version'] == "1.0.0"
        assert data['author'] == "Author"
        assert data['description'] == "Description"
        assert data['enabled'] is True
        assert data['path'] == "/path"
        assert data['dependencies'] == ["dep1"]
        assert data['conflicts'] == ["conf1"]
        assert data['priority'] == 50

    def test_mod_validate_valid(self, Mod):
        """Test validating a valid mod."""
        mod = Mod(id="test", name="Test")
        is_valid, error = mod.validate()

        assert is_valid is True
        assert error is None

    def test_mod_validate_missing_id(self, Mod):
        """Test validating a mod with missing ID."""
        mod = Mod(id="", name="Test")
        is_valid, error = mod.validate()

        assert is_valid is False
        assert "ID" in error

    def test_mod_validate_missing_name(self, Mod):
        """Test validating a mod with missing name."""
        mod = Mod(id="test", name="")
        is_valid, error = mod.validate()

        assert is_valid is False
        assert "name" in error

    def test_mod_validate_invalid_priority(self, Mod):
        """Test validating a mod with invalid priority."""
        mod = Mod(id="test", name="Test", priority="invalid")
        is_valid, error = mod.validate()

        assert is_valid is False
        assert "Priority" in error


class TestModManager:
    """Tests for the ModManager class."""

    def test_mod_manager_creation(self, ModManager, temp_mods_dir):
        """Test creating a ModManager."""
        manager = ModManager(mods_directory=temp_mods_dir)

        assert manager.mods_directory == temp_mods_dir
        assert manager.mods == {}

    def test_discover_mods_empty_directory(self, ModManager, temp_mods_dir):
        """Test discovering mods in empty directory."""
        manager = ModManager(mods_directory=temp_mods_dir)
        mods = manager.discover_mods()

        assert mods == []
        assert manager.mods == {}

    def test_discover_mods_nonexistent_directory(self, ModManager):
        """Test discovering mods when directory doesn't exist."""
        manager = ModManager(mods_directory="/nonexistent/path")
        mods = manager.discover_mods()

        assert mods == []

    def test_discover_mods_with_manifest(self, ModManager, sample_mod_dir, temp_mods_dir):
        """Test discovering mods with manifest files."""
        manager = ModManager(mods_directory=temp_mods_dir)
        mods = manager.discover_mods()

        assert len(mods) == 1
        assert mods[0].id == "test_mod"
        assert mods[0].name == "Test Mod"

    def test_discover_mods_without_manifest(self, ModManager, temp_mods_dir):
        """Test discovering mods without manifest files."""
        # Create a mod directory without manifest
        mod_path = os.path.join(temp_mods_dir, "simple_mod")
        os.makedirs(mod_path)

        manager = ModManager(mods_directory=temp_mods_dir)
        mods = manager.discover_mods()

        assert len(mods) == 1
        assert mods[0].id == "simple_mod"
        assert mods[0].name == "simple_mod"

    def test_discover_mods_skips_hidden(self, ModManager, temp_mods_dir):
        """Test that discovery skips hidden directories."""
        # Create a hidden directory
        hidden_path = os.path.join(temp_mods_dir, ".hidden_mod")
        os.makedirs(hidden_path)

        manager = ModManager(mods_directory=temp_mods_dir)
        mods = manager.discover_mods()

        assert len(mods) == 0

    def test_get_mod(self, ModManager, sample_mod_dir, temp_mods_dir):
        """Test getting a mod by ID."""
        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        mod = manager.get_mod("test_mod")
        assert mod is not None
        assert mod.id == "test_mod"

        missing = manager.get_mod("nonexistent")
        assert missing is None

    def test_get_mod_list(self, ModManager, temp_mods_dir):
        """Test getting the mod list in order."""
        # Create multiple mods
        for i, (name, priority) in enumerate([("mod_c", 30), ("mod_a", 10), ("mod_b", 20)]):
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name, "priority": priority}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        mod_list = manager.get_mod_list()
        assert len(mod_list) == 3
        # Should be sorted by priority
        assert mod_list[0].id == "mod_a"
        assert mod_list[1].id == "mod_b"
        assert mod_list[2].id == "mod_c"

    def test_enable_mod(self, ModManager, sample_mod_dir, temp_mods_dir):
        """Test enabling a mod."""
        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        success, error = manager.enable_mod("test_mod")

        assert success is True
        assert error is None
        assert manager.get_mod("test_mod").enabled is True

    def test_enable_mod_not_found(self, ModManager, temp_mods_dir):
        """Test enabling a nonexistent mod."""
        manager = ModManager(mods_directory=temp_mods_dir)

        success, error = manager.enable_mod("nonexistent")

        assert success is False
        assert "not found" in error

    def test_disable_mod(self, ModManager, sample_mod_dir, temp_mods_dir):
        """Test disabling a mod."""
        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()
        manager.enable_mod("test_mod")

        success, error = manager.disable_mod("test_mod")

        assert success is True
        assert error is None
        assert manager.get_mod("test_mod").enabled is False

    def test_get_enabled_mods(self, ModManager, temp_mods_dir):
        """Test getting list of enabled mods."""
        # Create multiple mods
        for name in ["mod_a", "mod_b", "mod_c"]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name, "priority": 50}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        # Enable only some mods
        manager.enable_mod("mod_a")
        manager.enable_mod("mod_c")

        enabled = manager.get_enabled_mods()
        enabled_ids = [m.id for m in enabled]

        assert len(enabled) == 2
        assert "mod_a" in enabled_ids
        assert "mod_c" in enabled_ids
        assert "mod_b" not in enabled_ids


class TestModLoading:
    """Tests for mod loading and unloading."""

    def test_load_mod(self, ModManager, sample_mod_dir, temp_mods_dir):
        """Test loading a mod."""
        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()
        manager.enable_mod("test_mod")

        success, error = manager.load_mod("test_mod")

        assert success is True
        assert error is None
        assert manager.get_mod("test_mod")._loaded is True

    def test_load_mod_not_enabled(self, ModManager, sample_mod_dir, temp_mods_dir):
        """Test loading a mod that isn't enabled."""
        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        success, error = manager.load_mod("test_mod")

        assert success is False
        assert "not enabled" in error

    def test_load_mod_already_loaded(self, ModManager, sample_mod_dir, temp_mods_dir):
        """Test loading an already loaded mod."""
        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()
        manager.enable_mod("test_mod")
        manager.load_mod("test_mod")

        # Load again
        success, error = manager.load_mod("test_mod")

        assert success is True
        assert error is None

    def test_unload_mod(self, ModManager, sample_mod_dir, temp_mods_dir):
        """Test unloading a mod."""
        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()
        manager.enable_mod("test_mod")
        manager.load_mod("test_mod")

        success, message = manager.unload_mod("test_mod")

        assert success is True
        assert manager.get_mod("test_mod")._loaded is False

    def test_load_enabled_mods(self, ModManager, temp_mods_dir):
        """Test loading all enabled mods."""
        # Create multiple mods
        for name in ["mod_a", "mod_b"]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()
        manager.enable_mod("mod_a")
        manager.enable_mod("mod_b")

        results = manager.load_enabled_mods()

        assert len(results) == 2
        for mod_id, success, error in results:
            assert success is True


class TestLoadOrder:
    """Tests for load order management."""

    def test_set_load_order(self, ModManager, temp_mods_dir):
        """Test setting custom load order."""
        # Create multiple mods
        for name in ["mod_a", "mod_b", "mod_c"]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        success, error = manager.set_load_order(["mod_c", "mod_a", "mod_b"])

        assert success is True
        mod_list = manager.get_mod_list()
        assert mod_list[0].id == "mod_c"
        assert mod_list[1].id == "mod_a"
        assert mod_list[2].id == "mod_b"

    def test_set_load_order_invalid_id(self, ModManager, temp_mods_dir):
        """Test setting load order with invalid mod ID."""
        manager = ModManager(mods_directory=temp_mods_dir)

        success, error = manager.set_load_order(["nonexistent"])

        assert success is False
        assert "Unknown mod ID" in error

    def test_move_mod_up(self, ModManager, temp_mods_dir):
        """Test moving a mod up in load order."""
        for name in ["mod_a", "mod_b", "mod_c"]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name, "priority": ord(name[-1])}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        # Move mod_b up (from position 1 to 0)
        success, error = manager.move_mod_up("mod_b")

        assert success is True
        mod_list = manager.get_mod_list()
        assert mod_list[0].id == "mod_b"
        assert mod_list[1].id == "mod_a"

    def test_move_mod_up_already_first(self, ModManager, temp_mods_dir):
        """Test moving first mod up does nothing."""
        mod_path = os.path.join(temp_mods_dir, "mod_a")
        os.makedirs(mod_path)
        with open(os.path.join(mod_path, "mod.json"), 'w') as f:
            json.dump({"id": "mod_a", "name": "mod_a"}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        success, error = manager.move_mod_up("mod_a")

        assert success is True

    def test_move_mod_down(self, ModManager, temp_mods_dir):
        """Test moving a mod down in load order."""
        for name in ["mod_a", "mod_b", "mod_c"]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name, "priority": ord(name[-1])}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        # Move mod_a down (from position 0 to 1)
        success, error = manager.move_mod_down("mod_a")

        assert success is True
        mod_list = manager.get_mod_list()
        assert mod_list[0].id == "mod_b"
        assert mod_list[1].id == "mod_a"


class TestConflictDetection:
    """Tests for conflict detection."""

    def test_detect_conflicts_none(self, ModManager, temp_mods_dir):
        """Test detecting no conflicts."""
        for name in ["mod_a", "mod_b"]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()
        manager.enable_mod("mod_a")
        manager.enable_mod("mod_b")

        conflicts = manager.detect_conflicts()
        assert len(conflicts) == 0

    def test_detect_conflicts_found(self, ModManager, temp_mods_dir):
        """Test detecting conflicts between mods.

        This tests detect_conflicts for cases where conflicting mods
        might be enabled (e.g., from restored state before conflict
        was added to manifest).
        """
        # Create mod_a that conflicts with mod_b
        mod_a_path = os.path.join(temp_mods_dir, "mod_a")
        os.makedirs(mod_a_path)
        with open(os.path.join(mod_a_path, "mod.json"), 'w') as f:
            json.dump({"id": "mod_a", "name": "Mod A", "conflicts": ["mod_b"]}, f)

        mod_b_path = os.path.join(temp_mods_dir, "mod_b")
        os.makedirs(mod_b_path)
        with open(os.path.join(mod_b_path, "mod.json"), 'w') as f:
            json.dump({"id": "mod_b", "name": "Mod B"}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        # Directly set enabled to simulate restored state with conflicts
        manager.get_mod("mod_a").enabled = True
        manager.get_mod("mod_b").enabled = True

        conflicts = manager.detect_conflicts()
        assert len(conflicts) == 1
        assert "mod_a" in conflicts[0]
        assert "mod_b" in conflicts[0]

    def test_enable_mod_with_conflict(self, ModManager, temp_mods_dir):
        """Test that enabling a conflicting mod fails."""
        # Create mod_a that conflicts with mod_b
        mod_a_path = os.path.join(temp_mods_dir, "mod_a")
        os.makedirs(mod_a_path)
        with open(os.path.join(mod_a_path, "mod.json"), 'w') as f:
            json.dump({"id": "mod_a", "name": "Mod A", "conflicts": ["mod_b"]}, f)

        mod_b_path = os.path.join(temp_mods_dir, "mod_b")
        os.makedirs(mod_b_path)
        with open(os.path.join(mod_b_path, "mod.json"), 'w') as f:
            json.dump({"id": "mod_b", "name": "Mod B"}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()
        manager.enable_mod("mod_b")

        # Try to enable mod_a which conflicts with mod_b
        success, error = manager.enable_mod("mod_a")

        assert success is False
        assert "Conflicts" in error


class TestDependencies:
    """Tests for dependency handling."""

    def test_enable_mod_with_missing_dependency(self, ModManager, temp_mods_dir):
        """Test that enabling a mod with missing dependency fails."""
        mod_path = os.path.join(temp_mods_dir, "mod_a")
        os.makedirs(mod_path)
        with open(os.path.join(mod_path, "mod.json"), 'w') as f:
            json.dump({"id": "mod_a", "name": "Mod A", "dependencies": ["base_mod"]}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        success, error = manager.enable_mod("mod_a")

        assert success is False
        assert "Missing dependency" in error

    def test_enable_mod_with_disabled_dependency(self, ModManager, temp_mods_dir):
        """Test that enabling a mod with disabled dependency fails."""
        for name, deps in [("base_mod", []), ("mod_a", ["base_mod"])]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name, "dependencies": deps}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        success, error = manager.enable_mod("mod_a")

        assert success is False
        assert "not enabled" in error

    def test_enable_mod_with_satisfied_dependency(self, ModManager, temp_mods_dir):
        """Test enabling a mod with satisfied dependencies."""
        for name, deps in [("base_mod", []), ("mod_a", ["base_mod"])]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name, "dependencies": deps}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()
        manager.enable_mod("base_mod")

        success, error = manager.enable_mod("mod_a")

        assert success is True

    def test_disable_mod_with_dependents(self, ModManager, temp_mods_dir):
        """Test that disabling a mod with dependents fails."""
        for name, deps in [("base_mod", []), ("mod_a", ["base_mod"])]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name, "dependencies": deps}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()
        manager.enable_mod("base_mod")
        manager.enable_mod("mod_a")

        success, error = manager.disable_mod("base_mod")

        assert success is False
        assert "depends on this mod" in error


class TestStatePersistence:
    """Tests for state saving and loading."""

    def test_save_and_load_state(self, ModManager, temp_mods_dir):
        """Test that mod state is persisted."""
        for name in ["mod_a", "mod_b"]:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": name, "name": name}, f)

        # Create first manager and enable a mod
        manager1 = ModManager(mods_directory=temp_mods_dir)
        manager1.discover_mods()
        manager1.enable_mod("mod_a")
        manager1.set_load_order(["mod_b", "mod_a"])

        # Create second manager and verify state is restored
        manager2 = ModManager(mods_directory=temp_mods_dir)
        manager2.discover_mods()

        assert manager2.get_mod("mod_a").enabled is True
        assert manager2.get_mod("mod_b").enabled is False

        mod_list = manager2.get_mod_list()
        assert mod_list[0].id == "mod_b"
        assert mod_list[1].id == "mod_a"

    def test_state_file_location(self, ModManager, temp_mods_dir):
        """Test that state file is in correct location."""
        manager = ModManager(mods_directory=temp_mods_dir)
        expected_path = os.path.join(temp_mods_dir, ".mod_state.json")
        assert manager._state_file == expected_path


class TestMultipleMods:
    """Tests for scenarios with multiple mods."""

    def test_discover_multiple_mods(self, ModManager, temp_mods_dir):
        """Test discovering multiple mods."""
        for i in range(5):
            mod_path = os.path.join(temp_mods_dir, f"mod_{i}")
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": f"mod_{i}", "name": f"Mod {i}"}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        mods = manager.discover_mods()

        assert len(mods) == 5

    def test_enable_multiple_mods(self, ModManager, temp_mods_dir):
        """Test enabling multiple mods."""
        for i in range(3):
            mod_path = os.path.join(temp_mods_dir, f"mod_{i}")
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({"id": f"mod_{i}", "name": f"Mod {i}"}, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        for i in range(3):
            manager.enable_mod(f"mod_{i}")

        enabled = manager.get_enabled_mods()
        assert len(enabled) == 3

    def test_complex_dependency_chain(self, ModManager, temp_mods_dir):
        """Test a complex dependency chain."""
        # Create: mod_c depends on mod_b, which depends on mod_a
        mods_config = [
            ("mod_a", [], 10),
            ("mod_b", ["mod_a"], 20),
            ("mod_c", ["mod_b"], 30),
        ]

        for name, deps, priority in mods_config:
            mod_path = os.path.join(temp_mods_dir, name)
            os.makedirs(mod_path)
            with open(os.path.join(mod_path, "mod.json"), 'w') as f:
                json.dump({
                    "id": name,
                    "name": name,
                    "dependencies": deps,
                    "priority": priority
                }, f)

        manager = ModManager(mods_directory=temp_mods_dir)
        manager.discover_mods()

        # Try to enable mod_c without dependencies - should fail
        success, error = manager.enable_mod("mod_c")
        assert success is False

        # Enable in correct order
        manager.enable_mod("mod_a")
        manager.enable_mod("mod_b")
        success, error = manager.enable_mod("mod_c")
        assert success is True

        # Verify load order respects priorities
        enabled = manager.get_enabled_mods()
        assert enabled[0].id == "mod_a"
        assert enabled[1].id == "mod_b"
        assert enabled[2].id == "mod_c"

"""
Tests for the Gallery/CG Unlock System.

This module tests the gallery system including:
- GalleryItem class for CG images
- MusicTrack class for audio tracks
- SceneReplay class for scene replays
- GalleryManager for managing all gallery content
"""
import pytest


class TestGalleryItem:
    """Tests for the GalleryItem class."""

    def test_gallery_item_creation(self, load_system):
        """Test creating a GalleryItem with required parameters."""
        ns = load_system("gallery")
        GalleryItem = ns["GalleryItem"]

        item = GalleryItem(
            id="test_cg",
            name="Test CG",
            image_path="images/test.png"
        )

        assert item.id == "test_cg"
        assert item.name == "Test CG"
        assert item.image_path == "images/test.png"
        assert item.thumbnail == "images/test.png"  # Defaults to image_path
        assert item.category == "misc"  # Default category
        assert item.unlocked is False  # Default locked

    def test_gallery_item_with_thumbnail(self, load_system):
        """Test creating a GalleryItem with custom thumbnail."""
        ns = load_system("gallery")
        GalleryItem = ns["GalleryItem"]

        item = GalleryItem(
            id="test_cg",
            name="Test CG",
            image_path="images/test.png",
            thumbnail="images/thumbs/test_thumb.png"
        )

        assert item.thumbnail == "images/thumbs/test_thumb.png"

    def test_gallery_item_with_category(self, load_system):
        """Test creating a GalleryItem with specific category."""
        ns = load_system("gallery")
        GalleryItem = ns["GalleryItem"]

        item = GalleryItem(
            id="test_cg",
            name="Test CG",
            image_path="images/test.png",
            category="event"
        )

        assert item.category == "event"

    def test_gallery_item_unlock(self, load_system):
        """Test unlocking a GalleryItem."""
        ns = load_system("gallery")
        GalleryItem = ns["GalleryItem"]

        item = GalleryItem(
            id="test_cg",
            name="Test CG",
            image_path="images/test.png"
        )

        assert item.is_unlocked() is False
        item.unlock()
        assert item.is_unlocked() is True
        assert item.unlocked is True

    def test_gallery_item_lock(self, load_system):
        """Test locking a GalleryItem."""
        ns = load_system("gallery")
        GalleryItem = ns["GalleryItem"]

        item = GalleryItem(
            id="test_cg",
            name="Test CG",
            image_path="images/test.png",
            unlocked=True
        )

        assert item.is_unlocked() is True
        item.lock()
        assert item.is_unlocked() is False

    def test_gallery_item_repr(self, load_system):
        """Test string representation of GalleryItem."""
        ns = load_system("gallery")
        GalleryItem = ns["GalleryItem"]

        item = GalleryItem(
            id="test_cg",
            name="Test CG",
            image_path="images/test.png"
        )

        assert "test_cg" in repr(item)
        assert "Test CG" in repr(item)
        assert "locked" in repr(item)

        item.unlock()
        assert "unlocked" in repr(item)


class TestMusicTrack:
    """Tests for the MusicTrack class."""

    def test_music_track_creation(self, load_system):
        """Test creating a MusicTrack with required parameters."""
        ns = load_system("gallery")
        MusicTrack = ns["MusicTrack"]

        track = MusicTrack(
            id="bgm_test",
            name="Test Track",
            file_path="audio/bgm/test.ogg"
        )

        assert track.id == "bgm_test"
        assert track.name == "Test Track"
        assert track.file_path == "audio/bgm/test.ogg"
        assert track.unlocked is False

    def test_music_track_unlock(self, load_system):
        """Test unlocking a MusicTrack."""
        ns = load_system("gallery")
        MusicTrack = ns["MusicTrack"]

        track = MusicTrack(
            id="bgm_test",
            name="Test Track",
            file_path="audio/bgm/test.ogg"
        )

        assert track.is_unlocked() is False
        track.unlock()
        assert track.is_unlocked() is True

    def test_music_track_lock(self, load_system):
        """Test locking a MusicTrack."""
        ns = load_system("gallery")
        MusicTrack = ns["MusicTrack"]

        track = MusicTrack(
            id="bgm_test",
            name="Test Track",
            file_path="audio/bgm/test.ogg",
            unlocked=True
        )

        assert track.is_unlocked() is True
        track.lock()
        assert track.is_unlocked() is False

    def test_music_track_repr(self, load_system):
        """Test string representation of MusicTrack."""
        ns = load_system("gallery")
        MusicTrack = ns["MusicTrack"]

        track = MusicTrack(
            id="bgm_test",
            name="Test Track",
            file_path="audio/bgm/test.ogg"
        )

        assert "bgm_test" in repr(track)
        assert "Test Track" in repr(track)
        assert "locked" in repr(track)


class TestSceneReplay:
    """Tests for the SceneReplay class."""

    def test_scene_replay_creation(self, load_system):
        """Test creating a SceneReplay with required parameters."""
        ns = load_system("gallery")
        SceneReplay = ns["SceneReplay"]

        scene = SceneReplay(
            id="scene_test",
            name="Test Scene",
            label_name="test_scene_label"
        )

        assert scene.id == "scene_test"
        assert scene.name == "Test Scene"
        assert scene.label_name == "test_scene_label"
        assert scene.unlocked is False

    def test_scene_replay_unlock(self, load_system):
        """Test unlocking a SceneReplay."""
        ns = load_system("gallery")
        SceneReplay = ns["SceneReplay"]

        scene = SceneReplay(
            id="scene_test",
            name="Test Scene",
            label_name="test_scene_label"
        )

        assert scene.is_unlocked() is False
        scene.unlock()
        assert scene.is_unlocked() is True

    def test_scene_replay_lock(self, load_system):
        """Test locking a SceneReplay."""
        ns = load_system("gallery")
        SceneReplay = ns["SceneReplay"]

        scene = SceneReplay(
            id="scene_test",
            name="Test Scene",
            label_name="test_scene_label",
            unlocked=True
        )

        assert scene.is_unlocked() is True
        scene.lock()
        assert scene.is_unlocked() is False

    def test_scene_replay_repr(self, load_system):
        """Test string representation of SceneReplay."""
        ns = load_system("gallery")
        SceneReplay = ns["SceneReplay"]

        scene = SceneReplay(
            id="scene_test",
            name="Test Scene",
            label_name="test_scene_label"
        )

        assert "scene_test" in repr(scene)
        assert "Test Scene" in repr(scene)
        assert "locked" in repr(scene)


class TestGalleryManager:
    """Tests for the GalleryManager class."""

    def test_gallery_manager_creation(self, load_system):
        """Test creating a GalleryManager."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]

        manager = GalleryManager()

        assert manager.gallery_items == {}
        assert manager.music_tracks == {}
        assert manager.scene_replays == {}

    # -------------------------------------------------------------------------
    # Gallery Item Tests
    # -------------------------------------------------------------------------

    def test_register_gallery_item(self, load_system):
        """Test registering a gallery item."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        item = GalleryItem(
            id="test_cg",
            name="Test CG",
            image_path="images/test.png"
        )

        result = manager.register_gallery_item(item)

        assert result == item
        assert "test_cg" in manager.gallery_items
        assert manager.gallery_items["test_cg"] == item

    def test_get_gallery_item(self, load_system):
        """Test getting a gallery item by ID."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        item = GalleryItem(
            id="test_cg",
            name="Test CG",
            image_path="images/test.png"
        )
        manager.register_gallery_item(item)

        result = manager.get_gallery_item("test_cg")
        assert result == item

        result = manager.get_gallery_item("nonexistent")
        assert result is None

    def test_get_all_gallery_items(self, load_system):
        """Test getting all gallery items."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        item1 = GalleryItem(id="cg1", name="CG 1", image_path="images/1.png")
        item2 = GalleryItem(id="cg2", name="CG 2", image_path="images/2.png")

        manager.register_gallery_item(item1)
        manager.register_gallery_item(item2)

        result = manager.get_all_gallery_items()
        assert len(result) == 2
        assert item1 in result
        assert item2 in result

    def test_get_gallery_items_by_category(self, load_system):
        """Test filtering gallery items by category."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        item1 = GalleryItem(id="cg1", name="CG 1", image_path="images/1.png", category="event")
        item2 = GalleryItem(id="cg2", name="CG 2", image_path="images/2.png", category="scene")
        item3 = GalleryItem(id="cg3", name="CG 3", image_path="images/3.png", category="event")

        manager.register_gallery_item(item1)
        manager.register_gallery_item(item2)
        manager.register_gallery_item(item3)

        event_items = manager.get_gallery_items_by_category("event")
        assert len(event_items) == 2
        assert item1 in event_items
        assert item3 in event_items

        scene_items = manager.get_gallery_items_by_category("scene")
        assert len(scene_items) == 1
        assert item2 in scene_items

    def test_get_unlocked_gallery_items(self, load_system):
        """Test getting unlocked gallery items."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        item1 = GalleryItem(id="cg1", name="CG 1", image_path="images/1.png", unlocked=True)
        item2 = GalleryItem(id="cg2", name="CG 2", image_path="images/2.png", unlocked=False)
        item3 = GalleryItem(id="cg3", name="CG 3", image_path="images/3.png", unlocked=True)

        manager.register_gallery_item(item1)
        manager.register_gallery_item(item2)
        manager.register_gallery_item(item3)

        unlocked = manager.get_unlocked_gallery_items()
        assert len(unlocked) == 2
        assert item1 in unlocked
        assert item3 in unlocked
        assert item2 not in unlocked

    def test_get_locked_gallery_items(self, load_system):
        """Test getting locked gallery items."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        item1 = GalleryItem(id="cg1", name="CG 1", image_path="images/1.png", unlocked=True)
        item2 = GalleryItem(id="cg2", name="CG 2", image_path="images/2.png", unlocked=False)

        manager.register_gallery_item(item1)
        manager.register_gallery_item(item2)

        locked = manager.get_locked_gallery_items()
        assert len(locked) == 1
        assert item2 in locked
        assert item1 not in locked

    def test_unlock_gallery_item(self, load_system):
        """Test unlocking a gallery item through the manager."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        item = GalleryItem(id="cg1", name="CG 1", image_path="images/1.png")
        manager.register_gallery_item(item)

        assert item.unlocked is False
        result = manager.unlock_gallery_item("cg1")
        assert result is True
        assert item.unlocked is True

        # Test unlocking nonexistent item
        result = manager.unlock_gallery_item("nonexistent")
        assert result is False

    # -------------------------------------------------------------------------
    # Music Track Tests
    # -------------------------------------------------------------------------

    def test_register_music_track(self, load_system):
        """Test registering a music track."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        MusicTrack = ns["MusicTrack"]

        manager = GalleryManager()
        track = MusicTrack(
            id="bgm_test",
            name="Test Track",
            file_path="audio/test.ogg"
        )

        result = manager.register_music_track(track)

        assert result == track
        assert "bgm_test" in manager.music_tracks

    def test_get_music_track(self, load_system):
        """Test getting a music track by ID."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        MusicTrack = ns["MusicTrack"]

        manager = GalleryManager()
        track = MusicTrack(id="bgm_test", name="Test", file_path="audio/test.ogg")
        manager.register_music_track(track)

        result = manager.get_music_track("bgm_test")
        assert result == track

        result = manager.get_music_track("nonexistent")
        assert result is None

    def test_get_all_music_tracks(self, load_system):
        """Test getting all music tracks."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        MusicTrack = ns["MusicTrack"]

        manager = GalleryManager()
        track1 = MusicTrack(id="bgm1", name="Track 1", file_path="audio/1.ogg")
        track2 = MusicTrack(id="bgm2", name="Track 2", file_path="audio/2.ogg")

        manager.register_music_track(track1)
        manager.register_music_track(track2)

        result = manager.get_all_music_tracks()
        assert len(result) == 2

    def test_get_unlocked_music_tracks(self, load_system):
        """Test getting unlocked music tracks."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        MusicTrack = ns["MusicTrack"]

        manager = GalleryManager()
        track1 = MusicTrack(id="bgm1", name="Track 1", file_path="audio/1.ogg", unlocked=True)
        track2 = MusicTrack(id="bgm2", name="Track 2", file_path="audio/2.ogg", unlocked=False)

        manager.register_music_track(track1)
        manager.register_music_track(track2)

        unlocked = manager.get_unlocked_music_tracks()
        assert len(unlocked) == 1
        assert track1 in unlocked

    def test_unlock_music_track(self, load_system):
        """Test unlocking a music track through the manager."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        MusicTrack = ns["MusicTrack"]

        manager = GalleryManager()
        track = MusicTrack(id="bgm1", name="Track 1", file_path="audio/1.ogg")
        manager.register_music_track(track)

        assert track.unlocked is False
        result = manager.unlock_music_track("bgm1")
        assert result is True
        assert track.unlocked is True

    # -------------------------------------------------------------------------
    # Scene Replay Tests
    # -------------------------------------------------------------------------

    def test_register_scene_replay(self, load_system):
        """Test registering a scene replay."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        SceneReplay = ns["SceneReplay"]

        manager = GalleryManager()
        scene = SceneReplay(
            id="scene_test",
            name="Test Scene",
            label_name="test_label"
        )

        result = manager.register_scene_replay(scene)

        assert result == scene
        assert "scene_test" in manager.scene_replays

    def test_get_scene_replay(self, load_system):
        """Test getting a scene replay by ID."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        SceneReplay = ns["SceneReplay"]

        manager = GalleryManager()
        scene = SceneReplay(id="scene_test", name="Test", label_name="test")
        manager.register_scene_replay(scene)

        result = manager.get_scene_replay("scene_test")
        assert result == scene

        result = manager.get_scene_replay("nonexistent")
        assert result is None

    def test_get_all_scene_replays(self, load_system):
        """Test getting all scene replays."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        SceneReplay = ns["SceneReplay"]

        manager = GalleryManager()
        scene1 = SceneReplay(id="scene1", name="Scene 1", label_name="label1")
        scene2 = SceneReplay(id="scene2", name="Scene 2", label_name="label2")

        manager.register_scene_replay(scene1)
        manager.register_scene_replay(scene2)

        result = manager.get_all_scene_replays()
        assert len(result) == 2

    def test_get_unlocked_scene_replays(self, load_system):
        """Test getting unlocked scene replays."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        SceneReplay = ns["SceneReplay"]

        manager = GalleryManager()
        scene1 = SceneReplay(id="scene1", name="Scene 1", label_name="label1", unlocked=True)
        scene2 = SceneReplay(id="scene2", name="Scene 2", label_name="label2", unlocked=False)

        manager.register_scene_replay(scene1)
        manager.register_scene_replay(scene2)

        unlocked = manager.get_unlocked_scene_replays()
        assert len(unlocked) == 1
        assert scene1 in unlocked

    def test_unlock_scene_replay(self, load_system):
        """Test unlocking a scene replay through the manager."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        SceneReplay = ns["SceneReplay"]

        manager = GalleryManager()
        scene = SceneReplay(id="scene1", name="Scene 1", label_name="label1")
        manager.register_scene_replay(scene)

        assert scene.unlocked is False
        result = manager.unlock_scene_replay("scene1")
        assert result is True
        assert scene.unlocked is True

    # -------------------------------------------------------------------------
    # Completion Percentage Tests
    # -------------------------------------------------------------------------

    def test_gallery_completion_empty(self, load_system):
        """Test gallery completion with no items."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]

        manager = GalleryManager()

        assert manager.get_gallery_completion() == 0.0

    def test_gallery_completion_partial(self, load_system):
        """Test gallery completion with some unlocked items."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        manager.register_gallery_item(GalleryItem(id="cg1", name="CG 1", image_path="1.png", unlocked=True))
        manager.register_gallery_item(GalleryItem(id="cg2", name="CG 2", image_path="2.png", unlocked=False))
        manager.register_gallery_item(GalleryItem(id="cg3", name="CG 3", image_path="3.png", unlocked=False))
        manager.register_gallery_item(GalleryItem(id="cg4", name="CG 4", image_path="4.png", unlocked=True))

        completion = manager.get_gallery_completion()
        assert completion == 50.0  # 2 out of 4

    def test_gallery_completion_full(self, load_system):
        """Test gallery completion with all items unlocked."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        manager.register_gallery_item(GalleryItem(id="cg1", name="CG 1", image_path="1.png", unlocked=True))
        manager.register_gallery_item(GalleryItem(id="cg2", name="CG 2", image_path="2.png", unlocked=True))

        completion = manager.get_gallery_completion()
        assert completion == 100.0

    def test_music_completion(self, load_system):
        """Test music completion percentage."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        MusicTrack = ns["MusicTrack"]

        manager = GalleryManager()
        manager.register_music_track(MusicTrack(id="bgm1", name="Track 1", file_path="1.ogg", unlocked=True))
        manager.register_music_track(MusicTrack(id="bgm2", name="Track 2", file_path="2.ogg", unlocked=False))

        completion = manager.get_music_completion()
        assert completion == 50.0

    def test_scene_completion(self, load_system):
        """Test scene completion percentage."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        SceneReplay = ns["SceneReplay"]

        manager = GalleryManager()
        manager.register_scene_replay(SceneReplay(id="s1", name="Scene 1", label_name="l1", unlocked=True))
        manager.register_scene_replay(SceneReplay(id="s2", name="Scene 2", label_name="l2", unlocked=True))
        manager.register_scene_replay(SceneReplay(id="s3", name="Scene 3", label_name="l3", unlocked=False))

        completion = manager.get_scene_completion()
        assert abs(completion - 66.666666) < 0.01  # Approximately 66.67%

    def test_total_completion(self, load_system):
        """Test total completion across all content types."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]
        MusicTrack = ns["MusicTrack"]
        SceneReplay = ns["SceneReplay"]

        manager = GalleryManager()

        # 2 CGs (1 unlocked)
        manager.register_gallery_item(GalleryItem(id="cg1", name="CG 1", image_path="1.png", unlocked=True))
        manager.register_gallery_item(GalleryItem(id="cg2", name="CG 2", image_path="2.png", unlocked=False))

        # 2 tracks (1 unlocked)
        manager.register_music_track(MusicTrack(id="bgm1", name="Track 1", file_path="1.ogg", unlocked=True))
        manager.register_music_track(MusicTrack(id="bgm2", name="Track 2", file_path="2.ogg", unlocked=False))

        # 2 scenes (0 unlocked)
        manager.register_scene_replay(SceneReplay(id="s1", name="Scene 1", label_name="l1", unlocked=False))
        manager.register_scene_replay(SceneReplay(id="s2", name="Scene 2", label_name="l2", unlocked=False))

        # Total: 6 items, 2 unlocked = 33.33%
        completion = manager.get_total_completion()
        assert abs(completion - 33.333333) < 0.01

    def test_category_completion(self, load_system):
        """Test completion percentage for a specific category."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        manager.register_gallery_item(GalleryItem(id="e1", name="Event 1", image_path="1.png", category="event", unlocked=True))
        manager.register_gallery_item(GalleryItem(id="e2", name="Event 2", image_path="2.png", category="event", unlocked=False))
        manager.register_gallery_item(GalleryItem(id="s1", name="Scene 1", image_path="3.png", category="scene", unlocked=True))

        event_completion = manager.get_category_completion("event")
        assert event_completion == 50.0

        scene_completion = manager.get_category_completion("scene")
        assert scene_completion == 100.0

        empty_completion = manager.get_category_completion("nonexistent")
        assert empty_completion == 0.0

    # -------------------------------------------------------------------------
    # Utility Method Tests
    # -------------------------------------------------------------------------

    def test_get_available_categories(self, load_system):
        """Test getting list of categories with items."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        manager.register_gallery_item(GalleryItem(id="e1", name="Event 1", image_path="1.png", category="event"))
        manager.register_gallery_item(GalleryItem(id="s1", name="Scene 1", image_path="2.png", category="scene"))
        manager.register_gallery_item(GalleryItem(id="e2", name="Event 2", image_path="3.png", category="event"))

        categories = manager.get_available_categories()
        assert "event" in categories
        assert "scene" in categories
        assert len(categories) == 2

    def test_clear_all(self, load_system):
        """Test clearing all registered items."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]
        MusicTrack = ns["MusicTrack"]
        SceneReplay = ns["SceneReplay"]

        manager = GalleryManager()
        manager.register_gallery_item(GalleryItem(id="cg1", name="CG", image_path="1.png"))
        manager.register_music_track(MusicTrack(id="bgm1", name="Track", file_path="1.ogg"))
        manager.register_scene_replay(SceneReplay(id="s1", name="Scene", label_name="l1"))

        assert len(manager.get_all_gallery_items()) == 1
        assert len(manager.get_all_music_tracks()) == 1
        assert len(manager.get_all_scene_replays()) == 1

        manager.clear_all()

        assert len(manager.get_all_gallery_items()) == 0
        assert len(manager.get_all_music_tracks()) == 0
        assert len(manager.get_all_scene_replays()) == 0


class TestGalleryCategories:
    """Tests for gallery category constants."""

    def test_gallery_categories_defined(self, load_system):
        """Test that GALLERY_CATEGORIES constant is defined."""
        ns = load_system("gallery")

        assert "GALLERY_CATEGORIES" in ns
        categories = ns["GALLERY_CATEGORIES"]

        # Check expected categories exist
        assert "character" in categories
        assert "scene" in categories
        assert "background" in categories
        assert "event" in categories
        assert "ending" in categories
        assert "misc" in categories


class TestPersistentStorage:
    """Tests for persistent storage functionality."""

    def test_persistent_key_generation(self, load_system):
        """Test that persistent keys are generated correctly."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        item = GalleryItem(id="test_cg", name="Test", image_path="test.png")

        key = manager._get_persistent_key(item, "cg")
        assert key == "gallery_cg_test_cg"

    def test_save_and_load_persistent_state(self, load_system):
        """Test saving and loading persistent state."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()
        item = GalleryItem(id="test_cg", name="Test", image_path="test.png")

        # Save unlocked state
        item.unlock()
        manager._save_persistent_state(item, "cg")

        # Create new item and load state
        item2 = GalleryItem(id="test_cg", name="Test", image_path="test.png")
        manager._load_persistent_state(item2, "cg")

        assert item2.unlocked is True


class TestIntegration:
    """Integration tests for the gallery system."""

    def test_full_workflow(self, load_system):
        """Test a complete workflow of registering, unlocking, and querying."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]
        MusicTrack = ns["MusicTrack"]
        SceneReplay = ns["SceneReplay"]

        manager = GalleryManager()

        # Register content
        cg1 = GalleryItem(id="cg1", name="CG 1", image_path="cg1.png", category="event")
        cg2 = GalleryItem(id="cg2", name="CG 2", image_path="cg2.png", category="event")
        track = MusicTrack(id="bgm1", name="Main Theme", file_path="main.ogg")
        scene = SceneReplay(id="scene1", name="Opening", label_name="opening")

        manager.register_gallery_item(cg1)
        manager.register_gallery_item(cg2)
        manager.register_music_track(track)
        manager.register_scene_replay(scene)

        # Initial state: nothing unlocked
        assert manager.get_total_completion() == 0.0
        assert len(manager.get_unlocked_gallery_items()) == 0

        # Unlock some content
        manager.unlock_gallery_item("cg1")
        manager.unlock_music_track("bgm1")

        # Check partial completion
        assert len(manager.get_unlocked_gallery_items()) == 1
        assert len(manager.get_unlocked_music_tracks()) == 1
        assert manager.get_gallery_completion() == 50.0
        assert manager.get_music_completion() == 100.0
        assert manager.get_scene_completion() == 0.0

        # Total: 2 out of 4 = 50%
        assert manager.get_total_completion() == 50.0

        # Unlock remaining
        manager.unlock_gallery_item("cg2")
        manager.unlock_scene_replay("scene1")

        # Full completion
        assert manager.get_total_completion() == 100.0

    def test_multiple_categories(self, load_system):
        """Test working with multiple categories."""
        ns = load_system("gallery")
        GalleryManager = ns["GalleryManager"]
        GalleryItem = ns["GalleryItem"]

        manager = GalleryManager()

        # Create items in different categories
        for i in range(3):
            manager.register_gallery_item(
                GalleryItem(id=f"event{i}", name=f"Event {i}", image_path=f"e{i}.png", category="event")
            )
        for i in range(2):
            manager.register_gallery_item(
                GalleryItem(id=f"bg{i}", name=f"BG {i}", image_path=f"bg{i}.png", category="background")
            )

        # Verify category filtering
        assert len(manager.get_gallery_items_by_category("event")) == 3
        assert len(manager.get_gallery_items_by_category("background")) == 2

        # Verify available categories
        categories = manager.get_available_categories()
        assert len(categories) == 2
        assert "event" in categories
        assert "background" in categories

        # Unlock one from each
        manager.unlock_gallery_item("event0")
        manager.unlock_gallery_item("bg0")

        # Check category completion
        assert abs(manager.get_category_completion("event") - 33.333) < 0.01
        assert manager.get_category_completion("background") == 50.0

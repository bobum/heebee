# Gallery/CG Unlock System for Ren'Py Visual Novel
# This module provides a comprehensive gallery system with CG viewing,
# music playback, and scene replay functionality.

init python:
    # =========================================================================
    # GALLERY CATEGORIES - Define categories for organizing gallery content
    # =========================================================================

    GALLERY_CATEGORIES = {
        "character": "Character Art",
        "scene": "Scene CGs",
        "background": "Backgrounds",
        "event": "Event CGs",
        "ending": "Ending CGs",
        "misc": "Miscellaneous"
    }

    # =========================================================================
    # GALLERYITEM CLASS - Represents a single CG image in the gallery
    # =========================================================================

    class GalleryItem:
        """
        Represents a single CG image in the gallery.

        Attributes:
            id (str): Unique identifier for the gallery item
            name (str): Display name of the item
            image_path (str): Path to the full-size image
            thumbnail (str): Path to the thumbnail image (optional)
            category (str): Category for organizing the gallery
            unlocked (bool): Whether the item has been unlocked
        """

        def __init__(self, id, name, image_path, thumbnail=None, category="misc", unlocked=False):
            self.id = id
            self.name = name
            self.image_path = image_path
            self.thumbnail = thumbnail if thumbnail else image_path
            self.category = category
            self.unlocked = unlocked

        def unlock(self):
            """Unlock this gallery item."""
            self.unlocked = True

        def lock(self):
            """Lock this gallery item."""
            self.unlocked = False

        def is_unlocked(self):
            """Check if this item is unlocked."""
            return self.unlocked

        def __repr__(self):
            status = "unlocked" if self.unlocked else "locked"
            return f"GalleryItem({self.id}, {self.name}, {status})"

    # =========================================================================
    # MUSICTRACK CLASS - Represents a music track in the gallery
    # =========================================================================

    class MusicTrack:
        """
        Represents a music track in the gallery.

        Attributes:
            id (str): Unique identifier for the music track
            name (str): Display name of the track
            file_path (str): Path to the audio file
            unlocked (bool): Whether the track has been unlocked
        """

        def __init__(self, id, name, file_path, unlocked=False):
            self.id = id
            self.name = name
            self.file_path = file_path
            self.unlocked = unlocked

        def unlock(self):
            """Unlock this music track."""
            self.unlocked = True

        def lock(self):
            """Lock this music track."""
            self.unlocked = False

        def is_unlocked(self):
            """Check if this track is unlocked."""
            return self.unlocked

        def __repr__(self):
            status = "unlocked" if self.unlocked else "locked"
            return f"MusicTrack({self.id}, {self.name}, {status})"

    # =========================================================================
    # SCENEREPLAY CLASS - Represents a scene that can be replayed
    # =========================================================================

    class SceneReplay:
        """
        Represents a scene that can be replayed from the gallery.

        Attributes:
            id (str): Unique identifier for the scene
            name (str): Display name of the scene
            label_name (str): Ren'Py label to call for replay
            unlocked (bool): Whether the scene has been unlocked
        """

        def __init__(self, id, name, label_name, unlocked=False):
            self.id = id
            self.name = name
            self.label_name = label_name
            self.unlocked = unlocked

        def unlock(self):
            """Unlock this scene for replay."""
            self.unlocked = True

        def lock(self):
            """Lock this scene."""
            self.unlocked = False

        def is_unlocked(self):
            """Check if this scene is unlocked."""
            return self.unlocked

        def __repr__(self):
            status = "unlocked" if self.unlocked else "locked"
            return f"SceneReplay({self.id}, {self.name}, {status})"

    # =========================================================================
    # GALLERYMANAGER CLASS - Central manager for all gallery content
    # =========================================================================

    class GalleryManager:
        """
        Central manager for tracking all gallery items, music tracks, and scenes.

        This class provides methods to register items, manage unlock states,
        query items by category, and track completion percentage.
        """

        def __init__(self):
            self.gallery_items = {}
            self.music_tracks = {}
            self.scene_replays = {}
            self._persistent_key_prefix = "gallery_"

        # ---------------------------------------------------------------------
        # Gallery Item Management
        # ---------------------------------------------------------------------

        def register_gallery_item(self, item):
            """
            Register a gallery item with the manager.

            Args:
                item (GalleryItem): The gallery item to register

            Returns:
                GalleryItem: The registered item
            """
            self.gallery_items[item.id] = item
            # Check persistent state
            self._load_persistent_state(item, "cg")
            return item

        def get_gallery_item(self, item_id):
            """Get a gallery item by ID."""
            return self.gallery_items.get(item_id, None)

        def get_all_gallery_items(self):
            """Get all registered gallery items."""
            return list(self.gallery_items.values())

        def get_gallery_items_by_category(self, category):
            """
            Get all gallery items in a specific category.

            Args:
                category (str): The category to filter by

            Returns:
                list: List of GalleryItem objects in the category
            """
            return [item for item in self.gallery_items.values()
                    if item.category == category]

        def get_unlocked_gallery_items(self):
            """Get all unlocked gallery items."""
            return [item for item in self.gallery_items.values() if item.unlocked]

        def get_locked_gallery_items(self):
            """Get all locked gallery items."""
            return [item for item in self.gallery_items.values() if not item.unlocked]

        def unlock_gallery_item(self, item_id):
            """
            Unlock a gallery item and save to persistent storage.

            Args:
                item_id (str): ID of the item to unlock

            Returns:
                bool: True if successfully unlocked, False if item not found
            """
            item = self.get_gallery_item(item_id)
            if item:
                item.unlock()
                self._save_persistent_state(item, "cg")
                return True
            return False

        # ---------------------------------------------------------------------
        # Music Track Management
        # ---------------------------------------------------------------------

        def register_music_track(self, track):
            """
            Register a music track with the manager.

            Args:
                track (MusicTrack): The music track to register

            Returns:
                MusicTrack: The registered track
            """
            self.music_tracks[track.id] = track
            # Check persistent state
            self._load_persistent_state(track, "music")
            return track

        def get_music_track(self, track_id):
            """Get a music track by ID."""
            return self.music_tracks.get(track_id, None)

        def get_all_music_tracks(self):
            """Get all registered music tracks."""
            return list(self.music_tracks.values())

        def get_unlocked_music_tracks(self):
            """Get all unlocked music tracks."""
            return [track for track in self.music_tracks.values() if track.unlocked]

        def get_locked_music_tracks(self):
            """Get all locked music tracks."""
            return [track for track in self.music_tracks.values() if not track.unlocked]

        def unlock_music_track(self, track_id):
            """
            Unlock a music track and save to persistent storage.

            Args:
                track_id (str): ID of the track to unlock

            Returns:
                bool: True if successfully unlocked, False if track not found
            """
            track = self.get_music_track(track_id)
            if track:
                track.unlock()
                self._save_persistent_state(track, "music")
                return True
            return False

        # ---------------------------------------------------------------------
        # Scene Replay Management
        # ---------------------------------------------------------------------

        def register_scene_replay(self, scene):
            """
            Register a scene replay with the manager.

            Args:
                scene (SceneReplay): The scene replay to register

            Returns:
                SceneReplay: The registered scene
            """
            self.scene_replays[scene.id] = scene
            # Check persistent state
            self._load_persistent_state(scene, "scene")
            return scene

        def get_scene_replay(self, scene_id):
            """Get a scene replay by ID."""
            return self.scene_replays.get(scene_id, None)

        def get_all_scene_replays(self):
            """Get all registered scene replays."""
            return list(self.scene_replays.values())

        def get_unlocked_scene_replays(self):
            """Get all unlocked scene replays."""
            return [scene for scene in self.scene_replays.values() if scene.unlocked]

        def get_locked_scene_replays(self):
            """Get all locked scene replays."""
            return [scene for scene in self.scene_replays.values() if not scene.unlocked]

        def unlock_scene_replay(self, scene_id):
            """
            Unlock a scene replay and save to persistent storage.

            Args:
                scene_id (str): ID of the scene to unlock

            Returns:
                bool: True if successfully unlocked, False if scene not found
            """
            scene = self.get_scene_replay(scene_id)
            if scene:
                scene.unlock()
                self._save_persistent_state(scene, "scene")
                return True
            return False

        # ---------------------------------------------------------------------
        # Completion Statistics
        # ---------------------------------------------------------------------

        def get_gallery_completion(self):
            """
            Get completion percentage for gallery items.

            Returns:
                float: Completion percentage (0.0 to 100.0)
            """
            total = len(self.gallery_items)
            if total == 0:
                return 0.0
            unlocked = len(self.get_unlocked_gallery_items())
            return (unlocked / total) * 100.0

        def get_music_completion(self):
            """
            Get completion percentage for music tracks.

            Returns:
                float: Completion percentage (0.0 to 100.0)
            """
            total = len(self.music_tracks)
            if total == 0:
                return 0.0
            unlocked = len(self.get_unlocked_music_tracks())
            return (unlocked / total) * 100.0

        def get_scene_completion(self):
            """
            Get completion percentage for scene replays.

            Returns:
                float: Completion percentage (0.0 to 100.0)
            """
            total = len(self.scene_replays)
            if total == 0:
                return 0.0
            unlocked = len(self.get_unlocked_scene_replays())
            return (unlocked / total) * 100.0

        def get_total_completion(self):
            """
            Get overall completion percentage across all content types.

            Returns:
                float: Overall completion percentage (0.0 to 100.0)
            """
            total_items = (len(self.gallery_items) +
                          len(self.music_tracks) +
                          len(self.scene_replays))
            if total_items == 0:
                return 0.0

            unlocked_items = (len(self.get_unlocked_gallery_items()) +
                             len(self.get_unlocked_music_tracks()) +
                             len(self.get_unlocked_scene_replays()))
            return (unlocked_items / total_items) * 100.0

        def get_category_completion(self, category):
            """
            Get completion percentage for a specific gallery category.

            Args:
                category (str): The category to check

            Returns:
                float: Completion percentage (0.0 to 100.0)
            """
            items = self.get_gallery_items_by_category(category)
            if not items:
                return 0.0
            unlocked = sum(1 for item in items if item.unlocked)
            return (unlocked / len(items)) * 100.0

        # ---------------------------------------------------------------------
        # Persistent Storage Helpers
        # ---------------------------------------------------------------------

        def _get_persistent_key(self, item, item_type):
            """Generate a persistent storage key for an item."""
            return f"{self._persistent_key_prefix}{item_type}_{item.id}"

        def _save_persistent_state(self, item, item_type):
            """Save an item's unlock state to persistent storage."""
            key = self._get_persistent_key(item, item_type)
            setattr(persistent, key, item.unlocked)

        def _load_persistent_state(self, item, item_type):
            """Load an item's unlock state from persistent storage."""
            key = self._get_persistent_key(item, item_type)
            stored_value = getattr(persistent, key, None)
            if stored_value is not None:
                item.unlocked = stored_value

        def sync_all_persistent_states(self):
            """Reload all items' states from persistent storage."""
            for item in self.gallery_items.values():
                self._load_persistent_state(item, "cg")
            for track in self.music_tracks.values():
                self._load_persistent_state(track, "music")
            for scene in self.scene_replays.values():
                self._load_persistent_state(scene, "scene")

        # ---------------------------------------------------------------------
        # Utility Methods
        # ---------------------------------------------------------------------

        def get_available_categories(self):
            """Get list of categories that have registered items."""
            categories = set()
            for item in self.gallery_items.values():
                categories.add(item.category)
            return sorted(list(categories))

        def clear_all(self):
            """Clear all registered items (for testing purposes)."""
            self.gallery_items.clear()
            self.music_tracks.clear()
            self.scene_replays.clear()

# =============================================================================
# GLOBAL GALLERY MANAGER INSTANCE
# =============================================================================

default gallery_manager = GalleryManager()

# =============================================================================
# GALLERY STATE VARIABLES
# =============================================================================

default gallery_current_category = "all"
default gallery_current_image = None
default music_player_current_track = None
default music_player_playing = False

# =============================================================================
# EXAMPLE GALLERY CONTENT REGISTRATION
# =============================================================================

init python:
    def setup_example_gallery():
        """Initialize example gallery content."""

        # Example CG images
        cg1 = GalleryItem(
            id="cg_elena_meeting",
            name="First Meeting with Elena",
            image_path="images/cg/elena_meeting.png",
            thumbnail="images/cg/thumbs/elena_meeting_thumb.png",
            category="event"
        )

        cg2 = GalleryItem(
            id="cg_elena_confession",
            name="Elena's Confession",
            image_path="images/cg/elena_confession.png",
            thumbnail="images/cg/thumbs/elena_confession_thumb.png",
            category="event"
        )

        cg3 = GalleryItem(
            id="cg_market_scene",
            name="The Market Square",
            image_path="images/cg/market_scene.png",
            thumbnail="images/cg/thumbs/market_scene_thumb.png",
            category="scene"
        )

        cg4 = GalleryItem(
            id="cg_ending_good",
            name="Good Ending",
            image_path="images/cg/ending_good.png",
            thumbnail="images/cg/thumbs/ending_good_thumb.png",
            category="ending"
        )

        cg5 = GalleryItem(
            id="bg_forest",
            name="Enchanted Forest",
            image_path="images/bg/forest.png",
            thumbnail="images/bg/thumbs/forest_thumb.png",
            category="background"
        )

        # Register CGs
        gallery_manager.register_gallery_item(cg1)
        gallery_manager.register_gallery_item(cg2)
        gallery_manager.register_gallery_item(cg3)
        gallery_manager.register_gallery_item(cg4)
        gallery_manager.register_gallery_item(cg5)

        # Example music tracks
        track1 = MusicTrack(
            id="bgm_main_theme",
            name="Main Theme",
            file_path="audio/bgm/main_theme.ogg"
        )

        track2 = MusicTrack(
            id="bgm_peaceful",
            name="Peaceful Days",
            file_path="audio/bgm/peaceful.ogg"
        )

        track3 = MusicTrack(
            id="bgm_battle",
            name="Battle Theme",
            file_path="audio/bgm/battle.ogg"
        )

        # Register music tracks
        gallery_manager.register_music_track(track1)
        gallery_manager.register_music_track(track2)
        gallery_manager.register_music_track(track3)

        # Example scene replays
        scene1 = SceneReplay(
            id="scene_prologue",
            name="Prologue",
            label_name="prologue_replay"
        )

        scene2 = SceneReplay(
            id="scene_elena_route_start",
            name="Elena's Route - Beginning",
            label_name="elena_route_start_replay"
        )

        scene3 = SceneReplay(
            id="scene_finale",
            name="The Finale",
            label_name="finale_replay"
        )

        # Register scene replays
        gallery_manager.register_scene_replay(scene1)
        gallery_manager.register_scene_replay(scene2)
        gallery_manager.register_scene_replay(scene3)

# =============================================================================
# CG GALLERY SCREEN - Grid view of all CG images
# =============================================================================

screen cg_gallery_screen():
    tag menu

    use game_menu(_("CG Gallery"), scroll="viewport"):

        style_prefix "gallery"

        vbox:
            spacing 20

            # Completion bar
            hbox:
                xfill True
                text "Gallery Completion: " size 20 color "#ffffff"
                $ completion = gallery_manager.get_gallery_completion()
                text "{:.1f}%".format(completion) size 20 color "#66ff66"

            null height 10

            # Category filter buttons
            hbox:
                spacing 10
                textbutton "All" action SetVariable("gallery_current_category", "all"):
                    style "gallery_category_button"
                    if gallery_current_category == "all":
                        background "#4444aa"

                for cat_id, cat_name in GALLERY_CATEGORIES.items():
                    $ cat_items = gallery_manager.get_gallery_items_by_category(cat_id)
                    if cat_items:
                        textbutton cat_name action SetVariable("gallery_current_category", cat_id):
                            style "gallery_category_button"
                            if gallery_current_category == cat_id:
                                background "#4444aa"

            null height 20

            # CG grid
            grid 4 None:
                spacing 15
                xfill True

                if gallery_current_category == "all":
                    $ display_items = gallery_manager.get_all_gallery_items()
                else:
                    $ display_items = gallery_manager.get_gallery_items_by_category(gallery_current_category)

                for item in display_items:
                    button:
                        xysize (180, 135)
                        if item.unlocked:
                            background "#333333"
                            action [SetVariable("gallery_current_image", item), ShowMenu("image_viewer_screen")]
                            hovered tt.Action(item.name)

                            # Thumbnail
                            add item.thumbnail fit "contain" align (0.5, 0.5)
                        else:
                            background "#222222"
                            action NullAction()

                            # Locked placeholder
                            frame:
                                xysize (180, 135)
                                background "#1a1a1a"
                                text "?" align (0.5, 0.5) size 40 color "#444444"

# =============================================================================
# IMAGE VIEWER SCREEN - Fullscreen image display
# =============================================================================

screen image_viewer_screen():
    tag menu
    modal True

    if gallery_current_image:
        # Fullscreen image
        add gallery_current_image.image_path fit "contain" align (0.5, 0.5)

        # Image name overlay
        frame:
            xalign 0.5
            yalign 0.0
            padding (20, 10)
            background "#000000aa"

            text gallery_current_image.name size 24 color "#ffffff"

        # Navigation buttons
        hbox:
            xalign 0.5
            yalign 1.0
            yoffset -20
            spacing 20

            textbutton "Previous" action Function(gallery_navigate_image, -1):
                style "gallery_nav_button"

            textbutton "Close" action Return():
                style "gallery_nav_button"

            textbutton "Next" action Function(gallery_navigate_image, 1):
                style "gallery_nav_button"

        # Keyboard navigation
        key "K_LEFT" action Function(gallery_navigate_image, -1)
        key "K_RIGHT" action Function(gallery_navigate_image, 1)
        key "K_ESCAPE" action Return()

init python:
    def gallery_navigate_image(direction):
        """Navigate to previous/next unlocked image."""
        global gallery_current_image

        unlocked = gallery_manager.get_unlocked_gallery_items()
        if not unlocked or gallery_current_image not in unlocked:
            return

        current_idx = unlocked.index(gallery_current_image)
        new_idx = (current_idx + direction) % len(unlocked)
        gallery_current_image = unlocked[new_idx]

# =============================================================================
# MUSIC PLAYER SCREEN - Music selection and playback
# =============================================================================

screen music_player_screen():
    tag menu

    use game_menu(_("Music Player"), scroll="viewport"):

        style_prefix "music"

        vbox:
            spacing 20

            # Completion bar
            hbox:
                xfill True
                text "Music Unlocked: " size 20 color "#ffffff"
                $ completion = gallery_manager.get_music_completion()
                text "{:.1f}%".format(completion) size 20 color "#66ff66"

            null height 10

            # Now playing display
            frame:
                xfill True
                padding (20, 15)
                background "#333355"

                vbox:
                    spacing 10

                    text "Now Playing:" size 18 color "#aaaaaa"

                    if music_player_current_track:
                        text music_player_current_track.name size 28 color "#ffffff"
                    else:
                        text "No track selected" size 28 color "#666666"

                    # Playback controls
                    hbox:
                        xalign 0.5
                        spacing 30

                        textbutton "Stop" action Function(music_player_stop):
                            style "music_control_button"

                        if music_player_playing:
                            textbutton "Pause" action Function(music_player_pause):
                                style "music_control_button"
                        else:
                            textbutton "Play" action Function(music_player_play):
                                style "music_control_button"

            null height 20

            # Track list
            text "Available Tracks" size 24 color "#ffffff"

            null height 10

            for track in gallery_manager.get_all_music_tracks():
                frame:
                    xfill True
                    padding (15, 10)

                    if track.unlocked:
                        background "#333333"
                        hbox:
                            spacing 20

                            # Play button
                            textbutton ">" action Function(music_player_select, track):
                                style "music_play_button"
                                if music_player_current_track == track and music_player_playing:
                                    text_color "#66ff66"

                            # Track name
                            text track.name size 20 color "#ffffff" yalign 0.5

                            # Currently playing indicator
                            if music_player_current_track == track and music_player_playing:
                                text "(Playing)" size 16 color "#66ff66" yalign 0.5
                    else:
                        background "#222222"
                        hbox:
                            spacing 20
                            text "?" size 20 color "#444444"
                            text "Locked" size 20 color "#444444" yalign 0.5

init python:
    def music_player_select(track):
        """Select and play a music track."""
        global music_player_current_track, music_player_playing

        music_player_current_track = track
        music_player_playing = True
        renpy.music.play(track.file_path, channel="music", loop=True)

    def music_player_play():
        """Resume playing the current track."""
        global music_player_playing

        if music_player_current_track:
            music_player_playing = True
            renpy.music.play(music_player_current_track.file_path, channel="music", loop=True)

    def music_player_pause():
        """Pause the current track."""
        global music_player_playing

        music_player_playing = False
        renpy.music.stop(channel="music", fadeout=0.5)

    def music_player_stop():
        """Stop the current track."""
        global music_player_current_track, music_player_playing

        music_player_current_track = None
        music_player_playing = False
        renpy.music.stop(channel="music", fadeout=0.5)

# =============================================================================
# SCENE REPLAY SCREEN - Scene selection for replay
# =============================================================================

screen scene_replay_screen():
    tag menu

    use game_menu(_("Scene Replay"), scroll="viewport"):

        style_prefix "scene"

        vbox:
            spacing 20

            # Completion bar
            hbox:
                xfill True
                text "Scenes Unlocked: " size 20 color "#ffffff"
                $ completion = gallery_manager.get_scene_completion()
                text "{:.1f}%".format(completion) size 20 color "#66ff66"

            null height 20

            # Scene list
            for scene in gallery_manager.get_all_scene_replays():
                frame:
                    xfill True
                    padding (20, 15)

                    if scene.unlocked:
                        background "#333333"
                        hbox:
                            spacing 20

                            # Scene name
                            text scene.name size 22 color "#ffffff" xfill True yalign 0.5

                            # Replay button
                            textbutton "Replay" action Function(scene_replay_start, scene):
                                style "scene_replay_button"
                    else:
                        background "#222222"
                        hbox:
                            spacing 20
                            text "???" size 22 color "#444444" xfill True yalign 0.5
                            text "Locked" size 18 color "#444444" yalign 0.5

init python:
    def scene_replay_start(scene):
        """Start replaying a scene."""
        renpy.call_in_new_context(scene.label_name)

# =============================================================================
# GALLERY HUB SCREEN - Main gallery menu
# =============================================================================

screen gallery_hub_screen():
    tag menu

    use game_menu(_("Gallery"), scroll="viewport"):

        style_prefix "gallery_hub"

        vbox:
            spacing 30

            # Total completion
            frame:
                xfill True
                padding (20, 15)
                background "#333355"

                hbox:
                    xfill True
                    text "Total Completion: " size 24 color "#ffffff"
                    $ total_completion = gallery_manager.get_total_completion()
                    text "{:.1f}%".format(total_completion) size 24 color "#66ff66"

            null height 20

            # Gallery sections
            vbox:
                spacing 20

                # CG Gallery
                button:
                    xfill True
                    padding (20, 20)
                    background "#333333"
                    hover_background "#444444"
                    action ShowMenu("cg_gallery_screen")

                    hbox:
                        spacing 20

                        # Icon placeholder
                        frame:
                            xysize (60, 60)
                            background "#555555"
                            text "CG" align (0.5, 0.5) size 20 color "#ffffff"

                        vbox:
                            text "CG Gallery" size 24 color "#ffffff"
                            $ cg_count = len(gallery_manager.get_unlocked_gallery_items())
                            $ cg_total = len(gallery_manager.get_all_gallery_items())
                            text "[cg_count]/[cg_total] unlocked" size 16 color "#aaaaaa"

                # Music Player
                button:
                    xfill True
                    padding (20, 20)
                    background "#333333"
                    hover_background "#444444"
                    action ShowMenu("music_player_screen")

                    hbox:
                        spacing 20

                        frame:
                            xysize (60, 60)
                            background "#555555"
                            text "BGM" align (0.5, 0.5) size 18 color "#ffffff"

                        vbox:
                            text "Music Player" size 24 color "#ffffff"
                            $ music_count = len(gallery_manager.get_unlocked_music_tracks())
                            $ music_total = len(gallery_manager.get_all_music_tracks())
                            text "[music_count]/[music_total] unlocked" size 16 color "#aaaaaa"

                # Scene Replay
                button:
                    xfill True
                    padding (20, 20)
                    background "#333333"
                    hover_background "#444444"
                    action ShowMenu("scene_replay_screen")

                    hbox:
                        spacing 20

                        frame:
                            xysize (60, 60)
                            background "#555555"
                            text "SCN" align (0.5, 0.5) size 18 color "#ffffff"

                        vbox:
                            text "Scene Replay" size 24 color "#ffffff"
                            $ scene_count = len(gallery_manager.get_unlocked_scene_replays())
                            $ scene_total = len(gallery_manager.get_all_scene_replays())
                            text "[scene_count]/[scene_total] unlocked" size 16 color "#aaaaaa"

# =============================================================================
# GALLERY STYLES
# =============================================================================

style gallery_category_button:
    background "#333355"
    hover_background "#4444aa"
    padding (15, 8)

style gallery_category_button_text:
    color "#cccccc"
    hover_color "#ffffff"
    size 16

style gallery_nav_button:
    background "#333355"
    hover_background "#4444aa"
    padding (20, 10)

style gallery_nav_button_text:
    color "#cccccc"
    hover_color "#ffffff"
    size 20

style music_control_button:
    background "#333355"
    hover_background "#4444aa"
    padding (25, 10)

style music_control_button_text:
    color "#cccccc"
    hover_color "#ffffff"
    size 18

style music_play_button:
    background "#444466"
    hover_background "#5555aa"
    padding (10, 5)

style music_play_button_text:
    color "#ffffff"
    size 20

style scene_replay_button:
    background "#335533"
    hover_background "#447744"
    padding (15, 8)

style scene_replay_button_text:
    color "#ffffff"
    hover_color "#ffffff"
    size 16

# =============================================================================
# HELPER LABELS FOR UNLOCKING CONTENT
# =============================================================================

# Unlock a CG and optionally show it
label unlock_cg(cg_id, show_image=False):
    $ gallery_manager.unlock_gallery_item(cg_id)
    if show_image:
        $ item = gallery_manager.get_gallery_item(cg_id)
        if item:
            show expression item.image_path
            pause
            hide expression item.image_path
    return

# Unlock a music track
label unlock_music(track_id):
    $ gallery_manager.unlock_music_track(track_id)
    return

# Unlock a scene replay
label unlock_scene(scene_id):
    $ gallery_manager.unlock_scene_replay(scene_id)
    return

# =============================================================================
# EXAMPLE USAGE IN GAME SCRIPT
# =============================================================================

# Example showing how to unlock content during gameplay:
#
# label elena_meeting:
#     # Unlock the CG and display it
#     call unlock_cg("cg_elena_meeting", show_image=True)
#
#     "You meet Elena for the first time..."
#
#     # Unlock associated music when heard
#     call unlock_music("bgm_peaceful")
#
#     # At the end of important scenes, unlock replay
#     call unlock_scene("scene_elena_route_start")
#
#     return
#
# To open the gallery from the main menu:
#     textbutton "Gallery" action ShowMenu("gallery_hub_screen")

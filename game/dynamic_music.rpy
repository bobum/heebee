# Dynamic Music System for Heebee Visual Novel
# Provides layered, context-aware music with smooth transitions

init python:
    import time

    class MusicLayer:
        """
        Represents a single music layer that can be mixed with other layers.

        Attributes:
            id (str): Unique identifier for this layer
            file_path (str): Path to the audio file
            volume (float): Current volume level (0.0 to 1.0)
            active (bool): Whether this layer is currently playing
            base_volume (float): The baseline volume before intensity scaling
        """

        def __init__(self, id, file_path, volume=1.0, active=False):
            """
            Initialize a music layer.

            Args:
                id (str): Unique identifier for this layer
                file_path (str): Path to the audio file
                volume (float): Initial volume level (0.0 to 1.0)
                active (bool): Whether to start active
            """
            self.id = id
            self.file_path = file_path
            self.volume = max(0.0, min(1.0, volume))
            self.base_volume = self.volume
            self.active = active

        def set_volume(self, volume):
            """Set the layer's volume, clamped between 0.0 and 1.0."""
            self.volume = max(0.0, min(1.0, volume))

        def activate(self):
            """Activate this layer."""
            self.active = True

        def deactivate(self):
            """Deactivate this layer."""
            self.active = False

        def __repr__(self):
            return f"MusicLayer(id='{self.id}', file_path='{self.file_path}', volume={self.volume}, active={self.active})"


    class MusicManager:
        """
        Manages dynamic music playback with layered tracks and context awareness.

        Features:
        - Multiple simultaneous music layers
        - Smooth crossfades between tracks
        - Context-aware music selection
        - Intensity scaling for dynamic volume
        - Music ducking for dialogue

        Contexts:
            calm, tension, combat, romance, mystery, celebration, sadness
        """

        # Default context configurations
        # Maps context names to lists of layer IDs that should be active
        DEFAULT_CONTEXT_LAYERS = {
            "calm": ["base", "ambient"],
            "tension": ["base", "tension", "percussion"],
            "combat": ["base", "combat", "percussion", "intensity"],
            "romance": ["base", "melody", "strings"],
            "mystery": ["base", "ambient", "mystery"],
            "celebration": ["base", "melody", "percussion", "celebration"],
            "sadness": ["base", "ambient", "strings", "melancholy"],
        }

        # Intensity ranges for each context (min, max multiplier)
        CONTEXT_INTENSITY_RANGE = {
            "calm": (0.3, 0.7),
            "tension": (0.5, 1.0),
            "combat": (0.7, 1.0),
            "romance": (0.4, 0.8),
            "mystery": (0.3, 0.8),
            "celebration": (0.6, 1.0),
            "sadness": (0.2, 0.6),
        }

        def __init__(self):
            """Initialize the music manager."""
            self.layers = {}  # Dict of layer_id -> MusicLayer
            self.current_context = "calm"
            self.current_track = None
            self.intensity = 0.5  # 0.0 to 1.0
            self.master_volume = 1.0
            self.is_ducked = False
            self.duck_volume = 0.3  # Volume multiplier when ducked
            self.context_layers = dict(self.DEFAULT_CONTEXT_LAYERS)
            self._fade_in_progress = False
            self._pending_track = None
            self._transition_start_time = None
            self._transition_duration = 0

        def add_layer(self, layer_id, file_path, volume=1.0, active=False):
            """
            Add a new music layer.

            Args:
                layer_id (str): Unique identifier for the layer
                file_path (str): Path to the audio file
                volume (float): Initial volume (0.0 to 1.0)
                active (bool): Whether to start active

            Returns:
                MusicLayer: The created layer

            Raises:
                ValueError: If a layer with this ID already exists
            """
            if layer_id in self.layers:
                raise ValueError(f"Layer '{layer_id}' already exists")

            layer = MusicLayer(layer_id, file_path, volume, active)
            self.layers[layer_id] = layer
            return layer

        def remove_layer(self, layer_id):
            """
            Remove a music layer.

            Args:
                layer_id (str): ID of the layer to remove

            Returns:
                MusicLayer: The removed layer

            Raises:
                KeyError: If the layer doesn't exist
            """
            if layer_id not in self.layers:
                raise KeyError(f"Layer '{layer_id}' not found")

            layer = self.layers.pop(layer_id)
            # Stop playback in Ren'Py if running
            self._stop_layer_playback(layer)
            return layer

        def get_layer(self, layer_id):
            """
            Get a layer by ID.

            Args:
                layer_id (str): ID of the layer

            Returns:
                MusicLayer: The layer, or None if not found
            """
            return self.layers.get(layer_id)

        def set_context(self, context):
            """
            Set the current music context, activating appropriate layers.

            Args:
                context (str): The context name (calm, tension, combat, etc.)

            Raises:
                ValueError: If the context is not recognized
            """
            if context not in self.context_layers:
                raise ValueError(f"Unknown context: '{context}'. Valid contexts: {list(self.context_layers.keys())}")

            self.current_context = context
            target_layers = self.context_layers[context]

            # Deactivate all layers first
            for layer in self.layers.values():
                layer.deactivate()

            # Activate layers for this context
            for layer_id in target_layers:
                if layer_id in self.layers:
                    self.layers[layer_id].activate()

            # Apply intensity scaling for this context
            self._apply_intensity()

            # Update Ren'Py playback
            self._update_playback()

        def add_context(self, context_name, layer_ids, intensity_range=(0.3, 1.0)):
            """
            Add a custom context configuration.

            Args:
                context_name (str): Name for the new context
                layer_ids (list): List of layer IDs to activate for this context
                intensity_range (tuple): (min, max) intensity multipliers
            """
            self.context_layers[context_name] = list(layer_ids)
            self.CONTEXT_INTENSITY_RANGE[context_name] = intensity_range

        def set_intensity(self, level):
            """
            Set the intensity level, affecting volume of active layers.

            Args:
                level (float): Intensity from 0.0 (minimal) to 1.0 (maximum)
            """
            self.intensity = max(0.0, min(1.0, level))
            self._apply_intensity()
            self._update_playback()

        def _apply_intensity(self):
            """Apply intensity scaling to all active layers based on context."""
            if self.current_context in self.CONTEXT_INTENSITY_RANGE:
                min_mult, max_mult = self.CONTEXT_INTENSITY_RANGE[self.current_context]
            else:
                min_mult, max_mult = 0.3, 1.0

            # Calculate the actual multiplier based on intensity
            multiplier = min_mult + (max_mult - min_mult) * self.intensity

            for layer in self.layers.values():
                if layer.active:
                    # Scale volume from base_volume
                    layer.volume = layer.base_volume * multiplier

        def fade_to(self, track, duration=2.0):
            """
            Crossfade to a new track.

            Args:
                track (str): Path to the new track, or None to fade out
                duration (float): Fade duration in seconds

            Returns:
                bool: True if fade started successfully
            """
            if duration <= 0:
                duration = 0.1  # Minimum duration

            self._fade_in_progress = True
            self._pending_track = track
            self._transition_start_time = time.time()
            self._transition_duration = duration

            # In Ren'Py, this would use renpy.music.play with fadeout/fadein
            self._perform_crossfade(track, duration)

            self.current_track = track
            self._fade_in_progress = False
            return True

        def _perform_crossfade(self, track, duration):
            """
            Perform the actual crossfade. Overridden in Ren'Py environment.

            Args:
                track (str): New track path
                duration (float): Fade duration
            """
            # In testing, this is a no-op
            # In Ren'Py, this calls renpy.music.play()
            try:
                if track:
                    renpy.music.play(track, fadeout=duration, fadein=duration)
                else:
                    renpy.music.stop(fadeout=duration)
            except NameError:
                # Not in Ren'Py environment (testing)
                pass

        def duck_music(self, enable=True):
            """
            Enable or disable music ducking (volume reduction during dialogue).

            Args:
                enable (bool): True to duck, False to restore
            """
            self.is_ducked = enable
            self._update_playback()

        def set_duck_volume(self, volume):
            """
            Set the volume multiplier used when ducking.

            Args:
                volume (float): Volume multiplier (0.0 to 1.0)
            """
            self.duck_volume = max(0.0, min(1.0, volume))

        def set_master_volume(self, volume):
            """
            Set the master volume for all music.

            Args:
                volume (float): Master volume (0.0 to 1.0)
            """
            self.master_volume = max(0.0, min(1.0, volume))
            self._update_playback()

        def get_effective_volume(self, layer_id):
            """
            Get the effective volume of a layer after all modifiers.

            Args:
                layer_id (str): ID of the layer

            Returns:
                float: Effective volume, or 0.0 if layer not found/inactive
            """
            layer = self.layers.get(layer_id)
            if not layer or not layer.active:
                return 0.0

            volume = layer.volume * self.master_volume
            if self.is_ducked:
                volume *= self.duck_volume
            return volume

        def get_active_layers(self):
            """
            Get all currently active layers.

            Returns:
                list: List of active MusicLayer objects
            """
            return [layer for layer in self.layers.values() if layer.active]

        def _update_playback(self):
            """Update Ren'Py music playback based on current state."""
            try:
                for layer in self.layers.values():
                    if layer.active:
                        effective_volume = self.get_effective_volume(layer.id)
                        # In Ren'Py, we'd update the channel volume
                        # renpy.music.set_volume(effective_volume, channel=layer.id)
            except NameError:
                # Not in Ren'Py environment
                pass

        def _stop_layer_playback(self, layer):
            """Stop playback of a specific layer."""
            try:
                # In Ren'Py, we'd stop the channel
                # renpy.music.stop(channel=layer.id)
                pass
            except NameError:
                pass

        def reset(self):
            """Reset the music manager to initial state."""
            for layer in list(self.layers.values()):
                self.remove_layer(layer.id)
            self.layers = {}
            self.current_context = "calm"
            self.current_track = None
            self.intensity = 0.5
            self.master_volume = 1.0
            self.is_ducked = False
            self._fade_in_progress = False

        def get_state(self):
            """
            Get the current state of the music manager.

            Returns:
                dict: Current state information
            """
            return {
                "context": self.current_context,
                "track": self.current_track,
                "intensity": self.intensity,
                "master_volume": self.master_volume,
                "is_ducked": self.is_ducked,
                "layers": {
                    layer_id: {
                        "file_path": layer.file_path,
                        "volume": layer.volume,
                        "active": layer.active,
                        "effective_volume": self.get_effective_volume(layer_id)
                    }
                    for layer_id, layer in self.layers.items()
                }
            }


# Create the global music manager instance
default music_manager = MusicManager()

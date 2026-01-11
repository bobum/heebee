# Weather/Atmosphere System for Ren'Py Visual Novel
# This module provides comprehensive weather state management with visual effects,
# transitions, ambient sounds, and gameplay modifiers.

init python:
    import random
    import math

    # =========================================================================
    # WEATHER TYPES - Constants for weather conditions
    # =========================================================================

    class WeatherType:
        """
        Enumeration of available weather types.
        Each type has associated visual effects, sounds, and gameplay modifiers.
        """
        SUNNY = "sunny"
        CLOUDY = "cloudy"
        RAIN = "rain"
        SNOW = "snow"
        FOG = "fog"
        STORM = "storm"
        CLEAR = "clear"  # Night clear sky

        @classmethod
        def all_types(cls):
            """Return list of all weather types."""
            return [cls.SUNNY, cls.CLOUDY, cls.RAIN, cls.SNOW, cls.FOG, cls.STORM, cls.CLEAR]

        @classmethod
        def is_valid(cls, weather_type):
            """Check if a weather type is valid."""
            return weather_type in cls.all_types()

    # =========================================================================
    # SEASON TYPES - Optional seasonal support
    # =========================================================================

    class Season:
        """Enumeration of seasons affecting weather probabilities."""
        SPRING = "spring"
        SUMMER = "summer"
        AUTUMN = "autumn"
        WINTER = "winter"

        @classmethod
        def all_seasons(cls):
            """Return list of all seasons."""
            return [cls.SPRING, cls.SUMMER, cls.AUTUMN, cls.WINTER]

        @classmethod
        def is_valid(cls, season):
            """Check if a season is valid."""
            return season in cls.all_seasons()

    # =========================================================================
    # WEATHER CONFIGURATION - Settings for each weather type
    # =========================================================================

    WEATHER_CONFIG = {
        WeatherType.SUNNY: {
            "label": "Sunny",
            "description": "Clear skies with bright sunshine",
            "icon": "weather_sunny",
            "ambient_sound": "audio/ambient/birds_chirping.ogg",
            "overlay_alpha": 0.0,
            "tint_color": "#ffffcc",
            "modifiers": {
                "mood": 10,
                "energy": 5,
                "visibility": 100
            },
            "particle_effect": None,
            "transition_time": 2.0
        },
        WeatherType.CLOUDY: {
            "label": "Cloudy",
            "description": "Overcast skies with gray clouds",
            "icon": "weather_cloudy",
            "ambient_sound": "audio/ambient/wind_light.ogg",
            "overlay_alpha": 0.2,
            "tint_color": "#cccccc",
            "modifiers": {
                "mood": 0,
                "energy": 0,
                "visibility": 80
            },
            "particle_effect": None,
            "transition_time": 3.0
        },
        WeatherType.RAIN: {
            "label": "Rain",
            "description": "Steady rainfall with puddles forming",
            "icon": "weather_rain",
            "ambient_sound": "audio/ambient/rain_medium.ogg",
            "overlay_alpha": 0.3,
            "tint_color": "#8899aa",
            "modifiers": {
                "mood": -5,
                "energy": -5,
                "visibility": 60
            },
            "particle_effect": "rain_particles",
            "transition_time": 4.0
        },
        WeatherType.SNOW: {
            "label": "Snow",
            "description": "Gentle snowfall blanketing the world",
            "icon": "weather_snow",
            "ambient_sound": "audio/ambient/wind_soft.ogg",
            "overlay_alpha": 0.25,
            "tint_color": "#eeeeff",
            "modifiers": {
                "mood": 5,
                "energy": -10,
                "visibility": 50
            },
            "particle_effect": "snow_particles",
            "transition_time": 5.0
        },
        WeatherType.FOG: {
            "label": "Fog",
            "description": "Thick fog reducing visibility",
            "icon": "weather_fog",
            "ambient_sound": "audio/ambient/silence_eerie.ogg",
            "overlay_alpha": 0.5,
            "tint_color": "#aaaaaa",
            "modifiers": {
                "mood": -10,
                "energy": 0,
                "visibility": 20
            },
            "particle_effect": "fog_overlay",
            "transition_time": 6.0
        },
        WeatherType.STORM: {
            "label": "Storm",
            "description": "Heavy rain with thunder and lightning",
            "icon": "weather_storm",
            "ambient_sound": "audio/ambient/storm_thunder.ogg",
            "overlay_alpha": 0.4,
            "tint_color": "#667788",
            "modifiers": {
                "mood": -15,
                "energy": -10,
                "visibility": 30
            },
            "particle_effect": "storm_particles",
            "transition_time": 3.0
        },
        WeatherType.CLEAR: {
            "label": "Clear Night",
            "description": "Clear night sky with stars visible",
            "icon": "weather_clear_night",
            "ambient_sound": "audio/ambient/crickets_night.ogg",
            "overlay_alpha": 0.1,
            "tint_color": "#334455",
            "modifiers": {
                "mood": 5,
                "energy": 0,
                "visibility": 70
            },
            "particle_effect": None,
            "transition_time": 4.0
        }
    }

    # =========================================================================
    # SEASONAL WEATHER PROBABILITIES
    # =========================================================================

    SEASONAL_WEATHER_WEIGHTS = {
        Season.SPRING: {
            WeatherType.SUNNY: 25,
            WeatherType.CLOUDY: 30,
            WeatherType.RAIN: 30,
            WeatherType.SNOW: 5,
            WeatherType.FOG: 5,
            WeatherType.STORM: 5
        },
        Season.SUMMER: {
            WeatherType.SUNNY: 50,
            WeatherType.CLOUDY: 20,
            WeatherType.RAIN: 10,
            WeatherType.SNOW: 0,
            WeatherType.FOG: 5,
            WeatherType.STORM: 15
        },
        Season.AUTUMN: {
            WeatherType.SUNNY: 20,
            WeatherType.CLOUDY: 35,
            WeatherType.RAIN: 25,
            WeatherType.SNOW: 5,
            WeatherType.FOG: 10,
            WeatherType.STORM: 5
        },
        Season.WINTER: {
            WeatherType.SUNNY: 15,
            WeatherType.CLOUDY: 25,
            WeatherType.RAIN: 10,
            WeatherType.SNOW: 35,
            WeatherType.FOG: 10,
            WeatherType.STORM: 5
        }
    }

    # =========================================================================
    # TIME OF DAY SUPPORT
    # =========================================================================

    class TimeOfDay:
        """Time periods affecting weather appearance."""
        DAWN = "dawn"
        MORNING = "morning"
        NOON = "noon"
        AFTERNOON = "afternoon"
        DUSK = "dusk"
        NIGHT = "night"

        @classmethod
        def all_times(cls):
            """Return list of all time periods."""
            return [cls.DAWN, cls.MORNING, cls.NOON, cls.AFTERNOON, cls.DUSK, cls.NIGHT]

        @classmethod
        def is_valid(cls, time_of_day):
            """Check if a time of day is valid."""
            return time_of_day in cls.all_times()

    TIME_TINT_MODIFIERS = {
        TimeOfDay.DAWN: "#ffddcc",
        TimeOfDay.MORNING: "#ffffff",
        TimeOfDay.NOON: "#ffffee",
        TimeOfDay.AFTERNOON: "#fff8e0",
        TimeOfDay.DUSK: "#ffccaa",
        TimeOfDay.NIGHT: "#334466"
    }

    # =========================================================================
    # WEATHER MANAGER CLASS
    # =========================================================================

    class WeatherManager:
        """
        Central manager for weather state, transitions, and effects.

        Attributes:
            current_weather (str): Current weather type
            previous_weather (str): Previous weather type (for transitions)
            current_season (str): Current season
            current_time (str): Current time of day
            is_transitioning (bool): Whether weather is currently transitioning
            transition_progress (float): Progress of current transition (0.0-1.0)
            weather_history (list): Log of weather changes
            callbacks (list): Functions to call on weather change
        """

        def __init__(self, initial_weather=None, initial_season=None, initial_time=None):
            """
            Initialize the WeatherManager.

            Args:
                initial_weather (str): Starting weather type (default: SUNNY)
                initial_season (str): Starting season (default: SPRING)
                initial_time (str): Starting time of day (default: MORNING)
            """
            self._current_weather = initial_weather or WeatherType.SUNNY
            self.previous_weather = None
            self._current_season = initial_season or Season.SPRING
            self._current_time = initial_time or TimeOfDay.MORNING
            self.is_transitioning = False
            self.transition_progress = 0.0
            self.transition_target = None
            self.transition_duration = 0.0
            self.weather_history = []
            self.callbacks = []
            self._effects_enabled = True
            self._sounds_enabled = True

        # ---------------------------------------------------------------------
        # Properties
        # ---------------------------------------------------------------------

        @property
        def current_weather(self):
            """Get the current weather type."""
            return self._current_weather

        @current_weather.setter
        def current_weather(self, value):
            """Set the current weather type with validation."""
            if WeatherType.is_valid(value):
                self._current_weather = value
            else:
                raise ValueError(f"Invalid weather type: {value}")

        @property
        def current_season(self):
            """Get the current season."""
            return self._current_season

        @current_season.setter
        def current_season(self, value):
            """Set the current season with validation."""
            if Season.is_valid(value):
                self._current_season = value
            else:
                raise ValueError(f"Invalid season: {value}")

        @property
        def current_time(self):
            """Get the current time of day."""
            return self._current_time

        @current_time.setter
        def current_time(self, value):
            """Set the current time of day with validation."""
            if TimeOfDay.is_valid(value):
                self._current_time = value
            else:
                raise ValueError(f"Invalid time of day: {value}")

        # ---------------------------------------------------------------------
        # Weather Configuration Access
        # ---------------------------------------------------------------------

        def get_weather_config(self, weather_type=None):
            """
            Get configuration for a weather type.

            Args:
                weather_type (str): Weather type to get config for (default: current)

            Returns:
                dict: Weather configuration dictionary
            """
            wtype = weather_type or self._current_weather
            return WEATHER_CONFIG.get(wtype, WEATHER_CONFIG[WeatherType.SUNNY])

        def get_weather_label(self, weather_type=None):
            """Get display label for weather type."""
            return self.get_weather_config(weather_type).get("label", "Unknown")

        def get_weather_description(self, weather_type=None):
            """Get description for weather type."""
            return self.get_weather_config(weather_type).get("description", "")

        def get_ambient_sound(self, weather_type=None):
            """Get ambient sound path for weather type."""
            return self.get_weather_config(weather_type).get("ambient_sound", "")

        def get_modifiers(self, weather_type=None):
            """Get gameplay modifiers for weather type."""
            return self.get_weather_config(weather_type).get("modifiers", {})

        def get_modifier(self, modifier_name, weather_type=None):
            """Get a specific modifier value."""
            modifiers = self.get_modifiers(weather_type)
            return modifiers.get(modifier_name, 0)

        def get_overlay_alpha(self, weather_type=None):
            """Get overlay alpha value for weather type."""
            return self.get_weather_config(weather_type).get("overlay_alpha", 0.0)

        def get_tint_color(self, weather_type=None):
            """Get tint color for weather type."""
            return self.get_weather_config(weather_type).get("tint_color", "#ffffff")

        def get_combined_tint(self):
            """Get combined tint from weather and time of day."""
            weather_tint = self.get_tint_color()
            time_tint = TIME_TINT_MODIFIERS.get(self._current_time, "#ffffff")
            # Simple blend - in practice you might want more sophisticated blending
            return weather_tint

        # ---------------------------------------------------------------------
        # Weather Change Methods
        # ---------------------------------------------------------------------

        def set_weather(self, weather_type, log=True):
            """
            Immediately set the weather to a new type.

            Args:
                weather_type (str): The weather type to set
                log (bool): Whether to log this change

            Returns:
                bool: True if successful, False if invalid type
            """
            if not WeatherType.is_valid(weather_type):
                return False

            self.previous_weather = self._current_weather
            self._current_weather = weather_type
            self.is_transitioning = False
            self.transition_progress = 0.0
            self.transition_target = None

            if log:
                self._log_change(weather_type, "immediate")

            self._trigger_callbacks()
            return True

        def transition_weather(self, weather_type, duration=None):
            """
            Start a smooth transition to a new weather type.

            Args:
                weather_type (str): Target weather type
                duration (float): Transition duration in seconds (default: from config)

            Returns:
                bool: True if transition started, False if invalid type
            """
            if not WeatherType.is_valid(weather_type):
                return False

            if weather_type == self._current_weather:
                return True  # Already at target weather

            config = self.get_weather_config(weather_type)
            self.transition_target = weather_type
            self.transition_duration = duration if duration is not None else config.get("transition_time", 3.0)
            self.is_transitioning = True
            self.transition_progress = 0.0

            self._log_change(weather_type, "transition", self.transition_duration)
            return True

        def update_transition(self, delta_time):
            """
            Update transition progress. Call this each frame during transitions.

            Args:
                delta_time (float): Time elapsed since last update in seconds

            Returns:
                bool: True if transition completed, False otherwise
            """
            if not self.is_transitioning or self.transition_target is None:
                return False

            self.transition_progress += delta_time / self.transition_duration

            if self.transition_progress >= 1.0:
                self.transition_progress = 1.0
                self.previous_weather = self._current_weather
                self._current_weather = self.transition_target
                self.is_transitioning = False
                self.transition_target = None
                self._trigger_callbacks()
                return True

            return False

        def cancel_transition(self):
            """Cancel any ongoing weather transition."""
            self.is_transitioning = False
            self.transition_progress = 0.0
            self.transition_target = None

        def complete_transition(self):
            """Immediately complete any ongoing transition."""
            if self.is_transitioning and self.transition_target:
                self.previous_weather = self._current_weather
                self._current_weather = self.transition_target
                self.is_transitioning = False
                self.transition_progress = 1.0
                self.transition_target = None
                self._trigger_callbacks()
                return True
            return False

        # ---------------------------------------------------------------------
        # Random Weather
        # ---------------------------------------------------------------------

        def random_weather(self, exclude_current=True, use_season=True):
            """
            Set a random weather type.

            Args:
                exclude_current (bool): Whether to exclude current weather from choices
                use_season (bool): Whether to use seasonal probabilities

            Returns:
                str: The new weather type
            """
            if use_season and self._current_season in SEASONAL_WEATHER_WEIGHTS:
                weights = SEASONAL_WEATHER_WEIGHTS[self._current_season]
                choices = []
                probs = []

                for wtype, weight in weights.items():
                    if exclude_current and wtype == self._current_weather:
                        continue
                    if weight > 0:
                        choices.append(wtype)
                        probs.append(weight)

                if choices:
                    # Normalize probabilities
                    total = sum(probs)
                    probs = [p / total for p in probs]

                    # Weighted random choice
                    r = random.random()
                    cumulative = 0
                    for i, prob in enumerate(probs):
                        cumulative += prob
                        if r <= cumulative:
                            new_weather = choices[i]
                            break
                    else:
                        new_weather = choices[-1]
                else:
                    new_weather = WeatherType.SUNNY
            else:
                choices = WeatherType.all_types()
                if exclude_current:
                    choices = [w for w in choices if w != self._current_weather]
                new_weather = random.choice(choices)

            self.set_weather(new_weather)
            return new_weather

        def random_transition(self, duration=None, exclude_current=True, use_season=True):
            """
            Start a transition to a random weather type.

            Args:
                duration (float): Transition duration (default: from config)
                exclude_current (bool): Whether to exclude current weather
                use_season (bool): Whether to use seasonal probabilities

            Returns:
                str: The target weather type
            """
            # Temporarily store current weather
            current = self._current_weather

            # Get random weather (this will set it immediately)
            target = self.random_weather(exclude_current, use_season)

            # Restore current and start transition
            self._current_weather = current
            self.transition_weather(target, duration)

            return target

        # ---------------------------------------------------------------------
        # Season and Time Management
        # ---------------------------------------------------------------------

        def set_season(self, season):
            """
            Set the current season.

            Args:
                season (str): Season to set

            Returns:
                bool: True if successful, False if invalid
            """
            if not Season.is_valid(season):
                return False
            self._current_season = season
            return True

        def advance_season(self):
            """
            Advance to the next season.

            Returns:
                str: The new season
            """
            seasons = Season.all_seasons()
            current_index = seasons.index(self._current_season)
            next_index = (current_index + 1) % len(seasons)
            self._current_season = seasons[next_index]
            return self._current_season

        def set_time(self, time_of_day):
            """
            Set the current time of day.

            Args:
                time_of_day (str): Time to set

            Returns:
                bool: True if successful, False if invalid
            """
            if not TimeOfDay.is_valid(time_of_day):
                return False
            self._current_time = time_of_day
            return True

        def advance_time(self):
            """
            Advance to the next time period.

            Returns:
                str: The new time of day
            """
            times = TimeOfDay.all_times()
            current_index = times.index(self._current_time)
            next_index = (current_index + 1) % len(times)
            self._current_time = times[next_index]
            return self._current_time

        def is_daytime(self):
            """Check if it's currently daytime."""
            return self._current_time in [
                TimeOfDay.DAWN, TimeOfDay.MORNING,
                TimeOfDay.NOON, TimeOfDay.AFTERNOON
            ]

        def is_nighttime(self):
            """Check if it's currently nighttime."""
            return self._current_time in [TimeOfDay.DUSK, TimeOfDay.NIGHT]

        # ---------------------------------------------------------------------
        # Effect Controls
        # ---------------------------------------------------------------------

        def enable_effects(self):
            """Enable weather visual effects."""
            self._effects_enabled = True

        def disable_effects(self):
            """Disable weather visual effects."""
            self._effects_enabled = False

        def are_effects_enabled(self):
            """Check if effects are enabled."""
            return self._effects_enabled

        def enable_sounds(self):
            """Enable weather ambient sounds."""
            self._sounds_enabled = True

        def disable_sounds(self):
            """Disable weather ambient sounds."""
            self._sounds_enabled = False

        def are_sounds_enabled(self):
            """Check if sounds are enabled."""
            return self._sounds_enabled

        # ---------------------------------------------------------------------
        # Callbacks
        # ---------------------------------------------------------------------

        def add_callback(self, callback):
            """
            Add a callback function to be called on weather changes.

            Args:
                callback: Function taking (new_weather, previous_weather) args
            """
            if callback not in self.callbacks:
                self.callbacks.append(callback)

        def remove_callback(self, callback):
            """Remove a callback function."""
            if callback in self.callbacks:
                self.callbacks.remove(callback)

        def _trigger_callbacks(self):
            """Trigger all registered callbacks."""
            for callback in self.callbacks:
                try:
                    callback(self._current_weather, self.previous_weather)
                except Exception:
                    pass  # Silently ignore callback errors

        # ---------------------------------------------------------------------
        # History and Logging
        # ---------------------------------------------------------------------

        def _log_change(self, weather_type, change_type, duration=None):
            """Log a weather change."""
            entry = {
                "weather": weather_type,
                "type": change_type,
                "from": self._current_weather,
                "season": self._current_season,
                "time": self._current_time
            }
            if duration is not None:
                entry["duration"] = duration
            self.weather_history.append(entry)

        def get_history(self, limit=10):
            """Get recent weather history."""
            return self.weather_history[-limit:]

        def clear_history(self):
            """Clear weather history."""
            self.weather_history = []

        # ---------------------------------------------------------------------
        # Utility Methods
        # ---------------------------------------------------------------------

        def get_state(self):
            """
            Get complete weather state for saving.

            Returns:
                dict: Weather state dictionary
            """
            return {
                "weather": self._current_weather,
                "season": self._current_season,
                "time": self._current_time,
                "is_transitioning": self.is_transitioning,
                "transition_progress": self.transition_progress,
                "transition_target": self.transition_target,
                "effects_enabled": self._effects_enabled,
                "sounds_enabled": self._sounds_enabled
            }

        def load_state(self, state):
            """
            Load weather state from saved data.

            Args:
                state (dict): Weather state dictionary
            """
            self._current_weather = state.get("weather", WeatherType.SUNNY)
            self._current_season = state.get("season", Season.SPRING)
            self._current_time = state.get("time", TimeOfDay.MORNING)
            self.is_transitioning = state.get("is_transitioning", False)
            self.transition_progress = state.get("transition_progress", 0.0)
            self.transition_target = state.get("transition_target")
            self._effects_enabled = state.get("effects_enabled", True)
            self._sounds_enabled = state.get("sounds_enabled", True)

        def __repr__(self):
            """String representation of weather manager."""
            return f"WeatherManager(weather={self._current_weather}, season={self._current_season}, time={self._current_time})"

# =============================================================================
# GLOBAL WEATHER MANAGER INSTANCE
# =============================================================================

default weather_manager = WeatherManager()

# =============================================================================
# WEATHER VISUAL TRANSFORMS AND EFFECTS
# =============================================================================

# -----------------------------------------------------------------------------
# Rain Particle Effect
# -----------------------------------------------------------------------------

transform rain_particle_fall(start_x, duration):
    # Rain drops fall from top to bottom at an angle
    xpos start_x
    ypos -50
    alpha 0.7
    linear duration xpos start_x + 100 ypos 1080
    alpha 0.0

transform rain_particle:
    # Single rain drop animation
    alpha 0.0
    pause renpy.random.random() * 0.5
    alpha 0.8
    linear 0.4 + renpy.random.random() * 0.3 yoffset 600 xoffset 50
    alpha 0.0
    yoffset 0
    xoffset 0
    repeat

# -----------------------------------------------------------------------------
# Snow Particle Effect
# -----------------------------------------------------------------------------

transform snow_particle_fall(start_x, duration):
    # Snowflakes fall slowly with gentle swaying
    xpos start_x
    ypos -30
    alpha 0.9
    parallel:
        linear duration ypos 1080
    parallel:
        ease duration / 4 xpos start_x + 30
        ease duration / 4 xpos start_x - 30
        ease duration / 4 xpos start_x + 20
        ease duration / 4 xpos start_x
    alpha 0.0

transform snow_particle:
    # Single snowflake animation with drift
    alpha 0.0
    pause renpy.random.random() * 1.0
    alpha 0.9
    parallel:
        linear 2.0 + renpy.random.random() * 2.0 yoffset 500
    parallel:
        ease 0.5 xoffset 20
        ease 0.5 xoffset -20
        ease 0.5 xoffset 10
        ease 0.5 xoffset 0
    alpha 0.0
    yoffset 0
    xoffset 0
    repeat

# -----------------------------------------------------------------------------
# Fog Effect
# -----------------------------------------------------------------------------

transform fog_drift:
    # Fog layer drifting slowly across screen
    alpha 0.4
    xpos -200
    linear 30.0 xpos 200
    xpos -200
    repeat

transform fog_pulse:
    # Fog opacity pulsing
    alpha 0.3
    ease 5.0 alpha 0.5
    ease 5.0 alpha 0.3
    repeat

# -----------------------------------------------------------------------------
# Storm Effects
# -----------------------------------------------------------------------------

transform lightning_flash:
    # Lightning flash effect
    alpha 0.0
    pause renpy.random.random() * 5.0 + 3.0
    alpha 0.8
    pause 0.1
    alpha 0.0
    pause 0.1
    alpha 0.6
    pause 0.05
    alpha 0.0
    repeat

transform storm_rain_heavy:
    # Heavy rain for storms
    alpha 0.0
    pause renpy.random.random() * 0.3
    alpha 0.9
    linear 0.25 + renpy.random.random() * 0.15 yoffset 700 xoffset 80
    alpha 0.0
    yoffset 0
    xoffset 0
    repeat

# -----------------------------------------------------------------------------
# Weather Overlay Transitions
# -----------------------------------------------------------------------------

transform weather_fade_in(duration=1.0):
    alpha 0.0
    linear duration alpha 1.0

transform weather_fade_out(duration=1.0):
    alpha 1.0
    linear duration alpha 0.0

transform weather_crossfade(duration=2.0):
    alpha 0.0
    linear duration / 2 alpha 1.0
    pause duration / 2

# -----------------------------------------------------------------------------
# Sun/Light Effects
# -----------------------------------------------------------------------------

transform sun_rays:
    # Animated sun rays
    alpha 0.3
    rotate 0
    linear 60.0 rotate 360
    rotate 0
    repeat

transform sun_pulse:
    # Pulsing sun glow
    alpha 0.2
    ease 3.0 alpha 0.4
    ease 3.0 alpha 0.2
    repeat

# -----------------------------------------------------------------------------
# Cloud Movement
# -----------------------------------------------------------------------------

transform cloud_drift_slow:
    xpos -300
    linear 120.0 xpos 2200
    xpos -300
    repeat

transform cloud_drift_medium:
    xpos -200
    linear 80.0 xpos 2100
    xpos -200
    repeat

transform cloud_drift_fast:
    xpos -250
    linear 40.0 xpos 2150
    xpos -250
    repeat

# =============================================================================
# WEATHER OVERLAY SCREEN
# =============================================================================

screen weather_overlay():
    # Main weather effects overlay
    # This screen should be shown above the scene but below UI

    zorder 50
    layer "master"

    if weather_manager.are_effects_enabled():
        # Get current weather config
        $ w_config = weather_manager.get_weather_config()
        $ w_alpha = weather_manager.get_overlay_alpha()

        # Weather tint overlay
        if w_alpha > 0:
            frame:
                xfill True
                yfill True
                background weather_manager.get_tint_color()
                at Transform(alpha=w_alpha * 0.3)

        # Particle effects based on weather type
        if weather_manager.current_weather == "rain":
            # Rain particles
            for i in range(20):
                $ rx = renpy.random.randint(0, 1920)
                text "{color=#aaccff}|{/color}" at rain_particle:
                    xpos rx

        elif weather_manager.current_weather == "snow":
            # Snow particles
            for i in range(15):
                $ sx = renpy.random.randint(0, 1920)
                text "{color=#ffffff}*{/color}" at snow_particle:
                    xpos sx

        elif weather_manager.current_weather == "storm":
            # Heavy rain + lightning
            for i in range(30):
                $ rx = renpy.random.randint(0, 1920)
                text "{color=#8899bb}|{/color}" at storm_rain_heavy:
                    xpos rx

            # Lightning flash overlay
            frame:
                xfill True
                yfill True
                background "#ffffff"
                at lightning_flash

        elif weather_manager.current_weather == "fog":
            # Fog overlay
            frame:
                xfill True
                yfill True
                background "#888888"
                at fog_pulse

        elif weather_manager.current_weather == "sunny" and weather_manager.is_daytime():
            # Sun glow effect (subtle)
            frame:
                xpos 1600
                ypos 50
                xsize 200
                ysize 200
                background "#ffff88"
                at sun_pulse

# =============================================================================
# WEATHER INDICATOR UI
# =============================================================================

screen weather_indicator():
    # Small weather indicator shown in corner of screen
    # Shows current weather icon and label

    zorder 100

    frame:
        xalign 1.0
        yalign 0.0
        xoffset -10
        yoffset 10
        padding (10, 8)
        background "#00000088"

        hbox:
            spacing 8

            # Weather icon placeholder (text-based)
            $ w_type = weather_manager.current_weather
            if w_type == "sunny":
                text "{color=#ffcc00}[sun]{/color}" size 20
            elif w_type == "cloudy":
                text "{color=#aaaaaa}[cloud]{/color}" size 20
            elif w_type == "rain":
                text "{color=#6699cc}[rain]{/color}" size 20
            elif w_type == "snow":
                text "{color=#ffffff}[snow]{/color}" size 20
            elif w_type == "fog":
                text "{color=#888888}[fog]{/color}" size 20
            elif w_type == "storm":
                text "{color=#666699}[storm]{/color}" size 20
            elif w_type == "clear":
                text "{color=#334466}[moon]{/color}" size 20

            # Weather label
            text weather_manager.get_weather_label() size 16 color "#ffffff"

            # Season indicator
            text "([weather_manager.current_season])" size 12 color "#aaaaaa"

# =============================================================================
# WEATHER DEBUG/INFO SCREEN
# =============================================================================

screen weather_debug():
    # Debug screen showing all weather information

    zorder 200
    modal False

    frame:
        xalign 0.0
        yalign 1.0
        xoffset 10
        yoffset -10
        padding (15, 12)
        background "#000000cc"

        vbox:
            spacing 5

            text "Weather Debug" size 18 color "#ffcc00"
            null height 5

            text "Weather: [weather_manager.current_weather]" size 14 color "#ffffff"
            text "Season: [weather_manager.current_season]" size 14 color "#ffffff"
            text "Time: [weather_manager.current_time]" size 14 color "#ffffff"

            null height 5

            $ mods = weather_manager.get_modifiers()
            $ mood_color = "#88ff88" if mods.get('mood', 0) >= 0 else "#ff8888"
            $ energy_color = "#88ff88" if mods.get('energy', 0) >= 0 else "#ff8888"
            text "Modifiers:" size 14 color "#aaaaaa"
            text "  Mood: [mods.get('mood', 0)]" size 12 color mood_color
            text "  Energy: [mods.get('energy', 0)]" size 12 color energy_color
            text "  Visibility: [mods.get('visibility', 100)]%" size 12 color "#ffffff"

            if weather_manager.is_transitioning:
                null height 5
                text "Transitioning to: [weather_manager.transition_target]" size 12 color "#ffaa00"
                $ prog = int(weather_manager.transition_progress * 100)
                text "Progress: [prog]%" size 12 color "#ffaa00"

# =============================================================================
# HELPER LABELS FOR EASY WEATHER CONTROL
# =============================================================================

# Set weather immediately
label set_weather(weather_type):
    $ weather_manager.set_weather(weather_type)
    return

# Transition to weather
label transition_weather(weather_type, duration=None):
    $ weather_manager.transition_weather(weather_type, duration)
    return

# Random weather change
label random_weather():
    $ weather_manager.random_weather()
    return

# Set season
label set_season(season):
    $ weather_manager.set_season(season)
    return

# Set time of day
label set_time(time_of_day):
    $ weather_manager.set_time(time_of_day)
    return

# Advance time
label advance_time():
    $ weather_manager.advance_time()
    return

# Show weather effects
label show_weather_effects():
    show screen weather_overlay
    show screen weather_indicator
    return

# Hide weather effects
label hide_weather_effects():
    hide screen weather_overlay
    hide screen weather_indicator
    return

# =============================================================================
# WEATHER CHANGE WITH NOTIFICATION
# =============================================================================

label weather_change_notify(weather_type, transition=True, duration=None):
    $ old_weather = weather_manager.current_weather
    if transition:
        $ weather_manager.transition_weather(weather_type, duration)
    else:
        $ weather_manager.set_weather(weather_type)

    $ new_label = weather_manager.get_weather_label()
    $ renpy.notify("Weather changed to: " + new_label)
    return

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

# Example label demonstrating weather system:
#
# label weather_example:
#     # Show weather effects
#     call show_weather_effects
#
#     # Set initial weather
#     $ weather_manager.set_weather(WeatherType.SUNNY)
#     $ weather_manager.set_season(Season.SUMMER)
#
#     "It's a beautiful sunny day."
#
#     # Transition to rain
#     $ weather_manager.transition_weather(WeatherType.RAIN, 3.0)
#     "Dark clouds are gathering..."
#
#     # Wait for transition (in actual game, use timer or loop)
#     pause 3.0
#
#     "And now it's raining."
#
#     # Check weather modifiers
#     $ mood_mod = weather_manager.get_modifier("mood")
#     if mood_mod < 0:
#         "The rain dampens your spirits."
#
#     # Random weather
#     $ weather_manager.random_weather()
#     $ new_weather = weather_manager.get_weather_label()
#     "The weather suddenly changes to [new_weather]."
#
#     return

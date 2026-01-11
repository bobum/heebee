"""
Comprehensive tests for the Weather/Atmosphere System.

Tests cover:
- WeatherType enum functionality
- Season and TimeOfDay enums
- WeatherManager class methods
- Weather transitions
- Random weather selection
- Seasonal weather probabilities
- Time and season management
- State saving/loading
- Callbacks
"""
import pytest
from pathlib import Path


class TestWeatherType:
    """Tests for WeatherType enum/constants."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherType = self.ns["WeatherType"]

    def test_weather_types_defined(self):
        """Test that all weather types are defined."""
        assert self.WeatherType.SUNNY == "sunny"
        assert self.WeatherType.CLOUDY == "cloudy"
        assert self.WeatherType.RAIN == "rain"
        assert self.WeatherType.SNOW == "snow"
        assert self.WeatherType.FOG == "fog"
        assert self.WeatherType.STORM == "storm"
        assert self.WeatherType.CLEAR == "clear"

    def test_all_types_returns_list(self):
        """Test that all_types() returns all weather types."""
        all_types = self.WeatherType.all_types()
        assert isinstance(all_types, list)
        assert len(all_types) == 7
        assert "sunny" in all_types
        assert "cloudy" in all_types
        assert "rain" in all_types
        assert "snow" in all_types
        assert "fog" in all_types
        assert "storm" in all_types
        assert "clear" in all_types

    def test_is_valid_with_valid_types(self):
        """Test is_valid returns True for valid weather types."""
        assert self.WeatherType.is_valid("sunny") is True
        assert self.WeatherType.is_valid("rain") is True
        assert self.WeatherType.is_valid("storm") is True

    def test_is_valid_with_invalid_types(self):
        """Test is_valid returns False for invalid weather types."""
        assert self.WeatherType.is_valid("hurricane") is False
        assert self.WeatherType.is_valid("tornado") is False
        assert self.WeatherType.is_valid("") is False
        assert self.WeatherType.is_valid(None) is False


class TestSeason:
    """Tests for Season enum/constants."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.Season = self.ns["Season"]

    def test_seasons_defined(self):
        """Test that all seasons are defined."""
        assert self.Season.SPRING == "spring"
        assert self.Season.SUMMER == "summer"
        assert self.Season.AUTUMN == "autumn"
        assert self.Season.WINTER == "winter"

    def test_all_seasons_returns_list(self):
        """Test that all_seasons() returns all seasons."""
        all_seasons = self.Season.all_seasons()
        assert isinstance(all_seasons, list)
        assert len(all_seasons) == 4
        assert "spring" in all_seasons
        assert "summer" in all_seasons
        assert "autumn" in all_seasons
        assert "winter" in all_seasons

    def test_is_valid_with_valid_seasons(self):
        """Test is_valid returns True for valid seasons."""
        assert self.Season.is_valid("spring") is True
        assert self.Season.is_valid("winter") is True

    def test_is_valid_with_invalid_seasons(self):
        """Test is_valid returns False for invalid seasons."""
        assert self.Season.is_valid("monsoon") is False
        assert self.Season.is_valid("") is False


class TestTimeOfDay:
    """Tests for TimeOfDay enum/constants."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.TimeOfDay = self.ns["TimeOfDay"]

    def test_times_defined(self):
        """Test that all times of day are defined."""
        assert self.TimeOfDay.DAWN == "dawn"
        assert self.TimeOfDay.MORNING == "morning"
        assert self.TimeOfDay.NOON == "noon"
        assert self.TimeOfDay.AFTERNOON == "afternoon"
        assert self.TimeOfDay.DUSK == "dusk"
        assert self.TimeOfDay.NIGHT == "night"

    def test_all_times_returns_list(self):
        """Test that all_times() returns all time periods."""
        all_times = self.TimeOfDay.all_times()
        assert isinstance(all_times, list)
        assert len(all_times) == 6

    def test_is_valid_with_valid_times(self):
        """Test is_valid returns True for valid times."""
        assert self.TimeOfDay.is_valid("dawn") is True
        assert self.TimeOfDay.is_valid("night") is True

    def test_is_valid_with_invalid_times(self):
        """Test is_valid returns False for invalid times."""
        assert self.TimeOfDay.is_valid("midnight") is False


class TestWeatherConfig:
    """Tests for weather configuration constants."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WEATHER_CONFIG = self.ns["WEATHER_CONFIG"]
        self.WeatherType = self.ns["WeatherType"]

    def test_config_exists_for_all_types(self):
        """Test that configuration exists for all weather types."""
        for wtype in self.WeatherType.all_types():
            assert wtype in self.WEATHER_CONFIG

    def test_config_has_required_fields(self):
        """Test that each config has required fields."""
        required_fields = [
            "label", "description", "icon", "ambient_sound",
            "overlay_alpha", "tint_color", "modifiers", "transition_time"
        ]
        for wtype, config in self.WEATHER_CONFIG.items():
            for field in required_fields:
                assert field in config, f"Missing {field} in {wtype} config"

    def test_modifiers_have_expected_keys(self):
        """Test that modifiers contain expected gameplay modifiers."""
        expected_modifiers = ["mood", "energy", "visibility"]
        for wtype, config in self.WEATHER_CONFIG.items():
            modifiers = config["modifiers"]
            for mod in expected_modifiers:
                assert mod in modifiers, f"Missing {mod} modifier in {wtype}"

    def test_overlay_alpha_in_range(self):
        """Test that overlay alpha values are in valid range."""
        for wtype, config in self.WEATHER_CONFIG.items():
            alpha = config["overlay_alpha"]
            assert 0.0 <= alpha <= 1.0, f"Invalid alpha {alpha} for {wtype}"

    def test_visibility_in_range(self):
        """Test that visibility values are in valid range."""
        for wtype, config in self.WEATHER_CONFIG.items():
            visibility = config["modifiers"]["visibility"]
            assert 0 <= visibility <= 100, f"Invalid visibility for {wtype}"


class TestWeatherManagerInit:
    """Tests for WeatherManager initialization."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]
        self.Season = self.ns["Season"]
        self.TimeOfDay = self.ns["TimeOfDay"]

    def test_default_initialization(self):
        """Test WeatherManager with default values."""
        manager = self.WeatherManager()
        assert manager.current_weather == self.WeatherType.SUNNY
        assert manager.current_season == self.Season.SPRING
        assert manager.current_time == self.TimeOfDay.MORNING
        assert manager.is_transitioning is False
        assert manager.transition_progress == 0.0

    def test_custom_initialization(self):
        """Test WeatherManager with custom initial values."""
        manager = self.WeatherManager(
            initial_weather=self.WeatherType.RAIN,
            initial_season=self.Season.WINTER,
            initial_time=self.TimeOfDay.NIGHT
        )
        assert manager.current_weather == self.WeatherType.RAIN
        assert manager.current_season == self.Season.WINTER
        assert manager.current_time == self.TimeOfDay.NIGHT

    def test_effects_enabled_by_default(self):
        """Test that effects are enabled by default."""
        manager = self.WeatherManager()
        assert manager.are_effects_enabled() is True
        assert manager.are_sounds_enabled() is True


class TestWeatherManagerSetWeather:
    """Tests for WeatherManager.set_weather method."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]

    def test_set_valid_weather(self):
        """Test setting valid weather types."""
        manager = self.WeatherManager()
        result = manager.set_weather(self.WeatherType.RAIN)
        assert result is True
        assert manager.current_weather == self.WeatherType.RAIN

    def test_set_invalid_weather(self):
        """Test setting invalid weather type returns False."""
        manager = self.WeatherManager()
        original = manager.current_weather
        result = manager.set_weather("tornado")
        assert result is False
        assert manager.current_weather == original

    def test_set_weather_updates_previous(self):
        """Test that previous_weather is updated."""
        manager = self.WeatherManager()
        manager.set_weather(self.WeatherType.RAIN)
        assert manager.previous_weather == self.WeatherType.SUNNY
        manager.set_weather(self.WeatherType.SNOW)
        assert manager.previous_weather == self.WeatherType.RAIN

    def test_set_weather_cancels_transition(self):
        """Test that set_weather cancels any ongoing transition."""
        manager = self.WeatherManager()
        manager.transition_weather(self.WeatherType.RAIN, 5.0)
        assert manager.is_transitioning is True
        manager.set_weather(self.WeatherType.SNOW)
        assert manager.is_transitioning is False
        assert manager.transition_target is None

    def test_set_weather_logs_change(self):
        """Test that weather changes are logged."""
        manager = self.WeatherManager()
        manager.set_weather(self.WeatherType.RAIN)
        assert len(manager.weather_history) == 1
        assert manager.weather_history[0]["weather"] == self.WeatherType.RAIN
        assert manager.weather_history[0]["type"] == "immediate"


class TestWeatherManagerTransition:
    """Tests for WeatherManager transition methods."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]

    def test_transition_starts_correctly(self):
        """Test that transition_weather starts a transition."""
        manager = self.WeatherManager()
        result = manager.transition_weather(self.WeatherType.RAIN, 5.0)
        assert result is True
        assert manager.is_transitioning is True
        assert manager.transition_target == self.WeatherType.RAIN
        assert manager.transition_duration == 5.0
        assert manager.transition_progress == 0.0

    def test_transition_invalid_weather(self):
        """Test transition with invalid weather returns False."""
        manager = self.WeatherManager()
        result = manager.transition_weather("tornado", 5.0)
        assert result is False
        assert manager.is_transitioning is False

    def test_transition_to_same_weather(self):
        """Test transition to same weather succeeds without transitioning."""
        manager = self.WeatherManager()
        result = manager.transition_weather(self.WeatherType.SUNNY)
        assert result is True
        assert manager.is_transitioning is False

    def test_update_transition_progress(self):
        """Test that update_transition advances progress."""
        manager = self.WeatherManager()
        manager.transition_weather(self.WeatherType.RAIN, 10.0)
        manager.update_transition(2.0)  # 2 seconds
        assert manager.transition_progress == pytest.approx(0.2, rel=0.01)

    def test_update_transition_completes(self):
        """Test that transition completes when progress reaches 1.0."""
        manager = self.WeatherManager()
        manager.transition_weather(self.WeatherType.RAIN, 2.0)
        result = manager.update_transition(2.5)  # More than duration
        assert result is True
        assert manager.is_transitioning is False
        assert manager.current_weather == self.WeatherType.RAIN

    def test_cancel_transition(self):
        """Test canceling a transition."""
        manager = self.WeatherManager()
        manager.transition_weather(self.WeatherType.RAIN, 5.0)
        manager.cancel_transition()
        assert manager.is_transitioning is False
        assert manager.transition_target is None
        assert manager.current_weather == self.WeatherType.SUNNY

    def test_complete_transition_immediately(self):
        """Test completing a transition immediately."""
        manager = self.WeatherManager()
        manager.transition_weather(self.WeatherType.RAIN, 5.0)
        result = manager.complete_transition()
        assert result is True
        assert manager.is_transitioning is False
        assert manager.current_weather == self.WeatherType.RAIN


class TestWeatherManagerRandom:
    """Tests for random weather selection."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]
        self.Season = self.ns["Season"]

    def test_random_weather_returns_valid_type(self):
        """Test that random_weather returns a valid weather type."""
        manager = self.WeatherManager()
        for _ in range(10):
            new_weather = manager.random_weather()
            assert self.WeatherType.is_valid(new_weather)

    def test_random_weather_excludes_current(self):
        """Test that random_weather excludes current by default."""
        manager = self.WeatherManager()
        # Set to a specific weather and call random multiple times
        # With exclude_current=True (default), we should get different weather each time
        different_weather_count = 0
        for _ in range(10):
            manager.set_weather(self.WeatherType.RAIN)
            original = manager.current_weather
            new_weather = manager.random_weather(exclude_current=True)
            if new_weather != original:
                different_weather_count += 1
        # All should be different when exclude_current=True
        assert different_weather_count == 10

    def test_random_weather_can_include_current(self):
        """Test random_weather with exclude_current=False."""
        manager = self.WeatherManager()
        # Just verify it doesn't crash
        new_weather = manager.random_weather(exclude_current=False)
        assert self.WeatherType.is_valid(new_weather)

    def test_random_weather_uses_season(self):
        """Test that random_weather respects seasonal probabilities."""
        manager = self.WeatherManager()
        manager.set_season(self.Season.WINTER)
        # Run many times - in winter, snow should appear more often
        weather_counts = {}
        for _ in range(100):
            manager.set_weather(self.WeatherType.SUNNY)  # Reset
            new_weather = manager.random_weather(use_season=True)
            weather_counts[new_weather] = weather_counts.get(new_weather, 0) + 1
        # Snow should appear (winter has 35% snow probability)
        assert self.WeatherType.SNOW in weather_counts

    def test_random_transition(self):
        """Test random_transition starts a transition."""
        manager = self.WeatherManager()
        original = manager.current_weather
        target = manager.random_transition(duration=3.0)
        assert manager.is_transitioning is True
        assert manager.transition_target == target
        assert manager.current_weather == original  # Not changed yet


class TestSeasonManagement:
    """Tests for season management."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.Season = self.ns["Season"]

    def test_set_valid_season(self):
        """Test setting a valid season."""
        manager = self.WeatherManager()
        result = manager.set_season(self.Season.WINTER)
        assert result is True
        assert manager.current_season == self.Season.WINTER

    def test_set_invalid_season(self):
        """Test setting an invalid season returns False."""
        manager = self.WeatherManager()
        original = manager.current_season
        result = manager.set_season("monsoon")
        assert result is False
        assert manager.current_season == original

    def test_advance_season(self):
        """Test advancing through seasons."""
        manager = self.WeatherManager()
        manager.set_season(self.Season.SPRING)

        new_season = manager.advance_season()
        assert new_season == self.Season.SUMMER
        assert manager.current_season == self.Season.SUMMER

        new_season = manager.advance_season()
        assert new_season == self.Season.AUTUMN

        new_season = manager.advance_season()
        assert new_season == self.Season.WINTER

        new_season = manager.advance_season()
        assert new_season == self.Season.SPRING  # Wraps around


class TestTimeManagement:
    """Tests for time of day management."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.TimeOfDay = self.ns["TimeOfDay"]

    def test_set_valid_time(self):
        """Test setting a valid time of day."""
        manager = self.WeatherManager()
        result = manager.set_time(self.TimeOfDay.NIGHT)
        assert result is True
        assert manager.current_time == self.TimeOfDay.NIGHT

    def test_set_invalid_time(self):
        """Test setting an invalid time returns False."""
        manager = self.WeatherManager()
        original = manager.current_time
        result = manager.set_time("midnight")
        assert result is False
        assert manager.current_time == original

    def test_advance_time(self):
        """Test advancing through time periods."""
        manager = self.WeatherManager()
        manager.set_time(self.TimeOfDay.DAWN)

        times = []
        for _ in range(7):  # Go through full cycle plus one
            times.append(manager.current_time)
            manager.advance_time()

        assert times[0] == self.TimeOfDay.DAWN
        assert times[1] == self.TimeOfDay.MORNING
        assert times[2] == self.TimeOfDay.NOON
        assert times[3] == self.TimeOfDay.AFTERNOON
        assert times[4] == self.TimeOfDay.DUSK
        assert times[5] == self.TimeOfDay.NIGHT
        assert times[6] == self.TimeOfDay.DAWN  # Wrapped

    def test_is_daytime(self):
        """Test is_daytime method."""
        manager = self.WeatherManager()

        manager.set_time(self.TimeOfDay.MORNING)
        assert manager.is_daytime() is True

        manager.set_time(self.TimeOfDay.NOON)
        assert manager.is_daytime() is True

        manager.set_time(self.TimeOfDay.NIGHT)
        assert manager.is_daytime() is False

    def test_is_nighttime(self):
        """Test is_nighttime method."""
        manager = self.WeatherManager()

        manager.set_time(self.TimeOfDay.NIGHT)
        assert manager.is_nighttime() is True

        manager.set_time(self.TimeOfDay.DUSK)
        assert manager.is_nighttime() is True

        manager.set_time(self.TimeOfDay.MORNING)
        assert manager.is_nighttime() is False


class TestWeatherConfig:
    """Tests for weather configuration access methods."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]

    def test_get_weather_config(self):
        """Test getting weather configuration."""
        manager = self.WeatherManager()
        config = manager.get_weather_config(self.WeatherType.RAIN)
        assert "label" in config
        assert config["label"] == "Rain"

    def test_get_weather_config_defaults_to_current(self):
        """Test that get_weather_config uses current weather by default."""
        manager = self.WeatherManager()
        manager.set_weather(self.WeatherType.SNOW)
        config = manager.get_weather_config()
        assert config["label"] == "Snow"

    def test_get_weather_label(self):
        """Test getting weather labels."""
        manager = self.WeatherManager()
        assert manager.get_weather_label(self.WeatherType.SUNNY) == "Sunny"
        assert manager.get_weather_label(self.WeatherType.STORM) == "Storm"

    def test_get_weather_description(self):
        """Test getting weather descriptions."""
        manager = self.WeatherManager()
        desc = manager.get_weather_description(self.WeatherType.FOG)
        assert "fog" in desc.lower() or "visibility" in desc.lower()

    def test_get_ambient_sound(self):
        """Test getting ambient sound paths."""
        manager = self.WeatherManager()
        sound = manager.get_ambient_sound(self.WeatherType.RAIN)
        assert "rain" in sound.lower()

    def test_get_modifiers(self):
        """Test getting gameplay modifiers."""
        manager = self.WeatherManager()
        mods = manager.get_modifiers(self.WeatherType.STORM)
        assert "mood" in mods
        assert "energy" in mods
        assert "visibility" in mods

    def test_get_specific_modifier(self):
        """Test getting a specific modifier value."""
        manager = self.WeatherManager()
        visibility = manager.get_modifier("visibility", self.WeatherType.FOG)
        assert visibility < 50  # Fog has low visibility

    def test_get_overlay_alpha(self):
        """Test getting overlay alpha values."""
        manager = self.WeatherManager()
        sunny_alpha = manager.get_overlay_alpha(self.WeatherType.SUNNY)
        fog_alpha = manager.get_overlay_alpha(self.WeatherType.FOG)
        assert sunny_alpha < fog_alpha  # Fog should have higher alpha

    def test_get_tint_color(self):
        """Test getting tint colors."""
        manager = self.WeatherManager()
        tint = manager.get_tint_color(self.WeatherType.SUNNY)
        assert tint.startswith("#")
        assert len(tint) == 7  # #RRGGBB format


class TestEffectControls:
    """Tests for effect enable/disable controls."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]

    def test_enable_disable_effects(self):
        """Test enabling and disabling visual effects."""
        manager = self.WeatherManager()
        assert manager.are_effects_enabled() is True

        manager.disable_effects()
        assert manager.are_effects_enabled() is False

        manager.enable_effects()
        assert manager.are_effects_enabled() is True

    def test_enable_disable_sounds(self):
        """Test enabling and disabling sounds."""
        manager = self.WeatherManager()
        assert manager.are_sounds_enabled() is True

        manager.disable_sounds()
        assert manager.are_sounds_enabled() is False

        manager.enable_sounds()
        assert manager.are_sounds_enabled() is True


class TestCallbacks:
    """Tests for callback functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]

    def test_add_callback(self):
        """Test adding a callback."""
        manager = self.WeatherManager()
        callback_called = {"called": False, "args": None}

        def test_callback(new_weather, old_weather):
            callback_called["called"] = True
            callback_called["args"] = (new_weather, old_weather)

        manager.add_callback(test_callback)
        manager.set_weather(self.WeatherType.RAIN)

        assert callback_called["called"] is True
        assert callback_called["args"][0] == self.WeatherType.RAIN

    def test_remove_callback(self):
        """Test removing a callback."""
        manager = self.WeatherManager()
        callback_count = {"count": 0}

        def test_callback(new_weather, old_weather):
            callback_count["count"] += 1

        manager.add_callback(test_callback)
        manager.set_weather(self.WeatherType.RAIN)
        assert callback_count["count"] == 1

        manager.remove_callback(test_callback)
        manager.set_weather(self.WeatherType.SNOW)
        assert callback_count["count"] == 1  # Not called again

    def test_callback_on_transition_complete(self):
        """Test that callback is triggered when transition completes."""
        manager = self.WeatherManager()
        callback_data = {"called": False}

        def test_callback(new_weather, old_weather):
            callback_data["called"] = True
            callback_data["new"] = new_weather

        manager.add_callback(test_callback)
        manager.transition_weather(self.WeatherType.RAIN, 1.0)

        # Callback not called yet during transition
        manager.update_transition(0.5)
        assert callback_data["called"] is False

        # Complete transition
        manager.update_transition(0.6)
        assert callback_data["called"] is True
        assert callback_data["new"] == self.WeatherType.RAIN


class TestStateSaveLoad:
    """Tests for state saving and loading."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]
        self.Season = self.ns["Season"]
        self.TimeOfDay = self.ns["TimeOfDay"]

    def test_get_state(self):
        """Test getting weather state."""
        manager = self.WeatherManager()
        manager.set_weather(self.WeatherType.RAIN)
        manager.set_season(self.Season.WINTER)
        manager.set_time(self.TimeOfDay.NIGHT)

        state = manager.get_state()
        assert state["weather"] == self.WeatherType.RAIN
        assert state["season"] == self.Season.WINTER
        assert state["time"] == self.TimeOfDay.NIGHT

    def test_load_state(self):
        """Test loading weather state."""
        manager = self.WeatherManager()
        state = {
            "weather": self.WeatherType.SNOW,
            "season": self.Season.AUTUMN,
            "time": self.TimeOfDay.DUSK,
            "effects_enabled": False,
            "sounds_enabled": False
        }

        manager.load_state(state)
        assert manager.current_weather == self.WeatherType.SNOW
        assert manager.current_season == self.Season.AUTUMN
        assert manager.current_time == self.TimeOfDay.DUSK
        assert manager.are_effects_enabled() is False
        assert manager.are_sounds_enabled() is False

    def test_state_roundtrip(self):
        """Test saving and loading state preserves all values."""
        manager1 = self.WeatherManager()
        manager1.set_weather(self.WeatherType.STORM)
        manager1.set_season(self.Season.SUMMER)
        manager1.set_time(self.TimeOfDay.AFTERNOON)
        manager1.disable_effects()

        state = manager1.get_state()

        manager2 = self.WeatherManager()
        manager2.load_state(state)

        assert manager2.current_weather == manager1.current_weather
        assert manager2.current_season == manager1.current_season
        assert manager2.current_time == manager1.current_time
        assert manager2.are_effects_enabled() == manager1.are_effects_enabled()


class TestWeatherHistory:
    """Tests for weather history tracking."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]

    def test_history_logged_on_set(self):
        """Test that set_weather logs to history."""
        manager = self.WeatherManager()
        manager.set_weather(self.WeatherType.RAIN)
        manager.set_weather(self.WeatherType.SNOW)

        history = manager.get_history()
        assert len(history) == 2
        assert history[0]["weather"] == self.WeatherType.RAIN
        assert history[1]["weather"] == self.WeatherType.SNOW

    def test_history_logged_on_transition_start(self):
        """Test that transition_weather logs to history."""
        manager = self.WeatherManager()
        manager.transition_weather(self.WeatherType.RAIN, 5.0)

        history = manager.get_history()
        assert len(history) == 1
        assert history[0]["type"] == "transition"
        assert history[0]["duration"] == 5.0

    def test_get_history_with_limit(self):
        """Test getting limited history."""
        manager = self.WeatherManager()
        for wtype in [self.WeatherType.RAIN, self.WeatherType.SNOW,
                      self.WeatherType.FOG, self.WeatherType.STORM]:
            manager.set_weather(wtype)

        history = manager.get_history(limit=2)
        assert len(history) == 2
        assert history[-1]["weather"] == self.WeatherType.STORM

    def test_clear_history(self):
        """Test clearing weather history."""
        manager = self.WeatherManager()
        manager.set_weather(self.WeatherType.RAIN)
        manager.set_weather(self.WeatherType.SNOW)
        assert len(manager.weather_history) > 0

        manager.clear_history()
        assert len(manager.weather_history) == 0


class TestSeasonalWeatherWeights:
    """Tests for seasonal weather probability configuration."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.SEASONAL_WEATHER_WEIGHTS = self.ns["SEASONAL_WEATHER_WEIGHTS"]
        self.Season = self.ns["Season"]
        self.WeatherType = self.ns["WeatherType"]

    def test_weights_exist_for_all_seasons(self):
        """Test that weights exist for all seasons."""
        for season in self.Season.all_seasons():
            assert season in self.SEASONAL_WEATHER_WEIGHTS

    def test_weights_are_non_negative(self):
        """Test that all weights are non-negative."""
        for season, weights in self.SEASONAL_WEATHER_WEIGHTS.items():
            for wtype, weight in weights.items():
                assert weight >= 0, f"Negative weight for {wtype} in {season}"

    def test_winter_has_high_snow_probability(self):
        """Test that winter has higher snow probability than summer."""
        winter_snow = self.SEASONAL_WEATHER_WEIGHTS[self.Season.WINTER][self.WeatherType.SNOW]
        summer_snow = self.SEASONAL_WEATHER_WEIGHTS[self.Season.SUMMER][self.WeatherType.SNOW]
        assert winter_snow > summer_snow

    def test_summer_has_high_sunny_probability(self):
        """Test that summer has high sunny probability."""
        summer_sunny = self.SEASONAL_WEATHER_WEIGHTS[self.Season.SUMMER][self.WeatherType.SUNNY]
        # Summer should have sunny as the most common weather
        for wtype, weight in self.SEASONAL_WEATHER_WEIGHTS[self.Season.SUMMER].items():
            if wtype != self.WeatherType.SUNNY:
                assert summer_sunny >= weight


class TestWeatherManagerRepr:
    """Tests for WeatherManager string representation."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]

    def test_repr(self):
        """Test string representation of WeatherManager."""
        manager = self.WeatherManager()
        repr_str = repr(manager)
        assert "WeatherManager" in repr_str
        assert "sunny" in repr_str
        assert "spring" in repr_str
        assert "morning" in repr_str


class TestPropertySetters:
    """Tests for property setters with validation."""

    @pytest.fixture(autouse=True)
    def setup(self, load_system):
        """Load the weather system before each test."""
        self.ns = load_system("weather")
        self.WeatherManager = self.ns["WeatherManager"]
        self.WeatherType = self.ns["WeatherType"]
        self.Season = self.ns["Season"]
        self.TimeOfDay = self.ns["TimeOfDay"]

    def test_weather_property_setter_valid(self):
        """Test setting weather via property with valid value."""
        manager = self.WeatherManager()
        manager.current_weather = self.WeatherType.RAIN
        assert manager.current_weather == self.WeatherType.RAIN

    def test_weather_property_setter_invalid(self):
        """Test setting weather via property with invalid value raises error."""
        manager = self.WeatherManager()
        with pytest.raises(ValueError):
            manager.current_weather = "tornado"

    def test_season_property_setter_valid(self):
        """Test setting season via property with valid value."""
        manager = self.WeatherManager()
        manager.current_season = self.Season.WINTER
        assert manager.current_season == self.Season.WINTER

    def test_season_property_setter_invalid(self):
        """Test setting season via property with invalid value raises error."""
        manager = self.WeatherManager()
        with pytest.raises(ValueError):
            manager.current_season = "monsoon"

    def test_time_property_setter_valid(self):
        """Test setting time via property with valid value."""
        manager = self.WeatherManager()
        manager.current_time = self.TimeOfDay.NIGHT
        assert manager.current_time == self.TimeOfDay.NIGHT

    def test_time_property_setter_invalid(self):
        """Test setting time via property with invalid value raises error."""
        manager = self.WeatherManager()
        with pytest.raises(ValueError):
            manager.current_time = "midnight"

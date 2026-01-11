"""
Tests for the minigames system.

Tests all minigame types:
- Number guessing logic
- Rock-Paper-Scissors outcomes
- Memory match game logic
- QTE timing mechanics
- Pattern puzzle matching
"""
import pytest
import time
from unittest.mock import patch


class TestMinigameBase:
    """Tests for the MinigameBase class."""

    def test_initialization(self, load_system):
        """Test default initialization values."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]("Test Game")

        assert game.name == "Test Game"
        assert game.score == 0
        assert game.high_score == 0
        assert game.difficulty == game.MEDIUM
        assert game.is_active is False
        assert game.result is None
        assert game.attempts == 0
        assert game.wins == 0
        assert game.losses == 0

    def test_start_game(self, load_system):
        """Test starting a game."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()

        game.start()

        assert game.is_active is True
        assert game.result is None
        assert game.attempts == 1

    def test_end_game_win(self, load_system):
        """Test ending a game with a win."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()
        game.start()
        game.score = 100

        game.end(won=True)

        assert game.is_active is False
        assert game.result == "win"
        assert game.wins == 1
        assert game.high_score == 100

    def test_end_game_lose(self, load_system):
        """Test ending a game with a loss."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()
        game.start()

        game.end(won=False)

        assert game.is_active is False
        assert game.result == "lose"
        assert game.losses == 1

    def test_high_score_only_updates_on_higher(self, load_system):
        """Test high score only updates when beaten."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()

        game.start()
        game.score = 100
        game.end(won=True)
        assert game.high_score == 100

        game.start()
        game.score = 50
        game.end(won=True)
        assert game.high_score == 100  # Should not decrease

    def test_set_difficulty(self, load_system):
        """Test setting difficulty levels."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()

        game.set_difficulty(game.EASY)
        assert game.difficulty == 1

        game.set_difficulty(game.HARD)
        assert game.difficulty == 3

        # Invalid difficulty should not change
        game.set_difficulty(99)
        assert game.difficulty == 3

    def test_get_difficulty_name(self, load_system):
        """Test difficulty name retrieval."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()

        game.set_difficulty(1)
        assert game.get_difficulty_name() == "Easy"

        game.set_difficulty(2)
        assert game.get_difficulty_name() == "Medium"

        game.set_difficulty(3)
        assert game.get_difficulty_name() == "Hard"

    def test_add_score(self, load_system):
        """Test score addition."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()

        game.add_score(50)
        assert game.score == 50

        game.add_score(25)
        assert game.score == 75

    def test_get_win_rate(self, load_system):
        """Test win rate calculation."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()

        # No attempts
        assert game.get_win_rate() == 0

        # 1 win, 1 loss = 50%
        game.start()
        game.end(won=True)
        game.start()
        game.end(won=False)
        assert game.get_win_rate() == 50

    def test_reset(self, load_system):
        """Test game reset."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()
        game.score = 100
        game.result = "win"

        game.reset()

        assert game.score == 0
        assert game.result is None


class TestNumberGuessingGame:
    """Tests for the NumberGuessingGame class."""

    def test_initialization(self, load_system):
        """Test number guessing game initialization."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()

        assert game.name == "Number Guessing"
        assert game.target == 0
        assert game.min_num == 1
        assert game.max_num == 100
        assert game.guesses_left == 7

    def test_start_easy_difficulty(self, load_system):
        """Test starting on easy difficulty."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.set_difficulty(game.EASY)

        game.start()

        assert game.min_num == 1
        assert game.max_num == 50
        assert game.max_guesses == 10
        assert game.guesses_left == 10
        assert game.min_num <= game.target <= game.max_num

    def test_start_hard_difficulty(self, load_system):
        """Test starting on hard difficulty."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.set_difficulty(game.HARD)

        game.start()

        assert game.min_num == 1
        assert game.max_num == 200
        assert game.max_guesses == 6
        assert game.guesses_left == 6

    def test_correct_guess(self, load_system):
        """Test making a correct guess."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.start()
        game.target = 50

        hint = game.make_guess(50)

        assert "Correct" in hint
        assert game.result == "win"
        assert game.is_active is False
        assert game.score > 0

    def test_guess_too_low_far(self, load_system):
        """Test guess that is much too low."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.start()
        game.target = 75

        hint = game.make_guess(50)

        assert "Much higher" in hint
        assert game.is_active is True

    def test_guess_too_low_medium(self, load_system):
        """Test guess that is moderately too low."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.start()
        game.target = 70

        hint = game.make_guess(55)

        assert "Higher!" in hint
        assert "Much" not in hint

    def test_guess_too_low_close(self, load_system):
        """Test guess that is slightly too low."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.start()
        game.target = 55

        hint = game.make_guess(50)

        assert "little higher" in hint

    def test_guess_too_high_far(self, load_system):
        """Test guess that is much too high."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.start()
        game.target = 25

        hint = game.make_guess(50)

        assert "Much lower" in hint

    def test_guess_too_high_medium(self, load_system):
        """Test guess that is moderately too high."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.start()
        game.target = 30

        hint = game.make_guess(45)

        assert "Lower!" in hint
        assert "Much" not in hint

    def test_guess_too_high_close(self, load_system):
        """Test guess that is slightly too high."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.start()
        game.target = 45

        hint = game.make_guess(50)

        assert "little lower" in hint

    def test_run_out_of_guesses(self, load_system):
        """Test running out of guesses."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.start()
        game.target = 100
        game.guesses_left = 1

        hint = game.make_guess(1)

        assert "Out of guesses" in hint
        assert game.result == "lose"
        assert game.is_active is False

    def test_guess_history_tracking(self, load_system):
        """Test that guesses are tracked in history."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.start()
        game.target = 50

        game.make_guess(25)
        game.make_guess(75)

        assert game.guess_history == [25, 75]

    def test_guess_when_not_active(self, load_system):
        """Test making a guess when game is not active."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()

        hint = game.make_guess(50)

        assert hint == "Game not active!"

    def test_score_based_on_remaining_guesses(self, load_system):
        """Test that score increases with more remaining guesses."""
        ns = load_system("minigames")
        game = ns["NumberGuessingGame"]()
        game.set_difficulty(game.MEDIUM)
        game.start()
        game.target = 50

        # First guess correct = more points
        game.make_guess(50)
        score_with_many_guesses = game.score

        # Reset and try with fewer guesses
        game.reset()
        game.start()
        game.target = 50
        game.make_guess(25)
        game.make_guess(75)
        game.make_guess(60)
        game.make_guess(55)
        game.make_guess(52)
        game.make_guess(50)
        score_with_few_guesses = game.score

        assert score_with_many_guesses > score_with_few_guesses


class TestRockPaperScissorsGame:
    """Tests for the RockPaperScissorsGame class."""

    def test_initialization(self, load_system):
        """Test RPS game initialization."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()

        assert game.name == "Rock-Paper-Scissors"
        assert game.rounds_to_win == 3
        assert game.player_wins == 0
        assert game.npc_wins == 0

    def test_start_easy_difficulty(self, load_system):
        """Test starting on easy difficulty."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()
        game.set_difficulty(game.EASY)

        game.start()

        assert game.rounds_to_win == 2

    def test_start_hard_difficulty(self, load_system):
        """Test starting on hard difficulty."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()
        game.set_difficulty(game.HARD)

        game.start()

        assert game.rounds_to_win == 4

    def test_rock_beats_scissors(self, load_system):
        """Test rock beats scissors."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()
        game.start()

        import random
        original_choice = random.choice

        def mock_choice(choices):
            if choices == game.CHOICES:
                return game.SCISSORS
            return original_choice(choices)

        random.choice = mock_choice
        result = game.play_round(game.ROCK)
        random.choice = original_choice

        assert result == "win"
        assert game.player_wins == 1

    def test_paper_beats_rock(self, load_system):
        """Test paper beats rock."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()
        game.start()

        import random
        original_choice = random.choice

        def mock_choice(choices):
            if choices == game.CHOICES:
                return game.ROCK
            return original_choice(choices)

        random.choice = mock_choice
        result = game.play_round(game.PAPER)
        random.choice = original_choice

        assert result == "win"

    def test_scissors_beats_paper(self, load_system):
        """Test scissors beats paper."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()
        game.start()

        import random
        original_choice = random.choice

        def mock_choice(choices):
            if choices == game.CHOICES:
                return game.PAPER
            return original_choice(choices)

        random.choice = mock_choice
        result = game.play_round(game.SCISSORS)
        random.choice = original_choice

        assert result == "win"

    def test_rock_loses_to_paper(self, load_system):
        """Test rock loses to paper."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()
        game.start()

        import random
        original_choice = random.choice

        def mock_choice(choices):
            if choices == game.CHOICES:
                return game.PAPER
            return original_choice(choices)

        random.choice = mock_choice
        result = game.play_round(game.ROCK)
        random.choice = original_choice

        assert result == "lose"
        assert game.npc_wins == 1

    def test_tie_result(self, load_system):
        """Test tie when both choose same."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()
        game.start()

        import random
        original_choice = random.choice

        def mock_choice(choices):
            if choices == game.CHOICES:
                return game.ROCK
            return original_choice(choices)

        random.choice = mock_choice
        result = game.play_round(game.ROCK)
        random.choice = original_choice

        assert result == "tie"
        assert game.player_wins == 0
        assert game.npc_wins == 0

    def test_player_wins_match(self, load_system):
        """Test player winning the match."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()
        game.set_difficulty(game.EASY)  # Only need 2 wins
        game.start()

        import random
        original_choice = random.choice

        def mock_choice(choices):
            if choices == game.CHOICES:
                return game.SCISSORS
            return original_choice(choices)

        random.choice = mock_choice

        game.play_round(game.ROCK)
        game.play_round(game.ROCK)

        random.choice = original_choice

        assert game.result == "win"
        assert game.is_active is False

    def test_npc_wins_match(self, load_system):
        """Test NPC winning the match."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()
        game.set_difficulty(game.EASY)  # Only need 2 wins
        game.start()

        import random
        original_choice = random.choice

        def mock_choice(choices):
            if choices == game.CHOICES:
                return game.PAPER
            return original_choice(choices)

        random.choice = mock_choice

        game.play_round(game.ROCK)
        game.play_round(game.ROCK)

        random.choice = original_choice

        assert game.result == "lose"
        assert game.is_active is False

    def test_get_counter(self, load_system):
        """Test getting the counter to a choice."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()

        assert game._get_counter(game.ROCK) == game.PAPER
        assert game._get_counter(game.PAPER) == game.SCISSORS
        assert game._get_counter(game.SCISSORS) == game.ROCK

    def test_beats_helper(self, load_system):
        """Test the _beats helper method."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()

        assert game._beats(game.ROCK, game.SCISSORS) is True
        assert game._beats(game.PAPER, game.ROCK) is True
        assert game._beats(game.SCISSORS, game.PAPER) is True

        assert game._beats(game.ROCK, game.PAPER) is False
        assert game._beats(game.ROCK, game.ROCK) is False

    def test_play_when_not_active(self, load_system):
        """Test playing when game is not active."""
        ns = load_system("minigames")
        game = ns["RockPaperScissorsGame"]()

        result = game.play_round(game.ROCK)

        assert result is None


class TestMemoryCardGame:
    """Tests for the MemoryCardGame class."""

    def test_initialization(self, load_system):
        """Test memory game initialization."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()

        assert game.name == "Memory Match"
        assert game.grid_size == 4
        assert game.pairs_found == 0
        assert game.moves == 0

    def test_start_easy_difficulty(self, load_system):
        """Test starting on easy difficulty."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.set_difficulty(game.EASY)

        game.start()

        assert game.grid_size == 3
        assert game.total_pairs == 6
        assert len(game.cards) == 12  # 6 pairs

    def test_start_medium_difficulty(self, load_system):
        """Test starting on medium difficulty."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.set_difficulty(game.MEDIUM)

        game.start()

        assert game.grid_size == 4
        assert game.total_pairs == 8
        assert len(game.cards) == 16

    def test_start_hard_difficulty(self, load_system):
        """Test starting on hard difficulty."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.set_difficulty(game.HARD)

        game.start()

        assert game.total_pairs == 10
        assert len(game.cards) == 20

    def test_cards_are_pairs(self, load_system):
        """Test that cards contain valid pairs."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        # Count occurrences of each symbol
        from collections import Counter
        counts = Counter(game.cards)

        # Each symbol should appear exactly twice
        for count in counts.values():
            assert count == 2

    def test_pick_first_card(self, load_system):
        """Test picking the first card."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.start()

        result = game.pick_card(0)

        assert result == game.cards[0]
        assert game.first_pick == 0
        assert game.second_pick is None
        assert game.revealed[0] is True

    def test_pick_second_card(self, load_system):
        """Test picking the second card."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.start()

        game.pick_card(0)
        result = game.pick_card(1)

        assert result == game.cards[1]
        assert game.first_pick == 0
        assert game.second_pick == 1
        assert game.moves == 1
        assert game.can_pick is False

    def test_cannot_pick_revealed_card(self, load_system):
        """Test that revealed cards cannot be picked."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.start()

        game.pick_card(0)
        result = game.pick_card(0)  # Try to pick same card

        assert result is None
        assert game.second_pick is None

    def test_check_match_success(self, load_system):
        """Test checking a successful match."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.start()

        # Find a matching pair
        first_idx = 0
        first_card = game.cards[0]
        second_idx = None
        for i, card in enumerate(game.cards):
            if i != 0 and card == first_card:
                second_idx = i
                break

        game.pick_card(first_idx)
        game.pick_card(second_idx)

        result = game.check_match()

        assert result is True
        assert game.matched[first_idx] is True
        assert game.matched[second_idx] is True
        assert game.pairs_found == 1
        assert game.score > 0
        assert game.can_pick is True

    def test_check_match_failure(self, load_system):
        """Test checking a failed match."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.start()

        # Find non-matching cards
        first_idx = 0
        first_card = game.cards[0]
        second_idx = None
        for i, card in enumerate(game.cards):
            if card != first_card:
                second_idx = i
                break

        game.pick_card(first_idx)
        game.pick_card(second_idx)

        result = game.check_match()

        assert result is False
        assert game.matched[first_idx] is False
        assert game.matched[second_idx] is False

    def test_hide_unmatched(self, load_system):
        """Test hiding unmatched cards."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.start()

        # Find non-matching cards
        first_idx = 0
        first_card = game.cards[0]
        second_idx = None
        for i, card in enumerate(game.cards):
            if card != first_card:
                second_idx = i
                break

        game.pick_card(first_idx)
        game.pick_card(second_idx)
        game.check_match()

        game.hide_unmatched()

        assert game.revealed[first_idx] is False
        assert game.revealed[second_idx] is False
        assert game.first_pick is None
        assert game.second_pick is None
        assert game.can_pick is True

    def test_win_game(self, load_system):
        """Test winning the memory game."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        # Match all pairs
        matched_indices = set()
        while game.is_active:
            # Find unmatched pair
            for i, card in enumerate(game.cards):
                if i in matched_indices:
                    continue
                for j, other_card in enumerate(game.cards):
                    if j <= i or j in matched_indices:
                        continue
                    if card == other_card:
                        game.pick_card(i)
                        game.pick_card(j)
                        game.check_match()
                        matched_indices.add(i)
                        matched_indices.add(j)
                        break
                break

        assert game.result == "win"
        assert game.pairs_found == game.total_pairs

    def test_get_card_display(self, load_system):
        """Test getting card display values."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.start()

        # Unrevealed card
        assert game.get_card_display(0) == "?"

        # Revealed card
        game.pick_card(0)
        assert game.get_card_display(0) == game.cards[0]

    def test_pick_invalid_index(self, load_system):
        """Test picking a card with invalid index."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()
        game.start()

        assert game.pick_card(-1) is None
        assert game.pick_card(100) is None

    def test_pick_when_not_active(self, load_system):
        """Test picking when game is not active."""
        ns = load_system("minigames")
        game = ns["MemoryCardGame"]()

        result = game.pick_card(0)

        assert result is None


class TestQTESystem:
    """Tests for the QTESystem class."""

    def test_initialization(self, load_system):
        """Test QTE system initialization."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()

        assert qte.name == "Quick-Time Event"
        assert qte.time_limit == 2.0
        assert qte.max_failures == 3
        assert qte.sequence_length == 5

    def test_start_easy_difficulty(self, load_system):
        """Test starting on easy difficulty."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.set_difficulty(qte.EASY)

        qte.start()

        assert qte.time_limit == 3.0
        assert qte.sequence_length == 4
        assert qte.max_failures == 4
        assert len(qte.sequence) == 4

    def test_start_hard_difficulty(self, load_system):
        """Test starting on hard difficulty."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.set_difficulty(qte.HARD)

        qte.start()

        assert qte.time_limit == 1.5
        assert qte.sequence_length == 8
        assert qte.max_failures == 2
        assert len(qte.sequence) == 8

    def test_sequence_contains_valid_keys(self, load_system):
        """Test that sequence only contains valid keys."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.start()

        for key in qte.sequence:
            assert key in qte.KEYS

    def test_correct_input(self, load_system):
        """Test correct key input."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.start()

        correct_key = qte.current_key
        result = qte.check_input(correct_key)

        assert result == "success"
        assert qte.successes == 1
        assert qte.score > 0

    def test_wrong_input(self, load_system):
        """Test wrong key input."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.start()

        # Find a wrong key
        correct_key = qte.current_key
        wrong_keys = [k for k in qte.KEYS if k != correct_key]
        wrong_key = wrong_keys[0]

        result = qte.check_input(wrong_key)

        assert result == "wrong"
        assert qte.failures == 1

    def test_timeout(self, load_system):
        """Test timeout on input."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.start()

        # Simulate time passing beyond limit
        qte.start_time = time.time() - qte.time_limit - 1

        result = qte.check_input(qte.current_key)

        assert result == "timeout"
        assert qte.failures == 1

    def test_fail_on_max_failures(self, load_system):
        """Test game ends on max failures."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.set_difficulty(qte.EASY)  # 4 max failures
        qte.start()

        # Get wrong key repeatedly
        for _ in range(4):
            if qte.is_active:
                correct_key = qte.current_key
                wrong_keys = [k for k in qte.KEYS if k != correct_key]
                qte.check_input(wrong_keys[0])

        assert qte.result == "lose"
        assert qte.is_active is False

    def test_win_by_completing_sequence(self, load_system):
        """Test winning by completing the sequence."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.set_difficulty(qte.EASY)
        qte.start()

        # Complete all inputs correctly
        while qte.is_active:
            correct_key = qte.current_key
            qte.check_input(correct_key)

        assert qte.result == "win"
        assert qte.successes == qte.sequence_length

    def test_quick_response_bonus(self, load_system):
        """Test bonus points for quick response."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.set_difficulty(qte.MEDIUM)
        qte.start()

        # Immediate response (within half time limit)
        correct_key = qte.current_key
        qte.check_input(correct_key)
        score_quick = qte.score

        # Reset and try slow response
        qte.reset()
        qte.start()
        qte.start_time = time.time() - (qte.time_limit / 2) - 0.1
        correct_key = qte.current_key
        qte.check_input(correct_key)
        score_slow = qte.score

        assert score_quick > score_slow

    def test_get_time_remaining(self, load_system):
        """Test getting remaining time."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.start()

        time_remaining = qte.get_time_remaining()

        assert 0 < time_remaining <= qte.time_limit

    def test_get_time_remaining_when_not_waiting(self, load_system):
        """Test time remaining when not waiting."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()
        qte.start()
        qte.is_waiting = False

        assert qte.get_time_remaining() == 0

    def test_get_key_display(self, load_system):
        """Test key display formatting."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()

        assert qte.get_key_display("up") == "[UP]"
        assert qte.get_key_display("down") == "[DOWN]"
        assert qte.get_key_display("action") == "[ACTION]"

    def test_check_input_when_not_active(self, load_system):
        """Test input when game not active."""
        ns = load_system("minigames")
        qte = ns["QTESystem"]()

        result = qte.check_input("up")

        assert result is None


class TestPatternMatchGame:
    """Tests for the PatternMatchGame class."""

    def test_initialization(self, load_system):
        """Test pattern game initialization."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()

        assert game.name == "Pattern Match"
        assert game.max_length == 10
        assert len(game.pattern) == 0

    def test_start_easy_difficulty(self, load_system):
        """Test starting on easy difficulty."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.set_difficulty(game.EASY)

        game.start()

        assert game.max_length == 6
        assert len(game.pattern) == 1

    def test_start_hard_difficulty(self, load_system):
        """Test starting on hard difficulty."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.set_difficulty(game.HARD)

        game.start()

        assert game.max_length == 15
        assert len(game.pattern) == 1

    def test_pattern_contains_valid_colors(self, load_system):
        """Test that pattern only contains valid colors."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.start()

        for color in game.pattern:
            assert color in game.COLORS

    def test_get_next_pattern_color(self, load_system):
        """Test getting next pattern color during display."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.start()

        color = game.get_next_pattern_color()

        assert color == game.pattern[0]
        assert game.showing_pattern is False  # Only one color in initial pattern

    def test_correct_color_input(self, load_system):
        """Test correct color input."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.start()
        game.showing_pattern = False

        correct_color = game.pattern[0]
        result = game.input_color(correct_color)

        assert result == "next_round"
        assert len(game.pattern) == 2  # Pattern grows
        assert game.score > 0

    def test_wrong_color_input(self, load_system):
        """Test wrong color input."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.start()
        game.showing_pattern = False

        correct_color = game.pattern[0]
        wrong_colors = [c for c in game.COLORS if c != correct_color]

        result = game.input_color(wrong_colors[0])

        assert result == "wrong"
        assert game.result == "lose"
        assert game.is_active is False

    def test_partial_correct_input(self, load_system):
        """Test partial correct input in longer pattern."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.start()

        # Add more colors to pattern
        game.pattern = ["red", "blue", "green"]
        game.current_length = 3
        game.player_input = []
        game.showing_pattern = False

        result1 = game.input_color("red")
        assert result1 == "correct"

        result2 = game.input_color("blue")
        assert result2 == "correct"

        # Last input completes the round
        result3 = game.input_color("green")
        assert result3 == "next_round"

    def test_cannot_input_during_pattern_display(self, load_system):
        """Test that input is blocked during pattern display."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.start()
        game.showing_pattern = True

        result = game.input_color("red")

        assert result is None

    def test_win_by_completing_max_pattern(self, load_system):
        """Test winning by completing maximum pattern length."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.set_difficulty(game.EASY)  # max_length = 6
        game.start()
        game.showing_pattern = False

        # Complete patterns until max length
        while game.is_active:
            game.showing_pattern = False
            for color in game.pattern:
                if game.is_active:
                    game.input_color(color)

        assert game.result == "win"

    def test_pattern_grows_each_round(self, load_system):
        """Test that pattern grows after each successful round."""
        ns = load_system("minigames")
        game = ns["PatternMatchGame"]()
        game.start()
        game.showing_pattern = False

        initial_length = len(game.pattern)
        game.input_color(game.pattern[0])

        assert len(game.pattern) == initial_length + 1


class TestRewardSystem:
    """Tests for the RewardSystem class."""

    def test_no_reward_on_loss(self, load_system):
        """Test that losing gives no rewards."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()
        game.start()
        game.end(won=False)

        rewards = ns["RewardSystem"].calculate_reward(game)

        assert rewards["gold"] == 0
        assert rewards["xp"] == 0
        assert rewards["items"] == []

    def test_base_reward_on_win(self, load_system):
        """Test base rewards on winning."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()
        game.set_difficulty(game.EASY)
        game.start()
        game.end(won=True)

        rewards = ns["RewardSystem"].calculate_reward(game, base_gold=10, base_xp=5)

        # EASY = 1, so multiplier is 1
        assert rewards["gold"] == 10  # 10 * 1 + 0 (no score bonus)
        assert rewards["xp"] == 5     # 5 * 1 + 0

    def test_difficulty_multiplier(self, load_system):
        """Test that difficulty increases rewards."""
        ns = load_system("minigames")
        RewardSystem = ns["RewardSystem"]
        MinigameBase = ns["MinigameBase"]

        easy_game = MinigameBase()
        easy_game.set_difficulty(easy_game.EASY)
        easy_game.start()
        easy_game.end(won=True)

        hard_game = MinigameBase()
        hard_game.set_difficulty(hard_game.HARD)
        hard_game.start()
        hard_game.end(won=True)

        easy_rewards = RewardSystem.calculate_reward(easy_game)
        hard_rewards = RewardSystem.calculate_reward(hard_game)

        assert hard_rewards["gold"] > easy_rewards["gold"]
        assert hard_rewards["xp"] > easy_rewards["xp"]

    def test_score_bonus(self, load_system):
        """Test score-based bonus rewards."""
        ns = load_system("minigames")
        game = ns["MinigameBase"]()
        game.set_difficulty(game.EASY)
        game.start()
        game.score = 100  # Should add 10 gold bonus (100 // 10)
        game.end(won=True)

        rewards = ns["RewardSystem"].calculate_reward(game, base_gold=10, base_xp=5)

        assert rewards["gold"] == 20  # 10 * 1 + 10
        assert rewards["xp"] == 10    # 5 * 1 + 5


class TestSlidingPuzzleGame:
    """Tests for the SlidingPuzzleGame class."""

    def test_initialization(self, load_system):
        """Test sliding puzzle initialization."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()

        assert game.name == "Sliding Puzzle"
        assert game.size == 3
        assert game.moves == 0

    def test_start_easy_difficulty(self, load_system):
        """Test starting on easy difficulty."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.EASY)

        game.start()

        assert game.size == 3
        assert game.target_moves == 20
        assert len(game.tiles) == 9

    def test_start_hard_difficulty(self, load_system):
        """Test starting on hard difficulty."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.HARD)

        game.start()

        assert game.size == 4
        assert game.target_moves == 30
        assert len(game.tiles) == 16

    def test_tiles_contain_correct_values(self, load_system):
        """Test that tiles contain correct numbers."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.start()

        expected = set(range(game.size * game.size))
        actual = set(game.tiles)

        assert expected == actual

    def test_valid_moves(self, load_system):
        """Test getting valid moves."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        # Force empty position to center for predictable test
        game.tiles = [1, 2, 3, 4, 0, 5, 6, 7, 8]
        game.empty_pos = 4

        valid_moves = game._get_valid_moves()

        # Center position should have 4 valid moves
        assert len(valid_moves) == 4
        assert 1 in valid_moves  # above
        assert 7 in valid_moves  # below
        assert 3 in valid_moves  # left
        assert 5 in valid_moves  # right

    def test_corner_valid_moves(self, load_system):
        """Test valid moves from corner."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        # Force empty to top-left corner
        game.tiles = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        game.empty_pos = 0

        valid_moves = game._get_valid_moves()

        assert len(valid_moves) == 2
        assert 1 in valid_moves  # right
        assert 3 in valid_moves  # below

    def test_move_tile(self, load_system):
        """Test moving a tile."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        # Set up a known state
        game.tiles = [1, 2, 3, 4, 0, 5, 6, 7, 8]
        game.empty_pos = 4

        result = game.move_tile(1)  # Move tile above empty

        assert result is True
        assert game.tiles[4] == 2  # Tile 2 moved down
        assert game.tiles[1] == 0  # Empty moved up
        assert game.empty_pos == 1
        assert game.moves == 1

    def test_cannot_move_invalid_tile(self, load_system):
        """Test that invalid tiles cannot be moved."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        game.tiles = [1, 2, 3, 4, 0, 5, 6, 7, 8]
        game.empty_pos = 4

        result = game.move_tile(0)  # Corner tile, not adjacent

        assert result is False
        assert game.moves == 0

    def test_is_solved(self, load_system):
        """Test solved state detection."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        # Set to solved state
        game.tiles = [1, 2, 3, 4, 5, 6, 7, 8, 0]

        assert game._is_solved() is True

        # Unsolved state
        game.tiles = [1, 2, 3, 4, 5, 6, 7, 0, 8]

        assert game._is_solved() is False

    def test_win_on_solve(self, load_system):
        """Test game ends on solving puzzle."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        # One move away from solved
        game.tiles = [1, 2, 3, 4, 5, 6, 7, 0, 8]
        game.empty_pos = 7

        game.move_tile(8)

        assert game.result == "win"
        assert game.is_active is False
        assert game.score > 0

    def test_bonus_for_few_moves(self, load_system):
        """Test bonus score for fewer moves."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        # Solve with few moves
        game.tiles = [1, 2, 3, 4, 5, 6, 7, 0, 8]
        game.empty_pos = 7
        game.moves = 5  # Well under target

        game.move_tile(8)

        score_few_moves = game.score

        # Reset and solve with many moves
        game.reset()
        game.start()
        game.tiles = [1, 2, 3, 4, 5, 6, 7, 0, 8]
        game.empty_pos = 7
        game.moves = 50  # Over target

        game.move_tile(8)

        score_many_moves = game.score

        assert score_few_moves > score_many_moves

    def test_get_tile(self, load_system):
        """Test getting tile display value."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.start()

        game.tiles = [1, 0, 2, 3, 4, 5, 6, 7, 8]

        assert game.get_tile(0) == 1
        assert game.get_tile(1) == ""  # Empty tile
        assert game.get_tile(2) == 2

    def test_can_move(self, load_system):
        """Test checking if tile can move."""
        ns = load_system("minigames")
        game = ns["SlidingPuzzleGame"]()
        game.set_difficulty(game.EASY)
        game.start()

        game.tiles = [1, 2, 3, 4, 0, 5, 6, 7, 8]
        game.empty_pos = 4

        assert game.can_move(1) is True   # Adjacent
        assert game.can_move(0) is False  # Not adjacent
        assert game.can_move(8) is False  # Not adjacent
